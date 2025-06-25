"""
User Communication Service
Ensures all errors and important messages reach the UI
"""
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class UserCommunicationService:
    """Centralized service for user-facing communications"""
    
    def __init__(self):
        self.error_translations = {
            # SSL/Network errors
            "SSL error": "The app needs to connect to external servers. We're fixing the security settings...",
            "certificate": "Security certificate issue detected. Adding necessary permissions...",
            "transport security": "Network security settings need adjustment. Fixing now...",
            "Failed to load": "The app couldn't fetch data from the server. Checking network settings...",
            "api.quotable.io": "Setting up access to quote API service...",
            "external API": "Configuring network permissions for external APIs...",
            
            # JSON/Parsing errors
            "Invalid \\escape": "Code formatting issue detected. Applying automatic fixes...",
            "JSON": "Response formatting issue. Retrying with better formatting...",
            "parse error": "Code structure issue found. Attempting to fix...",
            
            # Build errors
            "Build failed": "The app didn't compile. Looking for issues to fix...",
            "syntax error": "Found a code error. Applying automatic correction...",
            "Type '.*' has no member": "Missing code component detected. Adding required code...",
            "Cannot find '.*' in scope": "Missing reference found. Fixing imports...",
            
            # Modification errors
            "No modifications processed": "Couldn't apply the changes. Trying a different approach...",
            "Files unchanged": "The AI didn't make the requested changes. Retrying with clearer instructions...",
            
            # Generic errors
            "Connection error": "Network connection issue. Retrying...",
            "Timeout": "Request took too long. Trying again...",
            "Internal server error": "Something went wrong on our end. Please try again.",
        }
        
        # Callback to send messages to UI
        self.notify_callback = None
    
    def set_notify_callback(self, callback):
        """Set the callback function to send messages to UI"""
        self.notify_callback = callback
    
    def translate_error(self, technical_error: str) -> str:
        """Translate technical error to user-friendly message"""
        error_lower = technical_error.lower()
        
        # Check each pattern
        for pattern, message in self.error_translations.items():
            if pattern.lower() in error_lower:
                return message
        
        # Default message
        if "error" in error_lower:
            return "An issue was detected. Working on a fix..."
        
        return "Processing your request..."
    
    async def notify_error(self, project_id: str, error: str, context: Optional[Dict[str, Any]] = None):
        """Send user-friendly error notification"""
        user_message = self.translate_error(error)
        
        # Add actionable guidance based on error type
        suggestion = self._get_suggestion(error)
        
        notification = {
            "type": "error",
            "message": user_message,
            "technical_details": error,  # For debug mode
            "status": "error",
        }
        
        if suggestion:
            notification["suggestion"] = suggestion
        
        if context:
            notification.update(context)
        
        logger.info(f"Sending user notification: {user_message}")
        logger.debug(f"Technical error: {error}")
        
        if self.notify_callback:
            await self.notify_callback(project_id, notification)
    
    def _get_suggestion(self, error: str) -> Optional[str]:
        """Get actionable suggestion for user based on error"""
        error_lower = error.lower()
        
        if "ssl" in error_lower or "certificate" in error_lower:
            if "localhost" in error_lower or "127.0.0.1" in error_lower:
                return "For local development servers, the app needs special permissions. Try using a public API instead, or ask me to add development server support."
            else:
                return "I'm adding security permissions for external APIs. This should be fixed automatically in the next build."
        
        elif "failed to load" in error_lower or "api" in error_lower:
            return "The external API might be down or require authentication. Try checking if the API is accessible in your browser."
        
        elif "json" in error_lower or "parse" in error_lower:
            return "The code format needs adjustment. I'll try a different approach automatically."
        
        elif "timeout" in error_lower:
            return "The request is taking too long. Try simplifying your app or breaking it into smaller features."
        
        elif "no modifications processed" in error_lower:
            return "Try describing your change differently, or ask for one specific change at a time."
        
        return None
    
    async def notify_status(self, project_id: str, message: str, status: str = "processing"):
        """Send status update to UI"""
        notification = {
            "type": "status",
            "message": message,
            "status": status
        }
        
        if self.notify_callback:
            await self.notify_callback(project_id, notification)
    
    async def notify_progress(self, project_id: str, step: str, progress: int, total: int = 100):
        """Send progress update to UI"""
        notification = {
            "type": "progress",
            "step": step,
            "progress": progress,
            "total": total,
            "message": f"{step}: {progress}% complete"
        }
        
        if self.notify_callback:
            await self.notify_callback(project_id, notification)
    
    async def notify_manual_action_needed(self, project_id: str, issue: str, action_required: str, how_to_fix: str):
        """Notify user when manual intervention is required"""
        notification = {
            "type": "manual_action",
            "message": f"⚠️ {issue}",
            "action_required": action_required,
            "how_to_fix": how_to_fix,
            "status": "needs_action"
        }
        
        logger.info(f"Manual action required: {issue}")
        
        if self.notify_callback:
            await self.notify_callback(project_id, notification)
    
    def should_show_technical_details(self, user_preferences: Optional[Dict] = None) -> bool:
        """Check if user wants to see technical details"""
        if not user_preferences:
            return False
        
        return user_preferences.get("debug_mode", False) or user_preferences.get("show_technical", False)


# Global instance
user_comm_service = UserCommunicationService()