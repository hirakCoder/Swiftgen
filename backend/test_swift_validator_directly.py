#!/usr/bin/env python3
"""
Test Swift Validator Directly
"""

import os
import sys
from swift_validator import SwiftValidator

def test_validator():
    """Test the Swift validator with sample code"""
    validator = SwiftValidator()
    
    # Test 1: Semicolon removal
    code_with_semicolons = """
import SwiftUI

struct ContentView: View {
    let title = "Hello";
    let count = 5;
    
    var body: some View {
        Text(title);
        Text("Count: \\(count)");
    }
}
"""
    
    print("Test 1: Semicolon Removal")
    print("=" * 50)
    fixed_code, fixes = validator.apply_auto_fixes(code_with_semicolons)
    print(f"Fixes applied: {fixes}")
    print(f"Semicolons removed: {'Yes' if ';' not in fixed_code else 'No'}")
    print()
    
    # Test 2: Hashable conformance
    code_with_foreach = """
struct TodoItem {
    let id: UUID
    let title: String
}

struct ContentView: View {
    let items = [TodoItem]()
    
    var body: some View {
        ForEach(items) { item in
            Text(item.title)
        }
    }
}
"""
    
    print("Test 2: Hashable Conformance")
    print("=" * 50)
    fixed_code, fixes = validator.apply_auto_fixes(code_with_foreach)
    print(f"Fixes applied: {fixes}")
    print(f"Hashable added: {'Yes' if 'Hashable' in fixed_code else 'No'}")
    print()
    
    # Test 3: Create temp file and validate
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.swift', delete=False) as f:
        f.write(fixed_code)
        temp_file = f.name
    
    print("Test 3: Swift Validation")
    print("=" * 50)
    is_valid, errors = validator.validate_swift_file(temp_file)
    print(f"Valid Swift: {is_valid}")
    if errors:
        print(f"Errors: {errors}")
    
    os.unlink(temp_file)

if __name__ == "__main__":
    test_validator()