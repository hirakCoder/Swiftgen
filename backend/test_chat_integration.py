#!/usr/bin/env python3
"""
Test script for LLM Chat Integration
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from enhanced_claude_service import EnhancedClaudeService
from llm_chat_handler import LLMChatHandler

async def test_chat_handler():
    print("🧪 Testing LLM Chat Handler Integration")
    print("=" * 50)
    
    # Initialize services
    enhanced_service = EnhancedClaudeService()
    chat_handler = LLMChatHandler(enhanced_service)
    
    # Test cases
    test_messages = [
        ("How are you?", None),
        ("What can you do?", None),
        ("Create a todo app", None),
        ("Hi there!", None),
        ("Build a social media app like Instagram", None),
        ("Can you help me?", None),
        ("Thanks!", {"has_active_project": True}),
    ]
    
    for message, context in test_messages:
        print(f"\n💬 User: {message}")
        if context:
            print(f"   Context: {context}")
        
        try:
            response = await chat_handler.handle_message(message, context)
            if response:
                print(f"🤖 SwiftGen AI: {response}")
            else:
                print("🔧 [Would route to technical handler]")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n✅ Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_chat_handler())