#!/usr/bin/env python3
"""Simple modification test"""

import requests
import time
import subprocess

def test_modification():
    """Test a modification and monitor logs"""
    
    print("🧪 Testing Modification System")
    print("=" * 60)
    
    # First, let's check if there's an existing project we can modify
    # or create a new one
    
    # Step 1: Create a simple app
    print("\n1️⃣ Creating Timer App...")
    response = requests.post("http://localhost:8000/api/generate", json={
        "app_name": "QuickTimer",
        "description": "Create a simple timer app with start, stop and reset buttons"
    })
    
    if response.status_code != 200:
        print(f"❌ Failed to create app: {response.status_code}")
        return
    
    result = response.json()
    project_id = result.get('project_id')
    print(f"✅ Project created: {project_id}")
    
    # Step 2: Wait for build
    print("\n⏳ Waiting for initial build (30 seconds)...")
    time.sleep(30)
    
    # Check status
    status_resp = requests.get(f"http://localhost:8000/api/projects/{project_id}/status")
    if status_resp.status_code == 200:
        status = status_resp.json()
        print(f"📊 Build status: {status.get('build_status')}")
        print(f"📁 Files: {status.get('file_count')}")
    
    # Step 3: Tail the log file
    print("\n📋 Starting log monitor...")
    log_process = subprocess.Popen(
        ['tail', '-f', 'server_fixed.log'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    # Step 4: Make modification
    print("\n2️⃣ Making Modification: Add dark mode toggle...")
    mod_response = requests.post("http://localhost:8000/api/modify", json={
        "project_id": project_id,
        "modification": "Add a dark mode toggle switch in the navigation bar that changes the app's color scheme"
    })
    
    if mod_response.status_code == 200:
        print("✅ Modification request sent")
    else:
        print(f"❌ Modification failed: {mod_response.status_code}")
    
    # Monitor logs for 45 seconds
    print("\n📊 Monitoring logs for 45 seconds...")
    print("-" * 60)
    
    start_time = time.time()
    duplicate_found = False
    modification_details = []
    errors = []
    
    while time.time() - start_time < 45:
        line = log_process.stdout.readline()
        if line:
            line = line.strip()
            
            # Look for key patterns
            if "duplicate" in line.lower() or "used twice" in line.lower():
                duplicate_found = True
                print(f"❌ DUPLICATE: {line}")
            elif "files_modified" in line.lower():
                modification_details.append(line)
                print(f"📝 MODIFIED: {line}")
            elif "error" in line.lower() and "INFO:SwiftGen" not in line:
                errors.append(line)
                print(f"⚠️  ERROR: {line}")
            elif "[OPTIMIZED]" in line:
                print(f"🔧 {line}")
            elif "modification_summary" in line.lower():
                print(f"📋 {line}")
    
    log_process.terminate()
    
    # Step 5: Check final status
    print("\n" + "-" * 60)
    print("3️⃣ Final Check...")
    
    time.sleep(5)
    final_status = requests.get(f"http://localhost:8000/api/projects/{project_id}/status")
    if final_status.status_code == 200:
        status = final_status.json()
        print(f"📊 Final build status: {status.get('build_status')}")
    
    # Summary
    print("\n📊 TEST SUMMARY:")
    print(f"   Duplicate files detected: {'YES ❌' if duplicate_found else 'NO ✅'}")
    print(f"   Modification details found: {'YES ✅' if modification_details else 'NO ❌'}")
    print(f"   Errors encountered: {len(errors)}")
    
    if modification_details:
        print("\n   Modification details:")
        for detail in modification_details[:3]:
            print(f"   - {detail}")

if __name__ == "__main__":
    test_modification()