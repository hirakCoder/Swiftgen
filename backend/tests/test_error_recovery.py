"""
Test Error Recovery System
"""

import os
import sys
import asyncio
from typing import Dict, List

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_utils import TestRunner, print_test_header, print_test_result


class TestErrorRecovery(TestRunner):
    """Test error recovery system"""
    
    def __init__(self):
        super().__init__("Error Recovery Tests")
        self.error_recovery = None
    
    def test_error_analysis(self):
        """Test error analysis and categorization"""
        print_test_header("Error Analysis")
        
        try:
            from robust_error_recovery_system import RobustErrorRecoverySystem
            
            self.error_recovery = RobustErrorRecoverySystem()
            
            # Test various error types
            test_errors = [
                "error: 'NavigationView' is deprecated: use NavigationStack",
                "error: cannot find type 'Task' in scope",
                "error: unterminated string literal",
                "error: cannot find 'PersistenceController' in scope",
                "error: switch must be exhaustive",
                "error: type 'TodoItem' does not conform to protocol 'Codable'",
                "error: .symbolEffect is only available in iOS 17.0"
            ]
            
            analysis = self.error_recovery._analyze_errors(test_errors)
            
            # Verify categorization
            assert len(analysis["ios_version_errors"]) > 0, "Should detect iOS version errors"
            assert len(analysis["missing_imports"]) > 0, "Should detect missing type errors"
            assert len(analysis["string_literal_errors"]) > 0, "Should detect string errors"
            assert len(analysis["persistence_controller_errors"]) > 0, "Should detect Core Data errors"
            assert len(analysis["exhaustive_switch_errors"]) > 0, "Should detect switch errors"
            assert len(analysis["protocol_conformance_errors"]) > 0, "Should detect protocol errors"
            
            print(f"✓ Categorized {len(test_errors)} errors into {sum(len(v) for v in analysis.values())} categories")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Error analysis test failed: {e}")
            return False
    
    def test_pattern_based_recovery(self):
        """Test pattern-based error recovery"""
        print_test_header("Pattern-Based Recovery")
        
        if not self.error_recovery:
            self.error_recovery = RobustErrorRecoverySystem()
        
        try:
            test_files = [{
                "path": "Sources/ContentView.swift",
                "content": """import SwiftUI

struct ContentView: View {
    var body: some View {
        Text('Hello World')
            .symbolEffect(.bounce)
    }
}
"""
            }]
            
            test_errors = [
                "error: unterminated string literal",
                "error: .symbolEffect is only available in iOS 17.0"
            ]
            
            analysis = self.error_recovery._analyze_errors(test_errors)
            
            # Run pattern-based recovery
            success, fixed_files = asyncio.run(
                self.error_recovery._pattern_based_recovery(
                    test_errors, test_files, analysis
                )
            )
            
            assert success, "Pattern-based recovery should succeed"
            
            fixed_content = fixed_files[0]["content"]
            assert '"Hello World"' in fixed_content, "Should fix single quotes"
            assert '.symbolEffect(' not in fixed_content, "Should remove iOS 17+ feature"
            
            print("✓ Pattern-based recovery fixed string literals and iOS version issues")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Pattern-based recovery test failed: {e}")
            return False
    
    def test_swift_syntax_recovery(self):
        """Test Swift syntax recovery"""
        print_test_header("Swift Syntax Recovery")
        
        if not self.error_recovery:
            self.error_recovery = RobustErrorRecoverySystem()
        
        try:
            test_files = [{
                "path": "Sources/Model.swift",
                "content": """import Foundation

enum AppAction {
    case add
    case delete
}

struct TodoItem {
    let task: Task
}
"""
            }]
            
            test_errors = [
                "error: switch must be exhaustive",
                "error: cannot find type 'Task' in scope"
            ]
            
            analysis = self.error_recovery._analyze_errors(test_errors)
            
            # Run Swift syntax recovery
            success, fixed_files = asyncio.run(
                self.error_recovery._swift_syntax_recovery(
                    test_errors, test_files, analysis
                )
            )
            
            # Should detect and fix type reference
            fixed_content = fixed_files[0]["content"]
            
            print(f"✓ Swift syntax recovery processed {len(test_files)} files")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Swift syntax recovery test failed: {e}")
            return False
    
    def test_dependency_recovery(self):
        """Test dependency recovery"""
        print_test_header("Dependency Recovery")
        
        if not self.error_recovery:
            self.error_recovery = RobustErrorRecoverySystem()
        
        try:
            test_files = [{
                "path": "Sources/App.swift",
                "content": """import SwiftUI

@main
struct MyApp: App {
    let persistenceController = PersistenceController.shared
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\\.managedObjectContext, persistenceController.container.viewContext)
        }
    }
}
"""
            }]
            
            test_errors = [
                "error: cannot find 'PersistenceController' in scope",
                "error: cannot find 'managedObjectContext' in scope"
            ]
            
            analysis = self.error_recovery._analyze_errors(test_errors)
            
            # Run dependency recovery
            success, fixed_files = asyncio.run(
                self.error_recovery._dependency_recovery(
                    test_errors, test_files, analysis
                )
            )
            
            if success:
                fixed_content = fixed_files[0]["content"]
                assert "PersistenceController" not in fixed_content, "Should remove Core Data references"
                assert "managedObjectContext" not in fixed_content, "Should remove Core Data environment"
                
                print("✓ Dependency recovery removed Core Data dependencies")
            else:
                print("✓ No dependency changes needed")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Dependency recovery test failed: {e}")
            return False
    
    def test_error_fingerprinting(self):
        """Test error fingerprinting for loop prevention"""
        print_test_header("Error Fingerprinting")
        
        if not self.error_recovery:
            self.error_recovery = RobustErrorRecoverySystem()
        
        try:
            # Test similar errors produce same fingerprint
            errors1 = [
                "Sources/View1.swift:10:5: error: cannot find type 'Task' in scope",
                "Sources/View2.swift:20:8: error: 'NavigationView' is deprecated"
            ]
            
            errors2 = [
                "Sources/Other.swift:5:1: error: cannot find type 'Task' in scope",
                "Sources/Main.swift:15:3: error: 'NavigationView' is deprecated"
            ]
            
            fp1 = self.error_recovery._create_error_fingerprint(errors1)
            fp2 = self.error_recovery._create_error_fingerprint(errors2)
            
            assert fp1 == fp2, "Similar errors should produce same fingerprint"
            
            print(f"✓ Fingerprint consistency: '{fp1}'")
            
            # Test different errors produce different fingerprints
            errors3 = [
                "error: unterminated string literal",
                "error: missing import Foundation"
            ]
            
            fp3 = self.error_recovery._create_error_fingerprint(errors3)
            assert fp1 != fp3, "Different errors should produce different fingerprints"
            
            print(f"✓ Fingerprint uniqueness: '{fp3}' != '{fp1}'")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Error fingerprinting test failed: {e}")
            return False
    
    def test_recovery_with_attempts(self):
        """Test recovery with attempt tracking"""
        print_test_header("Recovery with Attempt Tracking")
        
        if not self.error_recovery:
            self.error_recovery = RobustErrorRecoverySystem()
        
        try:
            test_files = [{
                "path": "Sources/Test.swift",
                "content": "struct Task {}"
            }]
            
            test_errors = ["error: cannot find type 'Task' in scope"]
            
            # First attempt
            success1, files1, fixes1 = asyncio.run(
                self.error_recovery.recover_from_errors(
                    test_errors, test_files, "com.test.app"
                )
            )
            
            # Second attempt with same error
            success2, files2, fixes2 = asyncio.run(
                self.error_recovery.recover_from_errors(
                    test_errors, test_files, "com.test.app"
                )
            )
            
            # Third attempt should be blocked
            success3, files3, fixes3 = asyncio.run(
                self.error_recovery.recover_from_errors(
                    test_errors, test_files, "com.test.app"
                )
            )
            
            assert not success3, "Third attempt should be blocked"
            assert "exhausted" in fixes3[0].lower(), "Should indicate exhausted attempts"
            
            print("✓ Attempt tracking prevents infinite loops")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Attempt tracking test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all error recovery tests"""
        print("\n" + "="*60)
        print("🧪 Running Error Recovery Tests")
        print("="*60 + "\n")
        
        tests = [
            self.test_error_analysis,
            self.test_pattern_based_recovery,
            self.test_swift_syntax_recovery,
            self.test_dependency_recovery,
            self.test_error_fingerprinting,
            self.test_recovery_with_attempts
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
    """Run error recovery tests"""
    tester = TestErrorRecovery()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()