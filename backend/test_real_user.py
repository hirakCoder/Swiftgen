#!/usr/bin/env python3
"""Test like a real user through the chat interface"""

import requests
import json
import time

def chat_with_swiftgen(message):
    """Send a chat message like a real user"""
    
    response = requests.post("http://localhost:8000/api/chat", json={
        "message": message,
        "session_id": "test_session_123"
    })
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def test_real_user_flow():
    """Test the flow a real user would experience"""
    
    print("🧪 Testing Real User Experience")
    print("=" * 60)
    
    # Test 1: Create a simple app
    print("\n1️⃣ User: Create a todo list app")
    response = chat_with_swiftgen("Create a todo list app where I can add tasks and mark them as complete")
    
    if response:
        print(f"   Bot: {response.get('response', 'No response')[:100]}...")
        project_id = response.get('project_id')
        if project_id:
            print(f"   Project: {project_id}")
            
            # Wait for build
            print("   ⏳ Waiting 30 seconds for build...")
            time.sleep(30)
            
            # Test 2: Simple modification
            print("\n2️⃣ User: Add dark mode")
            mod_response = chat_with_swiftgen("Can you add a dark mode toggle to the app?")
            
            if mod_response:
                print(f"   Bot: {mod_response.get('response', 'No response')[:100]}...")
                
                # Monitor for 30 seconds
                print("   ⏳ Waiting 30 seconds for modification...")
                time.sleep(30)
                
                # Test 3: Another modification
                print("\n3️⃣ User: Add swipe to delete")
                swipe_response = chat_with_swiftgen("Add swipe to delete functionality for the todo items")
                
                if swipe_response:
                    print(f"   Bot: {swipe_response.get('response', 'No response')[:100]}...")
                    
                    print("   ⏳ Waiting 30 seconds...")
                    time.sleep(30)
                    
                    # Test 4: Complex modification
                    print("\n4️⃣ User: Add categories")
                    cat_response = chat_with_swiftgen("I want to organize my todos into categories like Work, Personal, Shopping")
                    
                    if cat_response:
                        print(f"   Bot: {cat_response.get('response', 'No response')[:100]}...")

    print("\n" + "=" * 60)
    print("📊 Test Complete")
    print("\nCheck the UI at http://localhost:8000 to see:")
    print("- Were modifications clear about what changed?")
    print("- Did builds succeed without duplicate file errors?")
    print("- Was the user experience smooth?")

if __name__ == "__main__":
    test_real_user_flow()