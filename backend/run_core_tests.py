#!/usr/bin/env python3
"""
Quick runner for core functionality tests
"""

import subprocess
import sys
import time

def main():
    print("=" * 60)
    print("Running SwiftGen Core Functionality Tests")
    print("=" * 60)
    
    # Make sure server is running
    print("\nChecking server status...")
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=2)
        print("✅ Server is running")
    except:
        print("❌ Server is not running. Please start it with:")
        print("   cd backend && source venv/bin/activate && python main.py")
        sys.exit(1)
    
    # Run the core functionality tests
    print("\nRunning tests...")
    result = subprocess.run(
        [sys.executable, "test_core_functionality.py"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    # Also run the main test suite if requested
    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        print("\n" + "=" * 60)
        print("Running Full Test Suite")
        print("=" * 60)
        
        result = subprocess.run(
            [sys.executable, "test_suite.py"],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
    
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()