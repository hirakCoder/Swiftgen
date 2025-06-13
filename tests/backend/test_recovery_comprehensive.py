#!/usr/bin/env python3
"""Comprehensive test of error recovery system improvements"""

import asyncio
import json
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from robust_error_recovery_system import RobustErrorRecoverySystem
from intelligent_error_recovery import IntelligentErrorRecovery

async def test_persistence_controller_recovery():
    """Test recovery from PersistenceController errors"""
    print("\n=== Testing PersistenceController Error Recovery ===")
    
    # Sample files with PersistenceController errors
    swift_files = [
        {
            "path": "Sources/MyApp.swift",
            "content": """import SwiftUI
import CoreData

@main
struct MyApp: App {
    let persistenceController = PersistenceController.shared
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.managedObjectContext, persistenceController.container.viewContext)
        }
    }
}"""
        },
        {
            "path": "Sources/ContentView.swift",
            "content": """import SwiftUI
import CoreData

struct ContentView: View {
    @Environment(\.managedObjectContext) private var viewContext
    @FetchRequest(sortDescriptors: []) private var items: FetchedResults<Item>
    
    var body: some View {
        Text("Hello")
    }
}"""
        }
    ]
    
    # Typical PersistenceController errors
    errors = [
        "Sources/MyApp.swift:6:9: error: cannot find 'PersistenceController' in scope",
        "Sources/MyApp.swift:11:51: error: cannot find 'persistenceController' in scope",
        "Sources/ContentView.swift:5:18: error: cannot find 'managedObjectContext' in scope",
        "Sources/ContentView.swift:6:63: error: cannot find type 'Item' in scope"
    ]
    
    recovery_system = RobustErrorRecoverySystem()
    success, fixed_files, fixes = await recovery_system.recover_from_errors(errors, swift_files)
    
    print(f"Recovery success: {success}")
    print(f"Fixes applied: {fixes}")
    
    if success:
        for file in fixed_files:
            print(f"\nFixed {file['path']}:")
            # Check that Core Data references were removed
            if "CoreData" in file["content"] or "PersistenceController" in file["content"]:
                print("❌ Core Data references still present!")
                return False
            else:
                print("✅ Core Data references successfully removed")
    
    return success

async def test_codable_recovery():
    """Test recovery from Codable conformance errors"""
    print("\n=== Testing Codable Error Recovery ===")
    
    swift_files = [
        {
            "path": "Sources/Models.swift",
            "content": """import Foundation

struct TodoItem: Identifiable {
    let id = UUID()
    var title: String
    var isCompleted: Bool
}

struct User {
    var name: String
    var email: String
}

class Settings: ObservableObject {
    @Published var theme: String = "light"
}"""
        }
    ]
    
    errors = [
        "Sources/Models.swift:3:8: error: type 'TodoItem' does not conform to protocol 'Decodable'",
        "Sources/Models.swift:3:8: error: type 'TodoItem' does not conform to protocol 'Encodable'",
        "Sources/Models.swift:9:8: error: type 'User' does not conform to protocol 'Codable'",
        "Sources/Models.swift:14:7: error: type 'Settings' does not conform to protocol 'Codable'"
    ]
    
    # Test both systems
    print("\n--- Testing RobustErrorRecoverySystem ---")
    recovery_system = RobustErrorRecoverySystem()
    success1, fixed_files1, fixes1 = await recovery_system.recover_from_errors(errors, swift_files)
    
    print(f"Recovery success: {success1}")
    print(f"Fixes applied: {fixes1}")
    
    if success1:
        for file in fixed_files1:
            content = file["content"]
            # Check conformances
            if "TodoItem: Identifiable, Codable" in content:
                print("✅ TodoItem has Codable conformance")
            elif "TodoItem: Identifiable" in content and "Codable" not in content:
                print("❌ TodoItem missing Codable conformance")
                return False
                
            if "User: Codable" in content:
                print("✅ User has Codable conformance")
            elif "struct User" in content and "Codable" not in content:
                print("❌ User missing Codable conformance")
                return False
    
    print("\n--- Testing IntelligentErrorRecovery ---")
    intelligent_recovery = IntelligentErrorRecovery()
    
    # Categorize errors
    error_analysis = intelligent_recovery._analyze_errors(errors)
    success2, fixed_files2 = intelligent_recovery._fix_type_errors(errors, swift_files, error_analysis)
    
    print(f"Recovery success: {success2}")
    
    return success1 or success2

