"""
Chat Response Generator for SwiftGen
Generates contextual, varied responses based on user requests
"""
import random
import re
from typing import Dict, Optional, Tuple


class ChatResponseGenerator:
    """Generates contextual chat responses avoiding repetitive messages"""
    
    def __init__(self):
        self.recent_responses = []  # Track recent responses to avoid repetition
        self.max_history = 10
    
    def generate_modification_response(self, message: str, app_name: str, context: Optional[Dict] = None) -> str:
        """Generate a contextual response for modification requests"""
        mod_lower = message.lower()
        
        # Extract what's being modified
        feature = self._extract_feature(message)
        
        # Determine action type and generate response
        if any(word in mod_lower for word in ['dark mode', 'dark theme', 'night mode']):
            responses = [
                f"I'll implement a dark mode toggle for {app_name}. This will include theme persistence.",
                f"Adding dark theme support to {app_name} with a toggle switch.",
                f"I'll create a dark mode feature for {app_name} that users can toggle.",
            ]
        elif any(word in mod_lower for word in ['button', 'btn']):
            button_action = self._extract_button_details(message)
            responses = [
                f"I'll add {button_action} to {app_name}.",
                f"Adding the requested button functionality to {app_name}.",
                f"I'll implement {button_action} in {app_name} for you.",
            ]
        elif any(word in mod_lower for word in ['color', 'colour', 'theme']):
            color_detail = self._extract_color_details(message)
            responses = [
                f"I'll update the {color_detail} in {app_name}.",
                f"Changing {color_detail} as requested for {app_name}.",
                f"I'll apply the new {color_detail} to {app_name}.",
            ]
        elif any(word in mod_lower for word in ['fix', 'bug', 'error', 'issue', 'problem']):
            issue_type = self._extract_issue_type(message)
            responses = [
                f"I'll fix {issue_type} in {app_name} right away.",
                f"Let me resolve {issue_type} in {app_name} for you.",
                f"I'll investigate and fix {issue_type} in {app_name}.",
            ]
        elif any(word in mod_lower for word in ['add', 'implement', 'include']):
            responses = [
                f"I'll add {feature} to {app_name}.",
                f"Implementing {feature} in {app_name} now.",
                f"I'll include {feature} in {app_name} as requested.",
            ]
        elif any(word in mod_lower for word in ['remove', 'delete', 'take out']):
            responses = [
                f"I'll remove {feature} from {app_name}.",
                f"Removing {feature} from {app_name} as requested.",
                f"I'll take out {feature} from {app_name}.",
            ]
        elif any(word in mod_lower for word in ['change', 'modify', 'update']):
            responses = [
                f"I'll update {feature} in {app_name}.",
                f"Modifying {feature} in {app_name} as requested.",
                f"I'll change {feature} in {app_name} for you.",
            ]
        elif any(word in mod_lower for word in ['ssl', 'certificate', 'security', 'transport']):
            responses = [
                f"I'll fix the SSL/security issue in {app_name}. This may involve updating the Info.plist.",
                f"I'll resolve the App Transport Security issue in {app_name}.",
                f"Let me fix the certificate/SSL problem in {app_name}.",
            ]
        elif any(word in mod_lower for word in ['performance', 'optimize', 'speed', 'faster']):
            responses = [
                f"I'll optimize {app_name} for better performance.",
                f"Let me improve the performance of {app_name}.",
                f"I'll make {app_name} run faster and more efficiently.",
            ]
        elif any(word in mod_lower for word in ['ui', 'interface', 'design', 'layout']):
            responses = [
                f"I'll enhance the UI of {app_name} as requested.",
                f"Updating the interface design in {app_name}.",
                f"I'll improve the layout and design of {app_name}.",
            ]
        else:
            # Generic but still contextual
            responses = [
                f"I'll apply that modification to {app_name}.",
                f"Making the requested changes to {app_name}.",
                f"I'll update {app_name} with your requirements.",
                f"Implementing your request in {app_name}.",
            ]
        
        # Add progress indicator
        progress_messages = [
            " Watch the progress below...",
            " I'll update you as I work...",
            " You'll see real-time updates below...",
            " Progress will appear below...",
        ]
        
        # Select response avoiding recent ones
        response = self._select_unique_response(responses)
        response += random.choice(progress_messages)
        
        return response
    
    def generate_creation_response(self, message: str, app_name: str) -> str:
        """Generate a contextual response for app creation requests"""
        desc_lower = message.lower()
        
        # Determine app type and generate excitement
        if 'game' in desc_lower:
            excitement_options = [
                "🎮 Awesome! A game app!",
                "🎮 Great! Games are fun to build!",
                "🎮 Exciting! Let's create this game!",
            ]
        elif 'social' in desc_lower:
            excitement_options = [
                "🌐 Great choice! Social apps connect people!",
                "🌐 Excellent! Social networking is powerful!",
                "🌐 Perfect! Let's build this social platform!",
            ]
        elif any(word in desc_lower for word in ['fitness', 'health', 'workout']):
            excitement_options = [
                "💪 Fantastic! Health apps make a difference!",
                "💪 Great idea! Fitness apps help people!",
                "💪 Excellent! Let's build this health app!",
            ]
        elif any(word in desc_lower for word in ['food', 'restaurant', 'delivery']):
            excitement_options = [
                "🍕 Delicious idea! Food apps are popular!",
                "🍕 Great choice! Everyone loves food apps!",
                "🍕 Perfect! Let's create this food app!",
            ]
        elif any(word in desc_lower for word in ['todo', 'task', 'productivity']):
            excitement_options = [
                "📝 Excellent! Productivity apps are essential!",
                "📝 Great idea! Task management is important!",
                "📝 Perfect! Let's build this productivity tool!",
            ]
        elif any(word in desc_lower for word in ['finance', 'money', 'budget']):
            excitement_options = [
                "💰 Smart choice! Finance apps are valuable!",
                "💰 Excellent! Money management is crucial!",
                "💰 Great idea! Let's build this finance app!",
            ]
        else:
            excitement_options = [
                "✨ Excellent idea!",
                "🚀 Great concept!",
                "💡 Brilliant idea!",
                "⭐ Fantastic choice!",
            ]
        
        excitement = random.choice(excitement_options)
        
        # Generate action phrase
        action_phrases = [
            f"I'll create {app_name} for you right now.",
            f"Let me build {app_name} for you.",
            f"I'll develop {app_name} according to your specifications.",
            f"Building {app_name} with all your requirements.",
        ]
        
        action = random.choice(action_phrases)
        
        return f"{excitement} {action} Watch the progress below..."
    
    def generate_error_response(self, error_type: str, app_name: str) -> str:
        """Generate response for error situations"""
        if error_type == "ssl":
            return f"I've detected an SSL/certificate issue in {app_name}. I'll apply the appropriate fixes to resolve this."
        elif error_type == "build":
            return f"I see there are build errors in {app_name}. Let me fix those for you."
        elif error_type == "syntax":
            return f"I found some syntax issues in {app_name}. I'll correct them now."
        else:
            return f"I'll address the issue in {app_name} and ensure it works properly."
    
    def _extract_feature(self, message: str) -> str:
        """Extract the main feature being discussed"""
        # Remove common words
        words = message.lower().split()
        stop_words = {'the', 'a', 'an', 'to', 'in', 'for', 'and', 'or', 'but', 'with'}
        feature_words = [w for w in words if w not in stop_words]
        
        # Try to find the object of the action
        if 'button' in message.lower():
            return "the button"
        elif 'color' in message.lower() or 'colour' in message.lower():
            return "the colors"
        elif 'theme' in message.lower():
            return "the theme"
        elif 'ui' in message.lower() or 'interface' in message.lower():
            return "the user interface"
        else:
            return "that feature"
    
    def _extract_button_details(self, message: str) -> str:
        """Extract details about button modifications"""
        if 'color' in message.lower():
            match = re.search(r'(blue|red|green|yellow|orange|purple|black|white)', message.lower())
            if match:
                return f"a {match.group(1)} button"
        if 'add' in message.lower():
            return "the new button"
        return "the button functionality"
    
    def _extract_color_details(self, message: str) -> str:
        """Extract color change details"""
        colors = re.findall(r'(blue|red|green|yellow|orange|purple|black|white|dark|light)', message.lower())
        if colors:
            return f"color scheme to {colors[-1]}"
        return "color scheme"
    
    def _extract_issue_type(self, message: str) -> str:
        """Extract the type of issue being reported"""
        if 'ssl' in message.lower() or 'certificate' in message.lower():
            return "the SSL certificate issue"
        elif 'crash' in message.lower():
            return "the crash"
        elif 'slow' in message.lower() or 'performance' in message.lower():
            return "the performance issue"
        elif 'ui' in message.lower() or 'display' in message.lower():
            return "the display issue"
        else:
            return "that issue"
    
    def _select_unique_response(self, responses: list) -> str:
        """Select a response that hasn't been used recently"""
        # Filter out recently used responses
        available = [r for r in responses if r not in self.recent_responses]
        
        # If all have been used, reset and use any
        if not available:
            self.recent_responses = []
            available = responses
        
        selected = random.choice(available)
        
        # Add to history
        self.recent_responses.append(selected)
        if len(self.recent_responses) > self.max_history:
            self.recent_responses.pop(0)
        
        return selected