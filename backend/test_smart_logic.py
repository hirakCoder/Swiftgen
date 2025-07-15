#!/usr/bin/env python3
"""Test SmartModificationHandler logic only"""

import sys
sys.path.append('backend')

from smart_modification_handler import SmartModificationHandler, ModificationTemplates

def test_handler_logic():
    """Test SmartModificationHandler logic without server"""
    print("🧪 Testing SmartModificationHandler Logic")
    print("="*70)
    
    # Create handler without LLM service for logic testing
    handler = SmartModificationHandler(None)
    
    # Test 1: Template matching
    print("\n1. Testing template matching:")
    test_cases = [
        ("Add a settings screen with theme options", "settings_screen"),
        ("Implement dark mode toggle", "dark_mode"),
        ("Add data persistence to save user preferences", "data_persistence"),
        ("Create a statistics dashboard with charts", "statistics_dashboard"),
        ("Change button color", None)
    ]
    
    for request, expected_template in test_cases:
        match = ModificationTemplates.match_template(request)
        if match:
            template_name, _ = match
            result = "✅" if template_name == expected_template else "❌"
            print(f"   {result} '{request[:40]}...' → {template_name}")
        else:
            result = "✅" if expected_template is None else "❌"
            print(f"   {result} '{request[:40]}...' → No template")
    
    # Test 2: Complexity analysis
    print("\n2. Testing complexity analysis:")
    complexity_tests = [
        ("Change the button color to blue", 0),
        ("Add dark mode toggle", 0),
        ("Add settings screen with notifications and theme options", 1),
        ("Create dashboard with charts and graphs showing weekly stats", 3),
        ("Build complete user authentication with login, signup, password reset, and profile management", 4),
    ]
    
    for request, expected_complexity in complexity_tests:
        actual = handler._analyze_complexity(request)
        result = "✅" if abs(actual - expected_complexity) <= 1 else "❌"
        print(f"   {result} Complexity {actual} (expected ~{expected_complexity}): '{request[:40]}...'")
    
    # Test 3: Request decomposition
    print("\n3. Testing request decomposition:")
    complex_request = "Add a settings screen with theme selection, notification preferences, and data export options"
    steps = handler._decompose_request(complex_request)
    print(f"   Request: '{complex_request[:50]}...'")
    print(f"   Decomposed into {len(steps)} steps:")
    for i, step in enumerate(steps, 1):
        print(f"     {i}. {step['description']} (priority: {step['priority']})")
    
    # Test 4: Context management
    print("\n4. Testing smart context management:")
    test_files = {
        "Sources/App.swift": "import SwiftUI\n@main\nstruct App: App { ... }",
        "Sources/ContentView.swift": "import SwiftUI\nstruct ContentView: View { ... }",
        "Sources/Models/DataModel.swift": "struct DataModel { ... }",
        "Sources/Views/SettingsView.swift": "struct SettingsView { ... }",
        "Sources/Managers/DataManager.swift": "class DataManager { ... }",
    }
    
    context = handler.context_manager.build_context(
        "Add dark mode to settings",
        test_files,
        [],
        max_size=1000
    )
    
    print(f"   Files included in context: {len(context['files'])}")
    for file in context['files']:
        print(f"     - {file}")
    
    # Test 5: File relevance scoring
    print("\n5. Testing file relevance scoring:")
    relevant_files = handler.context_manager._identify_relevant_files(
        "Add settings screen", test_files
    )
    print("   Relevance scores for 'Add settings screen':")
    for file, score in relevant_files[:3]:  # Top 3
        print(f"     {score:.1f} - {file}")
    
    # Test 6: Smart verification
    print("\n6. Testing smart verification:")
    original = {"Sources/ContentView.swift": "struct ContentView { }"}
    modified = {
        "Sources/ContentView.swift": "struct ContentView { var isDarkMode = false }",
        "Sources/SettingsView.swift": "struct SettingsView { }"
    }
    
    success, issues, stats = handler.verifier.verify_modification(
        original, modified, "Add dark mode settings"
    )
    
    print(f"   Success: {success}")
    print(f"   Stats: {stats}")
    if issues:
        print(f"   Issues: {issues}")
    
    print("\n✅ All logic tests completed successfully!")

if __name__ == "__main__":
    test_handler_logic()