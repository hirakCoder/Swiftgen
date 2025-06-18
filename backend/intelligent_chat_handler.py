"""
Intelligent Chat Handler for SwiftGen AI
Provides enhanced conversational capabilities and user support
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

class IntelligentChatHandler:
    """Enhanced chat handler with better understanding and empathy"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Enhanced intent patterns
        self.intent_patterns = {
            "greeting": [
                r"\b(hi|hello|hey|good morning|good afternoon|good evening)\b",
                r"\b(greetings|sup|howdy)\b"
            ],
            "help": [
                r"\b(help|assist|support|guide|how to|what can you|what do you)\b",
                r"\b(stuck|confused|don't understand|explain)\b",
                r"\b(documentation|docs|tutorial|example)\b"
            ],
            "status": [
                r"\b(status|progress|where|current|what's happening)\b",
                r"\b(show me|tell me|update)\b.*\b(status|progress)\b"
            ],
            "frustration": [
                r"\b(not working|broken|failed|error|crash|bug)\b",
                r"\b(frustrat|annoying|stupid|hate|suck|terrible)\b",
                r"\b(why|doesn't work|won't work|can't get)\b",
                r"\b(stuck|confused|lost|don't know)\b",
                r"[!]{2,}|[?]{2,}",  # Multiple exclamation or question marks
                r"\b(ugh|argh|damn|dammit|wtf|ffs)\b"
            ],
            "appreciation": [
                r"\b(thank|thanks|awesome|great|excellent|perfect)\b",
                r"\b(good job|well done|nice|cool|amazing)\b",
                r"(:\)|😊|👍|🎉|✨)"
            ],
            "modification": [
                r"\b(add|change|modify|update|remove|delete|fix|improve)\b",
                r"\b(make|adjust|tweak|enhance|refactor)\b",
                r"\b(can you|please|want|need|should|would like)\b.*\b(change|add|modify)\b"
            ],
            "creation": [
                r"\b(create|build|make|develop|generate|new)\b.*\b(app|application)\b",
                r"\b(start|begin|init)\b.*\b(project|app)\b"
            ],
            "question": [
                r"^(what|how|when|where|why|can|does|is|are)\b",
                r"\?$"  # Ends with question mark
            ],
            "command": [
                r"^/(\w+)",  # Slash commands
                r"^\!(\w+)"   # Bang commands
            ]
        }
        
        # Command definitions
        self.commands = {
            "/help": "Show available commands and usage guide",
            "/status": "Display current app generation status",
            "/reset": "Clear current project and start fresh",
            "/examples": "Show example app descriptions",
            "/features": "List features of current app",
            "/modify": "Tips for modifying your app",
            "/debug": "Show debug information",
            "/about": "Learn about SwiftGen AI"
        }
        
        # Response templates
        self.responses = {
            "greeting": [
                "👋 Hello! I'm SwiftGen AI, ready to help you create amazing iOS apps. What would you like to build today?",
                "Hi there! Ready to turn your app ideas into reality. What kind of iOS app are you thinking about?",
                "Welcome! I can help you create, modify, or enhance iOS applications. What's your project?"
            ],
            "help_no_project": """I'm here to help! Here's what I can do:

🚀 **Create a new app**: Just describe what you want!
   Examples:
   - "Create a todo list app"
   - "Build a weather app with forecasts"
   - "Make a social media app like Instagram"

💬 **Commands**:
   - `/help` - Show this help message
   - `/examples` - See example apps
   - `/about` - Learn more about SwiftGen

Just tell me what kind of app you'd like to create!""",
            "help_with_project": """I can help you modify your {app_name}! Here's what you can do:

✏️ **Modify your app**: Just tell me what to change!
   Examples:
   - "Add a dark mode toggle"
   - "Change the color scheme to blue"
   - "Add a search feature"

💬 **Commands**:
   - `/status` - Check app status
   - `/features` - List current features
   - `/reset` - Start over with a new app
   - `/modify` - Modification tips

What would you like to change?""",
            "frustration_responses": [
                "I understand this can be frustrating. Let me help you get back on track. What specific issue are you encountering?",
                "I'm sorry you're having trouble. Let's work through this together. Can you tell me what's not working as expected?",
                "No worries, we'll figure this out! What error or problem are you seeing?",
                "I hear you - sometimes things don't go as planned. What's the main challenge you're facing right now?"
            ],
            "encouragement": [
                "You're doing great! ",
                "Excellent choice! ",
                "That's a fantastic idea! ",
                "Love it! "
            ]
        }
        
        # Example apps for inspiration
        self.example_apps = [
            {
                "name": "Simple Apps",
                "examples": [
                    "Calculator with history",
                    "Timer with presets", 
                    "Todo list with categories",
                    "Weather app with forecasts"
                ]
            },
            {
                "name": "Medium Complexity",
                "examples": [
                    "Recipe manager with photos",
                    "Expense tracker with charts",
                    "Habit tracker with streaks",
                    "Note-taking app with folders"
                ]
            },
            {
                "name": "Complex Apps",
                "examples": [
                    "Food delivery app like DoorDash",
                    "Ride sharing app like Uber",
                    "E-commerce app like Amazon",
                    "Social media app like Instagram"
                ]
            }
        ]
    
    def analyze_message(self, message: str, has_project: bool = False) -> Dict:
        """Analyze message for intent, sentiment, and content"""
        message_lower = message.lower().strip()
        
        # Detect primary intent
        primary_intent = None
        confidence = 0.0
        
        # Check for commands first
        command_match = re.match(r'^/(\w+)', message)
        if command_match:
            command = f"/{command_match.group(1)}"
            if command in self.commands:
                return {
                    "intent": "command",
                    "command": command,
                    "sentiment": "neutral",
                    "confidence": 1.0
                }
        
        # Check other intents
        intent_scores = {}
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    score += 1
            if score > 0:
                intent_scores[intent] = score
        
        # Determine primary intent
        if intent_scores:
            primary_intent = max(intent_scores.items(), key=lambda x: x[1])[0]
            max_score = max(intent_scores.values())
            confidence = min(max_score / 3.0, 1.0)  # Normalize confidence
        
        # Detect sentiment
        sentiment = self._detect_sentiment(message_lower, intent_scores)
        
        # Extract entities
        entities = self._extract_entities(message)
        
        return {
            "intent": primary_intent,
            "sentiment": sentiment,
            "confidence": confidence,
            "entities": entities,
            "has_question": message.strip().endswith('?'),
            "message_length": len(message.split()),
            "original_message": message
        }
    
    def _detect_sentiment(self, message: str, intent_scores: Dict) -> str:
        """Detect overall sentiment of the message"""
        if intent_scores.get("frustration", 0) > 0:
            return "negative"
        elif intent_scores.get("appreciation", 0) > 0:
            return "positive"
        elif intent_scores.get("greeting", 0) > 0:
            return "positive"
        else:
            return "neutral"
    
    def _extract_entities(self, message: str) -> Dict:
        """Extract relevant entities from the message"""
        entities = {
            "app_types": [],
            "features": [],
            "ui_elements": []
        }
        
        # App type keywords
        app_keywords = {
            "todo": "todo list",
            "weather": "weather",
            "calculator": "calculator",
            "social": "social media",
            "delivery": "food delivery",
            "uber": "ride sharing",
            "amazon": "e-commerce",
            "instagram": "social media"
        }
        
        # Feature keywords
        feature_keywords = [
            "dark mode", "search", "filter", "sort", "login", "authentication",
            "notifications", "chat", "messaging", "payment", "location", "map"
        ]
        
        # UI element keywords
        ui_keywords = [
            "button", "list", "table", "navigation", "tab", "color", "theme",
            "animation", "gesture", "swipe", "scroll"
        ]
        
        message_lower = message.lower()
        
        # Extract app types
        for keyword, app_type in app_keywords.items():
            if keyword in message_lower:
                entities["app_types"].append(app_type)
        
        # Extract features
        for feature in feature_keywords:
            if feature in message_lower:
                entities["features"].append(feature)
        
        # Extract UI elements
        for ui in ui_keywords:
            if ui in message_lower:
                entities["ui_elements"].append(ui)
        
        return entities
    
    def generate_response(self, analysis: Dict, project_context: Optional[Dict] = None) -> Dict:
        """Generate intelligent response based on analysis"""
        intent = analysis.get("intent")
        sentiment = analysis.get("sentiment")
        
        # Handle commands
        if intent == "command":
            return self._handle_command(analysis["command"], project_context)
        
        # Handle frustration with empathy
        if sentiment == "negative":
            response = self._handle_frustration(analysis, project_context)
            return {"type": "support", "message": response}
        
        # Handle different intents
        if intent == "greeting":
            return {"type": "greeting", "message": self._get_random_response("greeting")}
        
        elif intent == "help":
            if project_context:
                message = self.responses["help_with_project"].format(
                    app_name=project_context.get("app_name", "your app")
                )
            else:
                message = self.responses["help_no_project"]
            return {"type": "help", "message": message}
        
        elif intent == "status" and project_context:
            return self._generate_status_response(project_context)
        
        elif intent == "creation" and not project_context:
            return {"type": "creation", "message": "Great! Tell me more about your app idea. What features should it have?"}
        
        elif intent == "modification" and project_context:
            return {"type": "modification", "message": "I'll help you modify your app. Processing your request..."}
        
        # Handle questions
        elif analysis.get("has_question"):
            return self._handle_question(analysis, project_context)
        
        # Default contextual response
        else:
            return self._generate_contextual_response(analysis, project_context)
    
    def _handle_command(self, command: str, project_context: Optional[Dict]) -> Dict:
        """Handle slash commands"""
        if command == "/help":
            if project_context:
                message = self.responses["help_with_project"].format(
                    app_name=project_context.get("app_name", "your app")
                )
            else:
                message = self.responses["help_no_project"]
            return {"type": "help", "message": message}
        
        elif command == "/examples":
            examples_text = "📱 **Example Apps You Can Create:**\n\n"
            for category in self.example_apps:
                examples_text += f"**{category['name']}:**\n"
                for example in category['examples']:
                    examples_text += f"  • {example}\n"
                examples_text += "\n"
            return {"type": "examples", "message": examples_text}
        
        elif command == "/status":
            if project_context:
                return self._generate_status_response(project_context)
            else:
                return {"type": "info", "message": "No active project. Create a new app to get started!"}
        
        elif command == "/about":
            about_text = """🤖 **SwiftGen AI - Your iOS Development Partner**

I'm an AI-powered iOS app generator that can:
• Create complete SwiftUI apps from descriptions
• Generate apps ranging from simple calculators to complex platforms
• Modify existing apps based on your requests
• Fix common iOS development issues automatically

Built with multiple AI models for the best results!"""
            return {"type": "info", "message": about_text}
        
        else:
            return {"type": "error", "message": f"Unknown command: {command}. Type /help for available commands."}
    
    def _handle_frustration(self, analysis: Dict, project_context: Optional[Dict]) -> str:
        """Handle frustrated users with empathy and solutions"""
        import random
        
        base_response = random.choice(self.responses["frustration_responses"])
        
        # Add specific help based on context
        if project_context and "error" in analysis["original_message"].lower():
            base_response += "\n\nIf you're seeing an error, try:\n"
            base_response += "• Describing the error message\n"
            base_response += "• Telling me what you were trying to do\n"
            base_response += "• Using /status to check the current state"
        
        elif not project_context and "create" in analysis["original_message"].lower():
            base_response += "\n\nTo create an app, try something like:\n"
            base_response += '• "Create a todo list app"\n'
            base_response += '• "Build a weather app"\n'
            base_response += "• Use /examples to see more options"
        
        return base_response
    
    def _handle_question(self, analysis: Dict, project_context: Optional[Dict]) -> Dict:
        """Handle questions intelligently"""
        message = analysis["original_message"].lower()
        
        # Common questions and answers
        if "what can you" in message or "what do you" in message:
            return {"type": "help", "message": self.responses["help_no_project"]}
        
        elif "how do i" in message or "how to" in message:
            if "create" in message or "build" in message:
                return {"type": "guide", "message": "To create an app, just describe it! For example: 'Create a fitness tracking app with workout logging and progress charts'"}
            elif "modify" in message or "change" in message:
                return {"type": "guide", "message": "To modify your app, just tell me what to change! For example: 'Add a dark mode toggle to settings'"}
        
        elif "can you" in message:
            # Extract what they're asking about
            entities = analysis.get("entities", {})
            if entities.get("app_types"):
                return {"type": "capability", "message": f"Yes! I can create {entities['app_types'][0]} apps. Just tell me what features you'd like!"}
        
        # Default question response
        return {"type": "question", "message": "That's a great question! Could you provide more details about what you'd like to know?"}
    
    def _generate_status_response(self, project_context: Dict) -> Dict:
        """Generate detailed status response"""
        status = f"📊 **Current Project Status**\n\n"
        status += f"**App Name**: {project_context.get('app_name', 'Unknown')}\n"
        status += f"**Type**: {project_context.get('description', 'iOS App')[:50]}...\n"
        
        if project_context.get('features'):
            status += f"\n**Features**:\n"
            for feature in project_context['features'][:5]:
                status += f"  ✓ {feature}\n"
        
        if project_context.get('modifications'):
            status += f"\n**Recent Modifications**:\n"
            for mod in project_context['modifications'][-3:]:
                status += f"  • {mod}\n"
        
        status += f"\n**Bundle ID**: {project_context.get('bundle_id', 'Not set')}\n"
        status += f"\nUse `/modify` for tips on changing your app!"
        
        return {"type": "status", "message": status}
    
    def _generate_contextual_response(self, analysis: Dict, project_context: Optional[Dict]) -> Dict:
        """Generate context-aware response"""
        entities = analysis.get("entities", {})
        
        # If user mentioned app types
        if entities.get("app_types") and not project_context:
            app_type = entities["app_types"][0]
            encouragement = self._get_random_response("encouragement")
            return {
                "type": "suggestion",
                "message": f"{encouragement}A {app_type} app is a great choice! What specific features would you like to include?"
            }
        
        # If user mentioned features with existing project
        if entities.get("features") and project_context:
            features_text = ", ".join(entities["features"])
            return {
                "type": "modification",
                "message": f"I'll help you add {features_text} to your app. Let me process that modification..."
            }
        
        # Default responses based on context
        if project_context:
            return {
                "type": "prompt",
                "message": "What would you like to change about your app? You can modify features, UI, or add new functionality."
            }
        else:
            return {
                "type": "prompt", 
                "message": "I'm ready to help you create an iOS app! What kind of app would you like to build?"
            }
    
    def _get_random_response(self, response_type: str) -> str:
        """Get random response from templates"""
        import random
        responses = self.responses.get(response_type, ["I'm here to help!"])
        if isinstance(responses, list):
            return random.choice(responses)
        return responses
    
    def enhance_error_message(self, error: str) -> str:
        """Make error messages more user-friendly"""
        # Common error translations
        error_translations = {
            "422": "I couldn't understand that request. Could you rephrase it?",
            "timeout": "The request took too long. Let's try something simpler first.",
            "invalid": "That doesn't seem quite right. Could you provide more details?",
            "failed": "Something went wrong, but don't worry! Let's try a different approach."
        }
        
        for key, translation in error_translations.items():
            if key in error.lower():
                return translation
        
        return f"I encountered an issue: {error}\nLet's try something else or rephrase your request."