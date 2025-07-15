#!/usr/bin/env python3
"""Production readiness test for SwiftGen - July 14, 2025"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def log(message):
    """Log with timestamp"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

def test_app_generation(description, app_name, complexity="simple"):
    """Test app generation and build"""
    log(f"\n{'='*60}")
    log(f"Testing {complexity} app: {app_name}")
    log(f"{'='*60}")
    
    # Generate app
    log("Sending generation request...")
    response = requests.post(
        f"{BASE_URL}/api/generate",
        json={
            "description": description,
            "app_name": app_name
        }
    )
    
    if response.status_code != 200:
        log(f"❌ Generation failed: {response.text}")
        return False, None
    
    result = response.json()
    project_id = result.get("project_id")
    log(f"✅ Project created: {project_id}")
    
    # Wait for build
    wait_time = 30 if complexity == "simple" else 45
    log(f"⏳ Waiting {wait_time}s for build...")
    time.sleep(wait_time)
    
    # Check status
    log("Checking build status...")
    status_response = requests.get(f"{BASE_URL}/api/status/{project_id}")
    
    if status_response.status_code == 200:
        status = status_response.json()
        build_success = status.get("build_success", False)
        
        log(f"Build Status: {status.get('build_status', 'unknown')}")
        log(f"Build Success: {build_success}")
        log(f"Files Created: {len(status.get('files', []))}")
        
        if build_success:
            log(f"✅ {app_name} BUILD SUCCESSFUL!")
            return True, project_id
        else:
            log(f"❌ {app_name} build failed")
            if status.get("build_errors"):
                log(f"Errors: {status['build_errors'][:200]}...")
            return False, project_id
    else:
        log(f"❌ Could not get status: {status_response.status_code}")
        return False, project_id

def test_modification(project_id, modification):
    """Test app modification"""
    log(f"\n{'='*50}")
    log(f"Testing modification: {modification[:50]}...")
    log(f"{'='*50}")
    
    response = requests.post(
        f"{BASE_URL}/api/modify",
        json={
            "project_id": project_id,
            "modification": modification
        }
    )
    
    if response.status_code != 200:
        log(f"❌ Modification request failed: {response.text}")
        return False
    
    log("✅ Modification request sent")
    
    # Wait for modification
    log("⏳ Waiting 30s for modification...")
    time.sleep(30)
    
    # Check status
    status_response = requests.get(f"{BASE_URL}/api/status/{project_id}")
    
    if status_response.status_code == 200:
        status = status_response.json()
        build_success = status.get("build_success", False)
        
        if build_success:
            log("✅ Modification BUILD SUCCESSFUL!")
            return True
        else:
            log("❌ Modification build failed")
            return False
    else:
        log(f"❌ Could not get status after modification")
        return False

def main():
    """Run production readiness tests"""
    print("\n" + "="*70)
    print("🚀 SwiftGen Production Readiness Test - July 14, 2025")
    print("="*70)
    
    # Check health
    log("Checking server health...")
    try:
        health = requests.get(f"{BASE_URL}/health")
        if health.status_code == 200:
            log("✅ Server is healthy")
        else:
            log("❌ Server health check failed")
            return
    except Exception as e:
        log(f"❌ Cannot connect to server: {e}")
        return
    
    results = {
        "simple": {"success": 0, "failed": 0},
        "medium": {"success": 0, "failed": 0},
        "complex": {"success": 0, "failed": 0},
        "modifications": {"success": 0, "failed": 0}
    }
    
    # Test 1: Simple Counter App
    success, project_id = test_app_generation(
        "Create a simple counter app with increment and decrement buttons",
        "SimpleCounter",
        "simple"
    )
    if success:
        results["simple"]["success"] += 1
        
        # Test modification
        mod_success = test_modification(project_id, "Add a reset button that sets the counter to 0")
        if mod_success:
            results["modifications"]["success"] += 1
        else:
            results["modifications"]["failed"] += 1
    else:
        results["simple"]["failed"] += 1
    
    # Test 2: Timer App
    success, _ = test_app_generation(
        "Create a timer app with start, stop, and reset functionality",
        "TimerApp",
        "simple"
    )
    if success:
        results["simple"]["success"] += 1
    else:
        results["simple"]["failed"] += 1
    
    # Test 3: Todo App (Medium)
    success, project_id = test_app_generation(
        "Create a todo list app with add, remove, and mark complete functionality",
        "TodoApp",
        "medium"
    )
    if success:
        results["medium"]["success"] += 1
        
        # Test modification
        mod_success = test_modification(project_id, "Add categories to todos with colors")
        if mod_success:
            results["modifications"]["success"] += 1
        else:
            results["modifications"]["failed"] += 1
    else:
        results["medium"]["failed"] += 1
    
    # Test 4: Calculator App (Medium)
    success, _ = test_app_generation(
        "Create a basic calculator app with +, -, *, / operations",
        "Calculator",
        "medium"
    )
    if success:
        results["medium"]["success"] += 1
    else:
        results["medium"]["failed"] += 1
    
    # Test 5: Weather App (Complex)
    success, _ = test_app_generation(
        "Create a weather app that shows current weather and 5-day forecast with city search",
        "WeatherApp",
        "complex"
    )
    if success:
        results["complex"]["success"] += 1
    else:
        results["complex"]["failed"] += 1
    
    # Print summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    total_success = 0
    total_failed = 0
    
    for category, stats in results.items():
        success = stats["success"]
        failed = stats["failed"]
        total = success + failed
        
        if total > 0:
            rate = (success / total) * 100
            print(f"\n{category.upper()}:")
            print(f"  ✅ Success: {success}/{total} ({rate:.0f}%)")
            print(f"  ❌ Failed: {failed}/{total}")
            
            total_success += success
            total_failed += failed
    
    # Overall summary
    print("\n" + "-"*50)
    overall_total = total_success + total_failed
    if overall_total > 0:
        overall_rate = (total_success / overall_total) * 100
        print(f"\nOVERALL: {total_success}/{overall_total} ({overall_rate:.0f}%) successful")
        
        if overall_rate >= 80:
            print("\n✅ PRODUCTION READY - System meets quality threshold!")
        elif overall_rate >= 60:
            print("\n⚠️  PARTIALLY READY - System needs improvement")
        else:
            print("\n❌ NOT READY - Major issues need fixing")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()