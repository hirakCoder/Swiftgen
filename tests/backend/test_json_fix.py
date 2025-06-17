#!/usr/bin/env python3
"""Test the JSON parsing fix for modification responses"""

import json
import re

def test_json_parsing():
    """Test various problematic JSON responses"""
    
    test_cases = [
        # Case 1: Unescaped newlines
        {
            "name": "Unescaped newlines",
            "input": '{"content": "struct MyView: View {\n    var body: some View {\n        Text(\\"Hello\\")\\n    }\\n}"}',
            "should_fail": True
        },
        # Case 2: Invalid escape sequence
        {
            "name": "Invalid escape",
            "input": '{"content": "Text(\\"Hello\\").environment(\\.dismiss)"}',
            "should_fail": True
        },
        # Case 3: Valid JSON
        {
            "name": "Valid JSON",
            "input": '{"content": "struct MyView: View {\\n    var body: some View {\\n        Text(\\"Hello\\")\\n    }\\n}"}',
            "should_fail": False
        }
    ]
    
    for test in test_cases:
        print(f"\n=== Testing: {test['name']} ===")
        print(f"Input: {test['input'][:100]}...")
        
        try:
            # First attempt - direct parsing
            result = json.loads(test['input'])
            print("✅ Direct parsing succeeded")
            if test['should_fail']:
                print("⚠️  Expected to fail but succeeded")
        except json.JSONDecodeError as e:
            print(f"❌ Direct parsing failed: {e}")
            
            if not test['should_fail']:
                print("⚠️  Expected to succeed but failed")
            
            # Try our fix
            try:
                cleaned = test['input']
                
                # Fix unescaped newlines and tabs in strings
                def fix_string_escapes(match):
                    s = match.group(1)
                    s = s.replace('\n', '\\n').replace('\t', '\\t')
                    s = s.replace('\\', '\\\\').replace('"', '\\"')
                    return f'"{s}"'
                
                # This regex finds string values in JSON
                cleaned = re.sub(r'"([^"\\]*(\\.[^"\\]*)*)"', fix_string_escapes, cleaned)
                
                result = json.loads(cleaned)
                print("✅ Fixed parsing succeeded")
            except Exception as e2:
                print(f"❌ Fixed parsing failed: {e2}")

def test_actual_response():
    """Test with a response similar to what the LLM might generate"""
    
    response = '''```json
{
    "app_name": "Fancy Timer",
    "bundle_id": "com.swiftgen.fancytimer",
    "files": [
        {
            "path": "Sources/ContentView.swift",
            "content": "import SwiftUI\\n\\nstruct ContentView: View {\\n    @StateObject private var timerVM = TimerViewModel()\\n    \\n    var body: some View {\\n        ZStack {\\n            // Dark theme background\\n            Color.black.edgesIgnoringSafeArea(.all)\\n            \\n            VStack(spacing: 40) {\\n                Text(\\"Fancy Timer\\")\\n                    .font(.largeTitle)\\n                    .foregroundColor(.white)\\n                \\n                Text(timerVM.timeString)\\n                    .font(.system(size: 60, weight: .thin, design: .monospaced))\\n                    .foregroundColor(.white)\\n            }\\n        }\\n    }\\n}"
        }
    ],
    "modification_summary": "Added dark theme to timer app",
    "changes_made": ["Added dark background", "Changed text colors to white"]
}
```'''
    
    print("\n=== Testing actual LLM response ===")
    
    # Strip markdown code blocks
    if response.startswith("```json"):
        response = response[7:]
    if response.endswith("```"):
        response = response[:-3]
    
    try:
        result = json.loads(response)
        print("✅ Parsed successfully!")
        print(f"App name: {result.get('app_name')}")
        print(f"Files: {len(result.get('files', []))}")
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse: {e}")
        print(f"Error position: {e.pos}")
        print(f"Context: ...{response[max(0, e.pos-20):e.pos+20]}...")

if __name__ == "__main__":
    print("🧪 Testing JSON Parsing Fixes")
    print("=" * 60)
    
    test_json_parsing()
    test_actual_response()
    
    print("\n" + "=" * 60)
    print("✅ Test completed")