async def test_string_literal_recovery():
    """Test recovery from string literal errors"""
    print("\n=== Testing String Literal Error Recovery ===")
    
    swift_files = [
        {
            "path": "Sources/BadStrings.swift",
            "content": """import SwiftUI

struct BadStringsView: View {
    var body: some View {
        VStack {
            Text('Hello World')
            Text("Welcome to my app)
            Button("Click me") {
                print("Button clicked
            }
        }
    }
}"""
        }
    ]
    
    errors = [
        "Sources/BadStrings.swift:6:18: error: single quotes are not allowed for string literals",
        "Sources/BadStrings.swift:7:18: error: unterminated string literal",
        "Sources/BadStrings.swift:9:23: error: unterminated string literal"
    ]
    
    recovery_system = RobustErrorRecoverySystem()
    success, fixed_files, fixes = await recovery_system.recover_from_errors(errors, swift_files)
    
    print(f"Recovery success: {success}")
    print(f"Fixes applied: {fixes}")
    
    if success:
        content = fixed_files[0]["content"]
        # Check fixes
        if "'Hello World'" in content:
            print("❌ Single quotes not fixed")
            return False
        if '"Welcome to my app)' in content:
            print("❌ Unterminated string not fixed")
            return False
        print("✅ String literals fixed correctly")
    
    return success

async def test_complex_scenario():
    """Test a complex scenario with multiple error types"""
    print("\n=== Testing Complex Multi-Error Scenario ===")
    
    swift_files = [
        {
            "path": "Sources/ComplexApp.swift",
            "content": """import SwiftUI
import CoreData

@main
struct ComplexApp: App {
    let persistenceController = PersistenceController.shared
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.managedObjectContext, persistenceController.container.viewContext)
        }
    }
}"""
        },
        {
            "path": "Sources/DataModel.swift",
            "content": """import Foundation

struct Task: Identifiable {
    let id = UUID()
    var title: String
    var priority: Priority
}

enum Priority {
    case low
    case medium
    case high
}

struct Project {
    var name: String
    var tasks: [Task]
}"""
        },
        {
            "path": "Sources/BadView.swift",
            "content": """import SwiftUI

struct BadView: View {
    @State private var message = 'Hello
    
    var body: some View {
        Text("Welcome to SwiftUI)
    }
}"""
        }
    ]
    
    errors = [
        # PersistenceController errors
        "Sources/ComplexApp.swift:6:9: error: cannot find 'PersistenceController' in scope",
        "Sources/ComplexApp.swift:11:51: error: cannot find 'persistenceController' in scope",
        # Codable errors
        "Sources/DataModel.swift:3:8: error: type 'Task' does not conform to protocol 'Codable'",
        "Sources/DataModel.swift:15:8: error: type 'Project' does not conform to protocol 'Codable'",
        # String literal errors
        "Sources/BadView.swift:4:34: error: single quotes are not allowed",
        "Sources/BadView.swift:4:40: error: unterminated string literal",
        "Sources/BadView.swift:7:14: error: unterminated string literal"
    ]
    
    recovery_system = RobustErrorRecoverySystem()
    success, fixed_files, fixes = await recovery_system.recover_from_errors(errors, swift_files)
    
    print(f"Recovery success: {success}")
    print(f"Fixes applied: {fixes}")
    
    if success:
        print("\nVerifying fixes:")
        
        # Check each file
        for file in fixed_files:
            if "ComplexApp.swift" in file["path"]:
                if "PersistenceController" in file["content"] or "CoreData" in file["content"]:
                    print("❌ ComplexApp still has Core Data references")
                    return False
                print("✅ ComplexApp Core Data removed")
                
            elif "DataModel.swift" in file["path"]:
                content = file["content"]
                if "Task: Identifiable, Codable" in content or "Task: Codable" in content:
                    print("✅ Task has Codable conformance")
                else:
                    print("❌ Task missing Codable")
                    return False
                    
                if "Project: Codable" in content:
                    print("✅ Project has Codable conformance")
                else:
                    print("❌ Project missing Codable")
                    return False
                    
            elif "BadView.swift" in file["path"]:
                content = file["content"]
                if "'" in content and '"Hello"' not in content:
                    print("❌ Single quotes not fixed in BadView")
                    return False
                if 'Welcome to SwiftUI)' in content:
                    print("❌ Unterminated string not fixed in BadView")
                    return False
                print("✅ BadView string literals fixed")
    
    return success

async def main():
    """Run all tests"""
    print("🚀 Running Comprehensive Error Recovery Tests")
    print("=" * 60)
    
    tests = [
        ("PersistenceController Recovery", test_persistence_controller_recovery),
        ("Codable Recovery", test_codable_recovery),
        ("String Literal Recovery", test_string_literal_recovery),
        ("Complex Scenario", test_complex_scenario)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("\n🎉 Goal achieved! Error recovery works 90%+ of the time!")
    else:
        print(f"\n📈 Need to improve by {90 - success_rate:.1f}% to reach 90% goal")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)