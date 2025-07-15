#!/usr/bin/env python3
"""
Comprehensive Logging System for SwiftGen
Provides structured logging across all components with real-time monitoring
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import threading
from collections import defaultdict, deque

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class Component(Enum):
    MAIN = "main"
    GENERATION = "generation"
    BUILD = "build_service"
    WEBSOCKET = "websocket"
    SIMULATOR = "simulator"
    MODIFICATION = "modification"
    ERROR_RECOVERY = "error_recovery"
    PROJECT_MANAGER = "project_manager"
    LLM_SERVICE = "llm_service"
    VALIDATION = "validation"

@dataclass
class LogEntry:
    timestamp: str
    component: str
    project_id: Optional[str]
    level: str
    event: str
    message: str
    details: Dict[str, Any]
    duration_ms: Optional[int] = None
    request_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

class SwiftGenLogger:
    """Comprehensive logging system with real-time monitoring"""
    
    def __init__(self, log_directory: str = "logs"):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(exist_ok=True)
        
        # In-memory log storage for real-time monitoring
        self.recent_logs: deque = deque(maxlen=1000)
        self.project_logs: Dict[str, List[LogEntry]] = defaultdict(list)
        
        # Metrics tracking
        self.metrics = {
            "events_by_component": defaultdict(int),
            "events_by_level": defaultdict(int),
            "events_by_project": defaultdict(int),
            "average_durations": defaultdict(list),
            "error_count": 0,
            "success_count": 0
        }
        
        # Lock for thread safety
        self.lock = threading.Lock()
        
        # Active project tracking
        self.active_projects: Dict[str, Dict[str, Any]] = {}
        
        # Setup file handlers
        self.setup_file_logging()
        
        # Start metrics collection
        self.start_metrics_collection()
    
    def setup_file_logging(self):
        """Setup file-based logging"""
        # Main log file
        main_log_file = self.log_directory / "swiftgen.log"
        
        # Component-specific log files
        self.component_log_files = {
            component.value: self.log_directory / f"{component.value}.log"
            for component in Component
        }
        
        # Error log file
        self.error_log_file = self.log_directory / "errors.log"
        
        # Performance log file
        self.performance_log_file = self.log_directory / "performance.log"
    
    def start_metrics_collection(self):
        """Start background metrics collection"""
        def collect_metrics():
            while True:
                self.save_metrics()
                time.sleep(60)  # Save metrics every minute
        
        metrics_thread = threading.Thread(target=collect_metrics, daemon=True)
        metrics_thread.start()
    
    def log(self, 
            component: Component, 
            level: LogLevel, 
            event: str, 
            message: str, 
            project_id: Optional[str] = None,
            details: Optional[Dict[str, Any]] = None,
            duration_ms: Optional[int] = None,
            request_id: Optional[str] = None):
        """Main logging method"""
        
        if details is None:
            details = {}
        
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            component=component.value,
            project_id=project_id,
            level=level.value,
            event=event,
            message=message,
            details=details,
            duration_ms=duration_ms,
            request_id=request_id
        )
        
        with self.lock:
            # Add to recent logs
            self.recent_logs.append(entry)
            
            # Add to project logs
            if project_id:
                self.project_logs[project_id].append(entry)
            
            # Update metrics
            self.metrics["events_by_component"][component.value] += 1
            self.metrics["events_by_level"][level.value] += 1
            if project_id:
                self.metrics["events_by_project"][project_id] += 1
            
            if duration_ms:
                self.metrics["average_durations"][event].append(duration_ms)
            
            if level == LogLevel.ERROR:
                self.metrics["error_count"] += 1
            elif event.endswith("_success") or event.endswith("_completed"):
                self.metrics["success_count"] += 1
        
        # Write to files
        self.write_to_files(entry)
        
        # Console output for important events
        if level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            print(f"[{level.value}] {component.value}: {message}")
        elif level == LogLevel.INFO and event in ["generation_started", "build_completed", "app_launched"]:
            print(f"[{level.value}] {component.value}: {message}")
    
    def write_to_files(self, entry: LogEntry):
        """Write log entry to appropriate files"""
        log_line = entry.to_json() + "\\n"
        
        # Main log file
        main_log_file = self.log_directory / "swiftgen.log"
        with open(main_log_file, "a") as f:
            f.write(log_line)
        
        # Component-specific log file
        component_log_file = self.component_log_files.get(entry.component)
        if component_log_file:
            with open(component_log_file, "a") as f:
                f.write(log_line)
        
        # Error log file
        if entry.level in ["ERROR", "CRITICAL"]:
            with open(self.error_log_file, "a") as f:
                f.write(log_line)
        
        # Performance log file
        if entry.duration_ms:
            with open(self.performance_log_file, "a") as f:
                f.write(log_line)
    
    def save_metrics(self):
        """Save current metrics to file"""
        metrics_file = self.log_directory / "metrics.json"
        
        # Calculate averages
        processed_metrics = dict(self.metrics)
        processed_metrics["average_durations"] = {
            event: sum(durations) / len(durations) if durations else 0
            for event, durations in self.metrics["average_durations"].items()
        }
        
        # Add timestamp
        processed_metrics["last_updated"] = datetime.now().isoformat()
        
        with open(metrics_file, "w") as f:
            json.dump(processed_metrics, f, indent=2)
    
    def get_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent log entries"""
        with self.lock:
            return [entry.to_dict() for entry in list(self.recent_logs)[-limit:]]
    
    def get_project_logs(self, project_id: str) -> List[Dict[str, Any]]:
        """Get logs for specific project"""
        with self.lock:
            return [entry.to_dict() for entry in self.project_logs.get(project_id, [])]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        with self.lock:
            # Calculate success rate
            total_attempts = self.metrics["success_count"] + self.metrics["error_count"]
            success_rate = (self.metrics["success_count"] / total_attempts * 100) if total_attempts > 0 else 0
            
            return {
                **dict(self.metrics),
                "success_rate": f"{success_rate:.1f}%",
                "total_events": sum(self.metrics["events_by_component"].values()),
                "active_projects": len(self.active_projects)
            }
    
    def start_project_tracking(self, project_id: str, app_name: str, description: str):
        """Start tracking a new project"""
        with self.lock:
            self.active_projects[project_id] = {
                "app_name": app_name,
                "description": description,
                "started_at": datetime.now().isoformat(),
                "status": "started",
                "current_phase": "initialization"
            }
        
        self.log(
            Component.PROJECT_MANAGER,
            LogLevel.INFO,
            "project_started",
            f"Started tracking project: {app_name}",
            project_id=project_id,
            details={"app_name": app_name, "description": description}
        )
    
    def update_project_status(self, project_id: str, status: str, phase: str = None):
        """Update project status"""
        with self.lock:
            if project_id in self.active_projects:
                self.active_projects[project_id]["status"] = status
                if phase:
                    self.active_projects[project_id]["current_phase"] = phase
                self.active_projects[project_id]["last_updated"] = datetime.now().isoformat()
    
    def end_project_tracking(self, project_id: str, success: bool, final_status: str = None):
        """End project tracking"""
        with self.lock:
            if project_id in self.active_projects:
                self.active_projects[project_id]["status"] = final_status or ("completed" if success else "failed")
                self.active_projects[project_id]["ended_at"] = datetime.now().isoformat()
                
                # Calculate total duration
                started_at = datetime.fromisoformat(self.active_projects[project_id]["started_at"])
                total_duration = (datetime.now() - started_at).total_seconds() * 1000
                
                self.log(
                    Component.PROJECT_MANAGER,
                    LogLevel.INFO if success else LogLevel.ERROR,
                    "project_completed" if success else "project_failed",
                    f"Project {project_id} {'completed' if success else 'failed'}",
                    project_id=project_id,
                    duration_ms=int(total_duration),
                    details={"success": success, "final_status": final_status}
                )
    
    def get_active_projects(self) -> Dict[str, Dict[str, Any]]:
        """Get currently active projects"""
        with self.lock:
            return dict(self.active_projects)

