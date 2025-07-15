#!/usr/bin/env python3
"""Test SmartModificationHandler with actual server"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def create_test_app():
    """Create a simple app for testing modifications"""
    print("Creating test app...")
    
    url = f"{BASE_URL}/api/generate"
    payload = {
        "description": "Create a simple counter app with increment and decrement buttons",
        "app_name": "SmartCounterTest"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        if response.status_code == 200:
            result = response.json()
            project_id = result.get('project_id')
            print(f"✅ Created test app: {project_id}")
            return project_id
        else:
            print(f"❌ Failed to create app: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_modification(project_id, description, modification_request):
    """Test a single modification"""
    print(f"\n🔧 Testing: {description}")
    print(f"   Request: {modification_request[:80]}...")
    
    url = f"{BASE_URL}/api/modify"
    payload = {
        "project_id": project_id,
        "modification": modification_request
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload, timeout=180)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            success = result.get('success', False)
            message = result.get('message', '')
            llm = result.get('modified_by_llm', 'Unknown')
            
            status = "✅ SUCCESS" if success else "⚠️  PARTIAL"
            print(f"   {status} in {duration:.1f}s")
            print(f"   LLM: {llm}")
            print(f"   Message: {message[:100]}")
            
            # Check for specific features
            if "settings" in modification_request.lower():
                print("   📋 Note: Should have used settings template")
            if "dark mode" in modification_request.lower():
                print("   🌙 Note: Should have used dark mode template")
                
            return success
        else:
            print(f"   ❌ FAILED: Status {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def run_tests():
    """Run comprehensive modification tests"""
    print("🚀 Testing SmartModificationHandler with Server")
    print("="*70)
    
    # Check if server is running with SmartModificationHandler
    try:
        # You could add a /api/info endpoint to check which handler is active
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not running")
            return
    except:
        print("❌ Cannot connect to server")
        return
    
    # Create test app
    project_id = create_test_app()
    if not project_id:
        return
        
    print(f"\nWaiting for app to build...")
    time.sleep(30)
    
    # Test modifications
    test_cases = [
        {
            "name": "Simple Color Change",
            "request": "Change the increment button color to green",
            "complexity": "Simple (0)"
        },
        {
            "name": "Add Dark Mode (Template)",
            "request": "Add a dark mode toggle to the app",
            "complexity": "Simple with template (0)"
        },
        {
            "name": "Add Settings Screen (Template)",
            "request": "Add a settings screen with theme preferences and haptic feedback options",
            "complexity": "Medium with template (1-2)"
        },
        {
            "name": "Add Persistence (Template)",
            "request": "Add data persistence to save the counter value when app closes",
            "complexity": "Medium with template (1)"
        },
        {
            "name": "Complex Dashboard (Progressive)",
            "request": "Add a statistics dashboard showing daily count history, weekly trends chart, total counts by day, and export to CSV functionality",
            "complexity": "Complex with progressive (3-4)"
        },
        {
            "name": "Multiple Features",
            "request": "Add user profiles with login, different counters for each user, and sync data to cloud",
            "complexity": "Very complex (4-5)"
        }
    ]
    
    results = []
    
    for test in test_cases:
        print(f"\n{'='*70}")
        print(f"Test: {test['name']} - Complexity: {test['complexity']}")
        
        success = test_modification(project_id, test['name'], test['request'])
        results.append((test['name'], success))
        
        # Wait between modifications
        time.sleep(10)
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 Test Summary")
    print("="*70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    print(f"\nTotal: {passed}/{total} passed ({passed/total*100:.0f}%)")
    
    # Analysis
    print("\n📋 SmartModificationHandler Analysis:")
    print("- Simple modifications should complete quickly")
    print("- Template-based mods should be very reliable")
    print("- Complex mods should show progressive steps")
    print("- Context should stay under 20KB")
    print("- Partial success should be allowed for complex tasks")

if __name__ == "__main__":
    run_tests()