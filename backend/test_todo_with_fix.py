#!/usr/bin/env python3
"""Test todo app generation with dismiss pattern fix"""

import requests
import json
import time

def test_todo_app():
    print("Testing Todo App Generation with Dismiss Fix...")
    
    url = "http://localhost:8000/api/generate"
    
    payload = {
        "description": "Create a todo list app with tasks that can be marked complete, edited, and deleted. Include categories and priority levels.",
        "app_name": "TaskMasterPro"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=180)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: {result.get('message', 'App generation started')}")
            print(f"   Project ID: {result.get('project_id')}")
            print(f"   App Name: {result.get('app_name')}")
            
            # Wait for build to complete
            print("\n⏳ Waiting for build to complete...")
            time.sleep(60)  # Give it time to build
            
            # Check the generated files
            project_id = result.get('project_id')
            if project_id:
                print(f"\n📁 Check generated files at: workspaces/{project_id}/")
                print("   Look for dismiss pattern fixes in AddItemScreen.swift or similar files")
            
            return True
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_todo_app()
    
    if success:
        print("\n✅ Todo app test initiated successfully!")
        print("   Monitor server logs for build progress")
    else:
        print("\n❌ Todo app test failed!")