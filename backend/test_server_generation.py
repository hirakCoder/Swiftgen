#!/usr/bin/env python3
"""Test generation through the server API"""

import requests
import json
import time

def test_server_generation():
    print("🧪 Testing Server Generation")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test app
    test_app = {
        "description": "Create a weather app that shows current temperature and conditions with a clean interface",
        "app_name": "WeatherNow"
    }
    
    print(f"\n📱 Generating {test_app['app_name']}...")
    print(f"   Description: {test_app['description']}")
    
    try:
        # Send generation request
        response = requests.post(
            f"{base_url}/api/generate",
            json=test_app
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Server Response:")
            print(f"   Status: {result.get('status')}")
            print(f"   Project ID: {result.get('project_id')}")
            print(f"   App Name: {result.get('app_name')}")
            print(f"   Message: {result.get('message')}")
            
            # Wait a bit for generation
            print("\n⏳ Waiting for generation to complete...")
            time.sleep(10)
            
            # Check project status
            project_id = result.get('project_id')
            if project_id:
                status_response = requests.get(
                    f"{base_url}/api/projects/{project_id}/status"
                )
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"\n📊 Project Status:")
                    print(f"   Exists: {status.get('exists')}")
                    print(f"   Has files: {status.get('has_files')}")
                    print(f"   File count: {status.get('file_count')}")
                    print(f"   Build status: {status.get('build_status')}")
                else:
                    print(f"   ❌ Status check failed: {status_response.status_code}")
        else:
            print(f"\n❌ Generation request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("⚠️  Make sure the server is running (python backend/main.py)")
    print("Press Enter to continue...")
    input()
    test_server_generation()