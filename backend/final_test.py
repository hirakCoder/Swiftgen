#!/usr/bin/env python3
"""Final production test after all fixes - July 14, 2025"""

import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def test_generation(desc, name):
    """Test app generation"""
    log(f"\nTesting: {name}")
    
    # Generate
    resp = requests.post(f"{BASE_URL}/api/generate", 
                        json={"description": desc, "app_name": name})
    
    if resp.status_code != 200:
        log(f"❌ Generation failed: {resp.status_code}")
        return False
    
    project_id = resp.json().get("project_id")
    log(f"✅ Created: {project_id}")
    
    # Wait for build
    log("⏳ Building (30s)...")
    time.sleep(30)
    
    # Check status
    status = requests.get(f"{BASE_URL}/api/status/{project_id}")
    if status.status_code == 200:
        data = status.json()
        success = data.get("build_success", False)
        log(f"{'✅' if success else '❌'} Build: {data.get('build_status')}")
        return success
    else:
        log("❌ Status check failed")
        return False

# Main test
log("="*60)
log("🚀 SwiftGen Final Production Test")
log("="*60)

# Test simple apps
results = []

tests = [
    ("Create a simple counter app with + and - buttons", "Counter1"),
    ("Create a timer app with start/stop", "Timer1"),
    ("Create a todo list app", "Todo1"),
    ("Create a calculator app", "Calc1")
]

for desc, name in tests:
    results.append(test_generation(desc, name))
    
# Summary
log("\n" + "="*60)
log("📊 FINAL RESULTS")
log("="*60)

success = sum(results)
total = len(results)
rate = (success/total)*100 if total > 0 else 0

log(f"\n✅ Success: {success}/{total} ({rate:.0f}%)")
log(f"❌ Failed: {total-success}/{total}")

if rate >= 75:
    log("\n🎉 PRODUCTION READY!")
elif rate >= 50:
    log("\n⚠️  PARTIALLY READY")
else:
    log("\n❌ NOT READY")

log("="*60)