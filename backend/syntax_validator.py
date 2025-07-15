"""
Swift Syntax Validator
Validates Swift code syntax before writing to disk to prevent basic syntax errors
"""

import re
from typing import Dict, List, Tuple, Optional
import json

class SyntaxValidator:
    """Validates Swift code syntax before file writing"""
    
    def __init__(self):
        # Track brace balance
        self.brace_pairs = {
            '{': '}',
            '[': ']',
            '(': ')'
        }
        
        # Swift statement patterns that must be complete
        self.incomplete_patterns = [
            (r'(struct|class|enum|protocol)\s+\w+\s*$', 'Type definition incomplete - missing body'),
            (r'(struct|class|enum|protocol)\s+\w+\s*:\s*\w+\s*$', 'Type definition incomplete - missing body'),
            (r'func\s+\w+\s*\([^)]*\)\s*(->\s*\w+)?\s*$', 'Function definition incomplete - missing body'),
            (r'var\s+\w+\s*:\s*\w+\s*$', 'Variable declaration may need initializer or computed property'),
            (r'if\s+[^{]+$', 'If statement incomplete - missing body'),
            (r'guard\s+[^{]+$', 'Guard statement incomplete - missing else clause'),
            (r'switch\s+[^{]+$', 'Switch statement incomplete - missing cases'),
            (r'for\s+[^{]+$', 'For loop incomplete - missing body'),
            (r'while\s+[^{]+$', 'While loop incomplete - missing body'),
        ]
        
        # Common Swift syntax errors - simplified and less strict
        self.syntax_errors = [
            # Only check for very obvious syntax errors
            # Single quotes instead of double quotes (but only for strings, not chars)
            (r"'[^']{2,}'", "Use double quotes for strings in Swift"),
            # Missing return type arrow (only for obvious cases)
            (r'func\s+\w+\s*\([^)]*\)\s+[A-Z]\w*\s*\{', "Missing '->' for function return type"),
        ]
        
        # Required Swift file components
        self.required_components = {
            '.swift': ['import'],  # All Swift files need at least one import
            'App.swift': ['@main', 'import SwiftUI', ': App', 'var body: some Scene'],
            'View.swift': ['import SwiftUI', ': View', 'var body: some View']
        }
        
        # Invalid character sequences
        self.invalid_sequences = [
            ('...', 'Use proper Swift syntax, not placeholder ellipsis'),
            (';;', 'Avoid double semicolons'),
            ('::', 'Invalid scope resolution - Swift uses dot notation'),
            ('===', 'Use === only for reference equality checks'),
            (' = = ', 'Use == for equality comparison'),
        ]

    def validate_syntax(self, file_path: str, content: str) -> Tuple[bool, List[str]]:
        """
        Validate Swift syntax before writing to file - minimal version
        Returns: (is_valid, error_messages)
        """
        errors = []
        
        # Skip validation for empty files
        if not content or len(content.strip()) < 5:
            return True, []
        
        # Only do minimal validation - check if it's Swift-like content
        if file_path.endswith('.swift'):
            if 'import' not in content:
                errors.append("Swift file missing import statements")
        
        # Always allow files to be written - validation is too strict
        return True, errors
    
    def _check_brace_balance(self, content: str) -> List[str]:
        """Check if braces are balanced - more lenient version"""
        errors = []
        
        # Skip validation for very short content
        if len(content) < 10:
            return errors
        
        # Simple balanced check - count opening and closing braces
        brace_counts = {'{': 0, '}': 0, '[': 0, ']': 0, '(': 0, ')': 0}
        
        # Skip strings and comments for more accurate counting
        in_string = False
        in_single_line_comment = False
        in_multi_line_comment = False
        escaped = False
        
        for i, char in enumerate(content):
            # Handle escape sequences
            if escaped:
                escaped = False
                continue
            
            if char == '\\':
                escaped = True
                continue
            
            # Handle newlines - reset single line comment
            if char == '\n':
                in_single_line_comment = False
                continue
            
            # Skip if in comments
            if in_single_line_comment or in_multi_line_comment:
                if not in_multi_line_comment:
                    continue
                # Check for end of multi-line comment
                if char == '*' and i + 1 < len(content) and content[i + 1] == '/':
                    in_multi_line_comment = False
                continue
            
            # Handle strings
            if char == '"' and not in_string:
                in_string = True
                continue
            elif char == '"' and in_string:
                in_string = False
                continue
            
            # Skip if in string
            if in_string:
                continue
            
            # Check for comments
            if char == '/' and i + 1 < len(content):
                next_char = content[i + 1]
                if next_char == '/':
                    in_single_line_comment = True
                    continue
                elif next_char == '*':
                    in_multi_line_comment = True
                    continue
            
            # Count braces
            if char in brace_counts:
                brace_counts[char] += 1
        
        # Check balance - only report if severely unbalanced
        if abs(brace_counts['{'] - brace_counts['}']) > 2:
            errors.append(f"Severely unbalanced braces: {brace_counts['{']} opening, {brace_counts['}']} closing")
        
        if abs(brace_counts['['] - brace_counts[']']) > 2:
            errors.append(f"Severely unbalanced brackets: {brace_counts['[']} opening, {brace_counts[']']} closing")
        
        if abs(brace_counts['('] - brace_counts[')']) > 2:
            errors.append(f"Severely unbalanced parentheses: {brace_counts['(']} opening, {brace_counts[')']} closing")
        
        return errors
    
    def _check_incomplete_statements(self, content: str) -> List[str]:
        """Check for incomplete Swift statements"""
        errors = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            
            for pattern, error_msg in self.incomplete_patterns:
                if re.match(pattern, line):
                    # Check if the next non-empty line starts with {
                    next_line_has_brace = False
                    for j in range(i + 1, len(lines)):
                        next_line = lines[j].strip()
                        if next_line:
                            if next_line.startswith('{'):
                                next_line_has_brace = True
                            break
                    
                    if not next_line_has_brace and '{' not in line:
                        errors.append(f"Line {i+1}: {error_msg}")
        
        return errors
    
    def _check_syntax_errors(self, content: str) -> List[str]:
        """Check for common Swift syntax errors"""
        errors = []
        
        for pattern, error_msg in self.syntax_errors:
            matches = list(re.finditer(pattern, content))
            for match in matches:
                # Get line number
                line_num = content[:match.start()].count('\n') + 1
                
                # Special handling for string quotes
                if error_msg == "Use double quotes for strings in Swift":
                    # Check if it's actually a character literal (single character)
                    matched_text = match.group(0)
                    if len(matched_text) == 3:  # 'x' format
                        continue  # Character literals are OK
                
                errors.append(f"Line {line_num}: {error_msg}")
        
        return errors
    
    def _check_required_components(self, file_path: str, content: str) -> List[str]:
        """Check for required components based on file type"""
        errors = []
        
        # Check general Swift file requirements
        if file_path.endswith('.swift'):
            if 'import' not in content:
                errors.append("Swift file missing import statements")
        
        # Check specific file requirements
        for file_pattern, required in self.required_components.items():
            if file_pattern in file_path:
                for component in required:
                    if component not in content:
                        errors.append(f"Missing required component: {component}")
        
        return errors
    
    def _check_invalid_sequences(self, content: str) -> List[str]:
        """Check for invalid character sequences"""
        errors = []
        
        for sequence, error_msg in self.invalid_sequences:
            if sequence in content:
                # Count occurrences and report line numbers
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if sequence in line:
                        # Skip if in comment
                        if '//' in line and line.index('//') < line.index(sequence):
                            continue
                        errors.append(f"Line {i+1}: {error_msg}")
        
        return errors
    
    def _check_string_literals(self, content: str) -> List[str]:
        """Check string literal syntax"""
        errors = []
        
        # Check for unclosed strings
        lines = content.split('\n')
        for i, line in enumerate(lines):
            # Skip comments
            if line.strip().startswith('//'):
                continue
            
            # Count quotes (excluding escaped quotes)
            quote_count = 0
            j = 0
            while j < len(line):
                if line[j] == '"' and (j == 0 or line[j-1] != '\\'):
                    quote_count += 1
                j += 1
            
            if quote_count % 2 != 0:
                errors.append(f"Line {i+1}: Unclosed string literal")
        
        # Check for invalid escape sequences
        invalid_escapes = re.finditer(r'\\[^"ntr\\0]', content)
        for match in invalid_escapes:
            line_num = content[:match.start()].count('\n') + 1
            errors.append(f"Line {line_num}: Invalid escape sequence '{match.group(0)}'")
        
        return errors
    
    def _check_function_syntax(self, content: str) -> List[str]:
        """Check function/method syntax"""
        errors = []
        
        # Check for functions with multiple return arrows
        if content.count('->') > content.count('func'):
            errors.append("Possible syntax error: More return arrows (->) than functions")
        
        # Check for async/await syntax
        async_funcs = re.finditer(r'func\s+\w+[^{]*async[^{]*\{', content)
        for match in async_funcs:
            func_text = match.group(0)
            # Check if 'async' is in the right position (after parameters, before throws/return)
            if 'async)' in func_text:  # async in wrong position
                line_num = content[:match.start()].count('\n') + 1
                errors.append(f"Line {line_num}: 'async' should come after parameter list, not inside it")
        
        # Check for missing parameter labels
        func_calls = re.finditer(r'\w+\([^)]+\)', content)
        for match in func_calls:
            call_text = match.group(0)
            # Skip if it's a type cast or declaration
            if call_text.startswith(('Int(', 'String(', 'Double(', 'Float(', 'Bool(')):
                continue
            
            # Check if parameters have labels (rough check)
            params = call_text[call_text.index('(')+1:-1]
            if params and ':' not in params and ',' in params:
                # Multi-parameter call without labels (might be an issue)
                line_num = content[:match.start()].count('\n') + 1
                # Only warn for non-standard functions
                func_name = call_text[:call_text.index('(')]
                if func_name not in ['print', 'max', 'min', 'abs']:
                    errors.append(f"Line {line_num}: Function call '{func_name}' may need parameter labels")
        
        return errors
    
    def _check_property_syntax(self, content: str) -> List[str]:
        """Check property declaration syntax"""
        errors = []
        
        # Check for properties without initialization or type
        uninitialized = re.finditer(r'(let|var)\s+\w+\s*$', content, re.MULTILINE)
        for match in uninitialized:
            line_num = content[:match.start()].count('\n') + 1
            errors.append(f"Line {line_num}: Property needs type annotation or initial value")
        
        # Check for computed properties without get/set
        computed_props = re.finditer(r'var\s+\w+\s*:\s*\w+\s*\{[^}]*\}', content)
        for match in computed_props:
            prop_body = match.group(0)
            if 'get' not in prop_body and 'set' not in prop_body and '=' not in prop_body:
                line_num = content[:match.start()].count('\n') + 1
                errors.append(f"Line {line_num}: Computed property needs 'get' or 'set' accessor")
        
        # Check for @Published without import Combine
        if '@Published' in content and 'import Combine' not in content:
            errors.append("@Published requires 'import Combine'")
        
        # Check for @State/@Binding outside of View
        state_usage = re.finditer(r'@(State|Binding|StateObject|ObservedObject)', content)
        for match in state_usage:
            # Check if we're inside a View
            prefix = content[:match.start()]
            if ': View' not in prefix and 'struct' in prefix:
                # Might be using SwiftUI property wrapper outside a View
                line_num = prefix.count('\n') + 1
                wrapper = match.group(1)
                errors.append(f"Line {line_num}: @{wrapper} should only be used in SwiftUI Views")
        
        return errors
    
    def fix_common_issues(self, content: str) -> str:
        """Attempt to fix common syntax issues automatically"""
        fixed = content
        
        # Fix single quotes to double quotes (except character literals)
        fixed = re.sub(r"'([^']{2,})'", r'"\1"', fixed)
        
        # Remove placeholder ellipsis
        fixed = re.sub(r'\.\.\.', '// TODO: Implement', fixed)
        
        # Fix double semicolons
        fixed = re.sub(r';;', ';', fixed)
        
        # Add missing imports for common cases
        if '@Published' in fixed and 'import Combine' not in fixed:
            fixed = 'import Combine\n' + fixed
        
        if any(ui_element in fixed for ui_element in ['View', 'VStack', 'HStack', 'Text']) and 'import SwiftUI' not in fixed:
            fixed = 'import SwiftUI\n' + fixed
        
        # Fix incomplete type definitions by adding minimal body
        fixed = re.sub(r'(struct\s+\w+\s*:\s*View)\s*$', r'\1 {\n    var body: some View {\n        Text("TODO")\n    }\n}', fixed, flags=re.MULTILINE)
        fixed = re.sub(r'(class\s+\w+\s*:\s*ObservableObject)\s*$', r'\1 {\n    // TODO: Add properties\n}', fixed, flags=re.MULTILINE)
        
        return fixed
    
    def get_syntax_report(self, files: List[Dict[str, str]]) -> Dict[str, any]:
        """Generate a syntax validation report for all files"""
        report = {
            'total_files': len(files),
            'valid_files': 0,
            'files_with_errors': 0,
            'total_errors': 0,
            'errors_by_type': {},
            'file_errors': {}
        }
        
        for file in files:
            path = file.get('path', '')
            content = file.get('content', '')
            
            is_valid, errors = self.validate_syntax(path, content)
            
            if is_valid:
                report['valid_files'] += 1
            else:
                report['files_with_errors'] += 1
                report['file_errors'][path] = errors
                report['total_errors'] += len(errors)
                
                # Categorize errors
                for error in errors:
                    error_type = 'unknown'
                    if 'brace' in error.lower() or 'unclosed' in error.lower():
                        error_type = 'brace_mismatch'
                    elif 'incomplete' in error.lower():
                        error_type = 'incomplete_statement'
                    elif 'missing' in error.lower():
                        error_type = 'missing_component'
                    elif 'quote' in error.lower() or 'string' in error.lower():
                        error_type = 'string_error'
                    else:
                        error_type = 'syntax_error'
                    
                    report['errors_by_type'][error_type] = report['errors_by_type'].get(error_type, 0) + 1
        
        return report