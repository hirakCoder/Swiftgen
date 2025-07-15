"""
WebSocket Connection Manager for SwiftGen
Handles thread-safe WebSocket connections with automatic cleanup
"""

import asyncio
from typing import Dict, Set
from fastapi import WebSocket
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections with thread safety and cleanup"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_timestamps: Dict[str, datetime] = {}
        self.lock = asyncio.Lock()
        self.cleanup_interval = 300  # 5 minutes
        self.max_connection_age = 3600  # 1 hour
        
        # Start cleanup task
        asyncio.create_task(self._periodic_cleanup())
    
    async def connect(self, client_id: str, websocket: WebSocket):
        """Connect a new WebSocket client"""
        await websocket.accept()
        async with self.lock:
            # Disconnect existing connection if any
            if client_id in self.active_connections:
                await self.disconnect(client_id)
            
            self.active_connections[client_id] = websocket
            self.connection_timestamps[client_id] = datetime.now()
            logger.info(f"Client connected: {client_id}")
    
    async def disconnect(self, client_id: str):
        """Disconnect a WebSocket client"""
        async with self.lock:
            if client_id in self.active_connections:
                try:
                    websocket = self.active_connections[client_id]
                    await websocket.close()
                except Exception as e:
                    logger.error(f"Error closing connection {client_id}: {e}")
                
                del self.active_connections[client_id]
                if client_id in self.connection_timestamps:
                    del self.connection_timestamps[client_id]
                
                logger.info(f"Client disconnected: {client_id}")
    
    async def send_message(self, client_id: str, message: dict):
        """Send a message to a specific client"""
        async with self.lock:
            if client_id in self.active_connections:
                websocket = self.active_connections[client_id]
                try:
                    await websocket.send_json(message)
                    return True
                except Exception as e:
                    logger.error(f"Error sending message to {client_id}: {e}")
                    # Remove dead connection
                    await self._remove_connection(client_id)
                    return False
            else:
                logger.warning(f"Client not connected: {client_id}")
                return False
    
    async def broadcast(self, message: dict, exclude: Set[str] = None):
        """Broadcast a message to all connected clients"""
        exclude = exclude or set()
        disconnected = []
        
        async with self.lock:
            for client_id, websocket in self.active_connections.items():
                if client_id not in exclude:
                    try:
                        await websocket.send_json(message)
                    except Exception as e:
                        logger.error(f"Error broadcasting to {client_id}: {e}")
                        disconnected.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected:
            await self._remove_connection(client_id)
    
    async def _remove_connection(self, client_id: str):
        """Remove a connection without locking (internal use)"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.connection_timestamps:
            del self.connection_timestamps[client_id]
        logger.info(f"Removed stale connection: {client_id}")
    
    async def _periodic_cleanup(self):
        """Periodically clean up stale connections"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_stale_connections()
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {e}")
    
    async def _cleanup_stale_connections(self):
        """Remove connections older than max age"""
        now = datetime.now()
        stale_connections = []
        
        async with self.lock:
            for client_id, timestamp in self.connection_timestamps.items():
                age = (now - timestamp).total_seconds()
                if age > self.max_connection_age:
                    stale_connections.append(client_id)
        
        for client_id in stale_connections:
            logger.info(f"Removing stale connection: {client_id}")
            await self.disconnect(client_id)
    
    def get_active_connections(self) -> Dict[str, datetime]:
        """Get info about active connections"""
        return {
            client_id: self.connection_timestamps.get(client_id, datetime.now())
            for client_id in self.active_connections
        }
    
    async def health_check(self) -> Dict[str, any]:
        """Health check for connection manager"""
        active_count = len(self.active_connections)
        oldest_connection = None
        
        if self.connection_timestamps:
            oldest_timestamp = min(self.connection_timestamps.values())
            oldest_age = (datetime.now() - oldest_timestamp).total_seconds()
            oldest_connection = {
                'age_seconds': oldest_age,
                'timestamp': oldest_timestamp.isoformat()
            }
        
        return {
            'active_connections': active_count,
            'oldest_connection': oldest_connection,
            'status': 'healthy' if active_count < 100 else 'warning'
        }