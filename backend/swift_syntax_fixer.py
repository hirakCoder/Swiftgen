#!/usr/bin/env python3
"""
Direct Swift syntax fixer for common Claude generation errors
This should be integrated into the Claude service to prevent these issues
"""

import re
from typing import Tuple, List, Dict

class SwiftSyntaxFixer:
    """Fixes common Swift syntax errors that Claude generates"""
    
    @staticmethod
    def fix_swift_file(content: str, file_path: str) -> Tuple[str, List[str]]:
        """Fix Swift syntax issues in a file"""
        fixes_applied = []
        
        # Fix 1: Multi-line string literals used incorrectly
        # Claude sometimes uses """ for single-line strings
        if '"""' in content:
            # Find all occurrences of triple quotes
            lines = content.split('\n')
            fixed_lines = []
            
            for line in lines:
                original = line
                
                # Check if """ appears in a single line (not a proper multi-line string)
                if '"""' in line:
                    # Count occurrences
                    count = line.count('"""')
                    
                    # If even number, they might be paired incorrectly
                    if count >= 2:
                        # This is likely a single-line string with wrong quotes
                        # Common patterns: .navigationTitle("""text""")
                        patterns = [
                            (r'\.navigationTitle\("""([^"]+)"""\)', r'.navigationTitle("\1")'),
                            (r'\.alert\("""([^"]+)"""', r'.alert("\1"'),
                            (r'Text\("""([^"]+)"""\)', r'Text("\1")'),
                            (r'Button\("""([^"]+)"""', r'Button("\1"'),
                            (r'Label\("""([^"]+)"""', r'Label("\1"'),
                            (r'= """([^"]+)"""', r'= "\1"'),
                        ]
                        
                        for pattern, replacement in patterns:
                            if re.search(pattern, line):
                                line = re.sub(pattern, replacement, line)
                                fixes_applied.append(f"Fixed multi-line quotes in {pattern}")
                
                # Fix excessive quotes (4 or more)
                if '""""' in line:
                    line = re.sub(r'"{4,}', '"', line)
                    fixes_applied.append("Fixed excessive quotes")
                
                if line != original:
                    fixed_lines.append(line)
                else:
                    fixed_lines.append(original)
            
            content = '\n'.join(fixed_lines)
        
        # Fix 2: Unterminated string literals
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            original = line
            
            # Check for common unterminated string patterns
            # Pattern: ends with "} without closing quote
            if line.strip().endswith('"}') and line.count('"') % 2 != 0:
                # Find the last quote before "}
                last_quote_pos = line.rfind('"', 0, -2)
                if last_quote_pos != -1:
                    # Check if there's an opening quote
                    before_last = line[:last_quote_pos]
                    if before_last.count('"') % 2 != 0:
                        # Add closing quote
                        line = line[:-2] + '""}'
                        fixes_applied.append(f"Fixed unterminated string at line {i+1}")
            
            # Pattern: Line ends with incomplete escape sequence
            if line.rstrip().endswith('\\') and not line.rstrip().endswith('\\\\'):
                line = line.rstrip()[:-1] + '"'
                fixes_applied.append(f"Fixed incomplete escape sequence at line {i+1}")
            
            # Pattern: separatedBy with wrong escape
            if 'separatedBy:' in line and '\\\\' in line:
                # Fix common mistake: separatedBy: "\\ instead of "\\n"
                line = re.sub(r'separatedBy:\s*"\\\\+$', 'separatedBy: "\\n"', line)
                line = re.sub(r'separatedBy:\s*"\\\\+n"', 'separatedBy: "\\n"', line)
                if line != original:
                    fixes_applied.append(f"Fixed separatedBy escape at line {i+1}")
            
            fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        # Fix 3: Balance braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        if open_braces > close_braces:
            # Add missing closing braces
            missing = open_braces - close_braces
            content += '\n' + '}' * missing
            fixes_applied.append(f"Added {missing} missing closing braces")
        elif close_braces > open_braces:
            # Remove extra closing braces
            lines = content.split('\n')
            fixed_lines = []
            extra_braces = close_braces - open_braces
            removed = 0
            
            # Remove from the end, working backwards
            for i in range(len(lines) - 1, -1, -1):
                line = lines[i]
                if removed < extra_braces and line.strip() in ['}', '},']:
                    removed += 1
                    fixes_applied.append(f"Removed extra closing brace at line {i+1}")
                    continue
                fixed_lines.insert(0, line)
            
            content = '\n'.join(fixed_lines)
        
        # Fix 4: Ensure imports are present
        if 'SwiftUI' not in content and any(keyword in content for keyword in ['View', 'App', 'Text', 'Button']):
            content = 'import SwiftUI\n\n' + content
            fixes_applied.append("Added missing SwiftUI import")
        
        return content, fixes_applied


def integrate_into_claude_service():
    """Show how to integrate this into claude_service.py"""
    
    integration_code = '''
# Add this to claude_service.py in the _validate_and_fix_swift_files method:

from swift_syntax_fixer import SwiftSyntaxFixer

def _validate_and_fix_swift_files(self, files: List[Dict]) -> List[Dict]:
    """Validate and fix common Swift syntax errors"""
    
    fixed_files = []
    fixer = SwiftSyntaxFixer()
    
    for file in files:
        content = file.get("content", "")
        file_path = file.get("path", "")
        
        # Apply Swift syntax fixes
        fixed_content, fixes = fixer.fix_swift_file(content, file_path)
        
        if fixes:
            print(f"Applied {len(fixes)} fixes to {file_path}:")
            for fix in fixes:
                print(f"  - {fix}")
        
        fixed_files.append({
            "path": file_path,
            "content": fixed_content
        })
    
    return fixed_files
'''
    
    print("Integration code for claude_service.py:")
    print(integration_code)


# Test the fixer
def test_fixer():
    """Test the syntax fixer with problematic code"""
    
    test_cases = [
        # Test case 1: Multi-line string literals
        (
            '.navigationTitle("""My Recipes""")',
            '.navigationTitle("My Recipes")'
        ),
        # Test case 2: Unterminated string
        (
            'struct App {\n    var name = "Test\n"}',
            'struct App {\n    var name = "Test"\n"}'
        ),
        # Test case 3: Invalid escape
        (
            'let items = text.components(separatedBy: "\\',
            'let items = text.components(separatedBy: "\\n"'
        ),
    ]
    
    fixer = SwiftSyntaxFixer()
    
    print("Testing Swift syntax fixer...")
    for i, (input_code, expected) in enumerate(test_cases):
        fixed, fixes = fixer.fix_swift_file(input_code, "test.swift")
        print(f"\nTest {i+1}:")
        print(f"Input:    {repr(input_code)}")
        print(f"Fixed:    {repr(fixed)}")
        print(f"Expected: {repr(expected)}")
        print(f"Fixes:    {fixes}")
        print(f"✅ PASS" if fixed.strip() == expected.strip() else "❌ FAIL")


if __name__ == "__main__":
    print("Swift Syntax Fixer Utility")
    print("=" * 50)
    
    # Run tests
    test_fixer()
    
    print("\n" + "=" * 50)
    integrate_into_claude_service()
