#!/usr/bin/env python3
"""
Run REAL tests with actual server
This script actually tests app generation and modifications
"""

import os
import sys
import json
import time
import requests
import subprocess
from datetime import datetime

def log(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

def check_server():
    """Check if server is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_server():
    """Start the server"""
    log("Starting server...")
    # Start server in background
    server_process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    for i in range(30):
        time.sleep(1)
        if check_server():
            log("✅ Server started successfully")
            return server_process
    
    log("❌ Server failed to start")
    server_process.terminate()
    return None

def test_app_generation(description, expected_files):
    """Test generating an app"""
    log(f"\nTesting: {description}")
    
    try:
        # Send generation request
        response = requests.post(
            "http://localhost:8000/api/generate",
            json={"description": description},
            timeout=60
        )
        
        if response.status_code != 200:
            log(f"❌ Generation failed: {response.status_code}")
            return None
        
        data = response.json()
        project_id = data.get('project_id')
        log(f"Project ID: {project_id}")
        
        # Wait for generation
        log("Waiting for generation...")
        time.sleep(20)
        
        # Check results
        project_path = f"../workspaces/{project_id}"
        if not os.path.exists(project_path):
            log("❌ Project directory not created")
            return None
        
        # Count Swift files
        swift_files = []
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.endswith('.swift'):
                    swift_files.append(file)
        
        log(f"✅ Generated {len(swift_files)} Swift files")
        
        # Check for expected files
        for expected in expected_files:
            found = any(expected in f for f in swift_files)
            log(f"   {expected}: {'✅' if found else '❌'}")
        
        # Check build status
        build_dir = os.path.join(project_path, 'build/Build/Products/Debug-iphonesimulator')
        if os.path.exists(build_dir):
            apps = [f for f in os.listdir(build_dir) if f.endswith('.app')]
            if apps:
                log(f"✅ Build successful: {apps[0]}")
            else:
                log("❌ Build failed - no .app bundle")
        else:
            log("❌ No build directory")
        
        # Check for validator activity
        log_file = f"backend/debug_logs/debug_{project_id}.log"
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                content = f.read()
                if 'Swift validator' in content:
                    log("✅ Swift validator was active")
                if 'Added Hashable conformance' in content:
                    log("   - Fixed Hashable conformance")
                if 'Removed semicolons' in content:
                    log("   - Removed semicolons")
        
        return project_id
        
    except Exception as e:
        log(f"❌ Exception: {e}")
        return None

def test_modification(project_id, modification):
    """Test modifying an app"""
    log(f"\nTesting modification: {modification}")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/modify",
            json={
                "project_id": project_id,
                "modification_request": modification
            },
            timeout=60
        )
        
        if response.status_code == 200:
            log("✅ Modification accepted")
            time.sleep(10)
            return True
        else:
            log(f"❌ Modification failed: {response.status_code}")
            return False
            
    except Exception as e:
        log(f"❌ Exception: {e}")
        return False

def main():
    """Run real tests"""
    log("=== REAL SwiftGen Test Suite ===")
    log("This will actually generate apps and test modifications")
    
    # Check if server is running
    server_process = None
    if not check_server():
        log("Server not running")
        response = input("Start server? (y/n): ")
        if response.lower() == 'y':
            server_process = start_server()
            if not server_process:
                return
        else:
            log("Cannot test without server")
            return
    else:
        log("✅ Server already running")
    
    try:
        # Test 1: Simple Calculator
        project_id = test_app_generation(
            "Create a simple calculator app",
            ["CalculatorView", "ContentView"]
        )
        
        if project_id:
            # Test modification
            test_modification(project_id, "Change the background color to blue")
            test_modification(project_id, "Add a history feature")
        
        # Test 2: Todo App
        project_id = test_app_generation(
            "Create a todo list app",
            ["TodoItem", "TodoListView", "ContentView"]
        )
        
        # Test 3: Weather App (API)
        project_id = test_app_generation(
            "Create a weather app that shows current weather",
            ["WeatherService", "WeatherView", "ContentView"]
        )
        
        log("\n=== Test Complete ===")
        
    finally:
        if server_process:
            log("Stopping server...")
            server_process.terminate()

if __name__ == "__main__":
    main()