#!/usr/bin/env python3
"""
Emergency Generation Validator - Prevents Broken Code from Reaching Build
CRITICAL: This validates LLM output BEFORE project creation to prevent build failures
"""

import re
import os
from typing import Dict, List, Tuple, Optional
import json


class EmergencyGenerationValidator:
    """Validates LLM-generated code to prevent broken apps from being created"""
    
    def __init__(self):
        self.critical_errors = []
        self.warnings = []
        
    def validate_generated_code(self, generated_code: Dict) -> Tuple[bool, List[str], List[str]]:
        """
        Validate generated code for critical issues that WILL cause build failures
        Returns: (is_valid, critical_errors, warnings)
        """
        self.critical_errors = []
        self.warnings = []
        
        if not generated_code or "files" not in generated_code:
            self.critical_errors.append("No files generated")
            return False, self.critical_errors, self.warnings
            
        files = generated_code["files"]
        
        # 1. Check for duplicate files/classes
        self._check_duplicate_files(files)
        
        # 2. Check for missing dependencies
        self._check_missing_dependencies(files)
        
        # 3. Check for broken initializers
        self._check_broken_initializers(files)
        
        # 4. Check for complex/broken architecture
        self._check_overengineered_architecture(files)
        
        # 5. Check for missing imports
        self._check_missing_imports(files)
        
        # 6. Check for syntax issues
        self._check_syntax_issues(files)
        
        is_valid = len(self.critical_errors) == 0
        return is_valid, self.critical_errors, self.warnings
        
    def _check_duplicate_files(self, files: List[Dict]):
        """Check for duplicate class definitions"""
        class_names = {}
        file_paths = set()
        
        for file in files:
            path = file.get("path", "")
            content = file.get("content", "")
            
            # Check duplicate paths
            if path in file_paths:
                self.critical_errors.append(f"Duplicate file path: {path}")
            file_paths.add(path)
            
            # Extract class/struct names
            class_matches = re.findall(r'(?:class|struct)\s+(\w+)', content)
            for class_name in class_matches:
                if class_name in class_names:
                    self.critical_errors.append(f"Duplicate class/struct: {class_name} found in {path} and {class_names[class_name]}")
                else:
                    class_names[class_name] = path
                    
    def _check_missing_dependencies(self, files: List[Dict]):
        """Check for missing dependencies and undefined types"""
        # Find all defined types
        defined_types = set()
        used_types = set()
        
        for file in files:
            content = file.get("content", "")
            
            # Find defined classes/structs/protocols
            defined_matches = re.findall(r'(?:class|struct|protocol)\s+(\w+)', content)
            defined_types.update(defined_matches)
            
            # Find used types (rough heuristic)
            # Look for type usage patterns
            used_matches = re.findall(r':\s*(\w+)(?:Protocol)?', content)  # Inheritance/conformance
            used_matches += re.findall(r'let\s+\w+:\s*(\w+)', content)    # Property types
            used_matches += re.findall(r'var\s+\w+:\s*(\w+)', content)    # Property types
            used_matches += re.findall(r'(\w+)\(\)', content)             # Initializers
            
            used_types.update(used_matches)
            
        # Check for missing dependencies
        swift_built_ins = {'String', 'Int', 'Double', 'Bool', 'Date', 'UUID', 'Data', 'URL', 'ObservableObject', 'Published'}
        swiftui_types = {'View', 'Text', 'Button', 'VStack', 'HStack', 'NavigationStack', 'Color', 'Image', 'List', 'Form'}
        foundation_types = {'UserDefaults', 'Calendar', 'DateFormatter', 'Timer', 'JSONEncoder', 'JSONDecoder'}
        
        all_known_types = swift_built_ins | swiftui_types | foundation_types | defined_types
        
        for used_type in used_types:
            if used_type and used_type[0].isupper() and used_type not in all_known_types:
                # Filter out common false positives
                if used_type not in ['Protocol', 'Impl', 'Container', 'Manager', 'Service']:
                    self.critical_errors.append(f"Undefined type used: {used_type}")
                    
    def _check_broken_initializers(self, files: List[Dict]):
        """Check for broken initializer patterns"""
        for file in files:
            content = file.get("content", "")
            path = file.get("path", "")
            
            # Check for complex dependency injection that always breaks
            if '@Dependency(' in content:
                self.critical_errors.append(f"Complex dependency injection pattern in {path} - will fail")
                
            # Check for initializers with unavailable dependencies
            init_matches = re.findall(r'init\([^)]*(\w+Repository)[^)]*\)', content)
            for dep in init_matches:
                if not any(dep in f.get("content", "") for f in files if "Repository" in f.get("path", "")):
                    self.critical_errors.append(f"Initializer depends on undefined {dep}")
                    
    def _check_overengineered_architecture(self, files: List[Dict]):
        """Check for overengineered patterns that often break"""
        architecture_patterns = 0
        
        for file in files:
            content = file.get("content", "")
            path = file.get("path", "")
            
            # Count complex patterns
            if "Protocol" in content and "Impl" in content:
                architecture_patterns += 1
            if "DependencyContainer" in content:
                architecture_patterns += 1
            if "@Dependency" in content:
                architecture_patterns += 1
            if "Repository" in path and "Protocol" in path:
                architecture_patterns += 1
                
        if architecture_patterns > 3:
            self.critical_errors.append("Overengineered architecture - too many abstraction layers will cause build failures")
            
    def _check_missing_imports(self, files: List[Dict]):
        """Check for missing imports"""
        for file in files:
            content = file.get("content", "")
            path = file.get("path", "")
            
            # Check for SwiftUI usage without import
            swiftui_keywords = ['View', 'Text', 'Button', 'VStack', 'HStack', 'NavigationStack', '@State', '@Binding']
            if any(keyword in content for keyword in swiftui_keywords) and 'import SwiftUI' not in content:
                self.critical_errors.append(f"Missing 'import SwiftUI' in {path}")
                
            # Check for Foundation usage without import
            foundation_keywords = ['ObservableObject', '@Published', 'UUID', 'Date', 'UserDefaults']
            if any(keyword in content for keyword in foundation_keywords) and 'import Foundation' not in content:
                self.critical_errors.append(f"Missing 'import Foundation' in {path}")
                
    def _check_syntax_issues(self, files: List[Dict]):
        """Check for obvious syntax issues"""
        for file in files:
            content = file.get("content", "")
            path = file.get("path", "")
            
            # Check brace balance
            open_braces = content.count('{')
            close_braces = content.count('}')
            if open_braces != close_braces:
                self.critical_errors.append(f"Unbalanced braces in {path}: {open_braces} open, {close_braces} close")
                
            # Check for single quotes (Swift uses double quotes)
            if "'" in content and not content.count("'") == content.count("\\'"):
                self.warnings.append(f"Single quotes detected in {path} - should use double quotes")
                
    def fix_critical_issues(self, generated_code: Dict) -> Dict:
        """Attempt to fix critical issues automatically"""
        if not generated_code or "files" not in generated_code:
            return self._create_simple_working_app(generated_code.get("app_name", "MyApp"))
            
        files = generated_code["files"]
        
        # Remove duplicate files
        files = self._remove_duplicate_files(files)
        
        # Simplify overengineered architecture
        files = self._simplify_architecture(files)
        
        # Fix missing imports
        files = self._fix_missing_imports(files)
        
        # Fix syntax issues
        files = self._fix_syntax_issues(files)
        
        generated_code["files"] = files
        return generated_code
        
    def _remove_duplicate_files(self, files: List[Dict]) -> List[Dict]:
        """Remove duplicate files and classes"""
        seen_paths = set()
        seen_filenames = set()
        seen_classes = set()
        cleaned_files = []
        
        for file in files:
            path = file.get("path", "")
            content = file.get("content", "")
            
            # Extract filename from path
            filename = path.split('/')[-1] if '/' in path else path
            
            # Skip duplicate paths
            if path in seen_paths:
                print(f"[VALIDATOR] Skipping duplicate path: {path}")
                continue
                
            # Skip duplicate filenames (critical fix)
            if filename in seen_filenames:
                print(f"[VALIDATOR] Skipping duplicate filename: {filename} at {path}")
                continue
                
            # Check for duplicate classes
            class_matches = re.findall(r'(?:class|struct)\s+(\w+)', content)
            has_duplicate_class = any(class_name in seen_classes for class_name in class_matches)
            
            if not has_duplicate_class:
                seen_paths.add(path)
                seen_filenames.add(filename)
                seen_classes.update(class_matches)
                cleaned_files.append(file)
            else:
                print(f"[VALIDATOR] Skipping file with duplicate class: {path}")
                
        return cleaned_files
        
    def _simplify_architecture(self, files: List[Dict]) -> List[Dict]:
        """Simplify overengineered architecture"""
        simplified_files = []
        
        for file in files:
            content = file.get("content", "")
            path = file.get("path", "")
            
            # Skip overly complex architecture files
            if any(pattern in path.lower() for pattern in ["dependency", "container", "protocol"]):
                if "Architecture" in path or "DependencyContainer" in content:
                    continue  # Skip these complex files
                    
            # Simplify ViewModels with complex dependencies
            if "ViewModel" in path and ("@Dependency" in content or "DependencyContainer" in content):
                content = self._simplify_viewmodel(content)
                
            simplified_files.append({
                "path": path,
                "content": content
            })
            
        return simplified_files
        
    def _simplify_viewmodel(self, content: str) -> str:
        """Simplify a ViewModel by removing complex dependencies"""
        # Remove @Dependency lines
        content = re.sub(r'@Dependency\([^)]+\)[^\\n]*\\n?', '', content)
        
        # Remove complex repository dependencies
        content = re.sub(r'private let repository: [^\\n]+\\n', '', content)
        content = re.sub(r'init\([^)]*Repository[^)]*\) {[^}]*}', '', content, flags=re.DOTALL)
        
        # Remove repository calls and replace with simple implementations
        content = re.sub(r'repository\\.\\w+\\([^)]*\\)', '// Simple implementation', content)
        
        return content
        
    def _fix_missing_imports(self, files: List[Dict]) -> List[Dict]:
        """Fix missing imports"""
        for file in files:
            content = file.get("content", "")
            
            imports_needed = []
            
            # Check for SwiftUI
            swiftui_keywords = ['View', 'Text', 'Button', 'VStack', 'HStack', 'NavigationStack', '@State', '@Binding']
            if any(keyword in content for keyword in swiftui_keywords) and 'import SwiftUI' not in content:
                imports_needed.append('import SwiftUI')
                
            # Check for Foundation
            foundation_keywords = ['ObservableObject', '@Published', 'UUID', 'Date', 'UserDefaults']
            if any(keyword in content for keyword in foundation_keywords) and 'import Foundation' not in content:
                imports_needed.append('import Foundation')
                
            if imports_needed:
                import_section = '\\n'.join(imports_needed) + '\\n\\n'
                file["content"] = import_section + content
                
        return files
        
    def _fix_syntax_issues(self, files: List[Dict]) -> List[Dict]:
        """Fix basic syntax issues"""
        for file in files:
            content = file.get("content", "")
            
            # Fix brace balance
            open_braces = content.count('{')
            close_braces = content.count('}')
            if open_braces > close_braces:
                content += '\\n' + '}' * (open_braces - close_braces)
                
            # Fix single quotes
            content = re.sub(r"'([^']*)'", r'"\\1"', content)
            
            file["content"] = content
            
        return files
        
    def _create_simple_working_app(self, app_name: str) -> Dict:
        """Create a guaranteed working simple app as fallback"""
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', app_name.replace(' ', ''))
        if not clean_name:
            clean_name = "MyApp"
            
        return {
            "app_name": app_name,
            "files": [
                {
                    "path": "Sources/App.swift",
                    "content": f"""import SwiftUI

@main
struct {clean_name}App: App {{
    var body: some Scene {{
        WindowGroup {{
            ContentView()
        }}
    }}
}}"""
                },
                {
                    "path": "Sources/ContentView.swift",
                    "content": f"""import SwiftUI

struct ContentView: View {{
    @State private var counter = 0
    
    var body: some View {{
        NavigationStack {{
            VStack(spacing: 30) {{
                Text("{app_name}")
                    .font(.largeTitle.bold())
                    .foregroundColor(.primary)
                
                Text("\\(counter)")
                    .font(.system(size: 80, weight: .bold))
                    .foregroundColor(.blue)
                
                HStack(spacing: 20) {{
                    Button("−") {{
                        counter -= 1
                    }}
                    .buttonStyle(.borderedProminent)
                    .font(.title)
                    
                    Button("+") {{
                        counter += 1
                    }}
                    .buttonStyle(.borderedProminent)
                    .font(.title)
                }}
                
                Button("Reset") {{
                    counter = 0
                }}
                .buttonStyle(.bordered)
            }}
            .padding()
            .navigationTitle("{app_name}")
        }}
    }}
}}

#Preview {{
    ContentView()
}}"""
                }
            ],
            "features": ["Counter functionality", "Clean UI", "Guaranteed to work"]
        }


def validate_and_fix_generation(generated_code: Dict) -> Tuple[Dict, List[str], List[str]]:
    """Main entry point for validation and fixing"""
    validator = EmergencyGenerationValidator()
    
    # Validate first
    is_valid, errors, warnings = validator.validate_generated_code(generated_code)
    
    if not is_valid:
        # Attempt to fix
        print(f"[VALIDATOR] Found {len(errors)} critical errors, attempting fixes...")
        fixed_code = validator.fix_critical_issues(generated_code)
        
        # Validate again
        is_valid_after_fix, remaining_errors, remaining_warnings = validator.validate_generated_code(fixed_code)
        
        if is_valid_after_fix:
            print("[VALIDATOR] Successfully fixed critical errors")
            return fixed_code, [], remaining_warnings
        else:
            print("[VALIDATOR] Could not fix all errors, creating simple fallback app")
            fallback_app = validator._create_simple_working_app(generated_code.get("app_name", "MyApp"))
            return fallback_app, ["Used fallback app due to unfixable errors"], []
    
    return generated_code, [], warnings