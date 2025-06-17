"""
Test Comprehensive Validation System
"""

import os
import sys
from typing import Dict, List

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_utils import TestRunner, print_test_header, print_test_result, mock_swift_files_with_errors


class TestComprehensiveValidation(TestRunner):
    """Test comprehensive validation system"""
    
    def __init__(self):
        super().__init__("Comprehensive Validation Tests")
        self.validator = None
        self.pre_validator = None
    
    def test_comprehensive_validator(self):
        """Test ComprehensiveCodeValidator"""
        print_test_header("Comprehensive Code Validator")
        
        try:
            from comprehensive_code_validator import ComprehensiveCodeValidator
            self.validator = ComprehensiveCodeValidator(ios_target="16.0")
            
            # Test with files containing errors
            test_files = mock_swift_files_with_errors()
            
            issues = self.validator.validate_files(test_files)
            
            # Check for expected issues
            reserved_type_issues = [i for i in issues if i.category == "reserved_types"]
            import_issues = [i for i in issues if i.category == "missing_imports"]
            
            assert len(reserved_type_issues) > 0, "Should detect reserved type 'Task'"
            assert len(import_issues) > 0, "Should detect missing SwiftUI import"
            
            print(f"✓ Found {len(reserved_type_issues)} reserved type issues")
            print(f"✓ Found {len(import_issues)} import issues")
            
            # Test auto-fix
            fixed, fixed_files, applied_fixes = self.validator.auto_fix_issues(test_files, issues)
            
            if fixed:
                # Verify fixes
                fixed_content = fixed_files[0]["content"]
                assert "TodoItem" in fixed_content, "Should replace Task with TodoItem"
                assert "import SwiftUI" in fixed_files[1]["content"], "Should add missing import"
                
                print(f"✓ Applied {len(applied_fixes)} fixes successfully")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Comprehensive validator test failed: {e}")
            return False
    
    def test_pre_generation_validator(self):
        """Test PreGenerationValidator"""
        print_test_header("Pre-Generation Validator")
        
        try:
            from pre_generation_validator import PreGenerationValidator
            self.pre_validator = PreGenerationValidator()
            
            # Test problematic app types
            test_cases = [
                ("Task Manager", "A task management app", "TodoItem"),
                ("Photo Timer", "A timer app for photos", "AppTimer"),
                ("Data Analyzer", "Analyze data patterns", "AppData")
            ]
            
            for app_name, description, expected_warning in test_cases:
                enhanced_desc, _ = self.pre_validator.validate_and_enhance_prompt(
                    app_name, description
                )
                
                if expected_warning:
                    assert expected_warning in enhanced_desc, f"Should warn about {expected_warning}"
                    print(f"✓ Correctly warned about {expected_warning} for '{app_name}'")
            
            # Test code validation
            test_code = {
                "files": [
                    {
                        "path": "Sources/App.swift",
                        "content": """
struct Task {
    let name: String
}

enum State {
    case idle
    case loading
}
"""
                    }
                ]
            }
            
            valid, issues = self.pre_validator.validate_generated_code(test_code)
            assert not valid, "Should detect reserved types"
            assert len(issues) >= 2, "Should find Task and State issues"
            
            print(f"✓ Detected {len(issues)} issues in generated code")
            
            # Test fix
            fixed_code = self.pre_validator.fix_reserved_types_in_code(test_code)
            fixed_content = fixed_code["files"][0]["content"]
            
            assert "TodoItem" in fixed_content, "Should replace Task"
            assert "AppState" in fixed_content, "Should replace State"
            
            print("✓ Successfully fixed reserved types")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Pre-generation validator test failed: {e}")
            return False
    
    def test_modern_pattern_validator(self):
        """Test ModernPatternValidator"""
        print_test_header("Modern Pattern Validator")
        
        try:
            from modern_pattern_validator import ModernPatternValidator
            validator = ModernPatternValidator(target_ios_version="16.0")
            
            # Test deprecated patterns
            test_files = [{
                "path": "Sources/ContentView.swift",
                "content": """import SwiftUI

struct ContentView: View {
    @Environment(\\.presentationMode) var presentationMode
    
    var body: some View {
        NavigationView {
            VStack {
                Text("Hello")
                    .foregroundColor(.blue)
                
                Button("Dismiss") {
                    presentationMode.wrappedValue.dismiss()
                }
            }
        }
    }
}
"""
            }]
            
            issues = validator.validate_files(test_files)
            
            # Check for deprecation warnings
            nav_issues = [i for i in issues if "NavigationView" in i.message]
            present_issues = [i for i in issues if "presentationMode" in i.message]
            color_issues = [i for i in issues if "foregroundColor" in i.message]
            
            assert len(nav_issues) > 0, "Should detect NavigationView deprecation"
            assert len(present_issues) > 0, "Should detect presentationMode deprecation"
            
            print(f"✓ Found {len(nav_issues)} NavigationView issues")
            print(f"✓ Found {len(present_issues)} presentationMode issues")
            print(f"✓ Found {len(color_issues)} foregroundColor issues")
            
            # Test auto-fix
            fixed, fixed_files, fixes = validator.auto_fix_issues(test_files, issues)
            
            if fixed:
                fixed_content = fixed_files[0]["content"]
                assert "NavigationStack" in fixed_content, "Should replace NavigationView"
                assert "@Environment(\\.dismiss)" in fixed_content, "Should update dismiss pattern"
                assert "foregroundStyle" in fixed_content, "Should update color modifier"
                
                print(f"✓ Applied {len(fixes)} modern pattern fixes")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Modern pattern validator test failed: {e}")
            return False
    
    def test_modification_verifier(self):
        """Test ModificationVerifier"""
        print_test_header("Modification Verifier")
        
        try:
            from modification_verifier import ModificationVerifier
            verifier = ModificationVerifier()
            
            # Test with original and modified files
            original_files = [
                {"path": "Sources/ContentView.swift", "content": "Original content"},
                {"path": "Sources/Model.swift", "content": "Model content"}
            ]
            
            # Test case 1: Missing file
            modified_files_missing = [
                {"path": "Sources/ContentView.swift", "content": "Modified content"}
            ]
            
            issues = verifier.verify_modifications(
                original_files, 
                modified_files_missing,
                "Add a button"
            )
            
            assert len(issues) > 0, "Should detect missing file"
            assert "Missing files" in issues[0], "Should report missing Model.swift"
            
            print("✓ Correctly detected missing files")
            
            # Test case 2: No actual changes
            modified_files_unchanged = [
                {"path": "Sources/ContentView.swift", "content": "Original content"},
                {"path": "Sources/Model.swift", "content": "Model content"}
            ]
            
            issues = verifier.verify_modifications(
                original_files,
                modified_files_unchanged,
                "Add a button"
            )
            
            assert any("No changes detected" in issue for issue in issues), "Should detect no changes"
            
            print("✓ Correctly detected unchanged files")
            
            # Test case 3: Successful modification
            modified_files_changed = [
                {"path": "Sources/ContentView.swift", "content": "Modified with button"},
                {"path": "Sources/Model.swift", "content": "Model content"}
            ]
            
            issues = verifier.verify_modifications(
                original_files,
                modified_files_changed,
                "Add a button"
            )
            
            assert len(issues) == 0, "Should have no issues for valid modification"
            
            print("✓ Validated successful modification")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Modification verifier test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all comprehensive validation tests"""
        print("\n" + "="*60)
        print("🧪 Running Comprehensive Validation Tests")
        print("="*60 + "\n")
        
        tests = [
            self.test_comprehensive_validator,
            self.test_pre_generation_validator,
            self.test_modern_pattern_validator,
            self.test_modification_verifier
        ]
        
        results = []
        for test in tests:
            try:
                results.append(test())
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {e}")
                results.append(False)
        
        # Summary
        passed = sum(results)
        total = len(results)
        
        print("\n" + "="*60)
        print(f"📊 Test Summary: {passed}/{total} passed ({passed/total*100:.0f}%)")
        print("="*60)
        
        return all(results)


def main():
    """Run comprehensive validation tests"""
    tester = TestComprehensiveValidation()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()