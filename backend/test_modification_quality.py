#!/usr/bin/env python3
"""Test modification quality improvements"""

import asyncio
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_modification():
    from enhanced_claude_service import EnhancedClaudeService
    from ui_quality_validator import UIQualityValidator
    
    print("🧪 Testing Modification Quality")
    print("=" * 60)
    
    service = EnhancedClaudeService()
    validator = UIQualityValidator()
    
    # Sample app files (simple counter)
    existing_files = [
        {
            "path": "Sources/App.swift",
            "content": """import SwiftUI

@main
struct CounterApp: App {
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
    @State private var count = 0
    
    var body: some View {
        VStack(spacing: 30) {
            Text("Counter")
                .font(.largeTitle)
                .foregroundColor(.primary)
            
            Text("\\(count)")
                .font(.system(size: 60))
                .fontWeight(.bold)
                .foregroundColor(.primary)
            
            HStack(spacing: 20) {
                Button(action: { count -= 1 }) {
                    Image(systemName: "minus.circle.fill")
                        .font(.system(size: 44))
                        .foregroundColor(.red)
                }
                
                Button(action: { count += 1 }) {
                    Image(systemName: "plus.circle.fill")
                        .font(.system(size: 44))
                        .foregroundColor(.green)
                }
            }
            
            Button("Reset") {
                count = 0
            }
            .padding()
            .background(Color.accentColor)
            .foregroundColor(.white)
            .cornerRadius(10)
        }
        .padding()
    }
}"""
        }
    ]
    
    # Test modification
    modification_request = "Add a dark mode toggle to the app"
    
    print(f"\n📝 Modification Request: {modification_request}")
    print(f"   Existing files: {len(existing_files)}")
    
    try:
        # Perform modification
        result = await service.modify_ios_app(
            app_name="CounterApp",
            description="A simple counter app",
            modification=modification_request,
            files=existing_files
        )
        
        # Check result
        print(f"\n✅ Modification Result:")
        print(f"   Success: {result.get('success', 'NOT SET')}")
        print(f"   Files returned: {len(result.get('files', []))}")
        print(f"   Files modified: {result.get('files_modified', [])}")
        
        # Check UI quality of modified app
        if result.get('success') and 'files' in result:
            is_valid, issues, score = validator.validate_ui_quality(result['files'])
            
            print(f"\n🎨 UI Quality After Modification:")
            print(f"   Score: {score}/100")
            print(f"   Valid: {is_valid}")
            if issues:
                print(f"   Issues:")
                for issue in issues[:5]:
                    print(f"     - {issue}")
            
            # Check if dark mode was properly added
            dark_mode_found = False
            for file in result['files']:
                if '@AppStorage("isDarkMode")' in file.get('content', ''):
                    dark_mode_found = True
                    print(f"\n✅ Dark mode toggle properly implemented in {file['path']}")
                    break
            
            if not dark_mode_found:
                print("\n⚠️  Dark mode toggle not found in modified files")
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_modification())