"""
Swift Code Validator - Pre-build validation to catch obvious syntax errors
"""

import re
from typing import List, Dict, Tuple

class SwiftCodeValidator:
    """Validates Swift code for common syntax errors before attempting to build"""
    
    @staticmethod
    def validate_swift_code(code: str, filename: str) -> Tuple[bool, List[str]]:
        """
        Validates Swift code and returns (is_valid, errors)
        """
        errors = []
        
        # Check for ... in class/struct/enum declarations
        if re.search(r'(class|struct|enum)\s+\w+\.\.\.', code):
            errors.append(f"{filename}: Invalid syntax '...' in type declaration - code appears truncated")
            
        # Check for any ... at end of lines (indicates truncation)
        if re.search(r'\.\.\.\s*$', code, re.MULTILINE):
            errors.append(f"{filename}: Code appears to be truncated (found '...' at end of line)")
        
        # Check for Color.darkGray (should be .gray)
        if 'Color.darkGray' in code:
            errors.append(f"{filename}: 'Color.darkGray' doesn't exist in SwiftUI. Use '.gray' instead")
            
        # Check for unbalanced braces
        open_braces = code.count('{')
        close_braces = code.count('}')
        if open_braces != close_braces:
            errors.append(f"{filename}: Unbalanced braces - {open_braces} open, {close_braces} close")
            
        # Check for SwiftUI import in View files
        if 'struct' in code and ': View' in code and 'import SwiftUI' not in code:
            errors.append(f"{filename}: Missing 'import SwiftUI' for View")
            
        # Check for @main in App file
        if filename == "App.swift" and '@main' not in code:
            errors.append(f"{filename}: Missing @main attribute for App")
            
        # Check for common color mistakes
        invalid_colors = [
            ('darkGray', '.gray'),
            ('lightGray', '.gray.opacity(0.3)'),
            ('darkBlue', '.blue'),
            ('lightBlue', '.blue.opacity(0.3)')
        ]
        
        for invalid, valid in invalid_colors:
            if f'Color.{invalid}' in code or f'.{invalid})' in code:
                errors.append(f"{filename}: Invalid color '.{invalid}', use '{valid}' instead")
        
        # Check for incomplete class/struct definitions
        if re.search(r'(class|struct|enum)\s+\w+\s*\.\.\.', code):
            errors.append(f"{filename}: Incomplete type definition with '...'")
            
        # Check for @ObservableObject without import Combine
        if '@ObservableObject' in code and 'import Combine' not in code:
            errors.append(f"{filename}: Missing 'import Combine' for @ObservableObject")
            
        # Check for @Published without import Combine  
        if '@Published' in code and 'import Combine' not in code:
            errors.append(f"{filename}: Missing 'import Combine' for @Published")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def fix_common_issues(code: str) -> str:
        """
        Attempts to fix common issues in Swift code
        """
        # Fix Color.darkGray -> .gray
        code = code.replace('Color.darkGray', '.gray')
        code = code.replace('.darkGray)', '.gray)')
        
        # Fix incomplete class definitions
        code = re.sub(r'(class|struct|enum)(\s+\w+)\.\.\.', r'\1\2 {', code)
        
        # Add missing imports based on usage
        if '@ObservableObject' in code or '@Published' in code:
            if 'import Combine' not in code:
                # Add after SwiftUI import if present
                if 'import SwiftUI' in code:
                    code = code.replace('import SwiftUI', 'import SwiftUI\nimport Combine')
                else:
                    code = 'import Combine\n' + code
                    
        return code
    
    @staticmethod
    def validate_files(files: List[Dict[str, str]]) -> Tuple[bool, List[str], List[Dict[str, str]]]:
        """
        Validates multiple Swift files and attempts to fix issues
        Returns (all_valid, all_errors, fixed_files)
        """
        all_errors = []
        fixed_files = []
        
        for file in files:
            path = file['path']
            content = file['content']
            filename = path.split('/')[-1]
            
            # Validate original
            is_valid, errors = SwiftCodeValidator.validate_swift_code(content, filename)
            
            if not is_valid:
                # Try to fix
                fixed_content = SwiftCodeValidator.fix_common_issues(content)
                
                # Validate fixed version
                is_fixed_valid, fixed_errors = SwiftCodeValidator.validate_swift_code(fixed_content, filename)
                
                if is_fixed_valid or len(fixed_errors) < len(errors):
                    # Use fixed version
                    fixed_files.append({
                        'path': path,
                        'content': fixed_content
                    })
                    all_errors.extend(fixed_errors)
                else:
                    # Keep original and report errors
                    fixed_files.append(file)
                    all_errors.extend(errors)
            else:
                fixed_files.append(file)
                
        return len(all_errors) == 0, all_errors, fixed_files