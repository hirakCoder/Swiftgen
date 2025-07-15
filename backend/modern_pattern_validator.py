"""
Modern Swift Pattern Validator
Validates Swift code for modern patterns and best practices
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ValidationIssue:
    """Represents a validation issue found in code"""
    severity: str  # "error", "warning", "info"
    file_path: str
    line_number: int
    issue_type: str
    message: str
    suggestion: Optional[str] = None
    
class ModernPatternValidator:
    """Validates Swift code for modern patterns and iOS version compatibility"""
    
    def __init__(self, target_ios_version: str = "16.0"):
        self.target_ios_version = target_ios_version
        self.ios_major_version = int(target_ios_version.split('.')[0])
        
        # Define deprecated patterns and their replacements
        self.deprecated_patterns = {
            # Navigation patterns
            r'\bNavigationView\s*\{': {
                'issue': 'NavigationView is deprecated',
                'suggestion': 'Use NavigationStack for iOS 16+',
                'severity': 'warning'
            },
            
            # Observable patterns (for iOS 17+)
            r'@ObservableObject': {
                'issue': '@ObservableObject is legacy pattern',
                'suggestion': 'Use @Observable for iOS 17+ (keep @ObservableObject for iOS 16)',
                'severity': 'info' if self.ios_major_version < 17 else 'warning'
            },
            
            # Deprecated modifiers
            r'\.foregroundColor\(': {
                'issue': 'foregroundColor is deprecated',
                'suggestion': 'Use foregroundStyle instead',
                'severity': 'warning'
            },
            
            # iOS 17+ only features
            r'\.symbolEffect\(': {
                'issue': 'symbolEffect is only available in iOS 17+',
                'suggestion': 'Use .scaleEffect or .opacity animations for iOS 16',
                'severity': 'error' if self.ios_major_version < 17 else 'info'
            },
            
            r'\.bounce\b': {
                'issue': '.bounce is only available in iOS 17+',
                'suggestion': 'Use .animation(.spring()) for iOS 16',
                'severity': 'error' if self.ios_major_version < 17 else 'info'
            },
            
            r'@Observable\b': {
                'issue': '@Observable is only available in iOS 17+',
                'suggestion': 'Use ObservableObject + @Published for iOS 16',
                'severity': 'error' if self.ios_major_version < 17 else 'info'
            },
            
            r'\.scrollBounceBehavior\(': {
                'issue': 'scrollBounceBehavior is only available in iOS 17+',
                'suggestion': 'Remove for iOS 16 compatibility',
                'severity': 'error' if self.ios_major_version < 17 else 'info'
            },
            
            r'\.contentTransition\(': {
                'issue': 'contentTransition is only available in iOS 17+',
                'suggestion': 'Use alternative transition methods for iOS 16',
                'severity': 'error' if self.ios_major_version < 17 else 'info'
            }
        }
        
        # Dangerous concurrency patterns
        self.concurrency_issues = {
            r'DispatchSemaphore.*async': {
                'issue': 'DispatchSemaphore with async/await causes crashes',
                'suggestion': 'Use Task-based synchronization or AsyncStream',
                'severity': 'error'
            },
            
            r'DispatchQueue\.main\.async.*await': {
                'issue': 'Mixing GCD with async/await can cause issues',
                'suggestion': 'Use @MainActor or MainActor.run',
                'severity': 'warning'
            }
        }
        
        # Module import issues
        self.module_import_patterns = {
            r'^\s*import\s+(Components|Views|Models|ViewModels|Services)\b': {
                'issue': 'Local module imports are not valid in SwiftUI',
                'suggestion': 'Remove import and use types directly',
                'severity': 'error'
            }
        }
        
        # Missing @MainActor patterns
        self.mainactor_patterns = {
            r'class\s+\w+.*:.*View(?:Model)?.*\{': {
                'check_for': '@MainActor',
                'issue': 'View-related classes should be marked with @MainActor',
                'suggestion': 'Add @MainActor before class declaration',
                'severity': 'warning'
            }
        }
    
    def validate_files(self, swift_files: List[Dict[str, str]]) -> List[ValidationIssue]:
        """Validate a list of Swift files for modern patterns"""
        issues = []
        
        for file in swift_files:
            file_path = file.get('path', 'unknown')
            content = file.get('content', '')
            
            # Validate each file
            file_issues = self._validate_file(file_path, content)
            issues.extend(file_issues)
        
        return issues
    
    def _validate_file(self, file_path: str, content: str) -> List[ValidationIssue]:
        """Validate a single file"""
        issues = []
        lines = content.split('\n')
        
        # Check deprecated patterns
        for pattern, info in self.deprecated_patterns.items():
            matches = self._find_pattern_matches(content, pattern)
            for line_num, line_content in matches:
                issues.append(ValidationIssue(
                    severity=info['severity'],
                    file_path=file_path,
                    line_number=line_num,
                    issue_type='deprecated_pattern',
                    message=info['issue'],
                    suggestion=info['suggestion']
                ))
        
        # Check concurrency issues
        for pattern, info in self.concurrency_issues.items():
            matches = self._find_pattern_matches(content, pattern)
            for line_num, line_content in matches:
                issues.append(ValidationIssue(
                    severity=info['severity'],
                    file_path=file_path,
                    line_number=line_num,
                    issue_type='concurrency_issue',
                    message=info['issue'],
                    suggestion=info['suggestion']
                ))
        
        # Check module imports
        for pattern, info in self.module_import_patterns.items():
            matches = self._find_pattern_matches(content, pattern)
            for line_num, line_content in matches:
                issues.append(ValidationIssue(
                    severity=info['severity'],
                    file_path=file_path,
                    line_number=line_num,
                    issue_type='invalid_import',
                    message=info['issue'],
                    suggestion=info['suggestion']
                ))
        
        # Check @MainActor usage
        for pattern, info in self.mainactor_patterns.items():
            matches = self._find_pattern_matches(content, pattern)
            for line_num, line_content in matches:
                # Check if @MainActor is present in the previous few lines
                start_line = max(0, line_num - 3)
                previous_lines = '\n'.join(lines[start_line:line_num])
                if info['check_for'] not in previous_lines:
                    issues.append(ValidationIssue(
                        severity=info['severity'],
                        file_path=file_path,
                        line_number=line_num,
                        issue_type='missing_mainactor',
                        message=info['issue'],
                        suggestion=info['suggestion']
                    ))
        
        return issues
    
    def _find_pattern_matches(self, content: str, pattern: str) -> List[Tuple[int, str]]:
        """Find all matches of a pattern in content with line numbers"""
        matches = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                matches.append((i, line))
        
        return matches
    
    def get_critical_issues(self, issues: List[ValidationIssue]) -> List[ValidationIssue]:
        """Get only critical issues that would prevent compilation"""
        return [issue for issue in issues if issue.severity == 'error']
    
    def get_warnings(self, issues: List[ValidationIssue]) -> List[ValidationIssue]:
        """Get warning-level issues"""
        return [issue for issue in issues if issue.severity == 'warning']
    
    def format_issues_for_display(self, issues: List[ValidationIssue]) -> str:
        """Format issues for user-friendly display"""
        if not issues:
            return "✅ No validation issues found"
        
        output = []
        
        # Group by severity
        errors = [i for i in issues if i.severity == 'error']
        warnings = [i for i in issues if i.severity == 'warning']
        info = [i for i in issues if i.severity == 'info']
        
        if errors:
            output.append(f"❌ {len(errors)} Error(s):")
            for issue in errors[:5]:  # Show first 5
                output.append(f"  - {issue.file_path}:{issue.line_number} - {issue.message}")
                if issue.suggestion:
                    output.append(f"    💡 {issue.suggestion}")
        
        if warnings:
            output.append(f"\n⚠️  {len(warnings)} Warning(s):")
            for issue in warnings[:3]:  # Show first 3
                output.append(f"  - {issue.file_path}:{issue.line_number} - {issue.message}")
                if issue.suggestion:
                    output.append(f"    💡 {issue.suggestion}")
        
        if info:
            output.append(f"\nℹ️  {len(info)} Info message(s)")
        
        return '\n'.join(output)
    
    def auto_fix_issues(self, swift_files: List[Dict[str, str]], issues: List[ValidationIssue]) -> Tuple[bool, List[Dict[str, str]], List[str]]:
        """Attempt to automatically fix certain issues"""
        fixed_files = []
        fixes_applied = []
        
        # Group issues by file
        issues_by_file = {}
        for issue in issues:
            if issue.file_path not in issues_by_file:
                issues_by_file[issue.file_path] = []
            issues_by_file[issue.file_path].append(issue)
        
        # Process each file
        for file in swift_files:
            file_path = file.get('path', '')
            content = file.get('content', '')
            
            if file_path in issues_by_file:
                fixed_content, file_fixes = self._auto_fix_file(content, issues_by_file[file_path])
                if file_fixes:
                    fixes_applied.extend(file_fixes)
                    fixed_files.append({
                        'path': file_path,
                        'content': fixed_content
                    })
                else:
                    fixed_files.append(file)
            else:
                fixed_files.append(file)
        
        return len(fixes_applied) > 0, fixed_files, fixes_applied
    
    def _auto_fix_file(self, content: str, issues: List[ValidationIssue]) -> Tuple[str, List[str]]:
        """Auto-fix issues in a single file"""
        fixes = []
        
        # Simple replacements
        replacements = {
            '.foregroundColor(': '.foregroundStyle(',
            'NavigationView {': 'NavigationStack {',
            '.bounce': '.animation(.spring())',
            '.symbolEffect(': '// .symbolEffect( // iOS 17+ only\n            .scaleEffect('
        }
        
        for old, new in replacements.items():
            if old in content:
                content = content.replace(old, new)
                fixes.append(f"Replaced {old} with {new}")
        
        # Remove invalid imports
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if re.match(r'^\s*import\s+(Components|Views|Models|ViewModels|Services)\b', line):
                fixes.append(f"Removed invalid import: {line.strip()}")
                continue
            new_lines.append(line)
        
        if new_lines != lines:
            content = '\n'.join(new_lines)
        
        return content, fixes