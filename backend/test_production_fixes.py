#!/usr/bin/env python3
"""
Test script to verify all production fixes are working
"""

import requests
import json
import time
import sys
import os
from pathlib import Path

# API endpoint
API_BASE = "http://localhost:8000/api"

def test_simple_app_generation():
    """Test simple app generation to ensure all fixes work"""
    
    print("🧪 Testing Simple App Generation")
    print("=" * 50)
    
    # Test data
    test_requests = [
        {
            "name": "Simple Counter",
            "description": "Create a simple counter app with increment and decrement buttons",
            "expected_files": ["ContentView.swift", "App.swift"]
        },
        {
            "name": "Basic Timer",
            "description": "Create a basic timer app with start, stop, and reset functionality",
            "expected_files": ["ContentView.swift", "App.swift"]
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_requests, 1):
        print(f"\n📱 Test {i}: {test_case['name']}")
        print(f"Description: {test_case['description']}")
        
        try:
            # Make generation request
            response = requests.post(f"{API_BASE}/generate", json={
                "description": test_case["description"],
                "app_name": test_case["name"]
            }, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                project_id = data.get("project_id")
                
                print(f"✅ Generation successful! Project ID: {project_id}")
                
                # Check if files were created
                project_path = Path(f"../workspaces/{project_id}")
                if project_path.exists():
                    sources_path = project_path / "Sources"
                    if sources_path.exists():
                        swift_files = list(sources_path.glob("**/*.swift"))
                        print(f"📁 Created {len(swift_files)} Swift files:")
                        for file in swift_files:
                            rel_path = file.relative_to(project_path)
                            print(f"   - {rel_path}")
                        
                        # Check for duplicates
                        file_names = [f.name for f in swift_files]
                        duplicates = [name for name in file_names if file_names.count(name) > 1]
                        if duplicates:
                            print(f"❌ Found duplicate files: {duplicates}")
                            results.append({
                                "test": test_case["name"],
                                "status": "FAILED",
                                "error": f"Duplicate files found: {duplicates}"
                            })
                        else:
                            print("✅ No duplicate files found")
                            results.append({
                                "test": test_case["name"],
                                "status": "PASSED",
                                "files_created": len(swift_files)
                            })
                    else:
                        print("❌ Sources directory not found")
                        results.append({
                            "test": test_case["name"],
                            "status": "FAILED",
                            "error": "Sources directory not found"
                        })
                else:
                    print("❌ Project directory not found")
                    results.append({
                        "test": test_case["name"],
                        "status": "FAILED",
                        "error": "Project directory not found"
                    })
            else:
                print(f"❌ Request failed with status {response.status_code}")
                print(f"Response: {response.text}")
                results.append({
                    "test": test_case["name"],
                    "status": "FAILED",
                    "error": f"HTTP {response.status_code}: {response.text}"
                })
                
        except Exception as e:
            print(f"❌ Exception occurred: {e}")
            results.append({
                "test": test_case["name"],
                "status": "FAILED",
                "error": str(e)
            })
        
        # Small delay between tests
        time.sleep(2)
    
    # Print summary
    print(f"\n📊 Test Summary")
    print("=" * 50)
    
    passed = sum(1 for r in results if r["status"] == "PASSED")
    failed = sum(1 for r in results if r["status"] == "FAILED")
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {passed}/{len(results)} ({passed/len(results)*100:.1f}%)")
    
    if failed > 0:
        print("\n❌ Failed Tests:")
        for result in results:
            if result["status"] == "FAILED":
                print(f"  - {result['test']}: {result['error']}")
    
    return passed == len(results)

def check_server_health():
    """Check if the server is running"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False

def main():
    print("🚀 SwiftGen Production Fixes Test")
    print("=" * 50)
    
    # Check server health first
    if not check_server_health():
        print("\n❌ Server is not running. Please start the server first:")
        print("   cd backend && python3 main.py")
        sys.exit(1)
    
    # Run tests
    success = test_simple_app_generation()
    
    if success:
        print("\n🎉 All tests passed! The system is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please check the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()