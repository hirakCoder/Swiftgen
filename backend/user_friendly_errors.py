"""
User-friendly error messages for SwiftGen AI
Converts technical build errors into helpful suggestions
"""

class UserFriendlyErrorHandler:
    """Converts technical errors to user-friendly messages"""
    
    def __init__(self):
        self.error_mappings = {
            "ios_version": {
                "pattern": "is only available in iOS 17",
                "message": "❌ The requested features require iOS 17+, but your app targets iOS 16",
                "suggestions": [
                    "I'll automatically use iOS 16-compatible alternatives",
                    "The app will work on more devices with iOS 16 support"
                ]
            },
            "persistence": {
                "pattern": "PersistenceController|managedObjectContext",
                "message": "❌ Core Data references found but not configured",
                "suggestions": [
                    "I'll remove Core Data and use simple in-memory storage",
                    "For persistence, UserDefaults will be used instead"
                ]
            },
            "string_literal": {
                "pattern": "unterminated string literal",
                "message": "❌ String formatting issues detected",
                "suggestions": [
                    "I'll fix the string quotes automatically",
                    "This is usually caused by special characters"
                ]
            },
            "exhaustive_switch": {
                "pattern": "switch must be exhaustive",
                "message": "❌ Incomplete switch statement found",
                "suggestions": [
                    "I'll add missing cases or a default handler",
                    "This ensures all possibilities are covered"
                ]
            }
        }
    
    def get_user_friendly_message(self, errors: list) -> dict:
        """Convert technical errors to user-friendly format"""
        
        # Analyze error types
        error_types = set()
        for error in errors:
            for error_type, mapping in self.error_mappings.items():
                if mapping["pattern"] in error:
                    error_types.add(error_type)
        
        if not error_types:
            return {
                "title": "❌ Build failed with technical errors",
                "message": "I'm working on fixing these automatically...",
                "suggestions": []
            }
        
        # iOS version errors are highest priority
        if "ios_version" in error_types:
            mapping = self.error_mappings["ios_version"]
            return {
                "title": mapping["message"],
                "message": "Your modification uses features from iOS 17+, but the app supports iOS 16+",
                "suggestions": mapping["suggestions"],
                "action": "I'll automatically replace with iOS 16-compatible code"
            }
        
        # Get the most relevant error
        primary_type = list(error_types)[0]
        mapping = self.error_mappings[primary_type]
        
        return {
            "title": mapping["message"],
            "message": f"Found {len(errors)} issues that I can fix automatically",
            "suggestions": mapping["suggestions"],
            "action": "Applying automatic fixes..."
        }
    
    def format_for_websocket(self, errors: list) -> str:
        """Format error message for WebSocket notification"""
        friendly = self.get_user_friendly_message(errors)
        
        message = f"{friendly['title']}\n\n"
        if friendly.get('message'):
            message += f"{friendly['message']}\n\n"
        
        if friendly.get('suggestions'):
            message += "What I'll do:\n"
            for suggestion in friendly['suggestions']:
                message += f"• {suggestion}\n"
        
        if friendly.get('action'):
            message += f"\n🔧 {friendly['action']}"
        
        return message