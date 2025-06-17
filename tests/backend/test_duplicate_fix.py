#!/usr/bin/env python3
"""
Simple test to verify duplicate filename detection in ProjectManager
"""

import os
import sys

# Test the duplicate detection logic without running full project creation
def test_duplicate_detection():
    print("Testing duplicate filename detection logic...")
    
    # Simulate files with duplicate names
    test_files = [
        {"path": "Sources/App.swift", "content": "// App.swift"},
        {"path": "Sources/Views/SettingsView.swift", "content": "// Settings in Views"},
        {"path": "Sources/Views/Components/SettingsView.swift", "content": "// Settings in Components"},
        {"path": "Sources/SettingsView.swift", "content": "// Settings in root"},
        {"path": "Sources/Models/UserModel.swift", "content": "// User model"},
        {"path": "Sources/ViewModels/UserModel.swift", "content": "// User view model"},
    ]
    
    # Simulate the duplicate detection logic from project_manager.py
    filename_to_paths = {}
    skipped_files = []
    
    for file_info in test_files:
        path = file_info["path"]
        filename = os.path.basename(path)
        
        if filename in filename_to_paths:
            print(f"WARNING: Duplicate filename '{filename}' detected!")
            print(f"  Existing: {filename_to_paths[filename]}")
            print(f"  Skipping: {path}")
            skipped_files.append(path)
        else:
            filename_to_paths[filename] = path
    
    print("\n=== Results ===")
    print(f"Total files submitted: {len(test_files)}")
    print(f"Files that would be created: {len(filename_to_paths)}")
    print(f"Files skipped due to duplicates: {len(skipped_files)}")
    
    print("\nFinal file list:")
    for filename, path in sorted(filename_to_paths.items()):
        print(f"  {filename} -> {path}")
    
    print("\nSkipped files:")
    for path in skipped_files:
        print(f"  {path}")
    
    # Verify the logic worked correctly
    expected_kept = {
        "App.swift": "Sources/App.swift",
        "SettingsView.swift": "Sources/Views/SettingsView.swift",  # First occurrence
        "UserModel.swift": "Sources/Models/UserModel.swift",  # First occurrence
    }
    
    success = True
    for filename, expected_path in expected_kept.items():
        if filename_to_paths.get(filename) != expected_path:
            print(f"\nERROR: Expected {filename} to be at {expected_path}, but got {filename_to_paths.get(filename)}")
            success = False
    
    if success:
        print("\n✅ Duplicate detection logic is working correctly!")
    else:
        print("\n❌ Duplicate detection logic has issues!")
    
    return success

if __name__ == "__main__":
    success = test_duplicate_detection()
    sys.exit(0 if success else 1)