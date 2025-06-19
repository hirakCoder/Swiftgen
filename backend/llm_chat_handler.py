"""
LLM Chat Handler for SwiftGen AI
Handles conversational interactions with SwiftGen AI persona
"""

import re
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class LLMChatHandler:
    def __init__(self, claude_service):
        self.claude_service = claude_service
        
        # SwiftGen AI persona system prompt
        self.system_prompt = """You are SwiftGen AI, a friendly and professional iOS app generation assistant.

Your personality:
- Friendly, warm, and encouraging
- Excited about helping users build iOS apps
- Professional but approachable
- Concise and clear in responses

RESPONSE RULES:
1. When users greet you or ask how you are:
   - Respond naturally and warmly
   - Keep it brief (1-2 sentences)
   - Show enthusiasm about helping them
   - Example: "Hey! I'm doing great and excited to help you build something amazing! What kind of iOS app would you like to create?"

2. When users ask what you can do:
   - Briefly explain you can generate iOS apps from descriptions
   - Mention you can modify existing projects
   - Keep it conversational, not a feature list
   - Example: "I can turn your ideas into fully functional iOS apps! Just describe what you want and I'll handle all the Swift code, UI, and make it work perfectly."

3. For technical requests (create, build, make, generate, modify, fix):
   - Respond with EXACTLY this: "TECHNICAL_HANDOFF"
   - Nothing else, just that exact string

4. For other questions:
   - Be helpful and conversational
   - Stay focused on iOS app development
   - Keep responses under 3 sentences

IMPORTANT: 
- You ARE SwiftGen AI (not an AI assistant or LLM)
- Never break character or mention being an AI
- Always maintain enthusiasm for iOS development"""
        
        # Patterns that definitely indicate technical requests
        self.technical_patterns = [
            r'\b(create|build|make|generate|develop)\s+(?:a|an|the)?\s*(?:\w+\s+)?app\b',
            r'\b(modify|change|update|fix|add|remove)\s+(?:the|my)?\s*(?:app|project|code)\b',
            r'\bapp\s+(?:like|similar to|clone)\s+\w+',
            r'\b(?:food delivery|social media|chat|game|fitness)\s+app\b',
            r'\badd\s+(?:a|the)?\s*(?:feature|screen|button|functionality)\b',
            r'\bfix\s+(?:the|this)?\s*(?:error|bug|issue|problem)\b'
        ]
        
    def is_definitely_technical(self, message: str) -> bool:
        """Check if message is definitely a technical request"""
        message_lower = message.lower()
        
        for pattern in self.technical_patterns:
            if re.search(pattern, message_lower, re.IGNORECASE):
                return True
                
        return False
        
    async def handle_message(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Handle user message with LLM or route to technical handler
        Returns None if technical handling needed, or conversational response
        """
        try:
            # Quick check for obvious technical requests
            if self.is_definitely_technical(user_message):
                logger.info(f"Detected technical request, routing to handler: {user_message[:50]}...")
                return None
                
            # For ambiguous cases, let LLM decide
            logger.info(f"LLM analyzing message: {user_message[:50]}...")
            
            # Add context to help LLM understand current state
            context_info = ""
            if context:
                if context.get('has_active_project'):
                    context_info = "\nContext: User has an active project they're working on."
                if context.get('just_generated'):
                    context_info += "\nContext: Just finished generating an app for the user."
                    
            full_prompt = f"{user_message}{context_info}"
            
            # Get LLM response with SwiftGen AI persona
            response = await self.claude_service.get_completion(
                system_prompt=self.system_prompt,
                user_prompt=full_prompt,
                max_tokens=150,  # Keep responses concise
                temperature=0.7  # Add some personality
            )
            
            # Check if LLM determined this needs technical handling
            if response and "TECHNICAL_HANDOFF" in response:
                logger.info("LLM determined technical handling needed")
                return None
                
            # Return conversational response
            logger.info(f"Returning conversational response: {response[:50]}...")
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error in LLM chat handler: {e}")
            # Fallback to technical handling on error
            return None
            
    def get_error_response(self, error_type: str) -> str:
        """Get friendly error responses as SwiftGen AI"""
        error_responses = {
            'rate_limit': "Whoa, I'm getting a lot of requests! Give me just a moment to catch up, then try again.",
            'invalid_input': "Hmm, I didn't quite understand that. Could you describe what kind of iOS app you'd like to create?",
            'generation_failed': "I ran into a hiccup while building your app. Let me try a different approach - could you tell me more about what you envision?",
            'no_description': "I'm excited to build something for you! Just tell me what kind of iOS app you'd like - a game, productivity tool, social app, or anything else!",
            'server_error': "Oops, I'm having a technical moment. Let's try that again in just a second!"
        }
        
        return error_responses.get(error_type, 
            "Something unexpected happened, but I'm still here! What iOS app would you like me to create?")