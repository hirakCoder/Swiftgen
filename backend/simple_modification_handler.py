"""
Simple Modification Handler
Basic implementation for modification requests
"""

class SimpleModificationHandler:
    def __init__(self, claude_service=None):
        self.claude_service = claude_service
        self.max_retries = 3
        self.allow_partial_success = True
        
    def handle_modification(self, project_id: str, description: str, current_files: list):
        """Handle modification request"""
        # Basic implementation - just pass through to claude service
        if self.claude_service:
            return self.claude_service.modify_app(description, current_files)
        else:
            return {"success": False, "error": "No claude service available"}
