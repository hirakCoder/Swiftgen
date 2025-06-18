"""
Debug Logger for SwiftGen AI
Comprehensive logging system for debugging complex app generation
"""

import logging
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class DebugLogger:
    """Enhanced logger for debugging file operations and app generation"""
    
    def __init__(self, project_id: str = None):
        self.project_id = project_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Set up logging directory
        self.log_dir = Path("backend/debug_logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Create project-specific log file
        self.log_file = self.log_dir / f"debug_{self.project_id}.log"
        
        # Configure logger
        self.logger = logging.getLogger(f"SwiftGen_{self.project_id}")
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers = []
        
        # File handler with detailed formatting
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler with simpler formatting
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        self.logger.info(f"=== Debug Logger Initialized for Project {self.project_id} ===")
    
    def log_app_generation_start(self, description: str, app_name: str, complexity: str = None):
        """Log the start of app generation"""
        self.logger.info("=" * 80)
        self.logger.info(f"APP GENERATION STARTED")
        self.logger.info(f"App Name: {app_name}")
        self.logger.info(f"Description: {description[:200]}...")
        if complexity:
            self.logger.info(f"Detected Complexity: {complexity}")
        self.logger.info("=" * 80)
    
    def log_llm_request(self, provider: str, prompt_size: int, is_retry: bool = False):
        """Log LLM request details"""
        action = "RETRY" if is_retry else "REQUEST"
        self.logger.info(f"LLM {action}: {provider} (prompt size: {prompt_size} chars)")
    
    def log_llm_response(self, provider: str, success: bool, response_size: int = 0, error: str = None):
        """Log LLM response details"""
        if success:
            self.logger.info(f"LLM RESPONSE: {provider} SUCCESS (response size: {response_size} chars)")
        else:
            self.logger.error(f"LLM RESPONSE: {provider} FAILED - {error}")
    
    def log_file_structure(self, files: List[Dict], phase: str = "generated"):
        """Log file structure details"""
        self.logger.info(f"\n--- FILE STRUCTURE ({phase}) ---")
        self.logger.info(f"Total files: {len(files)}")
        
        # Group files by directory
        structure = {}
        for file in files:
            path = file.get("path", "")
            content_size = len(file.get("content", ""))
            
            # Extract directory
            parts = path.split("/")
            if len(parts) > 2:  # e.g., Sources/Views/File.swift
                directory = f"{parts[0]}/{parts[1]}"
            else:
                directory = parts[0] if parts else "root"
            
            if directory not in structure:
                structure[directory] = []
            
            structure[directory].append({
                "file": os.path.basename(path),
                "full_path": path,
                "size": content_size
            })
        
        # Log organized structure
        for directory, files in sorted(structure.items()):
            self.logger.info(f"\n  {directory}/")
            for file_info in sorted(files, key=lambda x: x['file']):
                self.logger.info(f"    - {file_info['file']} ({file_info['size']} bytes)")
        
        self.logger.info("--- END FILE STRUCTURE ---\n")
    
    def log_file_write(self, file_path: str, success: bool, size: int = 0, error: str = None):
        """Log individual file write operation"""
        if success:
            self.logger.debug(f"FILE WRITE SUCCESS: {file_path} ({size} bytes)")
        else:
            self.logger.error(f"FILE WRITE FAILED: {file_path} - {error}")
    
    def log_file_verification(self, file_path: str, exists: bool, size: int = 0):
        """Log file verification result"""
        if exists:
            self.logger.debug(f"FILE VERIFIED: {file_path} exists ({size} bytes)")
        else:
            self.logger.warning(f"FILE MISSING: {file_path} not found on disk")
    
    def log_build_attempt(self, attempt: int, max_attempts: int):
        """Log build attempt"""
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"BUILD ATTEMPT {attempt}/{max_attempts}")
        self.logger.info(f"{'='*60}")
    
    def log_build_error(self, error: str, error_type: str = None):
        """Log build error with categorization"""
        if error_type:
            self.logger.error(f"BUILD ERROR ({error_type}): {error}")
        else:
            self.logger.error(f"BUILD ERROR: {error}")
    
    def log_error_recovery(self, action: str, details: Dict[str, Any] = None):
        """Log error recovery actions"""
        self.logger.info(f"ERROR RECOVERY: {action}")
        if details:
            for key, value in details.items():
                self.logger.info(f"  - {key}: {value}")
    
    def log_missing_files_analysis(self, missing_files: List[Dict]):
        """Log analysis of missing files"""
        if missing_files:
            self.logger.warning(f"\n--- MISSING FILES ANALYSIS ---")
            self.logger.warning(f"Found {len(missing_files)} missing files/types:")
            for file_info in missing_files:
                self.logger.warning(f"  - Type: {file_info.get('type')}")
                self.logger.warning(f"    Suggested Path: {file_info.get('suggested_path')}")
                self.logger.warning(f"    Category: {file_info.get('category')}")
            self.logger.warning("--- END MISSING FILES ---\n")
    
    def log_directory_structure(self, project_path: str):
        """Log the actual directory structure on disk"""
        self.logger.info(f"\n--- DISK DIRECTORY STRUCTURE ---")
        sources_path = os.path.join(project_path, "Sources")
        
        if os.path.exists(sources_path):
            for root, dirs, files in os.walk(sources_path):
                level = root.replace(sources_path, '').count(os.sep)
                indent = "  " * level
                self.logger.info(f"{indent}{os.path.basename(root)}/")
                
                subindent = "  " * (level + 1)
                for file in sorted(files):
                    if file.endswith('.swift'):
                        file_path = os.path.join(root, file)
                        size = os.path.getsize(file_path)
                        self.logger.info(f"{subindent}{file} ({size} bytes)")
        else:
            self.logger.error(f"Sources directory not found at {sources_path}")
        
        self.logger.info("--- END DISK STRUCTURE ---\n")
    
    def log_final_result(self, success: bool, warnings: List[str] = None, errors: List[str] = None):
        """Log final generation result"""
        self.logger.info("\n" + "="*80)
        if success:
            self.logger.info("APP GENERATION SUCCESSFUL")
        else:
            self.logger.error("APP GENERATION FAILED")
        
        if warnings:
            self.logger.warning(f"Warnings ({len(warnings)}):")
            for warning in warnings:
                self.logger.warning(f"  - {warning}")
        
        if errors:
            self.logger.error(f"Errors ({len(errors)}):")
            for error in errors:
                self.logger.error(f"  - {error}")
        
        self.logger.info("="*80 + "\n")
    
    def get_log_file_path(self) -> str:
        """Get the path to the current log file"""
        return str(self.log_file)
    
    def save_generation_summary(self, summary: Dict[str, Any]):
        """Save a JSON summary of the generation process"""
        summary_file = self.log_dir / f"summary_{self.project_id}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        self.logger.info(f"Generation summary saved to {summary_file}")

# Singleton instance for easy access
_debug_logger = None

def get_debug_logger(project_id: str = None) -> DebugLogger:
    """Get or create debug logger instance"""
    global _debug_logger
    if _debug_logger is None or project_id:
        _debug_logger = DebugLogger(project_id)
    return _debug_logger