#!/usr/bin/env python3
"""
SwiftLint Integration for SwiftGen
Adds SwiftLint validation and auto-fixing to the build pipeline
"""

import os
import json
import subprocess
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class SwiftLintIntegration:
    """Integrates SwiftLint for better Swift code quality"""
    
    def __init__(self):
        self.swiftlint_available = self._check_swiftlint()
        
        # SwiftLint configuration for SwiftUI apps
        self.swiftlint_config = """
disabled_rules:
  - line_length
  - file_length
  - function_body_length
  - type_body_length
  
opt_in_rules:
  - empty_count
  - closure_spacing
  - contains_over_first_not_nil
  - discouraged_optional_collection
  - empty_string
  
excluded:
  - Carthage
  - Pods
  - build
  - .build
  - DerivedData

identifier_name:
  min_length: 2
  max_length: 40
  
custom_rules:
  no_semicolons:
    name: "No Semicolons"
    regex: ';\\s*$'
    message: "Swift doesn't require semicolons"
    severity: error
    
  force_https:
    name: "Force HTTPS"
    regex: 'http://(?!localhost)'
    message: "Use https:// for API calls (except localhost)"
    severity: warning
    match_kinds: string
    
  no_print_statements:
    name: "No Print Statements"
    regex: '\\bprint\\('
    message: "Use proper logging instead of print"
    severity: warning
    
  missing_hashable:
    name: "ForEach Hashable"
    regex: 'ForEach\\([^,)]+\\)\\s*\\{'
    message: "ForEach requires id parameter or Hashable conformance"
    severity: error
"""
    
    def _check_swiftlint(self) -> bool:
        """Check if SwiftLint is installed"""
        try:
            result = subprocess.run(['which', 'swiftlint'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"SwiftLint found at: {result.stdout.strip()}")
                return True
        except:
            pass
        
        logger.warning("SwiftLint not installed. Install with: brew install swiftlint")
        return False
    
    def create_config_file(self, project_path: str) -> str:
        """Create .swiftlint.yml in project directory"""
        config_path = os.path.join(project_path, '.swiftlint.yml')
        
        with open(config_path, 'w') as f:
            f.write(self.swiftlint_config)
        
        return config_path
    
    def lint_file(self, file_path: str, project_path: str = None) -> Tuple[bool, List[Dict], List[Dict]]:
        """Run SwiftLint on a single file"""
        if not self.swiftlint_available:
            return True, [], []
        
        try:
            # Create config if needed
            if project_path:
                self.create_config_file(project_path)
            
            # Run SwiftLint with JSON reporter
            cmd = ['swiftlint', 'lint', '--path', file_path, '--reporter', 'json']
            if project_path:
                cmd.extend(['--config', os.path.join(project_path, '.swiftlint.yml')])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Parse JSON output
            if result.stdout:
                issues = json.loads(result.stdout)
            else:
                issues = []
            
            # Separate warnings and errors
            warnings = [i for i in issues if i.get('severity') == 'warning']
            errors = [i for i in issues if i.get('severity') == 'error']
            
            return len(errors) == 0, warnings, errors
            
        except Exception as e:
            logger.error(f"SwiftLint error: {e}")
            return True, [], []
    
    def autocorrect_file(self, file_path: str, project_path: str = None) -> Tuple[bool, List[str]]:
        """Run SwiftLint autocorrect on a file"""
        if not self.swiftlint_available:
            return False, []
        
        try:
            # Run autocorrect
            cmd = ['swiftlint', 'autocorrect', '--path', file_path]
            if project_path:
                cmd.extend(['--config', os.path.join(project_path, '.swiftlint.yml')])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Parse output for corrections
            corrections = []
            for line in result.stdout.split('\n'):
                if 'Correcting' in line:
                    corrections.append(line.strip())
            
            return result.returncode == 0, corrections
            
        except Exception as e:
            logger.error(f"SwiftLint autocorrect error: {e}")
            return False, []
    
    def lint_project(self, project_path: str) -> Dict:
        """Lint entire project and return report"""
        if not self.swiftlint_available:
            return {'available': False}
        
        report = {
            'available': True,
            'files_linted': 0,
            'total_warnings': 0,
            'total_errors': 0,
            'autocorrected': 0,
            'file_reports': []
        }
        
        # Create config
        self.create_config_file(project_path)
        
        # Find all Swift files
        sources_dir = os.path.join(project_path, 'Sources')
        if not os.path.exists(sources_dir):
            return report
        
        for root, dirs, files in os.walk(sources_dir):
            for file in files:
                if file.endswith('.swift'):
                    file_path = os.path.join(root, file)
                    
                    # Lint file
                    success, warnings, errors = self.lint_file(file_path, project_path)
                    
                    report['files_linted'] += 1
                    report['total_warnings'] += len(warnings)
                    report['total_errors'] += len(errors)
                    
                    if warnings or errors:
                        # Try autocorrect
                        corrected, corrections = self.autocorrect_file(file_path, project_path)
                        if corrections:
                            report['autocorrected'] += len(corrections)
                        
                        report['file_reports'].append({
                            'file': os.path.relpath(file_path, project_path),
                            'warnings': len(warnings),
                            'errors': len(errors),
                            'autocorrected': len(corrections)
                        })
        
        return report
    
    def format_issue(self, issue: Dict) -> str:
        """Format a SwiftLint issue for display"""
        return f"{issue.get('file', 'unknown')}:{issue.get('line', 0)}:{issue.get('character', 0)}: {issue.get('severity', 'warning')}: {issue.get('reason', 'unknown issue')}"


def integrate_swiftlint_with_validator(swift_validator):
    """Add SwiftLint to the Swift validator"""
    
    swiftlint = SwiftLintIntegration()
    swift_validator.swiftlint = swiftlint
    
    # Store original validate method
    original_validate = swift_validator.validate_swift_file
    
    def enhanced_validate_swift_file(self, file_path: str) -> Tuple[bool, List[str]]:
        """Enhanced validation with SwiftLint"""
        # First run original validation
        valid, errors = original_validate(file_path)
        
        # Then run SwiftLint if available
        if hasattr(self, 'swiftlint') and self.swiftlint.swiftlint_available:
            # Get project path
            project_path = None
            path_parts = file_path.split('/')
            if 'workspaces' in path_parts:
                idx = path_parts.index('workspaces')
                if idx + 1 < len(path_parts):
                    project_path = '/'.join(path_parts[:idx+2])
            
            # Run SwiftLint
            lint_success, warnings, lint_errors = self.swiftlint.lint_file(file_path, project_path)
            
            # Add SwiftLint errors to validation errors
            for error in lint_errors:
                error_msg = self.swiftlint.format_issue(error)
                if error_msg not in errors:
                    errors.append(error_msg)
            
            # If SwiftLint found errors, mark as invalid
            if lint_errors:
                valid = False
        
        return valid, errors
    
    # Replace method
    import types
    swift_validator.validate_swift_file = types.MethodType(
        enhanced_validate_swift_file, swift_validator
    )
    
    # Add autocorrect capability
    def swiftlint_autocorrect(self, file_path: str) -> Tuple[bool, List[str]]:
        """Run SwiftLint autocorrect"""
        if hasattr(self, 'swiftlint') and self.swiftlint.swiftlint_available:
            return self.swiftlint.autocorrect_file(file_path)
        return False, []
    
    swift_validator.swiftlint_autocorrect = types.MethodType(
        swiftlint_autocorrect, swift_validator
    )
    
    logger.info("SwiftLint integrated with Swift validator")


def main():
    """Test SwiftLint integration"""
    print("Testing SwiftLint Integration")
    print("="*60)
    
    swiftlint = SwiftLintIntegration()
    
    if swiftlint.swiftlint_available:
        print("✅ SwiftLint is available")
        
        # Test on sample code
        test_code = '''import SwiftUI

struct ContentView: View {
    @State private var count = 0;
    
    var body: some View {
        VStack {
            Text("Count: \\(count)");
            print("Debug")
            Button("Increment") {
                count += 1;
            }
        }
    }
}'''
        
        # Write test file
        test_file = '/tmp/test_swiftlint.swift'
        with open(test_file, 'w') as f:
            f.write(test_code)
        
        # Lint it
        print("\nLinting test file...")
        success, warnings, errors = swiftlint.lint_file(test_file)
        
        print(f"Success: {success}")
        print(f"Warnings: {len(warnings)}")
        print(f"Errors: {len(errors)}")
        
        if errors:
            print("\nErrors found:")
            for error in errors:
                print(f"  - {swiftlint.format_issue(error)}")
        
        # Try autocorrect
        print("\nRunning autocorrect...")
        corrected, corrections = swiftlint.autocorrect_file(test_file)
        print(f"Corrections made: {len(corrections)}")
        
    else:
        print("❌ SwiftLint not available")
        print("Install with: brew install swiftlint")

if __name__ == "__main__":
    main()