#!/usr/bin/env python3
"""Test complex modifications like dark mode and new features"""

import requests
import json
import time

def test_dark_mode_addition():
    """Test adding dark mode to an existing app"""
    
    # Use the SimpleTimer app
    project_id = "proj_f7b3ac5a"
    
    print(f"Testing Dark Mode Addition on {project_id}...")
    
    url = "http://localhost:8000/api/modify"
    
    payload = {
        "project_id": project_id,
        "modification": """Add a dark mode toggle to the app. Include:
        1. A toggle switch in the top right corner
        2. Dark background (#1C1C1E) and light text for dark mode
        3. Smooth transition animations
        4. Remember user's preference using @AppStorage
        5. Update all UI elements to support both light and dark themes"""
    }
    
    try:
        print("Sending dark mode modification request...")
        response = requests.post(url, json=payload, timeout=180)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: {result.get('message', 'Modification completed')}")
            print(f"   Modified by: {result.get('modified_by_llm', 'Unknown')}")
            return True, project_id
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            print(f"   Error: {response.text}")
            return False, project_id
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False, project_id

def test_new_feature_addition():
    """Test adding a new major feature to the todo app"""
    
    project_id = "proj_3326e29e"  # TaskMasterPro
    
    print(f"\nTesting New Feature Addition on {project_id}...")
    
    url = "http://localhost:8000/api/modify"
    
    payload = {
        "project_id": project_id,
        "modification": """Add a statistics dashboard feature that shows:
        1. Total tasks completed today/this week/this month
        2. Completion rate percentage
        3. Tasks by category breakdown (pie chart style)
        4. Streak counter for consecutive days with completed tasks
        5. Add a new tab bar item called 'Stats' with an appropriate SF Symbol"""
    }
    
    try:
        print("Sending statistics feature request...")
        response = requests.post(url, json=payload, timeout=180)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: {result.get('message', 'Modification completed')}")
            print(f"   Modified by: {result.get('modified_by_llm', 'Unknown')}")
            return True, project_id
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            print(f"   Error: {response.text}")
            return False, project_id
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False, project_id

def test_multiple_sequential_mods(project_id):
    """Test multiple modifications on the same app sequentially"""
    
    print(f"\n{'='*60}")
    print(f"Testing Multiple Sequential Modifications on {project_id}")
    print(f"{'='*60}")
    
    url = "http://localhost:8000/api/modify"
    
    # Series of modifications a real user might request
    modifications = [
        {
            "name": "Add Sound Effects",
            "request": "Add sound effects to the timer app. Play a tick sound every second when running, and a completion chime when the timer reaches zero. Add a mute button to toggle sounds on/off."
        },
        {
            "name": "Add Preset Times",
            "request": "Add quick preset buttons for common times: 30 seconds, 1 minute, 2 minutes, 5 minutes, 10 minutes. Arrange them in a horizontal scroll view above the timer display."
        },
        {
            "name": "Add History Feature",
            "request": "Add a history feature that tracks the last 10 timer sessions. Show the date, duration, and whether it was completed or cancelled. Add a 'History' button that shows this in a sheet."
        }
    ]
    
    all_success = True
    
    for i, mod in enumerate(modifications, 1):
        print(f"\nModification {i}/3: {mod['name']}")
        print("-" * 40)
        
        payload = {
            "project_id": project_id,
            "modification": mod["request"]
        }
        
        try:
            response = requests.post(url, json=payload, timeout=180)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCCESS: {mod['name']} completed")
                print(f"   Modified by: {result.get('modified_by_llm', 'Unknown')}")
                
                # Wait between modifications like a real user
                if i < len(modifications):
                    print("   Waiting 10 seconds before next modification...")
                    time.sleep(10)
            else:
                print(f"❌ FAILED: {mod['name']}")
                print(f"   Error: {response.text}")
                all_success = False
                
        except Exception as e:
            print(f"❌ ERROR in {mod['name']}: {str(e)}")
            all_success = False
    
    return all_success

def test_user_workflow():
    """Test a realistic user workflow with feedback-based modifications"""
    
    print("\n" + "="*60)
    print("TESTING REALISTIC USER WORKFLOW")
    print("="*60)
    
    # Step 1: Create a calculator app
    print("\n📱 Step 1: Creating a Calculator App...")
    
    url = "http://localhost:8000/api/generate"
    payload = {
        "description": "Create a scientific calculator app with basic operations (add, subtract, multiply, divide) and scientific functions (sin, cos, tan, log, sqrt). Include a history of calculations.",
        "app_name": "SciCalc Pro"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=180)
        if response.status_code == 200:
            result = response.json()
            project_id = result.get('project_id')
            print(f"✅ Calculator app created: {project_id}")
            print("   Waiting for build to complete...")
            time.sleep(60)
            
            # Step 2: User wants to change the design
            print("\n🎨 Step 2: User doesn't like the colors...")
            
            url = "http://localhost:8000/api/modify"
            payload = {
                "project_id": project_id,
                "modification": "The calculator looks too plain. Make it more modern with a gradient background (dark blue to purple), rounded buttons with subtle shadows, and use SF Symbols for operations instead of plain text."
            }
            
            response = requests.post(url, json=payload, timeout=180)
            if response.status_code == 200:
                print("✅ Design updated successfully")
                time.sleep(5)
                
                # Step 3: User wants a specific feature
                print("\n🔧 Step 3: User wants programmer mode...")
                
                payload = {
                    "project_id": project_id,
                    "modification": "Add a programmer mode that can convert between decimal, binary, hexadecimal, and octal. Add a segmented control to switch between scientific and programmer modes."
                }
                
                response = requests.post(url, json=payload, timeout=180)
                if response.status_code == 200:
                    print("✅ Programmer mode added")
                    return True, project_id
                    
    except Exception as e:
        print(f"❌ Workflow failed: {str(e)}")
        return False, None
    
    return False, None

if __name__ == "__main__":
    print("🧪 COMPLEX MODIFICATIONS TEST SUITE")
    print("=" * 60)
    
    # Test 1: Add dark mode to timer app
    dark_mode_success, timer_id = test_dark_mode_addition()
    time.sleep(10)
    
    # Test 2: Add statistics to todo app
    stats_success, todo_id = test_new_feature_addition()
    time.sleep(10)
    
    # Test 3: Multiple sequential modifications
    if dark_mode_success:
        sequential_success = test_multiple_sequential_mods(timer_id)
    else:
        sequential_success = False
        print("\n⚠️ Skipping sequential modifications due to dark mode failure")
    
    time.sleep(10)
    
    # Test 4: Realistic user workflow
    workflow_success, calc_id = test_user_workflow()
    
    # Summary
    print("\n" + "="*60)
    print("📊 COMPLEX MODIFICATIONS TEST SUMMARY")
    print("="*60)
    print(f"Dark Mode Addition: {'✅ PASS' if dark_mode_success else '❌ FAIL'}")
    print(f"Statistics Feature: {'✅ PASS' if stats_success else '❌ FAIL'}")
    print(f"Sequential Modifications: {'✅ PASS' if sequential_success else '❌ FAIL'}")
    print(f"User Workflow Test: {'✅ PASS' if workflow_success else '❌ FAIL'}")
    
    total_passed = sum([dark_mode_success, stats_success, sequential_success, workflow_success])
    print(f"\nTotal: {total_passed}/4 tests passed")
    
    if total_passed == 4:
        print("\n🎉 All complex modification tests passed!")
    else:
        print("\n⚠️ Some tests failed. Check server logs for details.")