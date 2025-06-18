#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

from main import _is_complex_app

# Test complexity detection
test_descriptions = [
    "Create a food delivery app like DoorDash",
    "Build a restaurant ordering app",
    "Make a delivery app",
    "Create a simple calculator",
    "Build an e-commerce app",
    "Create a social media app"
]

print("🔍 Testing Complexity Detection:")
for desc in test_descriptions:
    is_complex = _is_complex_app(desc)
    print(f"  '{desc}' -> {'COMPLEX' if is_complex else 'SIMPLE'}")

# Test project.json reading
print("\n📁 Testing Project Complexity Reading:")
project_path = "/Users/hirakbanerjee/Desktop/SwiftGen/swiftgen-mvp/workspaces/proj_cm447idy/project.json"
if os.path.exists(project_path):
    import json
    with open(project_path, 'r') as f:
        project_data = json.load(f)
        complexity = project_data.get("app_complexity", "unknown")
        print(f"  proj_cm447idy complexity: {complexity}")
else:
    print(f"  Project not found: {project_path}")

print("\n✅ Test Complete")