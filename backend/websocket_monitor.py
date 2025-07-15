#!/usr/bin/env python3
"""
WebSocket Monitoring and Debugging System
Comprehensive WebSocket connection monitoring and error handling
"""

import asyncio
import json
import time
import websockets
from typing import Dict, List, Optional, Any
from datetime import datetime
from comprehensive_logger import logger, log_info, log_error, log_warn, Component
from collections import defaultdict

class WebSocketMonitor:
    """Monitor and debug WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[Any]] = defaultdict(list)
        self.connection_stats = {
            "total_connections": 0,
            "active_connections": 0,
            "failed_connections": 0,
            "messages_sent": 0,
            "messages_failed": 0,
            "connection_errors": []
        }
        self.message_queue: Dict[str, List[Dict]] = defaultdict(list)
        self.heartbeat_interval = 30  # seconds
        
    def register_connection(self, project_id: str, websocket):
        """Register a new WebSocket connection"""
        self.active_connections[project_id].append({
            "websocket": websocket,
            "connected_at": datetime.now(),
            "last_heartbeat": datetime.now(),
            "messages_sent": 0,
            "messages_failed": 0
        })
        
        self.connection_stats["total_connections"] += 1
        self.connection_stats["active_connections"] += 1
        
        log_info(Component.WEBSOCKET, "connection_registered", 
                f"WebSocket connection registered for project {project_id}", 
                project_id=project_id,
                details={"active_connections": len(self.active_connections[project_id])})
    
    def remove_connection(self, project_id: str, websocket):
        """Remove a WebSocket connection"""
        if project_id in self.active_connections:
            self.active_connections[project_id] = [
                conn for conn in self.active_connections[project_id] 
                if conn["websocket"] != websocket
            ]
            
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
        
        self.connection_stats["active_connections"] -= 1
        
        log_info(Component.WEBSOCKET, "connection_removed", 
                f"WebSocket connection removed for project {project_id}", 
                project_id=project_id)
    
    async def send_message(self, project_id: str, message: Dict[str, Any]) -> bool:
        """Send message to all connections for a project"""
        if project_id not in self.active_connections:
            log_warn(Component.WEBSOCKET, "no_connections", 
                    f"No active connections for project {project_id}", 
                    project_id=project_id)
            
            # Queue message for when connection is established
            self.message_queue[project_id].append(message)
            return False
        
        success_count = 0
        total_connections = len(self.active_connections[project_id])
        
        for conn_info in self.active_connections[project_id].copy():
            try:
                await conn_info["websocket"].send(json.dumps(message))
                conn_info["messages_sent"] += 1
                conn_info["last_heartbeat"] = datetime.now()
                success_count += 1
                
                log_info(Component.WEBSOCKET, "message_sent", 
                        f"Message sent to {project_id}: {message.get('type', 'unknown')}", 
                        project_id=project_id,
                        details={"message_type": message.get("type"), "status": message.get("status")})
                
            except websockets.exceptions.ConnectionClosed:
                log_warn(Component.WEBSOCKET, "connection_closed", 
                        f"Connection closed for project {project_id}", 
                        project_id=project_id)
                self.remove_connection(project_id, conn_info["websocket"])
                
            except Exception as e:
                log_error(Component.WEBSOCKET, "message_failed", 
                         f"Failed to send message to {project_id}: {str(e)}", 
                         project_id=project_id,
                         details={"error": str(e), "message_type": message.get("type")})
                
                conn_info["messages_failed"] += 1
                self.connection_stats["messages_failed"] += 1
        
        self.connection_stats["messages_sent"] += success_count
        
        return success_count > 0
    
    async def send_queued_messages(self, project_id: str):
        """Send queued messages when connection is established"""
        if project_id in self.message_queue and self.message_queue[project_id]:
            queued_messages = self.message_queue[project_id].copy()
            self.message_queue[project_id].clear()
            
            log_info(Component.WEBSOCKET, "sending_queued_messages", 
                    f"Sending {len(queued_messages)} queued messages to {project_id}", 
                    project_id=project_id)
            
            for message in queued_messages:
                await self.send_message(project_id, message)
    
    async def heartbeat_check(self):
        """Check connection health and send heartbeats"""
        while True:
            current_time = datetime.now()
            
            for project_id, connections in list(self.active_connections.items()):
                for conn_info in connections.copy():
                    time_since_heartbeat = (current_time - conn_info["last_heartbeat"]).total_seconds()
                    
                    if time_since_heartbeat > self.heartbeat_interval:
                        try:
                            await conn_info["websocket"].send(json.dumps({
                                "type": "heartbeat",
                                "timestamp": current_time.isoformat()
                            }))
                            conn_info["last_heartbeat"] = current_time
                            
                        except Exception as e:
                            log_error(Component.WEBSOCKET, "heartbeat_failed", 
                                     f"Heartbeat failed for {project_id}: {str(e)}", 
                                     project_id=project_id)
                            self.remove_connection(project_id, conn_info["websocket"])
            
            await asyncio.sleep(self.heartbeat_interval)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get current connection statistics"""
        return {
            **self.connection_stats,
            "active_projects": len(self.active_connections),
            "queued_messages": sum(len(queue) for queue in self.message_queue.values()),
            "connections_per_project": {
                project_id: len(connections) 
                for project_id, connections in self.active_connections.items()
            }
        }
    
    def get_project_connection_info(self, project_id: str) -> Dict[str, Any]:
        """Get connection info for specific project"""
        if project_id not in self.active_connections:
            return {
                "connected": False,
                "queued_messages": len(self.message_queue.get(project_id, [])),
                "connections": 0
            }
        
        connections = self.active_connections[project_id]
        return {
            "connected": True,
            "connections": len(connections),
            "queued_messages": len(self.message_queue.get(project_id, [])),
            "connection_details": [
                {
                    "connected_at": conn["connected_at"].isoformat(),
                    "last_heartbeat": conn["last_heartbeat"].isoformat(),
                    "messages_sent": conn["messages_sent"],
                    "messages_failed": conn["messages_failed"]
                }
                for conn in connections
            ]
        }

