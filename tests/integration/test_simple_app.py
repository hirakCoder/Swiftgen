#!/usr/bin/env python3
"""Test simple app generation to ensure core functionality works"""

import requests
import json
import time

def test_simple_app():
    """Test generating a simple app"""
    
    print("🧪 Testing Simple App Generation")
    print("=" * 60)
    
    # Test data
    payload = {
        "description": "Create a simple counter app with increment and decrement buttons",
        "ios_version": "17.0"
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    try:
        # Make request
        response = requests.post("http://localhost:8000/api/generate", json=payload)
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            project_id = result.get('project_id')
            if project_id:
                print(f"\n✅ Successfully started generation for project: {project_id}")
                print(f"App name: {result.get('app_name', 'Unknown')}")
                
                # Give it some time to process
                print("\nWaiting for generation to complete...")
                time.sleep(10)
                
                return True
            else:
                print("❌ No project ID in response")
                return False
        else:
            print(f"❌ Request failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_app()
    print("\n" + "=" * 60)
    if success:
        print("✅ Test passed! Core functionality is working.")
    else:
        print("❌ Test failed. Check the backend logs.")
    
    exit(0 if success else 1)