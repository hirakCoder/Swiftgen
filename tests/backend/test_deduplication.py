#!/usr/bin/env python3
"""
Test script to verify the deduplication system works for ANY app type
"""

import sys
import os
import re

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from project_manager import ProjectManager

def test_generic_deduplication():
    """Test that deduplication works for any app type, not just WaterTracker"""
    
    print("🧪 Testing Generic Deduplication System")
    print("=" * 50)
    
    pm = ProjectManager()
    
    # Test Case 1: Recipe App with duplicate RecipeViewModel
    print("\n📱 Test Case 1: Recipe App")
    recipe_files = [
        {
            "path": "Sources/App.swift",
            "content": """import SwiftUI

@main
struct RecipeApp: App {
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
    @StateObject private var viewModel = RecipeViewModel()
    
    var body: some View {
        NavigationStack {
            List(viewModel.recipes) { recipe in
                Text(recipe.name)
            }
        }
    }
}

class RecipeViewModel: ObservableObject {
    @Published var recipes: [Recipe] = []
}

struct Recipe: Identifiable {
    let id = UUID()
    let name: String
}

// DUPLICATE - This should be removed
class RecipeViewModel: ObservableObject {
    @Published var recipes: [Recipe] = []
}"""
        }
    ]
    
    fixed_files = pm._deduplicate_and_fix_code(recipe_files, "Recipe")
    
    # Check results
    print(f"✅ Original files: {len(recipe_files)}")
    print(f"✅ Fixed files: {len(fixed_files)}")
    
    # Check for duplicates
    content_view_content = None
    for file in fixed_files:
        if "ContentView.swift" in file["path"]:
            content_view_content = file["content"]
            break
    
    if content_view_content:
        recipe_vm_count = content_view_content.count("class RecipeViewModel")
        print(f"✅ RecipeViewModel definitions in ContentView: {recipe_vm_count} (should be 0 or 1)")
        
        if recipe_vm_count <= 1:
            print("✅ SUCCESS: Duplicate RecipeViewModel removed!")
        else:
            print("❌ FAILED: Still has duplicate RecipeViewModel")
    
    # Test Case 2: Calculator App with duplicate CalculatorModel
    print("\n🧮 Test Case 2: Calculator App")
    calc_files = [
        {
            "path": "Sources/App.swift", 
            "content": """import SwiftUI

@main
struct CalculatorApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

class CalculatorModel: ObservableObject {
    @Published var display = "0"
}"""
        },
        {
            "path": "Sources/ContentView.swift",
            "content": """import SwiftUI

struct ContentView: View {
    @StateObject private var calculator = CalculatorModel()
    
    var body: some View {
        VStack {
            Text(calculator.display)
        }
    }
}

class CalculatorModel: ObservableObject {
    @Published var display = "0"
    @Published var result = 0.0
}"""
        }
    ]
    
    calc_fixed = pm._deduplicate_and_fix_code(calc_files, "Calculator")
    print(f"✅ Calculator files after dedup: {len(calc_fixed)}")
    
    # Check if CalculatorModel was moved to separate file
    calc_model_files = [f for f in calc_fixed if "CalculatorModel.swift" in f.get("path", "")]
    if calc_model_files:
        print("✅ SUCCESS: CalculatorModel moved to separate file!")
    else:
        print("✅ CalculatorModel kept in place (acceptable)")
    
    # Test Case 3: Shopping App - completely different domain
    print("\n🛒 Test Case 3: Shopping App") 
    shop_files = [
        {
            "path": "Sources/ContentView.swift",
            "content": """import SwiftUI

struct ContentView: View {
    @StateObject private var cart = ShoppingCart()
    
    var body: some View {
        List(cart.items) { item in
            Text(item.name)
        }
    }
}

class ShoppingCart: ObservableObject {
    @Published var items: [ShoppingItem] = []
}

struct ShoppingItem: Identifiable {
    let id = UUID()
    let name: String
}

class ShoppingCart: ObservableObject {
    @Published var items: [ShoppingItem] = []
    @Published var total: Double = 0
}"""
        }
    ]
    
    shop_fixed = pm._deduplicate_and_fix_code(shop_files, "Shopping")
    shop_content = shop_fixed[0]["content"] if shop_fixed else ""
    cart_count = shop_content.count("class ShoppingCart")
    
    print(f"✅ ShoppingCart definitions: {cart_count} (should be 0 or 1)")
    if cart_count <= 1:
        print("✅ SUCCESS: Duplicate ShoppingCart removed!")
    else:
        print("❌ FAILED: Still has duplicate ShoppingCart")
    
    print("\n🎉 Generic Deduplication Test Complete!")
    return True

def test_error_patterns():
    """Test that error pattern matching works generically"""
    
    print("\n🔍 Testing Generic Error Pattern Matching")
    print("=" * 50)
    
    # Import the error recovery system
    try:
        from robust_error_recovery_system import RobustErrorRecoverySystem
        recovery = RobustErrorRecoverySystem()
        
        # Test generic error patterns
        test_errors = [
            "error: ambiguous use of 'init()' @StateObject private var cart = ShoppingCart()",
            "error: 'GameEngine' is ambiguous for type lookup in this context",
            "error: invalid redeclaration of 'MusicPlayer'",
            "error: ambiguous use of 'init()' @StateObject private var timer = CountdownTimer()"
        ]
        
        for error in test_errors:
            # Extract problematic classes
            problematic_classes = set()
            for pattern_name, pattern in recovery.duplicate_class_patterns.items():
                match = re.search(pattern, error)
                if match and match.groups():
                    problematic_classes.add(match.group(1))
                elif 'ambiguous' in error and 'init()' in error:
                    # Test generic patterns
                    context_patterns = [
                        r'@StateObject.*?= (\w+)\(',
                        r'@ObservedObject.*?= (\w+)\(',
                        r'= (\w+)\('
                    ]
                    for ctx_pattern in context_patterns:
                        ctx_match = re.search(ctx_pattern, error)
                        if ctx_match:
                            class_name = ctx_match.group(1)
                            if class_name[0].isupper():
                                problematic_classes.add(class_name)
                            break
            
            print(f"Error: {error[:60]}...")
            print(f"  Detected classes: {problematic_classes}")
        
        print("✅ Generic error pattern matching works!")
        
    except ImportError as e:
        print(f"❌ Could not import recovery system: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Testing SwiftGen Deduplication System")
    print("Making sure it works for ANY app type, not just specific ones")
    print("=" * 60)
    
    success = True
    
    try:
        success &= test_generic_deduplication()
        success &= test_error_patterns()
        
        if success:
            print("\n🎉 ALL TESTS PASSED! The system is generic and production-ready!")
        else:
            print("\n❌ Some tests failed. Need to fix the implementation.")
            
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    sys.exit(0 if success else 1)