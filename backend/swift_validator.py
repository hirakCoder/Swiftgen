#!/usr/bin/env python3
"""
Swift Validator - Integrates syntax validation into the build pipeline
Uses swiftc -parse for immediate validation and applies automatic fixes
"""

import os
import re
import subprocess
import json
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class SwiftValidator:
    """Validates and fixes Swift code before build attempts"""
    
    def __init__(self):
        # Type name mappings for common mismatches
        self.type_name_mappings = {
            "ErrorView": "AppErrorView",
            "ResultView": "OperationResultView"
        }
        
        # Common patterns that need fixing
        self.auto_fix_patterns = [
            # Remove semicolons
            (r';\s*\n', '\n'),
            (r';\s*$', ''),
            (r';\s*}', '}'),
            
            # Fix semicolons in declarations
            (r'private\s*;\s*var', 'private var'),
            (r'public\s*;\s*var', 'public var'),
            (r'private\s*;\s*func', 'private func'),
            (r'public\s*;\s*func', 'public func'),
            (r'private\s*;\s*let', 'private let'),
            (r'public\s*;\s*let', 'public let'),
            (r'internal\s*;\s*var', 'internal var'),
            (r'fileprivate\s*;\s*var', 'fileprivate var'),
            (r'static\s*;\s*let', 'static let'),
            (r'static\s*;\s*var', 'static var'),
            
            # Fix semicolons after method calls
            (r'\)\s*;\s*\n', ')\n'),
            (r'\)\s*;\s*\.', ').'),
            
            # Fix semicolons in guard statements
            (r',\s*;\s*let', ', let'),
            (r'\?\.\w+\s*,\s*;', '?.rate,'),
            
            # Fix ForEach without id
            (r'ForEach\(([^,)]+)\)\s*\{', r'ForEach(\1, id: \.self) {'),
            
            # Fix modifier placement
            (r'\.padding\(\)\s*\.background', '.background'),
            
            # Fix missing spaces
            (r'(\w)\{', r'\1 {'),
            (r'\}(\w)', r'} \1'),
        ]
        
        # Patterns that indicate missing conformance
        self.conformance_patterns = {
            'Hashable': [
                r"requires that '([^']+)' conform to 'Hashable'",
                r"generic struct 'ForEach' requires that '([^']+)' conform to 'Hashable'"
            ],
            'Identifiable': [
                r"requires that '([^']+)' conform to 'Identifiable'"
            ]
        }
    
    def validate_swift_file(self, file_path: str) -> Tuple[bool, List[str]]:
        """Validate a Swift file using swiftc"""
        try:
            # Create a minimal module map for SwiftUI
            import_check = """
import SwiftUI
import Foundation
"""
            
            # Read the file content
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Create temporary file with imports
            temp_file = file_path + '.tmp'
            with open(temp_file, 'w') as f:
                # Only add imports if not already present
                if 'import SwiftUI' not in content:
                    f.write(import_check)
                f.write(content)
            
            # Use swiftc to parse
            result = subprocess.run(
                ['swiftc', '-parse', '-target', 'arm64-apple-ios15.0', temp_file],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            # Parse errors
            errors = []
            if result.returncode != 0:
                for line in result.stderr.split('\n'):
                    if 'error:' in line and '.tmp' not in line:
                        # Clean up error message
                        error = line.replace(temp_file, os.path.basename(file_path))
                        errors.append(error.strip())
            
            return result.returncode == 0, errors
            
        except subprocess.TimeoutExpired:
            return False, ["Validation timeout"]
        except Exception as e:
            return False, [f"Validation error: {str(e)}"]
    
    def apply_auto_fixes(self, content: str) -> Tuple[str, List[str]]:
        """Apply automatic fixes to Swift content"""
        fixes_applied = []
        
        # Apply pattern-based fixes
        for pattern, replacement in self.auto_fix_patterns:
            matches = len(re.findall(pattern, content))
            if matches > 0:
                content = re.sub(pattern, replacement, content)
                fixes_applied.append(f"Fixed {matches} instances of pattern: {pattern}")
        
        return content, fixes_applied
    
    def add_missing_conformance(self, content: str, type_name: str, conformance: str) -> str:
        """Add missing protocol conformance to a type"""
        # Find the struct/class/enum definition
        patterns = [
            rf'(struct\s+{type_name}\s*)({{)',
            rf'(struct\s+{type_name}\s*:\s*[^{{]+)({{)',
            rf'(class\s+{type_name}\s*)({{)',
            rf'(class\s+{type_name}\s*:\s*[^{{]+)({{)',
            rf'(enum\s+{type_name}\s*)({{)',
            rf'(enum\s+{type_name}\s*:\s*[^{{]+)({{)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                if ':' in match.group(1):
                    # Already has conformance, add to it
                    replacement = match.group(1) + f', {conformance}' + match.group(2)
                else:
                    # No conformance yet
                    replacement = match.group(1).rstrip() + f': {conformance} ' + match.group(2)
                
                content = content[:match.start()] + replacement + content[match.end():]
                
                # If it's a struct that needs Identifiable, add id property
                if conformance == 'Identifiable' and 'struct' in match.group(1):
                    # Add id property after the opening brace
                    id_property = '\n    let id = UUID()\n'
                    brace_pos = content.find('{', match.start())
                    content = content[:brace_pos+1] + id_property + content[brace_pos+1:]
                
                break
        
        return content
    
    def fix_build_errors(self, file_path: str, build_errors: List[str], content: str = None) -> Tuple[bool, str, List[str]]:
        """Fix specific build errors in a file"""
        # If content not provided, try to read file (but this may fail with relative paths)
        if content is None:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
            except FileNotFoundError:
                # Return original content unchanged if file not found
                return False, "", []
        
        fixes_applied = []
        
        # Check for type name mismatch errors
        for error in build_errors:
            if "cannot find" in error and "in scope" in error:
                for old_type, new_type in self.type_name_mappings.items():
                    if f"cannot find '{old_type}' in scope" in error:
                        # Replace usage of old type with new type
                        content = re.sub(rf'\b{old_type}\b', new_type, content)
                        fixes_applied.append(f"Fixed type name: {old_type} -> {new_type}")
        
        # Check for conformance errors
        for error in build_errors:
            # Check Hashable conformance
            for pattern in self.conformance_patterns['Hashable']:
                match = re.search(pattern, error)
                if match:
                    type_name = match.group(1).split('.')[-1]  # Get last part if nested
                    content = self.add_missing_conformance(content, type_name, 'Hashable')
                    fixes_applied.append(f"Added Hashable conformance to {type_name}")
            
            # Check Identifiable conformance
            for pattern in self.conformance_patterns['Identifiable']:
                match = re.search(pattern, error)
                if match:
                    type_name = match.group(1).split('.')[-1]
                    content = self.add_missing_conformance(content, type_name, 'Identifiable')
                    fixes_applied.append(f"Added Identifiable conformance to {type_name}")
        
        # Apply general auto-fixes
        content, auto_fixes = self.apply_auto_fixes(content)
        fixes_applied.extend(auto_fixes)
        
        if fixes_applied:
            return True, content, fixes_applied
        else:
            return False, content, []
    
    def validate_and_fix_project(self, project_path: str) -> Dict:
        """Validate and fix all Swift files in a project"""
        report = {
            'project': project_path,
            'files_checked': 0,
            'files_valid': 0,
            'files_fixed': 0,
            'total_fixes': 0,
            'validation_errors': [],
            'fixes_applied': []
        }
        
        sources_dir = os.path.join(project_path, 'Sources')
        if not os.path.exists(sources_dir):
            report['validation_errors'].append("Sources directory not found")
            return report
        
        # First pass: validate all files
        swift_files = []
        for root, dirs, files in os.walk(sources_dir):
            for file in files:
                if file.endswith('.swift'):
                    file_path = os.path.join(root, file)
                    swift_files.append(file_path)
        
        report['files_checked'] = len(swift_files)
        
        # Validate and fix each file
        for file_path in swift_files:
            logger.info(f"Validating {os.path.basename(file_path)}")
            
            # Initial validation
            valid, errors = self.validate_swift_file(file_path)
            
            if valid:
                report['files_valid'] += 1
            else:
                # Try to fix
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Apply auto-fixes
                fixed_content, fixes = self.apply_auto_fixes(content)
                
                if fixes:
                    # Write fixed content
                    with open(file_path, 'w') as f:
                        f.write(fixed_content)
                    
                    report['files_fixed'] += 1
                    report['total_fixes'] += len(fixes)
                    report['fixes_applied'].extend([f"{os.path.basename(file_path)}: {fix}" for fix in fixes])
                    
                    # Re-validate
                    valid, errors = self.validate_swift_file(file_path)
                    if valid:
                        report['files_valid'] += 1
                    else:
                        report['validation_errors'].extend([f"{os.path.basename(file_path)}: {err}" for err in errors])
                else:
                    report['validation_errors'].extend([f"{os.path.basename(file_path)}: {err}" for err in errors])
        
        return report


def integrate_with_build_service(build_service_instance):
    """Integrate validator with build service"""
    validator = SwiftValidator()
    
    # Store original build method
    original_build = build_service_instance.build_project
    
    async def enhanced_build(project_path: str, project_id: str, bundle_id: str, app_complexity=None, **kwargs):
        """Enhanced build with validation"""
        logger.info("Running Swift validation before build")
        
        # Validate and fix
        validation_report = validator.validate_and_fix_project(project_path)
        
        if validation_report['validation_errors']:
            logger.warning(f"Validation found {len(validation_report['validation_errors'])} errors")
            for error in validation_report['validation_errors'][:5]:
                logger.warning(f"  {error}")
        
        if validation_report['fixes_applied']:
            logger.info(f"Applied {validation_report['total_fixes']} automatic fixes")
            for fix in validation_report['fixes_applied'][:5]:
                logger.info(f"  {fix}")
        
        # Continue with build
        return await original_build(project_path, project_id, bundle_id, app_complexity, **kwargs)
    
    # Replace build method
    build_service_instance.build_project = enhanced_build
    logger.info("Swift validator integrated with build service")


if __name__ == "__main__":
    # Test the validator
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        validator = SwiftValidator()
        
        print(f"Validating {file_path}...")
        valid, errors = validator.validate_swift_file(file_path)
        
        if valid:
            print("✅ File is valid Swift")
        else:
            print("❌ Validation errors:")
            for error in errors:
                print(f"  - {error}")
    else:
        print("Usage: python swift_validator.py <swift_file>")