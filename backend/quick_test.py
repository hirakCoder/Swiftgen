#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

from file_deduplication_system import FileDeduplicationSystem

# Test the deduplication system
project_path = "/Users/hirakbanerjee/Desktop/SwiftGen/swiftgen-mvp/workspaces/proj_97a0a41a"
if os.path.exists(project_path):
    dedup = FileDeduplicationSystem(project_path)
    status = dedup.get_status_report()
    print("Project status:")
    print(f"  Total files: {status['total_swift_files']}")
    print(f"  Duplicates: {status['duplicates']}")
    print(f"  Issues: {status['validation_issues']}")
    
    if status['duplicates']:
        print("\nRemoving duplicates...")
        removed = dedup.remove_duplicate_files()
        print(f"Removed: {removed}")
        
        # Check status after
        status2 = dedup.get_status_report()
        print(f"After cleanup - Total files: {status2['total_swift_files']}")
        print(f"After cleanup - Duplicates: {status2['duplicates']}")
else:
    print(f"Project path does not exist: {project_path}")

# Test syntax validator
print("\n" + "="*50)
print("Testing syntax validator...")

from syntax_validator import SyntaxValidator

validator = SyntaxValidator()
test_content = '''import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack {
            Text("Hello, World!")
            Button("Click me") {
                print("Button clicked")
            }
        }
    }
}'''

valid, errors = validator.validate_syntax('ContentView.swift', test_content)
print(f"Syntax validation result: {valid}")
print(f"Errors: {errors}")

print("\nAll tests completed!")