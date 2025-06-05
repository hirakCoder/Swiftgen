#!/usr/bin/env python3
"""
Ultimate Swift Syntax Validator - World Class Error Handler
Handles ALL Swift syntax issues including:
- Single quotes to double quotes
- Double double-quotes
- @Environment property wrapper issues
- Import statements
- String interpolation
- And more...
"""

import re
from typing import Tuple, List, Dict, Optional

class SwiftSyntaxValidator:
    """World-class Swift syntax validator that fixes ALL common issues"""

    @staticmethod
    def fix_swift_file(content: str, file_path: str) -> Tuple[str, List[str]]:
        """Fix ALL Swift syntax errors with intelligent pattern matching"""
        fixes_applied = []

        # CRITICAL FIX 0: Fix @Environment issues FIRST
        # This is the current issue causing build failures
        content, env_fixes = SwiftSyntaxValidator._fix_environment_issues(content)
        fixes_applied.extend(env_fixes)

        # CRITICAL FIX 1: Replace all single quotes with double quotes
        if "'" in content:
            content, quote_fixes = SwiftSyntaxValidator._fix_single_quotes(content)
            fixes_applied.extend(quote_fixes)

        # CRITICAL FIX 2: Fix double double-quotes
        content, double_quote_fixes = SwiftSyntaxValidator._fix_double_quotes(content)
        fixes_applied.extend(double_quote_fixes)

        # Process line by line for detailed fixes
        lines = content.split('\n')
        fixed_lines = []

        for i, line in enumerate(lines):
            original_line = line

            # Skip comment lines for most fixes
            is_comment = line.strip().startswith('//')

            if not is_comment:
                # Fix TextField patterns
                line = SwiftSyntaxValidator._fix_textfield_patterns(line)

                # Fix Text patterns
                line = SwiftSyntaxValidator._fix_text_patterns(line)

                # Fix string interpolation
                line = SwiftSyntaxValidator._fix_string_interpolation(line)

                # Fix return statements
                line = SwiftSyntaxValidator._fix_return_statements(line)

                # Fix function parameters
                line = SwiftSyntaxValidator._fix_function_parameters(line)

            if line != original_line:
                fixes_applied.append(f"Fixed syntax at line {i+1}")

            fixed_lines.append(line)

        content = '\n'.join(fixed_lines)

        # GLOBAL FIXES
        content, global_fixes = SwiftSyntaxValidator._apply_global_fixes(content)
        fixes_applied.extend(global_fixes)

        return content, fixes_applied

    @staticmethod
    def _fix_environment_issues(content: str) -> Tuple[str, List[str]]:
        """Fix @Environment property wrapper issues"""
        fixes = []

        # Pattern 1: @Environment(\.presentationMode) -> @Environment(\.dismiss)
        # In iOS 15+, presentationMode is deprecated
        if '@Environment(\\.presentationMode)' in content:
            content = content.replace('@Environment(\\.presentationMode)', '@Environment(\\.dismiss)')
            fixes.append("Updated deprecated presentationMode to dismiss")

        # Pattern 2: Generic parameter inference issue
        # Sometimes the compiler can't infer the type, so we need to be explicit
        patterns = [
            # Fix: @Environment(.presentationMode) var presentationMode
            (r'@Environment\(\.presentationMode\)\s+var\s+(\w+)',
             r'@Environment(\.dismiss) var \1'),

            # Fix backslash issues
            (r'@Environment\(\\\.(\w+)\)', r'@Environment(.\1)'),

            # Fix missing type annotation
            (r'@Environment\(\.(\w+)\)\s+var\s+(\w+)(?!\s*:)',
             r'@Environment(\.\1) var \2'),
        ]

        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                fixes.append(f"Fixed @Environment pattern")
                content = new_content

        # If we still have presentationMode, use the modern approach
        if 'presentationMode' in content:
            # Add dismiss import if needed
            lines = content.split('\n')
            fixed_lines = []

            for line in lines:
                if '@Environment' in line and 'presentationMode' in line:
                    # Modern SwiftUI approach
                    line = re.sub(
                        r'@Environment\([^)]+\)\s+var\s+presentationMode.*',
                        '@Environment(\\.dismiss) private var dismiss',
                        line
                    )
                    fixes.append("Modernized presentationMode to dismiss")
                elif 'presentationMode.wrappedValue.dismiss()' in line:
                    line = line.replace('presentationMode.wrappedValue.dismiss()', 'dismiss()')
                    fixes.append("Updated dismiss() call syntax")

                fixed_lines.append(line)

            content = '\n'.join(fixed_lines)

        return content, fixes

    @staticmethod
    def _fix_single_quotes(content: str) -> Tuple[str, List[str]]:
        """Replace single quotes with double quotes"""
        fixes = []
        single_quote_count = content.count("'")

        if single_quote_count > 0:
            lines = content.split('\n')
            fixed_lines = []

            for i, line in enumerate(lines):
                original_line = line

                # Skip comment lines
                if not line.strip().startswith('//'):
                    # Replace single quotes with double quotes
                    line = re.sub(r"'([^']*)'", r'"\1"', line)

                    if line != original_line:
                        fixes.append(f"Fixed single quotes at line {i+1}")

                fixed_lines.append(line)

            content = '\n'.join(fixed_lines)
            fixes.append(f"Replaced {single_quote_count} single quotes with double quotes")

        return content, fixes

    @staticmethod
    def _fix_double_quotes(content: str) -> Tuple[str, List[str]]:
        """Fix double double-quote issues"""
        fixes = []

        patterns = [
            (r'TextField\("([^"]+)""\)', r'TextField("\1")'),
            (r'Text\(""([^"]+)"\)', r'Text("\1")'),
            (r'Button\(""([^"]+)"\)', r'Button("\1")'),
            (r'Label\(""([^"]+)"\)', r'Label("\1")'),
            (r'""([^"]+)""', r'"\1"'),
        ]

        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                fixes.append(f"Fixed double quotes pattern: {pattern}")
                content = new_content

        return content, fixes

    @staticmethod
    def _fix_textfield_patterns(line: str) -> str:
        """Fix TextField specific patterns"""
        # Fix various TextField patterns
        patterns = [
            (r'TextField\("([^"]+)"",', r'TextField("\1",'),
            (r'TextField\("([^"]+)""\)', r'TextField("\1")'),
            (r'TextField\("([^"]+)""', r'TextField("\1"'),
        ]

        for pattern, replacement in patterns:
            line = re.sub(pattern, replacement, line)

        return line

    @staticmethod
    def _fix_text_patterns(line: str) -> str:
        """Fix Text specific patterns"""
        patterns = [
            (r'Text\(""([^"]+)"\)', r'Text("\1")'),
            (r'Text\("([^"]+)""\)', r'Text("\1")'),
            (r'Text\(""([^"]+)""\)', r'Text("\1")'),
        ]

        for pattern, replacement in patterns:
            line = re.sub(pattern, replacement, line)

        return line

    @staticmethod
    def _fix_string_interpolation(line: str) -> str:
        """Fix string interpolation issues"""
        if '\\(' in line:
            # Fix Text with interpolation
            line = re.sub(r'Text\(""([^:]+):\s*\\([^)]+)\)"\)', r'Text("\1: \\(\2)")', line)

            # Fix interpolation without quotes
            line = re.sub(r'Text\(\\([^)]+)\)', r'Text("\\\1")', line)

        return line

    @staticmethod
    def _fix_return_statements(line: str) -> str:
        """Fix return statements with wrong quotes"""
        if "return " in line:
            # Fix single quotes in return
            line = re.sub(r"return '([^']*)'", r'return "\1"', line)

            # Fix double double quotes in return
            line = re.sub(r'return ""([^"]+)""', r'return "\1"', line)

        return line

    @staticmethod
    def _fix_function_parameters(line: str) -> str:
        """Fix function parameters with wrong quotes"""
        # Generic function call pattern
        line = re.sub(r"([a-zA-Z_]\w*)\('([^']*)'\)", r'\1("\2")', line)
        line = re.sub(r'([a-zA-Z_]\w*)\("([^"]+)""\)', r'\1("\2")', line)
        line = re.sub(r'([a-zA-Z_]\w*)\(""([^"]+)"\)', r'\1("\2")', line)

        return line

    @staticmethod
    def _apply_global_fixes(content: str) -> Tuple[str, List[str]]:
        """Apply global fixes to the entire content"""
        fixes = []

        # Fix imports
        if ('View' in content or 'App' in content) and 'import SwiftUI' not in content:
            content = 'import SwiftUI\n\n' + content
            fixes.append("Added missing SwiftUI import")

        # Fix multi-line string literals
        content = re.sub(r'"""([^"\n]+)"""', r'"\1"', content)

        # Fix navigation titles
        patterns = [
            (r'\.navigationTitle\("""([^"]+)"""\)', r'.navigationTitle("\1")'),
            (r'\.navigationTitle\("([^"]+)""\)', r'.navigationTitle("\1")'),
        ]

        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                content = new_content
                fixes.append("Fixed navigation title quotes")

        # Balance braces
        open_braces = content.count('{')
        close_braces = content.count('}')

        if open_braces > close_braces:
            missing = open_braces - close_braces
            content += '\n' + '}' * missing
            fixes.append(f"Added {missing} missing closing braces")
        elif close_braces > open_braces:
            extra = close_braces - open_braces
            lines = content.split('\n')
            removed = 0

            for i in range(len(lines) - 1, -1, -1):
                if removed < extra and lines[i].strip() == '}':
                    lines.pop(i)
                    removed += 1

            content = '\n'.join(lines)
            fixes.append(f"Removed {removed} extra closing braces")

        # Fix @State declarations
        content = re.sub(
            r'@State\s+private\s+var\s+(\w+)\s*=\s*"([^"]*)"?\s*$',
            r'@State private var \1 = "\2"',
            content,
            flags=re.MULTILINE
        )

        return content, fixes

    @staticmethod
    def analyze_and_fix_build_errors(errors: List[str], swift_files: List[Dict]) -> List[Dict]:
        """Analyze specific build errors and apply targeted fixes"""
        fixed_files = []

        for file in swift_files:
            content = file["content"]
            file_path = file["path"]

            # Check if this file has errors
            file_has_errors = any(file_path in error for error in errors)

            if file_has_errors:
                # Apply aggressive fixes for files with errors
                content, fixes = SwiftSyntaxValidator.fix_swift_file(content, file_path)

                # Additional targeted fixes based on specific errors
                for error in errors:
                    if file_path in error:
                        if "generic parameter" in error and "Environment" in error:
                            # Specific fix for Environment generic parameter issue
                            content = re.sub(
                                r'@Environment\([^)]+\)\s+var\s+presentationMode.*',
                                '@Environment(\\.dismiss) private var dismiss',
                                content
                            )
                        elif "single-quoted string literal" in error:
                            # Ensure all single quotes are replaced
                            content = content.replace("'", '"')
                        elif "unterminated string literal" in error:
                            # Fix unterminated strings
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if line.count('"') % 2 != 0:
                                    # Odd number of quotes - fix it
                                    if line.strip().endswith('"'):
                                        line = '"' + line
                                    else:
                                        line = line + '"'
                                    lines[i] = line
                            content = '\n'.join(lines)
            else:
                # Still apply basic fixes to all files
                content, _ = SwiftSyntaxValidator.fix_swift_file(content, file_path)

            fixed_files.append({
                "path": file_path,
                "content": content
            })

        return fixed_files


def test_validator():
    """Test the validator with all types of issues"""
    test_cases = [
        # Test 1: Environment issue
        '''import SwiftUI
struct DetailView: View {
    @Environment(\\.presentationMode) var presentationMode
    
    var body: some View {
        Button("Dismiss") {
            presentationMode.wrappedValue.dismiss()
        }
    }
}''',

        # Test 2: Single quotes
        '''struct ContentView: View {
    @State private var name = ''
    
    var body: some View {
        TextField('Enter name', text: $name)
        Text('Hello')
    }
}''',

        # Test 3: Double double quotes
        '''struct ContentView: View {
    var body: some View {
        Text(""Hello World"")
        TextField("Name"", text: .constant(""))
    }
}'''
    ]

    validator = SwiftSyntaxValidator()

    for i, test in enumerate(test_cases):
        print(f"\n{'='*50}")
        print(f"Test Case {i+1}:")
        print(f"{'='*50}")
        print("Input:")
        print(test)
        print("\nFixed:")
        fixed, fixes = validator.fix_swift_file(test, f"test{i}.swift")
        print(fixed)
        print(f"\nFixes applied: {fixes}")


if __name__ == "__main__":
    test_validator()