# Global WebSocket monitor instance
ws_monitor = WebSocketMonitor()

# Enhanced WebSocket endpoint handler
async def handle_websocket_connection(websocket, project_id: str):
    """Enhanced WebSocket connection handler with comprehensive monitoring"""
    try:
        # Accept connection
        await websocket.accept()
        
        # Register connection
        ws_monitor.register_connection(project_id, websocket)
        
        # Send connection confirmation
        await ws_monitor.send_message(project_id, {
            "type": "connected",
            "message": "WebSocket connected successfully",
            "project_id": project_id,
            "timestamp": datetime.now().isoformat()
        })
        
        # Send any queued messages
        await ws_monitor.send_queued_messages(project_id)
        
        # Handle incoming messages
        while True:
            try:
                message = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
                if message == "ping":
                    await websocket.send("pong")
                    continue
                
                # Handle chat messages or other message types
                try:
                    msg_data = json.loads(message)
                    msg_type = msg_data.get("type")
                    
                    log_info(Component.WEBSOCKET, "message_received", 
                            f"Received {msg_type} message from {project_id}", 
                            project_id=project_id,
                            details={"message_type": msg_type})
                    
                    # Process message based on type
                    if msg_type == "chat":
                        # Handle chat message
                        pass
                    elif msg_type == "status_request":
                        # Send status update
                        pass
                        
                except json.JSONDecodeError:
                    # Handle plain text messages
                    log_info(Component.WEBSOCKET, "plain_text_message", 
                            f"Received plain text message from {project_id}", 
                            project_id=project_id)
                    
            except asyncio.TimeoutError:
                # Send heartbeat
                await ws_monitor.send_message(project_id, {
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat()
                })
                
    except websockets.exceptions.ConnectionClosed:
        log_info(Component.WEBSOCKET, "connection_closed", 
                f"WebSocket connection closed for {project_id}", 
                project_id=project_id)
        
    except Exception as e:
        log_error(Component.WEBSOCKET, "connection_error", 
                 f"WebSocket error for {project_id}: {str(e)}", 
                 project_id=project_id,
                 details={"error": str(e)})
        
        ws_monitor.connection_stats["failed_connections"] += 1
        ws_monitor.connection_stats["connection_errors"].append({
            "project_id": project_id,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
        
    finally:
        # Always remove connection
        ws_monitor.remove_connection(project_id, websocket)

# Start heartbeat monitoring
async def start_websocket_monitoring():
    """Start WebSocket monitoring background task"""
    await ws_monitor.heartbeat_check()

# Debug WebSocket connection
async def debug_websocket_connection(host: str = "localhost", port: int = 8000):
    """Debug WebSocket connection from client side"""
    try:
        uri = f"ws://{host}:{port}/ws/debug_test"
        
        log_info(Component.WEBSOCKET, "debug_connection_attempt", 
                f"Attempting WebSocket connection to {uri}")
        
        async with websockets.connect(uri) as websocket:
            log_info(Component.WEBSOCKET, "debug_connection_success", 
                    f"WebSocket connection successful to {uri}")
            
            # Send test message
            await websocket.send("ping")
            response = await websocket.recv()
            
            log_info(Component.WEBSOCKET, "debug_ping_success", 
                    f"Ping/pong successful: {response}")
            
            return True
            
    except Exception as e:
        log_error(Component.WEBSOCKET, "debug_connection_failed", 
                 f"WebSocket debug connection failed: {str(e)}",
                 details={"error": str(e), "host": host, "port": port})
        return False