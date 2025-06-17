"""
Test Basic SwiftGen Functionality
Tests app generation, modification, and build without full environment
"""

import os
import sys
import json
from typing import Dict, List

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_utils import TestRunner, print_test_header, print_test_result


class TestBasicFunctionality(TestRunner):
    """Test basic SwiftGen functionality"""
    
    def __init__(self):
        super().__init__("Basic Functionality Tests")
    
    def test_imports(self):
        """Test that all modules can be imported"""
        print_test_header("Module Imports")
        
        modules_to_test = [
            "models",
            "project_manager",
            "enhanced_prompts",
            "pre_generation_validator",
            "comprehensive_code_validator",
            "modern_pattern_validator",
            "modification_verifier",
            "modification_handler",
            "self_healing_generator",
            "robust_error_recovery_system"
        ]
        
        failed = []
        for module in modules_to_test:
            try:
                __import__(module)
                print(f"  ✓ {module}")
            except ImportError as e:
                print(f"  ✗ {module}: {e}")
                failed.append(module)
        
        if failed:
            print_test_result(False, f"{len(failed)} modules failed to import")
            return False
        
        print_test_result(True, "All modules imported successfully")
        return True
    
    def test_project_structure(self):
        """Test project structure creation"""
        print_test_header("Project Structure")
        
        try:
            from project_manager import ProjectManager
            
            pm = ProjectManager()
            
            # Test project creation
            test_app_name = "TestApp"
            test_bundle_id = "com.test.app"
            
            # Create mock project structure
            project_data = {
                "app_name": test_app_name,
                "bundle_id": test_bundle_id,
                "files": [
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
}
"""
                    },
                    {
                        "path": "Sources/ContentView.swift",
                        "content": """import SwiftUI

struct ContentView: View {
    var body: some View {
        Text("Hello, World!")
    }
}
"""
                    }
                ]
            }
            
            # Test project validation
            assert pm._sanitize_app_name(test_app_name) == test_app_name
            assert pm._is_valid_bundle_id(test_bundle_id)
            
            print("✓ Project structure validation passed")
            
            # Test project.yml generation
            project_yml = pm._generate_project_yml(test_app_name, test_bundle_id)
            assert "name:" in project_yml
            assert test_app_name in project_yml
            assert test_bundle_id in project_yml
            
            print("✓ Project.yml generation passed")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Project structure test failed: {e}")
            return False
    
    def test_validation_chain(self):
        """Test validation chain without dependencies"""
        print_test_header("Validation Chain")
        
        try:
            # Test pre-generation validation
            from pre_generation_validator import PreGenerationValidator
            pre_val = PreGenerationValidator()
            
            # Test with problematic app name
            enhanced_desc, app_name = pre_val.validate_and_enhance_prompt(
                "Task Manager",
                "A task management application"
            )
            
            assert "TodoItem" in enhanced_desc, "Should warn about Task reserved type"
            print("✓ Pre-generation validation working")
            
            # Test comprehensive validation
            from comprehensive_code_validator import ComprehensiveCodeValidator
            comp_val = ComprehensiveCodeValidator()
            
            # Test reserved types detection
            test_files = [{
                "path": "Sources/Model.swift",
                "content": "struct Task { let title: String }"
            }]
            
            issues = comp_val.validate_files(test_files)
            reserved_issues = [i for i in issues if i.category == "reserved_types"]
            
            assert len(reserved_issues) > 0, "Should detect reserved type Task"
            print("✓ Comprehensive validation detecting issues")
            
            # Test modern pattern validation
            from modern_pattern_validator import ModernPatternValidator
            modern_val = ModernPatternValidator()
            
            test_files = [{
                "path": "Sources/View.swift",
                "content": """NavigationView { Text("Test") }"""
            }]
            
            issues = modern_val.validate_files(test_files)
            nav_issues = [i for i in issues if "NavigationView" in i.message]
            
            assert len(nav_issues) > 0, "Should detect NavigationView deprecation"
            print("✓ Modern pattern validation working")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Validation chain test failed: {e}")
            return False
    
    def test_error_patterns(self):
        """Test error pattern loading and matching"""
        print_test_header("Error Patterns")
        
        try:
            from robust_error_recovery_system import RobustErrorRecoverySystem
            
            recovery = RobustErrorRecoverySystem()
            
            # Test error patterns loaded
            assert len(recovery.error_patterns) > 0, "Should have error patterns"
            print(f"✓ Loaded {len(recovery.error_patterns)} error pattern categories")
            
            # Test error analysis
            test_errors = [
                "error: 'NavigationView' is deprecated",
                "error: cannot find type 'Task' in scope",
                "error: unterminated string literal"
            ]
            
            analysis = recovery._analyze_errors(test_errors)
            
            assert len(analysis["ios_version_errors"]) > 0
            assert len(analysis["string_literal_errors"]) > 0
            
            print("✓ Error analysis categorizing correctly")
            
            # Test fingerprinting
            fp = recovery._create_error_fingerprint(test_errors)
            assert fp, "Should create fingerprint"
            print(f"✓ Error fingerprint: {fp}")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Error patterns test failed: {e}")
            return False
    
    def test_modification_handler(self):
        """Test modification handler"""
        print_test_header("Modification Handler")
        
        try:
            from modification_handler import ModificationHandler
            
            handler = ModificationHandler()
            
            # Test relevant file identification
            files = [
                {"path": "Sources/ContentView.swift", "content": "Button view content"},
                {"path": "Sources/Model.swift", "content": "Data model"},
                {"path": "Sources/ButtonView.swift", "content": "Custom button"}
            ]
            
            relevant = handler._identify_relevant_files("Add a red button", files)
            
            assert any("Button" in f["path"] or "button" in f["content"].lower() for f in relevant)
            print(f"✓ Identified {len(relevant)} relevant files for modification")
            
            # Test prompt preparation
            prompt = handler.prepare_modification_prompt(
                "TestApp",
                "Add a red button",
                files
            )
            
            assert "red button" in prompt
            assert "TestApp" in prompt
            print("✓ Modification prompt prepared successfully")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Modification handler test failed: {e}")
            return False
    
    def test_enhanced_prompts(self):
        """Test enhanced prompt system"""
        print_test_header("Enhanced Prompts")
        
        try:
            from enhanced_prompts import ENHANCED_IOS_SYSTEM_PROMPT, ENHANCED_USER_PROMPT_TEMPLATE
            
            # Check system prompt
            assert len(ENHANCED_IOS_SYSTEM_PROMPT) > 1000, "System prompt should be comprehensive"
            assert "iOS 16.0" in ENHANCED_IOS_SYSTEM_PROMPT
            assert "SwiftUI" in ENHANCED_IOS_SYSTEM_PROMPT
            assert "TodoItem" in ENHANCED_IOS_SYSTEM_PROMPT  # Reserved type warning
            
            print("✓ System prompt contains required elements")
            
            # Check user prompt template
            assert "{description}" in ENHANCED_USER_PROMPT_TEMPLATE
            assert "{app_name}" in ENHANCED_USER_PROMPT_TEMPLATE
            
            print("✓ User prompt template properly formatted")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Enhanced prompts test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all basic functionality tests"""
        print("\n" + "="*60)
        print("🧪 Running Basic Functionality Tests")
        print("="*60 + "\n")
        
        tests = [
            self.test_imports,
            self.test_project_structure,
            self.test_validation_chain,
            self.test_error_patterns,
            self.test_modification_handler,
            self.test_enhanced_prompts
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
    """Run basic functionality tests"""
    tester = TestBasicFunctionality()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()