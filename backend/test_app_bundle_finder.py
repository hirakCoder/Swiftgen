#!/usr/bin/env python3
"""Test the _find_app_bundle functionality"""

import os
from pathlib import Path

def test_find_app_bundle():
    """Test finding app bundles in build directories"""
    
    print("=== Testing App Bundle Finder ===\n")
    
    workspaces_dir = Path(__file__).parent.parent / "workspaces"
    
    # Check recent projects
    for project_dir in sorted(workspaces_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
        if project_dir.is_dir():
            print(f"\nProject: {project_dir.name}")
            
            # Method 1: Current implementation path
            build_dir1 = project_dir / "build" / "Build" / "Products"
            print(f"  Checking: {build_dir1.relative_to(workspaces_dir)}")
            
            if build_dir1.exists():
                apps_found = list(build_dir1.rglob("*.app"))
                if apps_found:
                    for app in apps_found:
                        print(f"    ✓ Found: {app.name}")
                        # Check if it's a directory
                        if app.is_dir():
                            print(f"      Type: Directory (correct)")
                        else:
                            print(f"      Type: File (incorrect!)")
                else:
                    print(f"    ✗ No .app bundles found")
                    # List what's there
                    items = list(build_dir1.rglob("*"))[:5]
                    if items:
                        print(f"    Contents: {[item.name for item in items]}")
            else:
                print(f"    ✗ Directory does not exist")
            
            # Method 2: Check alternative paths
            alt_paths = [
                project_dir / "DerivedData" / "Build" / "Products",
                project_dir / "build" / "Products",
                project_dir / "Build" / "Products"
            ]
            
            for alt_path in alt_paths:
                if alt_path.exists():
                    apps = list(alt_path.rglob("*.app"))
                    if apps:
                        print(f"  Alternative path has apps: {alt_path.relative_to(workspaces_dir)}")
                        for app in apps[:2]:
                            print(f"    - {app.name}")

if __name__ == "__main__":
    test_find_app_bundle()