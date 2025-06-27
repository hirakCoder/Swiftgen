#!/usr/bin/env python3
"""
Test dark mode modification functionality
"""

import asyncio
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_claude_service import EnhancedClaudeService
from modification_handler import ModificationHandler
from modification_verifier import ModificationVerifier

def create_simple_app():
    """Create a simple app to test dark mode modification"""
    return [
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

def test_dark_mode_implementation():
    """Test that dark mode implementation works correctly"""
    print("\n=== Testing Dark Mode Implementation ===")
    
    # Create modification handler
    mod_handler = ModificationHandler()
    
    # Test files
    files = create_simple_app()
    
    # Test dark mode implementation
    result = mod_handler._implement_dark_theme(files, "Add dark mode toggle")
    
    # Check that files were modified
    modified_files = result["files"]
    assert len(modified_files) == len(files), "All files should be returned"
    
    # Check App.swift modifications
    app_file = next(f for f in modified_files if "App.swift" in f["path"])
    app_content = app_file["content"]
    
    # Check for required dark mode code
    assert "@AppStorage" in app_content, "Should have @AppStorage for dark mode"
    assert "isDarkMode" in app_content, "Should have isDarkMode property"
    assert ".preferredColorScheme" in app_content, "Should have preferredColorScheme modifier"
    
    print("✅ App.swift properly modified for dark mode")
    
    # Check ContentView modifications
    content_file = next(f for f in modified_files if "ContentView.swift" in f["path"])
    content = content_file["content"]
    
    # Check for theme toggle
    assert "@AppStorage" in content, "ContentView should have @AppStorage"
    assert "Toggle" in content or "Button" in content, "Should have toggle mechanism"
    assert "moon" in content or "sun" in content, "Should have theme icons"
    
    print("✅ ContentView properly modified with theme toggle")
    
    # Check changes made
    changes = result.get("changes_made", [])
    assert len(changes) > 0, "Should report changes made"
    assert any("dark mode" in change.lower() for change in changes), "Should mention dark mode in changes"
    
    print(f"✅ Reported changes: {changes}")
    
    return True

async def test_dark_mode_via_llm():
    """Test dark mode modification through LLM service"""
    print("\n=== Testing Dark Mode via LLM Service ===")
    
    # Check if we have API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("⚠️ Skipping LLM test - no OPENAI_API_KEY set")
        return
    
    # Create service
    service = EnhancedClaudeService(
        claude_api_key=os.getenv("CLAUDE_API_KEY"),
        openai_api_key=openai_key
    )
    
    # Test files
    files = create_simple_app()
    
    # Request dark mode
    result = await service.modify_ios_app(
        app_name="TestApp",
        description="Test app",
        modification="Add a dark mode toggle to the app",
        files=files
    )
    
    if result and "files" in result:
        # Check modifications
        modified_files = result["files"]
        
        # Find App.swift
        app_file = next((f for f in modified_files if "App.swift" in f["path"]), None)
        if app_file:
            assert "isDarkMode" in app_file["content"], "App should have dark mode support"
            print("✅ LLM properly added dark mode to App.swift")
        
        # Check for reported changes
        changes = result.get("changes_made", [])
        print(f"✅ LLM reported changes: {changes}")
        
        return True
    else:
        print("❌ LLM failed to return valid modification")
        return False

def test_modification_verifier():
    """Test that modification verifier properly validates dark mode changes"""
    print("\n=== Testing Modification Verifier ===")
    
    verifier = ModificationVerifier()
    
    # Original files
    original_files = create_simple_app()
    
    # Create modified files (simulate dark mode addition)
    modified_files = []
    for file in original_files:
        content = file["content"]
        if "App.swift" in file["path"]:
            # Add dark mode to App
            content = content.replace(
                "@main\nstruct TestApp: App {",
                """@main
struct TestApp: App {
    @AppStorage("isDarkMode") private var isDarkMode = false"""
            )
            content = content.replace(
                "WindowGroup {",
                """WindowGroup {
            NavigationStack {"""
            )
            content = content.replace(
                "ContentView()",
                """ContentView()
                    .environmentObject(self)"""
            )
            content = content.replace(
                "}\n    }\n}",
                """            }
            .preferredColorScheme(isDarkMode ? .dark : .light)
        }
    }
}"""
            )
        modified_files.append({
            "path": file["path"],
            "content": content
        })
    
    # Verify modifications
    success, issues = verifier.verify_modifications(
        original_files,
        modified_files,
        "Add dark mode toggle",
        verbose=True
    )
    
    assert success, f"Verification should pass. Issues: {issues}"
    print("✅ Modification verifier passed")

def main():
    """Run all dark mode tests"""
    print("🧪 Testing Dark Mode Modifications")
    
    # Test direct implementation
    try:
        test_dark_mode_implementation()
    except Exception as e:
        print(f"❌ Dark mode implementation test failed: {e}")
        return False
    
    # Test modification verifier
    try:
        test_modification_verifier()
    except Exception as e:
        print(f"❌ Modification verifier test failed: {e}")
        return False
    
    # Test via LLM (async)
    try:
        asyncio.run(test_dark_mode_via_llm())
    except Exception as e:
        print(f"❌ LLM dark mode test failed: {e}")
    
    print("\n✅ Dark mode tests completed!")
    return True

if __name__ == "__main__":
    main()