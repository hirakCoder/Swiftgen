#!/usr/bin/env python3
"""
Test Swift Validator Integration
Verifies the validator integrates properly with existing systems
"""

import os
import json
from datetime import datetime

def test_integration():
    """Test that swift validator integrates without breaking existing functionality"""
    
    print("Swift Validator Integration Test")
    print("="*60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Import modules
    print("\n1. Testing module imports...")
    try:
        from swift_validator import SwiftValidator
        from swift_validator_integration import integrate_swift_validator
        from robust_error_recovery_system import RobustErrorRecoverySystem
        from build_service import BuildService
        print("✅ All modules imported successfully")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Import error: {e}")
        tests_failed += 1
        return
    
    # Test 2: Create validator instance
    print("\n2. Testing validator creation...")
    try:
        validator = SwiftValidator()
        print("✅ Swift validator created")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Validator creation error: {e}")
        tests_failed += 1
    
    # Test 3: Test validator on sample code with errors
    print("\n3. Testing validator on Swift code with errors...")
    sample_swift = '''import SwiftUI

struct CalculatorButton {
    let text: String
    let action: () -> Void
}

struct ContentView: View {
    var body: some View {
        ForEach(buttons) { button in
            Text(button.text);
        }
    }
}'''
    
    try:
        # Apply auto fixes
        fixed_content, fixes = validator.apply_auto_fixes(sample_swift)
        
        if ';' not in fixed_content:
            print("✅ Semicolon removed")
            tests_passed += 1
        else:
            print("❌ Semicolon not removed")
            tests_failed += 1
            
        if 'id: \\.self' in fixed_content or 'Identifiable' in fixed_content:
            print("✅ ForEach fix applied")
            tests_passed += 1
        else:
            print("❌ ForEach not fixed")
            tests_failed += 1
            
    except Exception as e:
        print(f"❌ Validation error: {e}")
        tests_failed += 2
    
    # Test 4: Test integration with error recovery
    print("\n4. Testing integration with error recovery system...")
    try:
        recovery_system = RobustErrorRecoverySystem()
        integrate_swift_validator(error_recovery_system=recovery_system)
        
        # Check if validator was added
        if hasattr(recovery_system, 'swift_validator'):
            print("✅ Validator added to recovery system")
            tests_passed += 1
        else:
            print("❌ Validator not added to recovery system")
            tests_failed += 1
            
        # Check if recovery method was added
        if hasattr(recovery_system, '_swift_validator_recovery'):
            print("✅ Validator recovery method added")
            tests_passed += 1
        else:
            print("❌ Validator recovery method not added")
            tests_failed += 1
            
    except Exception as e:
        print(f"❌ Integration error: {e}")
        tests_failed += 2
    
    # Test 5: Test that existing functionality still works
    print("\n5. Testing existing recovery strategies...")
    try:
        strategies = recovery_system._get_dynamic_recovery_strategies()
        
        # Should have at least 5 strategies (including new validator)
        if len(strategies) >= 5:
            print(f"✅ {len(strategies)} recovery strategies available")
            tests_passed += 1
        else:
            print(f"❌ Only {len(strategies)} strategies (expected 5+)")
            tests_failed += 1
            
        # Check order - validator should be second
        strategy_names = [s.__name__ for s in strategies]
        if len(strategy_names) > 1 and strategy_names[1] == '_swift_validator_recovery':
            print("✅ Validator strategy in correct position")
            tests_passed += 1
        else:
            print("❌ Validator strategy not in correct position")
            tests_failed += 1
            
    except Exception as e:
        print(f"❌ Strategy test error: {e}")
        tests_failed += 2
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_failed}")
    print(f"Success Rate: {(tests_passed/(tests_passed+tests_failed)*100):.1f}%")
    
    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'tests_passed': tests_passed,
        'tests_failed': tests_failed,
        'success_rate': (tests_passed/(tests_passed+tests_failed)*100)
    }
    
    with open('validator_integration_test.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nResults saved to validator_integration_test.json")
    
    if tests_failed == 0:
        print("\n✅ All tests passed! Integration is ready.")
    else:
        print(f"\n⚠️  {tests_failed} tests failed. Review the errors above.")

if __name__ == "__main__":
    test_integration()