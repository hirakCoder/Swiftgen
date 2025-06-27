#!/usr/bin/env python3
"""
Direct test of dark mode modification without dependencies
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modification_handler import ModificationHandler

def test_dark_mode_direct():
    """Test dark mode implementation directly"""
    print("\n=== Direct Dark Mode Test ===")
    
    # Create simple app files
    files = [
        {
            "path": "Sources/App.swift",
            "content": """import SwiftUI

@main
struct TestApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}"""
        },
        {
            "path": "Sources/ContentView.swift",
            "content": """import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack {
            Text("Hello, World!")
                .font(.largeTitle)
                .padding()
            
            Button("Test Button") {
                print("Button tapped")
            }
            .padding()
        }
    }
}"""
        }
    ]
    
    # Create handler
    handler = ModificationHandler()
    
    # Test create_minimal_modification with dark mode request
    print("\n1. Testing create_minimal_modification with dark mode request:")
    result = handler.create_minimal_modification(files, "Add dark mode toggle to the app")
    
    # Check result
    print(f"   - Files returned: {len(result.get('files', []))}")
    print(f"   - Summary: {result.get('modification_summary', 'None')}")
    print(f"   - Changes: {result.get('changes_made', [])}")
    print(f"   - Modified files: {result.get('files_modified', [])}")
    
    # Check App.swift changes
    app_file = next((f for f in result['files'] if 'App.swift' in f['path']), None)
    if app_file:
        content = app_file['content']
        if '@AppStorage' in content and 'isDarkMode' in content:
            print("   ✅ App.swift has dark mode support")
        else:
            print("   ❌ App.swift missing dark mode code")
            print(f"   Content preview: {content[:200]}...")
    
    # Check ContentView changes
    view_file = next((f for f in result['files'] if 'ContentView.swift' in f['path']), None)
    if view_file:
        content = view_file['content']
        if '@AppStorage' in content and ('Toggle' in content or 'moon' in content):
            print("   ✅ ContentView has theme toggle")
        else:
            print("   ❌ ContentView missing theme toggle")
    
    # Test direct _implement_dark_theme
    print("\n2. Testing _implement_dark_theme directly:")
    direct_result = handler._implement_dark_theme(files)
    
    print(f"   - Files returned: {len(direct_result.get('files', []))}")
    print(f"   - Changes: {direct_result.get('changes_made', [])}")
    
    # Save output for inspection
    output_file = "dark_mode_test_output.json"
    with open(output_file, 'w') as f:
        json.dump({
            "minimal_modification_result": result,
            "direct_implementation_result": direct_result
        }, f, indent=2)
    print(f"\n💾 Full output saved to {output_file}")
    
    return True

if __name__ == "__main__":
    test_dark_mode_direct()