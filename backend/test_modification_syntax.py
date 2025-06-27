#!/usr/bin/env python3
"""
Test and fix modification syntax issues
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modification_handler import ModificationHandler


def test_syntax_issue():
    """Test for the private; var syntax issue"""
    
    # Test content with the syntax error
    test_content = """
    private func refreshRates() {
        // function body
    }
    
    private; var darkModeToggle: some View {
        Toggle(isOn: $isDarkMode) {
            Text("Dark Mode")
        }
    }
    """
    
    # Check if we can detect and fix this
    print("Testing syntax error detection...")
    
    # Simple fix pattern
    import re
    fixed = re.sub(r'private\s*;\s*var', 'private var', test_content)
    fixed = re.sub(r'public\s*;\s*var', 'public var', fixed)
    fixed = re.sub(r'internal\s*;\s*var', 'internal var', fixed)
    fixed = re.sub(r'fileprivate\s*;\s*var', 'fileprivate var', fixed)
    
    # Also fix for func, let, etc.
    fixed = re.sub(r'private\s*;\s*func', 'private func', fixed)
    fixed = re.sub(r'private\s*;\s*let', 'private let', fixed)
    
    print("Original:")
    print(test_content)
    print("\nFixed:")
    print(fixed)
    
    # Check if the fix worked
    if '; var' not in fixed and '; func' not in fixed and '; let' not in fixed:
        print("\n✅ Fix successful!")
        return True
    else:
        print("\n❌ Fix failed!")
        return False


def add_syntax_fix_to_handler():
    """Add this fix to the modification handler"""
    
    fix_code = '''
def fix_swift_syntax_errors(self, content: str) -> str:
    """Fix common Swift syntax errors that may be introduced during modification"""
    import re
    
    # Fix semicolon errors in access modifiers
    content = re.sub(r'private\s*;\s*var', 'private var', content)
    content = re.sub(r'public\s*;\s*var', 'public var', content)
    content = re.sub(r'internal\s*;\s*var', 'internal var', content)
    content = re.sub(r'fileprivate\s*;\s*var', 'fileprivate var', content)
    
    # Also fix for func, let, etc.
    content = re.sub(r'private\s*;\s*func', 'private func', content)
    content = re.sub(r'public\s*;\s*func', 'public func', content)
    content = re.sub(r'private\s*;\s*let', 'private let', content)
    content = re.sub(r'public\s*;\s*let', 'public let', content)
    
    # Fix other common semicolon issues
    content = re.sub(r'}\s*;\s*else', '} else', content)
    content = re.sub(r'}\s*;\s*catch', '} catch', content)
    
    return content
'''
    
    print("\nSuggested fix to add to modification_handler.py:")
    print(fix_code)
    
    return fix_code


if __name__ == "__main__":
    print("🔍 Testing Swift Syntax Error Issue")
    print("=" * 60)
    
    # Test the syntax issue
    success = test_syntax_issue()
    
    # Suggest the fix
    add_syntax_fix_to_handler()
    
    if success:
        print("\n✅ Syntax fix pattern works correctly")
    else:
        print("\n❌ Syntax fix needs more work")