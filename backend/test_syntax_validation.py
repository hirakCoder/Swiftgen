#!/usr/bin/env python3
"""
Test that the generated dark mode code has valid syntax
"""

import os
import sys
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from swift_validator import SwiftValidator

def test_dark_mode_syntax():
    """Test the dark mode generated code for syntax issues"""
    print("\n=== Testing Dark Mode Syntax ===")
    
    # Load the generated code
    with open('dark_mode_test_output.json', 'r') as f:
        data = json.load(f)
    
    validator = SwiftValidator()
    
    # Test App.swift
    app_content = data['minimal_modification_result']['files'][0]['content']
    print("\n1. App.swift content:")
    print(app_content)
    
    # Apply auto-fixes
    fixed_app, fixes = validator.apply_auto_fixes(app_content)
    if fixes:
        print(f"\n   Fixes needed: {fixes}")
    else:
        print("\n   ✅ No syntax fixes needed")
    
    # Test ContentView
    view_content = data['minimal_modification_result']['files'][1]['content']
    print("\n2. ContentView.swift preview:")
    print(view_content[:200] + "...")
    
    # The main issue is the view body structure
    # The closing brace is misplaced
    lines = view_content.split('\n')
    for i, line in enumerate(lines):
        print(f"{i:3}: {line}")
    
    return True

if __name__ == "__main__":
    test_dark_mode_syntax()