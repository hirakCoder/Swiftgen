"""
Comprehensive Code Validator
Validates Swift/SwiftUI code for all common issues that cause compilation errors
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class CodeIssue:
    """Represents a code issue found during validation"""
    severity: str  # "error", "warning"
    category: str  # "reserved_type", "deprecated_api", "syntax", etc.
    file_path: str
    line_number: Optional[int]
    message: str
    fix: Optional[str] = None

class ComprehensiveCodeValidator:
    """Validates Swift/SwiftUI code for all common issues"""
    
    def __init__(self, ios_target: str = "16.0"):
        self.ios_target = ios_target
        self.ios_major = int(ios_target.split('.')[0])
        
        # Reserved types that cause "reference to generic type requires arguments" errors
        self.reserved_generic_types = {
            'Task': 'TodoItem or AppTask',  # Task<Success, Failure>
            'Result': 'AppResult',           # Result<Success, Failure>
            'Publisher': 'AppPublisher',     # Publisher<Output, Failure>
            'AsyncSequence': 'AppAsyncSequence',
            'AsyncStream': 'AppAsyncStream'
        }
        
        # Common Foundation/Swift types that shouldn't be redefined
        self.reserved_foundation_types = {
            'Data': 'AppData or ModelData',
            'URL': 'AppURL or LinkURL', 
            'Date': 'AppDate or EventDate',
            'UUID': 'Identifier or AppID',
            'Timer': 'AppTimer',
            'Bundle': 'AppBundle',
            'Notification': 'AppNotification',
            'Index': 'AppIndex',
            'Range': 'AppRange'
        }
        
        # SwiftUI/UIKit types
        self.reserved_ui_types = {
            'View': 'AppView or CustomView',
            'Text': 'AppText or Label',
            'Image': 'AppImage or Picture', 
            'Button': 'AppButton',
            'Color': 'AppColor or Theme',
            'Font': 'AppFont',
            'Animation': 'AppAnimation',
            'Transition': 'AppTransition',
            'Shape': 'AppShape',
            'Path': 'AppPath'
        }
        
        # Swift language reserved words
        self.swift_keywords = {
            'Type', 'Protocol', 'Any', 'AnyObject', 'Self', 'nil',
            'true', 'false', 'is', 'as', 'throws', 'throw', 'rethrows',
            'defer', 'where', 'case', 'break', 'continue', 'return',
            'if', 'else', 'for', 'while', 'repeat', 'switch', 'default',
            'func', 'var', 'let', 'class', 'struct', 'enum', 'protocol',
            'init', 'deinit', 'extension', 'subscript', 'operator',
            'typealias', 'associatedtype', 'inout', 'internal', 'private',
            'public', 'static', 'final', 'lazy', 'optional', 'required',
            'weak', 'unowned', 'guard', 'catch', 'try', 'super', 'self'
        }
        
        # Common naming conflicts
        self.common_conflicts = {
            'State': 'AppState or ViewState',  # Conflicts with @State
            'Action': 'AppAction or UserAction',
            'Error': 'AppError',  # Conflicts with Error protocol
            'Never': 'AppNever',  # Never type
            'Void': 'AppVoid',    # Void type
            'Optional': 'AppOptional'  # Optional type
        }
        
        # Deprecated APIs by iOS version
        self.deprecated_apis = {
            16: {
                'NavigationView': 'NavigationStack',
                '.foregroundColor(': '.foregroundStyle(',
                '.accentColor(': '.tint(',
                'UIApplication.shared.windows': 'Use window scene instead'
            },
            17: {
                '.onChange(of:': '.onChange(of:initial:',  # New signature
                'NavigationView': 'NavigationStack or NavigationSplitView'
            }
        }
        
        # iOS version-specific features
        self.ios_version_features = {
            17: [
                '@Observable',
                '.symbolEffect(',
                '.scrollBounceBehavior(',
                '.contentTransition(',
                '.bounce',
                'withObservationTracking'
            ],
            18: [
                '.handGestureShortcut(',
                '.meshGradient(',
                'MeshGradient'
            ]
        }
        
        # Common syntax errors
        self.syntax_patterns = {
            # Missing imports
            r'@Published\s+var': 'Needs: import Combine',
            r'ObservableObject': 'Needs: import Combine',
            r'\bTask\s*\{': 'Needs: import Foundation',
            
            # onChange signatures
            r'\.onChange\(of:\s*\w+\)\s*\{[^}]*\}': 'iOS 17+ onChange needs initial parameter',
            
            # Missing @MainActor
            r'class\s+\w+ViewModel\s*:': 'ViewModels should be @MainActor',
            
            # Incorrect async usage
            r'Task\s*\{[^}]*DispatchQueue\.main': 'Use @MainActor instead of DispatchQueue.main in Task'
        }
    
    def validate_files(self, files: List[Dict[str, str]]) -> List[CodeIssue]:
        """Validate all files and return issues"""
        all_issues = []
        
        for file in files:
            file_path = file.get('path', '')
            content = file.get('content', '')
            
            # Skip empty files
            if not content or len(content.strip()) < 10:
                continue
            
            issues = self.validate_file(file_path, content)
            all_issues.extend(issues)
        
        return all_issues
    
    def validate_file(self, file_path: str, content: str) -> List[CodeIssue]:
        """Validate a single file"""
        issues = []
        
        # Check reserved type definitions
        issues.extend(self._check_reserved_types(file_path, content))
        
        # Check deprecated APIs
        issues.extend(self._check_deprecated_apis(file_path, content))
        
        # Check iOS version features
        issues.extend(self._check_ios_features(file_path, content))
        
        # Check syntax issues
        issues.extend(self._check_syntax_issues(file_path, content))
        
        # Check missing imports
        issues.extend(self._check_missing_imports(file_path, content))
        
        # Check MainActor issues
        issues.extend(self._check_main_actor_issues(file_path, content))
        
        return issues
    
    def _check_reserved_types(self, file_path: str, content: str) -> List[CodeIssue]:
        """Check for reserved type definitions"""
        issues = []
        
        # Check generic types
        for reserved, suggestion in self.reserved_generic_types.items():
            pattern = rf'\b(struct|class|enum)\s+{reserved}\b'
            if re.search(pattern, content):
                issues.append(CodeIssue(
                    severity='error',
                    category='reserved_type',
                    file_path=file_path,
                    line_number=None,
                    message=f"Cannot use '{reserved}' as type name (it's a generic type)",
                    fix=f"Use {suggestion} instead"
                ))
        
        # Check Foundation types
        for reserved, suggestion in self.reserved_foundation_types.items():
            pattern = rf'\b(struct|class|enum)\s+{reserved}\b'
            if re.search(pattern, content):
                issues.append(CodeIssue(
                    severity='error',
                    category='reserved_type',
                    file_path=file_path,
                    line_number=None,
                    message=f"Cannot redefine Foundation type '{reserved}'",
                    fix=f"Use {suggestion} instead"
                ))
        
        # Check UI types
        for reserved, suggestion in self.reserved_ui_types.items():
            pattern = rf'\b(struct|class|enum)\s+{reserved}\b'
            if re.search(pattern, content):
                issues.append(CodeIssue(
                    severity='error',
                    category='reserved_type',
                    file_path=file_path,
                    line_number=None,
                    message=f"Cannot redefine SwiftUI type '{reserved}'",
                    fix=f"Use {suggestion} instead"
                ))
        
        # Check common conflicts
        for reserved, suggestion in self.common_conflicts.items():
            pattern = rf'\b(struct|class|enum)\s+{reserved}\b'
            if re.search(pattern, content):
                issues.append(CodeIssue(
                    severity='error',
                    category='reserved_type',
                    file_path=file_path,
                    line_number=None,
                    message=f"'{reserved}' conflicts with Swift type",
                    fix=f"Use {suggestion} instead"
                ))
        
        return issues
    
    def _check_deprecated_apis(self, file_path: str, content: str) -> List[CodeIssue]:
        """Check for deprecated APIs"""
        issues = []
        
        for ios_version, deprecated in self.deprecated_apis.items():
            if self.ios_major >= ios_version:
                for old_api, new_api in deprecated.items():
                    if old_api in content:
                        issues.append(CodeIssue(
                            severity='warning',
                            category='deprecated_api',
                            file_path=file_path,
                            line_number=None,
                            message=f"'{old_api}' is deprecated in iOS {ios_version}+",
                            fix=f"Use {new_api}"
                        ))
        
        return issues
    
    def _check_ios_features(self, file_path: str, content: str) -> List[CodeIssue]:
        """Check for iOS version-specific features"""
        issues = []
        
        for ios_version, features in self.ios_version_features.items():
            if self.ios_major < ios_version:
                for feature in features:
                    if feature in content:
                        issues.append(CodeIssue(
                            severity='error',
                            category='ios_version',
                            file_path=file_path,
                            line_number=None,
                            message=f"'{feature}' requires iOS {ios_version}+, but target is iOS {self.ios_target}",
                            fix=f"Remove {feature} or increase deployment target"
                        ))
        
        return issues
    
    def _check_syntax_issues(self, file_path: str, content: str) -> List[CodeIssue]:
        """Check for common syntax issues"""
        issues = []
        
        for pattern, message in self.syntax_patterns.items():
            if re.search(pattern, content):
                # Determine the category based on the message
                category = 'syntax'
                severity = 'warning'
                fix = None
                
                # MainActor related issues
                if '@MainActor' in message or 'MainActor' in message:
                    category = 'main_actor'
                    severity = 'error'  # MainActor issues can cause build errors
                    if 'ViewModel' in message:
                        fix = 'Add @MainActor to ViewModel class'
                
                issues.append(CodeIssue(
                    severity=severity,
                    category=category,
                    file_path=file_path,
                    line_number=None,
                    message=message,
                    fix=fix
                ))
        
        return issues
    
    def _check_missing_imports(self, file_path: str, content: str) -> List[CodeIssue]:
        """Check for missing imports"""
        issues = []
        
        # Check SwiftUI
        needs_swiftui = any(keyword in content for keyword in [
            'View', '@State', '@Binding', '@Published', 'VStack', 'HStack',
            'NavigationStack', 'NavigationView', 'List', 'ForEach'
        ])
        
        if needs_swiftui and 'import SwiftUI' not in content:
            issues.append(CodeIssue(
                severity='error',
                category='missing_import',
                file_path=file_path,
                line_number=None,
                message='Missing import SwiftUI',
                fix='Add: import SwiftUI'
            ))
        
        # Check Combine
        needs_combine = any(keyword in content for keyword in [
            '@Published', 'ObservableObject', 'PassthroughSubject'
        ])
        
        if needs_combine and 'import Combine' not in content:
            issues.append(CodeIssue(
                severity='error', 
                category='missing_import',
                file_path=file_path,
                line_number=None,
                message='Missing import Combine',
                fix='Add: import Combine'
            ))
        
        return issues
    
    def _check_main_actor_issues(self, file_path: str, content: str) -> List[CodeIssue]:
        """Check for MainActor isolation issues"""
        issues = []
        
        # Check ViewModels without @MainActor
        vm_pattern = r'class\s+(\w+ViewModel)\s*:\s*ObservableObject'
        for match in re.finditer(vm_pattern, content):
            class_name = match.group(1)
            # Check if @MainActor is present before this class
            class_start = match.start()
            prefix = content[max(0, class_start-100):class_start]
            if '@MainActor' not in prefix:
                issues.append(CodeIssue(
                    severity='error',
                    category='main_actor',
                    file_path=file_path,
                    line_number=None,
                    message=f"ViewModel '{class_name}' should be marked with @MainActor for UI updates",
                    fix='Add @MainActor before class declaration'
                ))
        
        # Check for Task with UI updates not using MainActor
        task_ui_pattern = r'Task\s*\{[^}]*?(@Published|\.text\s*=|\.isEnabled\s*=|\.opacity\s*=)[^}]*?\}'
        if re.search(task_ui_pattern, content, re.DOTALL):
            # Check if MainActor is used
            if '@MainActor' not in content and 'MainActor.run' not in content:
                issues.append(CodeIssue(
                    severity='error',
                    category='main_actor',
                    file_path=file_path,
                    line_number=None,
                    message='Task contains UI updates but lacks MainActor isolation',
                    fix='Add @MainActor annotation or use MainActor.run'
                ))
        
        # Check for async functions updating UI without MainActor
        async_ui_pattern = r'func\s+\w+\s*\([^)]*\)\s*async[^{]*\{[^}]*?(@Published|\.text\s*=|\.isEnabled\s*=)[^}]*?\}'
        for match in re.finditer(async_ui_pattern, content, re.DOTALL):
            func_text = match.group(0)
            if '@MainActor' not in func_text:
                issues.append(CodeIssue(
                    severity='error',
                    category='main_actor',
                    file_path=file_path,
                    line_number=None,
                    message='Async function updates UI without @MainActor',
                    fix='Add @MainActor to async function that updates UI'
                ))
        
        return issues
    
    def fix_issues(self, files: List[Dict[str, str]], issues: List[CodeIssue]) -> List[Dict[str, str]]:
        """Attempt to fix issues automatically"""
        fixed_files = []
        
        for file in files:
            content = file.get('content', '')
            path = file.get('path', '')
            
            # Apply fixes for this file
            file_issues = [i for i in issues if i.file_path == path]
            
            for issue in file_issues:
                if issue.category == 'reserved_type':
                    content = self._fix_reserved_type(content, issue)
                elif issue.category == 'deprecated_api':
                    content = self._fix_deprecated_api(content, issue)
                elif issue.category == 'missing_import':
                    content = self._fix_missing_import(content, issue)
                elif issue.category == 'main_actor':
                    content = self._fix_main_actor(content, issue)
            
            fixed_files.append({
                'path': path,
                'content': content
            })
        
        return fixed_files
    
    def _fix_reserved_type(self, content: str, issue: CodeIssue) -> str:
        """Fix reserved type issue"""
        # Extract the reserved type and suggestion from the message
        if "'" in issue.message:
            reserved = issue.message.split("'")[1]
            
            # Find the appropriate replacement
            replacement = None
            for types_dict in [self.reserved_generic_types, self.reserved_foundation_types, 
                             self.reserved_ui_types, self.common_conflicts]:
                if reserved in types_dict:
                    suggestion = types_dict[reserved]
                    # Take the first suggestion if multiple
                    replacement = suggestion.split(' or ')[0]
                    break
            
            if replacement:
                # Replace type definitions
                content = re.sub(rf'\b(struct|class|enum)\s+{reserved}\b', 
                               rf'\1 {replacement}', content)
                
                # Replace type usage
                content = re.sub(rf':\s*{reserved}\b', f': {replacement}', content)
                content = re.sub(rf':\s*\[{reserved}\]', f': [{replacement}]', content)
                content = re.sub(rf'<{reserved}>', f'<{replacement}>', content)
                content = re.sub(rf'\[{reserved}\]', f'[{replacement}]', content)
        
        return content
    
    def _fix_deprecated_api(self, content: str, issue: CodeIssue) -> str:
        """Fix deprecated API usage"""
        # Simple replacements based on known deprecations
        if 'NavigationView' in issue.message:
            content = content.replace('NavigationView', 'NavigationStack')
        elif 'foregroundColor' in issue.message:
            content = content.replace('.foregroundColor(', '.foregroundStyle(')
        elif 'accentColor' in issue.message:
            content = content.replace('.accentColor(', '.tint(')
        
        return content
    
    def _fix_missing_import(self, content: str, issue: CodeIssue) -> str:
        """Fix missing import"""
        if issue.fix and 'Add:' in issue.fix:
            import_statement = issue.fix.replace('Add: ', '')
            if import_statement not in content:
                # Add import at the beginning
                content = f"{import_statement}\n{content}"
        
        return content
    
    def _fix_main_actor(self, content: str, issue: CodeIssue) -> str:
        """Fix MainActor issues"""
        # Fix ViewModels that need @MainActor
        if 'ViewModel' in issue.message and '@MainActor' in issue.message:
            # First check if @MainActor already exists to avoid duplicates
            if '@MainActor' not in content:
                # Find ViewModel classes without @MainActor
                pattern = r'(class\s+\w+ViewModel\s*:\s*ObservableObject)'
                replacement = r'@MainActor\n\1'
                content = re.sub(pattern, replacement, content)
        
        # Fix duplicate @MainActor attributes
        if 'multiple global actor attributes' in issue.message:
            # Remove duplicate @MainActor
            content = re.sub(r'(@MainActor\s*\n\s*)+@MainActor', '@MainActor', content)
            # Also handle inline duplicates
            content = re.sub(r'@MainActor\s+@MainActor', '@MainActor', content)
        
        # Fix Task blocks using DispatchQueue.main
        if 'Task' in issue.message and 'DispatchQueue.main' in issue.message:
            # Replace DispatchQueue.main.async with MainActor.run
            content = re.sub(
                r'DispatchQueue\.main\.async\s*\{',
                r'await MainActor.run {',
                content
            )
            
            # Replace Task { DispatchQueue.main patterns
            content = re.sub(
                r'Task\s*\{([^}]*?)DispatchQueue\.main\.async\s*\{',
                r'Task { @MainActor in\1',
                content
            )
        
        # Fix UI updates not marked with @MainActor
        if 'UI update' in issue.message:
            # Add @MainActor to methods that update @Published properties
            pattern = r'(func\s+\w+[^{]*\{[^}]*@Published[^}]*\})'
            content = re.sub(
                pattern,
                r'@MainActor \1',
                content,
                flags=re.DOTALL
            )
        
        return content