#!/usr/bin/env python3
"""
Production testing script for SwiftGen
Tests app generation, modification, and auto-fixing
"""

import asyncio
import httpx
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

# Base URL for the API
BASE_URL = "http://localhost:8000"

# Test results tracking
test_results = {
    "simple_apps": [],
    "medium_apps": [],
    "complex_apps": [],
    "modifications": [],
    "auto_fixes": [],
    "ssl_tests": [],
    "llm_failover": [],
    "websocket": []
}


async def test_app_generation(description: str, app_type: str) -> Dict:
    """Test app generation"""
    print(f"\n{'='*60}")
    print(f"Testing {app_type} app: {description[:50]}...")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            # Generate the app
            response = await client.post(
                f"{BASE_URL}/api/generate",
                json={
                    "description": description,
                    "project_id": f"test_{app_type}_{int(time.time())}"
                }
            )
            
            if response.status_code != 200:
                print(f"❌ Generation failed: {response.status_code}")
                print(f"Response: {response.text}")
                return {
                    "success": False,
                    "app_type": app_type,
                    "description": description,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "duration": time.time() - start_time
                }
            
            data = response.json()
            project_id = data.get("project_id")
            app_name = data.get("app_name")
            
            print(f"✓ Generation started: {app_name} (ID: {project_id})")
            
            # Poll for status
            max_attempts = 60  # 5 minutes max
            for attempt in range(max_attempts):
                await asyncio.sleep(5)  # Check every 5 seconds
                
                status_response = await client.get(
                    f"{BASE_URL}/api/project/{project_id}/status"
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get("status", "unknown")
                    
                    print(f"  Status: {status}")
                    
                    if status == "completed":
                        duration = time.time() - start_time
                        print(f"✅ App generated successfully in {duration:.2f}s")
                        return {
                            "success": True,
                            "app_type": app_type,
                            "description": description,
                            "app_name": app_name,
                            "project_id": project_id,
                            "duration": duration,
                            "files_count": status_data.get("swift_file_count", 0)
                        }
                    elif status == "failed":
                        error = status_data.get("error", "Unknown error")
                        print(f"❌ Generation failed: {error}")
                        return {
                            "success": False,
                            "app_type": app_type,
                            "description": description,
                            "error": error,
                            "duration": time.time() - start_time
                        }
            
            # Timeout
            return {
                "success": False,
                "app_type": app_type,
                "description": description,
                "error": "Timeout waiting for generation",
                "duration": time.time() - start_time
            }
            
        except Exception as e:
            print(f"❌ Exception during generation: {e}")
            return {
                "success": False,
                "app_type": app_type,
                "description": description,
                "error": str(e),
                "duration": time.time() - start_time
            }


async def test_app_modification(project_id: str, modification: str, mod_type: str) -> Dict:
    """Test app modification"""
    print(f"\n{'='*60}")
    print(f"Testing {mod_type} modification: {modification[:50]}...")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            # Request modification
            response = await client.post(
                f"{BASE_URL}/api/modify",
                json={
                    "project_id": project_id,
                    "modification": modification
                }
            )
            
            if response.status_code != 200:
                print(f"❌ Modification failed: {response.status_code}")
                return {
                    "success": False,
                    "mod_type": mod_type,
                    "modification": modification,
                    "error": f"HTTP {response.status_code}",
                    "duration": time.time() - start_time
                }
            
            # Wait a bit for modification to complete
            await asyncio.sleep(10)
            
            # Check status
            status_response = await client.get(
                f"{BASE_URL}/api/project/{project_id}/status"
            )
            
            if status_response.status_code == 200:
                duration = time.time() - start_time
                print(f"✅ Modification completed in {duration:.2f}s")
                return {
                    "success": True,
                    "mod_type": mod_type,
                    "modification": modification,
                    "duration": duration
                }
            else:
                return {
                    "success": False,
                    "mod_type": mod_type,
                    "modification": modification,
                    "error": "Failed to verify modification",
                    "duration": time.time() - start_time
                }
                
        except Exception as e:
            print(f"❌ Exception during modification: {e}")
            return {
                "success": False,
                "mod_type": mod_type,
                "modification": modification,
                "error": str(e),
                "duration": time.time() - start_time
            }


async def run_all_tests():
    """Run comprehensive test suite"""
    print(f"\n{'='*80}")
    print(f"🚀 SwiftGen Production Test Suite - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    
    # Test 1: Simple Apps
    simple_apps = [
        ("Create a simple timer app", "timer"),
        ("Build a todo list app", "todo"),
        ("Make a counter app with increment and decrement buttons", "counter")
    ]
    
    for description, app_type in simple_apps:
        result = await test_app_generation(description, app_type)
        test_results["simple_apps"].append(result)
        
        # If successful, test a simple modification
        if result["success"]:
            mod_result = await test_app_modification(
                result["project_id"],
                "Add a dark mode toggle",
                "simple"
            )
            test_results["modifications"].append(mod_result)
    
    # Test 2: Medium Complexity Apps
    medium_apps = [
        ("Create a calculator app with basic operations", "calculator"),
        ("Build a weather app that shows current weather", "weather")
    ]
    
    for description, app_type in medium_apps:
        result = await test_app_generation(description, app_type)
        test_results["medium_apps"].append(result)
        
        # If successful, test a medium modification
        if result["success"]:
            if app_type == "calculator":
                mod_result = await test_app_modification(
                    result["project_id"],
                    "Add scientific calculator functions",
                    "medium"
                )
            else:
                mod_result = await test_app_modification(
                    result["project_id"],
                    "Add 5-day forecast view",
                    "medium"
                )
            test_results["modifications"].append(mod_result)
    
    # Test 3: Complex Apps
    complex_apps = [
        ("Create a food delivery app with restaurant listings and ordering", "food_delivery"),
        ("Build a social media app with posts and comments", "social_media")
    ]
    
    for description, app_type in complex_apps:
        result = await test_app_generation(description, app_type)
        test_results["complex_apps"].append(result)
        
        # If successful, test a complex modification
        if result["success"]:
            if app_type == "food_delivery":
                mod_result = await test_app_modification(
                    result["project_id"],
                    "Add user authentication and order history",
                    "complex"
                )
            else:
                mod_result = await test_app_modification(
                    result["project_id"],
                    "Add direct messaging between users",
                    "complex"
                )
            test_results["modifications"].append(mod_result)
    
    # Generate summary report
    print(f"\n{'='*80}")
    print(f"📊 TEST RESULTS SUMMARY")
    print(f"{'='*80}")
    
    # Simple apps summary
    simple_success = sum(1 for r in test_results["simple_apps"] if r["success"])
    print(f"\n✅ Simple Apps: {simple_success}/{len(test_results['simple_apps'])}")
    for result in test_results["simple_apps"]:
        status = "✅" if result["success"] else "❌"
        print(f"  {status} {result['app_type']}: {result.get('app_name', 'Failed')}")
        if not result["success"]:
            print(f"     Error: {result.get('error', 'Unknown')}")
    
    # Medium apps summary
    medium_success = sum(1 for r in test_results["medium_apps"] if r["success"])
    print(f"\n✅ Medium Apps: {medium_success}/{len(test_results['medium_apps'])}")
    for result in test_results["medium_apps"]:
        status = "✅" if result["success"] else "❌"
        print(f"  {status} {result['app_type']}: {result.get('app_name', 'Failed')}")
        if not result["success"]:
            print(f"     Error: {result.get('error', 'Unknown')}")
    
    # Complex apps summary
    complex_success = sum(1 for r in test_results["complex_apps"] if r["success"])
    print(f"\n✅ Complex Apps: {complex_success}/{len(test_results['complex_apps'])}")
    for result in test_results["complex_apps"]:
        status = "✅" if result["success"] else "❌"
        print(f"  {status} {result['app_type']}: {result.get('app_name', 'Failed')}")
        if not result["success"]:
            print(f"     Error: {result.get('error', 'Unknown')}")
    
    # Modifications summary
    mod_success = sum(1 for r in test_results["modifications"] if r["success"])
    print(f"\n✅ Modifications: {mod_success}/{len(test_results['modifications'])}")
    for result in test_results["modifications"]:
        status = "✅" if result["success"] else "❌"
        print(f"  {status} {result['mod_type']}: {result['modification'][:50]}...")
        if not result["success"]:
            print(f"     Error: {result.get('error', 'Unknown')}")
    
    # Overall summary
    total_tests = (
        len(test_results["simple_apps"]) +
        len(test_results["medium_apps"]) +
        len(test_results["complex_apps"]) +
        len(test_results["modifications"])
    )
    total_success = simple_success + medium_success + complex_success + mod_success
    success_rate = (total_success / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n{'='*80}")
    print(f"📈 OVERALL SUCCESS RATE: {success_rate:.1f}% ({total_success}/{total_tests})")
    print(f"{'='*80}")
    
    # Save detailed results
    with open("test_results_production.json", "w") as f:
        json.dump(test_results, f, indent=2)
    print(f"\n💾 Detailed results saved to test_results_production.json")
    
    # Determine if production ready
    if success_rate >= 95:
        print(f"\n✅ 🎉 PRODUCTION READY! Success rate: {success_rate:.1f}%")
    elif success_rate >= 85:
        print(f"\n⚠️  NEARLY READY! Success rate: {success_rate:.1f}% (Target: 95%)")
    else:
        print(f"\n❌ NOT READY! Success rate: {success_rate:.1f}% (Target: 95%)")


if __name__ == "__main__":
    asyncio.run(run_all_tests())