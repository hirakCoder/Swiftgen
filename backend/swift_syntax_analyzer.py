#!/usr/bin/env python3
"""
Swift Syntax Analyzer
Identifies common Swift syntax errors in generated code and suggests fixes
"""

import os
import re
import json
from typing import Dict, List, Tuple, Optional

class SwiftSyntaxAnalyzer:
    def __init__(self):
        # Common Swift syntax patterns that cause errors
        self.error_patterns = {
            'hashable_conformance': {
                'pattern': r"requires that '([^']+)' conform to 'Hashable'",
                'fix': 'Add Hashable conformance to the struct/enum',
                'example': 'struct MyStruct: Hashable { ... }'
            },
            'semicolon_error': {
                'pattern': r'consecutive statements.*must be separated by .*;',
                'fix': 'Remove unnecessary semicolons from Swift code',
                'example': 'let x = 5 // No semicolon needed'
            },
            'missing_initializer': {
                'pattern': r'no exact matches in call to initializer',
                'fix': 'Check initializer parameters match the type definition',
                'example': 'MyType(param1: value1, param2: value2)'
            },
            'expression_expected': {
                'pattern': r"expected expression, var, or let in 'if' condition",
                'fix': 'Ensure if conditions have valid expressions',
                'example': 'if let value = optionalValue { ... }'
            },
            'type_not_found': {
                'pattern': r"cannot find '([^']+)' in scope",
                'fix': 'Import required module or define the type',
                'example': 'import SwiftUI'
            },
            'invalid_modifier_order': {
                'pattern': r'modifier.*must be used|incorrect modifier order',
                'fix': 'Place modifiers in correct order after the view',
                'example': 'Text("Hello").font(.title).foregroundColor(.blue)'
            }
        }
        
        # Common code patterns that need fixing
        self.code_fixes = {
            # Remove semicolons
            r';\s*\n': '\n',
            r';\s*$': '',
            
            # Fix modifier placement
            r'\.foregroundColor\(([^)]+)\)\s*\{': '.foregroundColor($1)\n{',
            
            # Fix ForEach without id
            r'ForEach\(([^,)]+)\)\s*\{': 'ForEach($1, id: \\.self) {',
            
            # Fix missing Hashable
            r'struct (\w+Button)\s*\{': 'struct $1: Identifiable {\n    let id = UUID()',
        }
    
    def analyze_build_errors(self, error_output: str) -> List[Dict]:
        """Analyze build errors and categorize them"""
        errors = []
        
        lines = error_output.split('\n')
        for line in lines:
            if 'error:' in line:
                error_info = {
                    'line': line,
                    'type': 'unknown',
                    'fix_suggestion': None
                }
                
                # Match against known patterns
                for error_type, pattern_info in self.error_patterns.items():
                    if re.search(pattern_info['pattern'], line):
                        error_info['type'] = error_type
                        error_info['fix_suggestion'] = pattern_info['fix']
                        error_info['example'] = pattern_info['example']
                        break
                
                errors.append(error_info)
        
        return errors
    
    def analyze_swift_file(self, file_path: str) -> Dict:
        """Analyze a Swift file for common issues"""
        with open(file_path, 'r') as f:
            content = f.read()
        
        issues = {
            'file': file_path,
            'semicolons': 0,
            'missing_hashable': [],
            'foreach_without_id': [],
            'other_issues': []
        }
        
        # Count semicolons
        issues['semicolons'] = len(re.findall(r';\s*$', content, re.MULTILINE))
        
        # Check for structs that might need Hashable
        struct_matches = re.findall(r'struct\s+(\w+)\s*\{', content)
        for struct_name in struct_matches:
            if 'Button' in struct_name and 'Identifiable' not in content:
                issues['missing_hashable'].append(struct_name)
        
        # Check ForEach usage
        foreach_matches = re.findall(r'ForEach\([^)]+\)', content)
        for match in foreach_matches:
            if ', id:' not in match and '.enumerated()' not in match:
                issues['foreach_without_id'].append(match)
        
        return issues
    
    def suggest_fixes(self, file_path: str, build_errors: str) -> Dict:
        """Suggest fixes for a file based on build errors"""
        file_analysis = self.analyze_swift_file(file_path)
        error_analysis = self.analyze_build_errors(build_errors)
        
        suggestions = {
            'file': file_path,
            'critical_fixes': [],
            'warnings': [],
            'auto_fixable': []
        }
        
        # Add critical fixes based on build errors
        for error in error_analysis:
            if error['type'] != 'unknown':
                suggestions['critical_fixes'].append({
                    'error_type': error['type'],
                    'fix': error['fix_suggestion'],
                    'example': error.get('example', '')
                })
        
        # Add warnings based on file analysis
        if file_analysis['semicolons'] > 0:
            suggestions['warnings'].append(f"Found {file_analysis['semicolons']} semicolons that should be removed")
            suggestions['auto_fixable'].append('remove_semicolons')
        
        if file_analysis['missing_hashable']:
            suggestions['warnings'].append(f"Structs may need Hashable: {', '.join(file_analysis['missing_hashable'])}")
            suggestions['auto_fixable'].append('add_identifiable')
        
        if file_analysis['foreach_without_id']:
            suggestions['warnings'].append(f"ForEach loops need id parameter: {len(file_analysis['foreach_without_id'])} instances")
            suggestions['auto_fixable'].append('fix_foreach')
        
        return suggestions
    
    def apply_automatic_fixes(self, file_path: str) -> Tuple[bool, str]:
        """Apply automatic fixes to a Swift file"""
        with open(file_path, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Apply code fixes
        for pattern, replacement in self.code_fixes.items():
            content = re.sub(pattern, replacement, content)
        
        # Additional smart fixes
        
        # Fix ForEach without proper id
        content = re.sub(
            r'ForEach\(([^,)]+)\)\s*\{',
            r'ForEach(\1, id: \.self) {',
            content
        )
        
        # Add Identifiable to Button structs
        def add_identifiable(match):
            struct_name = match.group(1)
            if 'Button' in struct_name:
                return f'struct {struct_name}: Identifiable {{\n    let id = UUID()'
            return match.group(0)
        
        content = re.sub(r'struct (\w+Button)\s*\{', add_identifiable, content)
        
        # Check if changes were made
        if content != original_content:
            return True, content
        else:
            return False, content
    
    def analyze_project(self, project_path: str) -> Dict:
        """Analyze entire project for Swift syntax issues"""
        report = {
            'project': project_path,
            'total_files': 0,
            'files_with_issues': 0,
            'total_issues': 0,
            'fixable_issues': 0,
            'file_reports': []
        }
        
        sources_dir = os.path.join(project_path, 'Sources')
        if not os.path.exists(sources_dir):
            return report
        
        for root, dirs, files in os.walk(sources_dir):
            for file in files:
                if file.endswith('.swift'):
                    file_path = os.path.join(root, file)
                    report['total_files'] += 1
                    
                    # Analyze file
                    analysis = self.analyze_swift_file(file_path)
                    
                    # Count issues
                    issue_count = (
                        analysis['semicolons'] + 
                        len(analysis['missing_hashable']) + 
                        len(analysis['foreach_without_id'])
                    )
                    
                    if issue_count > 0:
                        report['files_with_issues'] += 1
                        report['total_issues'] += issue_count
                        report['fixable_issues'] += analysis['semicolons'] + len(analysis['foreach_without_id'])
                        
                        report['file_reports'].append({
                            'file': os.path.relpath(file_path, project_path),
                            'issues': issue_count,
                            'details': analysis
                        })
        
        return report

def main():
    """Test the analyzer on recent projects"""
    analyzer = SwiftSyntaxAnalyzer()
    
    # Find recent project
    workspace_dir = "../workspaces"
    projects = []
    
    if os.path.exists(workspace_dir):
        for item in os.listdir(workspace_dir):
            if item.startswith('proj_') or item.startswith('test_'):
                project_path = os.path.join(workspace_dir, item)
                if os.path.isdir(project_path):
                    projects.append((item, project_path))
    
    if not projects:
        print("No projects found to analyze")
        return
    
    # Analyze most recent project
    projects.sort(reverse=True)
    project_name, project_path = projects[0]
    
    print(f"Analyzing project: {project_name}")
    print("="*60)
    
    report = analyzer.analyze_project(project_path)
    
    print(f"\nProject Analysis Report:")
    print(f"Total Swift files: {report['total_files']}")
    print(f"Files with issues: {report['files_with_issues']}")
    print(f"Total issues found: {report['total_issues']}")
    print(f"Auto-fixable issues: {report['fixable_issues']}")
    
    if report['file_reports']:
        print("\nDetailed Issues:")
        for file_report in report['file_reports']:
            print(f"\n{file_report['file']}:")
            details = file_report['details']
            if details['semicolons']:
                print(f"  - Semicolons: {details['semicolons']}")
            if details['missing_hashable']:
                print(f"  - Missing Hashable/Identifiable: {', '.join(details['missing_hashable'])}")
            if details['foreach_without_id']:
                print(f"  - ForEach without id: {len(details['foreach_without_id'])} instances")
    
    # Save report
    with open('swift_syntax_analysis.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nFull report saved to swift_syntax_analysis.json")

if __name__ == "__main__":
    main()