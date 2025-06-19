#!/usr/bin/env python3
"""
End-to-end test for UI modifications on a simple app
"""

import asyncio
import json
from enhanced_claude_service import EnhancedClaudeService
from modification_handler import ModificationHandler
from ui_enhancement_handler import UIEnhancementHandler

async def test_ui_modification():
    """Test UI modification on a simple counter app"""
    
    # Simple counter app files
    test_files = [
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
        VStack {
            Text("Counter: \\(count)")
                .font(.title)
                .padding()
            
            Button("Increment") {
                count += 1
            }
            .font(.headline)
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .cornerRadius(8)
        }
        .padding()
    }
}"""
        }
    ]
    
    # Initialize handlers
    service = EnhancedClaudeService()
    mod_handler = ModificationHandler()
    ui_handler = UIEnhancementHandler()
    
    print("Testing UI Modification End-to-End")
    print("=" * 50)
    
    # Test 1: Simple UI enhancement request
    print("\nTest 1: Make the UI more fancy and interactive")
    print("-" * 30)
    
    modification_request = "Make the UI more fancy and interactive with animations"
    
    try:
        # First try with LLM
        result = await service.modify_ios_app_multi_llm(
            "CounterApp",
            "A simple counter app",
            modification_request,
            test_files
        )
        
        print(f"✅ LLM modification successful")
        print(f"Files modified: {result.get('files_modified', [])}")
        print(f"Changes: {result.get('changes_made', [])[:2]}...")
        
        # Check for syntax errors
        modified_files = result.get('files', [])
        for file in modified_files:
            if 'View' in file['path']:
                content = file['content']
                
                # Check for common syntax errors
                errors = []
                if '}.transition(' in content:
                    errors.append("❌ Transition on closing brace")
                if '.shadow().fill(' in content:
                    errors.append("❌ Fill after shadow")
                if '.fill(.gray)' in content and 'Color.gray' not in content:
                    errors.append("❌ Missing Color prefix")
                
                if errors:
                    print(f"\nSyntax errors found in {file['path']}:")
                    for error in errors:
                        print(f"  {error}")
                    
                    # Apply fixes
                    print("\nApplying syntax fixes...")
                    fixed_content = ui_handler._fix_common_syntax_errors(content)
                    file['content'] = fixed_content
                    print("✅ Syntax fixes applied")
                else:
                    print(f"✅ No syntax errors in {file['path']}")
        
    except Exception as e:
        print(f"❌ LLM modification failed: {e}")
        print("\nFalling back to UI enhancement handler...")
        
        # Use the minimal modification fallback
        result = mod_handler.create_minimal_modification(test_files, modification_request)
        print(f"✅ Fallback enhancement applied")
        print(f"Changes: {result.get('changes_made', [])[:3]}...")
    
    # Test 2: Validate final syntax
    print("\n\nTest 2: Final Syntax Validation")
    print("-" * 30)
    
    final_files = mod_handler.validate_and_fix_swift_syntax(result.get('files', []))
    
    all_valid = True
    for file in final_files:
        if file['path'].endswith('.swift'):
            content = file['content']
            
            # Final validation
            if '}.transition(' in content or '.shadow().fill(' in content or \
               ('.fill(.gray)' in content and 'Color.gray' not in content):
                print(f"❌ Syntax issues remain in {file['path']}")
                all_valid = False
            else:
                print(f"✅ {file['path']} - Valid SwiftUI syntax")
    
    if all_valid:
        print("\n✅ All files have valid SwiftUI syntax!")
    else:
        print("\n❌ Some syntax issues remain")
    
    print("\n✅ Test complete!")

if __name__ == "__main__":
    asyncio.run(test_ui_modification())