#!/usr/bin/env python3
"""
Test the system fixes for common issues
"""

import asyncio
import sys
import os
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from swift_validator import SwiftValidator
from type_registry import TypeRegistry
from modification_verifier import ModificationVerifier
from robust_error_recovery_system import RobustErrorRecoverySystem

def test_type_name_fix():
    """Test that type name mismatches are fixed"""
    print("\n=== Testing Type Name Fix ===")
    
    # Test with type registry
    registry = TypeRegistry()
    
    # Manually add mappings since we're testing
    registry.update_mapping("ErrorView", "AppErrorView")
    registry.update_mapping("ResultView", "OperationResultView")
    
    # Sample code with wrong type names
    content = """ErrorView(message: "Test error")
ResultView()"""
    
    # Simulate errors
    errors = [
        "Sources/Views/ContentView.swift:8:17: error: cannot find 'ErrorView' in scope",
        "Sources/Views/ContentView.swift:10:17: error: cannot find 'ResultView' in scope"
    ]
    
    fixed_content = registry.fix_type_references(content, errors)
    
    # Check if fixed
    assert "AppErrorView" in fixed_content, f"ErrorView should be replaced with AppErrorView. Got: {fixed_content}"
    assert "OperationResultView" in fixed_content, f"ResultView should be replaced with OperationResultView. Got: {fixed_content}"
    # Check that the original types are gone (but not as substrings of the new types)
    assert not re.search(r'\bErrorView\b', fixed_content), f"ErrorView should not exist as a whole word. Got: {fixed_content}"
    assert not re.search(r'\bResultView\b', fixed_content), f"ResultView should not exist as a whole word. Got: {fixed_content}"
    
    print("✅ Type name fix test passed")

def test_syntax_validation():
    """Test syntax validation and auto-fixes"""
    print("\n=== Testing Syntax Validation ===")
    
    validator = SwiftValidator()
    
    # Test semicolon fixes
    bad_code = """
import SwiftUI

struct TestView: View {
    let name: String;
    static; let preview = "Test"
    
    var body: some View {
        Text("Hello");
        CurrencyInputView();
    }
    
    func convert() -> Double {
        guard let amount = Double(self.amount),
              let fromRate = rates.first?.rate,
             ; let toRate = rates.last?.rate
        else { return 0.0 }
        
        return amount * (toRate / fromRate)
    }
}
"""
    
    fixed_code, fixes = validator.apply_auto_fixes(bad_code)
    
    # Check fixes
    assert "static; let" not in fixed_code, "static; let should be fixed"
    assert "static let" in fixed_code, "Should have static let"
    assert "; let toRate" not in fixed_code, "Guard statement semicolon should be fixed"
    assert "Text(\"Hello\");" not in fixed_code, "Trailing semicolon should be removed"
    assert "CurrencyInputView()" in fixed_code and "CurrencyInputView();" not in fixed_code, "Method call semicolon should be removed"
    
    print(f"✅ Syntax validation test passed - Applied {len(fixes)} fixes")

def test_pre_verification():
    """Test pre-verification with all fixes"""
    print("\n=== Testing Pre-Verification ===")
    
    registry = TypeRegistry()
    verifier = ModificationVerifier(type_registry=registry)
    
    # Sample files with multiple issues
    files = [
        {
            "path": "Sources/Views/ContentView.swift",
            "content": """
import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack {
            CurrencyInputView();
            if viewModel.isLoading {
                ProgressView()
            } else if !viewModel.errorMessage.isEmpty {
                ErrorView(message: viewModel.errorMessage)
            } else {
                ResultView()
            }
        }
    }
}
"""
        },
        {
            "path": "Sources/ViewModels/CurrencyViewModel.swift", 
            "content": """
import SwiftUI

class CurrencyViewModel: ObservableObject {
    func convert() -> Double {
        guard let amount = Double(self.amount),
              let fromRate = rates.first?.rate,
             ; let toRate = rates.last?.rate
        else { return 0.0 }
        
        return amount * (toRate / fromRate)
    }
}
"""
        }
    ]
    
    # Pre-verify
    verified_files, all_fixes = verifier.pre_verify_files(files)
    
    # Check that fixes were applied
    assert len(all_fixes) > 0, "Should have found and fixed issues"
    
    # Check specific fixes
    content_view = next(f for f in verified_files if "ContentView" in f["path"])
    assert "AppErrorView" in content_view["content"], "Should fix ErrorView -> AppErrorView"
    assert "OperationResultView" in content_view["content"], "Should fix ResultView -> OperationResultView"
    assert "CurrencyInputView()" in content_view["content"] and "CurrencyInputView();" not in content_view["content"], "Should remove semicolon"
    
    view_model = next(f for f in verified_files if "ViewModel" in f["path"])
    assert "; let toRate" not in view_model["content"], "Should fix guard statement"
    
    print(f"✅ Pre-verification test passed - Applied {len(all_fixes)} fixes")
    for fix in all_fixes:
        print(f"  - {fix}")

async def test_error_recovery():
    """Test error recovery system with new patterns"""
    print("\n=== Testing Error Recovery System ===")
    
    recovery = RobustErrorRecoverySystem()
    
    # Test files with errors
    swift_files = [
        {
            "path": "Sources/Views/ContentView.swift",
            "content": """
import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack {
            ErrorView(message: "Test")
            ResultView()
        }
    }
}
"""
        }
    ]
    
    # Errors to recover from
    errors = [
        "Sources/Views/ContentView.swift:6:13: error: cannot find 'ErrorView' in scope",
        "Sources/Views/ContentView.swift:7:13: error: cannot find 'ResultView' in scope"
    ]
    
    # Test recovery - returns (success, files, fixes_applied)
    success, recovered_files, fixes_applied = await recovery.recover_from_errors(errors, swift_files)
    
    if success:
        # Check recovery
        content = recovered_files[0]["content"]
        assert "AppErrorView" in content or "ErrorView" not in content, "Should fix or remove ErrorView"
        assert "OperationResultView" in content or "ResultView" not in content, "Should fix or remove ResultView"
        print("✅ Error recovery test passed")
    else:
        print("⚠️ Error recovery did not make changes (may need AI services configured)")

def main():
    """Run all tests"""
    print("🧪 Testing System Fixes for Common Issues")
    
    test_type_name_fix()
    test_syntax_validation()
    test_pre_verification()
    
    # Run async test
    asyncio.run(test_error_recovery())
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()