# Global logger instance
logger = SwiftGenLogger()

# Convenience functions for easy logging
def log_info(component: Component, event: str, message: str, project_id: str = None, **kwargs):
    logger.log(component, LogLevel.INFO, event, message, project_id=project_id, **kwargs)

def log_error(component: Component, event: str, message: str, project_id: str = None, **kwargs):
    logger.log(component, LogLevel.ERROR, event, message, project_id=project_id, **kwargs)

def log_warn(component: Component, event: str, message: str, project_id: str = None, **kwargs):
    logger.log(component, LogLevel.WARN, event, message, project_id=project_id, **kwargs)

def log_debug(component: Component, event: str, message: str, project_id: str = None, **kwargs):
    logger.log(component, LogLevel.DEBUG, event, message, project_id=project_id, **kwargs)

# Context manager for timing operations
class LogTimer:
    def __init__(self, component: Component, event: str, message: str, project_id: str = None):
        self.component = component
        self.event = event
        self.message = message
        self.project_id = project_id
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        log_info(self.component, f"{self.event}_started", f"Starting {self.message}", self.project_id)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = int((time.time() - self.start_time) * 1000)
        
        if exc_type:
            log_error(
                self.component, 
                f"{self.event}_failed", 
                f"Failed {self.message}: {exc_val}",
                self.project_id,
                duration_ms=duration_ms,
                details={"error": str(exc_val)}
            )
        else:
            log_info(
                self.component,
                f"{self.event}_completed",
                f"Completed {self.message}",
                self.project_id,
                duration_ms=duration_ms
            )

# Example usage:
# with LogTimer(Component.BUILD, "xcode_build", "Xcode build process", project_id):
#     # Build process here
#     pass