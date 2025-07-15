#!/usr/bin/env python3
"""Test modification functionality on existing apps"""

import requests
import json
import time

def test_simple_modification():
    """Test simple color and text modifications"""
    
    # Use the SimpleTimer app we created earlier
    project_id = "proj_f7b3ac5a"
    
    print(f"Testing Simple Modification on {project_id}...")
    
    url = "http://localhost:8000/api/modify"
    
    # Simple modification - change colors and button text
    payload = {
        "project_id": project_id,
        "modification": "Change the start button color to green, stop button to red, and reset button to orange. Also change the button text to use emojis: Start ▶️, Stop ⏸️, Reset 🔄"
    }
    
    try:
        print("Sending modification request...")
        response = requests.post(url, json=payload, timeout=180)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: {result.get('message', 'Modification completed')}")
            print(f"   Status: {result.get('status')}")
            if 'modified_by_llm' in result:
                print(f"   Modified by: {result.get('modified_by_llm')}")
            
            # Check for actual changes
            if 'files_modified' in result:
                print(f"   Files modified: {result.get('files_modified')}")
            
            return True
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_color_modification():
    """Test color scheme modification"""
    
    # Use the TaskMasterPro we just created
    project_id = "proj_3326e29e"
    
    print(f"\nTesting Color Scheme Modification on {project_id}...")
    
    url = "http://localhost:8000/api/modify"
    
    payload = {
        "project_id": project_id,
        "modification": "Change the app's color scheme to use a purple and gold theme. Make the navigation bar purple and accent colors gold."
    }
    
    try:
        print("Sending color modification request...")
        response = requests.post(url, json=payload, timeout=180)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: {result.get('message', 'Modification completed')}")
            return True
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Testing Modification Functionality")
    print("=" * 50)
    
    # Test 1: Simple button modifications
    test1_success = test_simple_modification()
    
    # Wait a bit between tests
    time.sleep(5)
    
    # Test 2: Color scheme modification
    test2_success = test_color_modification()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 MODIFICATION TEST SUMMARY")
    print("=" * 50)
    print(f"Simple Modification: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"Color Modification: {'✅ PASS' if test2_success else '❌ FAIL'}")
    
    if test1_success and test2_success:
        print("\n✅ All modification tests passed!")
    else:
        print("\n⚠️ Some modification tests failed. Check server logs for details.")