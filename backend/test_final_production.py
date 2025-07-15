#!/usr/bin/env python3
"""
Final production test for SwiftGen
Tests each type of app individually with detailed logging
"""

import requests
import time
import json
from datetime import datetime


def test_app_generation(description, app_type):
    """Test generating a single app"""
    print(f"\n{'='*80}")
    print(f"Testing {app_type.upper()} App Generation")
    print(f"Description: {description}")
    print(f"{'='*80}")
    
    project_id = f"prod_test_{app_type}_{int(time.time())}"
    start_time = time.time()
    
    try:
        # Step 1: Generate the app
        print("\n📤 Sending generation request...")
        response = requests.post(
            "http://localhost:8000/api/generate",
            json={
                "description": description,
                "project_id": project_id
            },
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to start generation: {response.status_code}")
            print(f"Response: {response.text}")
            return False, f"HTTP {response.status_code}"
        
        data = response.json()
        print(f"✓ Generation started")
        print(f"  Project ID: {project_id}")
        print(f"  App Name: {data.get('app_name')}")
        
        # Step 2: Poll for status
        print("\n⏳ Waiting for generation to complete...")
        max_attempts = 60  # 5 minutes
        for attempt in range(max_attempts):
            time.sleep(5)
            
            status_response = requests.get(
                f"http://localhost:8000/api/project/{project_id}/status",
                timeout=10
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get("status", "unknown")
                
                print(f"  Attempt {attempt + 1}/{max_attempts}: Status = {status}")
                
                if status == "completed":
                    duration = time.time() - start_time
                    files_count = status_data.get("swift_file_count", 0)
                    
                    print(f"\n✅ SUCCESS! App generated in {duration:.2f} seconds")
                    print(f"  Files created: {files_count}")
                    
                    # Get file list
                    files_response = requests.get(
                        f"http://localhost:8000/api/project/{project_id}/files",
                        timeout=10
                    )
                    
                    if files_response.status_code == 200:
                        files_data = files_response.json()
                        print(f"\n📁 Generated Files:")
                        for file in files_data.get("files", []):
                            print(f"    - {file['path']} ({file['size']} bytes)")
                    
                    return True, f"Success in {duration:.2f}s with {files_count} files"
                
                elif status == "failed":
                    error = status_data.get("error", "Unknown error")
                    print(f"\n❌ FAILED: {error}")
                    return False, error
            
            else:
                print(f"  Warning: Status check failed with {status_response.status_code}")
        
        print(f"\n❌ TIMEOUT: Generation did not complete in 5 minutes")
        return False, "Timeout"
        
    except requests.exceptions.Timeout:
        print(f"\n❌ REQUEST TIMEOUT")
        return False, "Request timeout"
    except Exception as e:
        print(f"\n❌ EXCEPTION: {str(e)}")
        return False, str(e)


def test_app_modification(project_id, modification, mod_type):
    """Test modifying an existing app"""
    print(f"\n{'='*60}")
    print(f"Testing {mod_type.upper()} Modification")
    print(f"Modification: {modification}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # Send modification request
        print("\n📤 Sending modification request...")
        response = requests.post(
            "http://localhost:8000/api/modify",
            json={
                "project_id": project_id,
                "modification": modification
            },
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to start modification: {response.status_code}")
            return False, f"HTTP {response.status_code}"
        
        print(f"✓ Modification request sent")
        
        # Wait and check status
        time.sleep(15)  # Give it time to process
        
        status_response = requests.get(
            f"http://localhost:8000/api/project/{project_id}/status",
            timeout=10
        )
        
        if status_response.status_code == 200:
            duration = time.time() - start_time
            print(f"\n✅ Modification completed in {duration:.2f} seconds")
            return True, f"Success in {duration:.2f}s"
        else:
            print(f"\n❌ Failed to verify modification")
            return False, "Verification failed"
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {str(e)}")
        return False, str(e)


def main():
    """Run production tests"""
    print(f"\n{'='*80}")
    print(f"🚀 SwiftGen Final Production Test")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    
    # Check server health first
    try:
        health_response = requests.get("http://localhost:8000/api/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"\n✅ Server is healthy")
            print(f"  LLMs available: {health_data['llm_availability']}")
        else:
            print(f"\n❌ Server health check failed")
            return
    except Exception as e:
        print(f"\n❌ Cannot connect to server: {e}")
        return
    
    results = {
        "simple": [],
        "medium": [],
        "complex": [],
        "modifications": []
    }
    
    # Test 1: Simple Timer App
    success, message = test_app_generation(
        "Create a simple timer app with start, stop and reset buttons",
        "timer"
    )
    results["simple"].append({"app": "timer", "success": success, "message": message})
    
    # If timer succeeded, test modification
    if success:
        project_id = f"prod_test_timer_{int(time.time()) - 300}"  # Approximate ID
        mod_success, mod_message = test_app_modification(
            project_id,
            "Add a dark mode toggle",
            "simple"
        )
        results["modifications"].append({
            "app": "timer",
            "mod_type": "simple",
            "success": mod_success,
            "message": mod_message
        })
    
    # Test 2: Todo App
    success, message = test_app_generation(
        "Build a todo list app with ability to add, complete and delete tasks",
        "todo"
    )
    results["simple"].append({"app": "todo", "success": success, "message": message})
    
    # Test 3: Counter App
    success, message = test_app_generation(
        "Make a counter app with increment and decrement buttons",
        "counter"
    )
    results["simple"].append({"app": "counter", "success": success, "message": message})
    
    # Test 4: Calculator App (Medium)
    success, message = test_app_generation(
        "Create a calculator app with basic arithmetic operations (+, -, *, /)",
        "calculator"
    )
    results["medium"].append({"app": "calculator", "success": success, "message": message})
    
    # Test 5: Weather App (Medium)
    success, message = test_app_generation(
        "Build a weather app that shows current temperature and conditions",
        "weather"
    )
    results["medium"].append({"app": "weather", "success": success, "message": message})
    
    # Summary Report
    print(f"\n{'='*80}")
    print(f"📊 PRODUCTION TEST SUMMARY")
    print(f"{'='*80}")
    
    # Calculate success rates
    simple_success = sum(1 for r in results["simple"] if r["success"])
    simple_total = len(results["simple"])
    medium_success = sum(1 for r in results["medium"] if r["success"])
    medium_total = len(results["medium"])
    mod_success = sum(1 for r in results["modifications"] if r["success"])
    mod_total = len(results["modifications"])
    
    total_success = simple_success + medium_success + mod_success
    total_tests = simple_total + medium_total + mod_total
    
    print(f"\n✅ Simple Apps: {simple_success}/{simple_total} ({simple_success/simple_total*100:.0f}%)")
    for result in results["simple"]:
        status = "✅" if result["success"] else "❌"
        print(f"  {status} {result['app']}: {result['message']}")
    
    print(f"\n✅ Medium Apps: {medium_success}/{medium_total} ({medium_success/medium_total*100:.0f}%)")
    for result in results["medium"]:
        status = "✅" if result["success"] else "❌"
        print(f"  {status} {result['app']}: {result['message']}")
    
    if mod_total > 0:
        print(f"\n✅ Modifications: {mod_success}/{mod_total} ({mod_success/mod_total*100:.0f}%)")
        for result in results["modifications"]:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['app']} ({result['mod_type']}): {result['message']}")
    
    # Overall verdict
    success_rate = (total_success / total_tests * 100) if total_tests > 0 else 0
    print(f"\n{'='*80}")
    print(f"📈 OVERALL SUCCESS RATE: {success_rate:.1f}% ({total_success}/{total_tests})")
    
    if success_rate >= 95:
        print(f"\n🎉 ✅ PRODUCTION READY! SwiftGen is performing excellently!")
    elif success_rate >= 85:
        print(f"\n⚠️  NEARLY READY! Just a few issues to resolve.")
    else:
        print(f"\n❌ NOT READY. Significant issues need to be addressed.")
    
    print(f"{'='*80}")
    
    # Save results
    with open("production_test_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "summary": {
                "total_tests": total_tests,
                "total_success": total_success,
                "success_rate": success_rate
            }
        }, f, indent=2)
    
    print(f"\n💾 Results saved to production_test_results.json")


if __name__ == "__main__":
    main()