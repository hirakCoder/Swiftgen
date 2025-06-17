"""
Self-Healing Generator for SwiftGen AI - FIXED VERSION
Implements predictive generation and automatic error recovery
"""

import os
import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import asyncio

class SelfHealingGenerator:
    """Generator that learns from failures and self-heals - FIXED VERSION"""

    def __init__(self, rag_kb=None, llm_service=None):
        self.rag_kb = rag_kb
        self.llm_service = llm_service
        self.max_attempts = 3

        # Common failure patterns and their fixes
        self.known_failure_patterns = {
            "phantom_dependency": {
                "pattern": r"cannot find.*Service.*in scope",
                "fix": self._fix_phantom_dependencies,
                "description": "External service dependencies that don't exist"
            },
            "reserved_type": {
                "pattern": r"struct\s+(Task|State|Action)\b",
                "fix": self._fix_reserved_types,
                "description": "Using Swift reserved types"
            },
            "missing_import": {
                "pattern": r"cannot find type.*in scope|Missing.*import",
                "fix": self._fix_missing_imports,
                "description": "Missing required imports"
            },
            "string_literal": {
                "pattern": r"unterminated string literal",
                "fix": self._fix_string_literals,
                "description": "String syntax errors"
            },
            "environment_issue": {
                "pattern": r"@Environment.*presentationMode",
                "fix": self._fix_environment_usage,
                "description": "Deprecated environment usage"
            }
        }

        # Track success patterns
        self.success_patterns = []
        self.failure_history = []

    async def generate_with_healing(self, description: str, app_name: str) -> Dict:
        """Generate code with automatic healing capabilities"""

        print(f"[SELF-HEALING] Starting generation for: {description}")

        # Step 1: Learn from similar successful apps
        working_patterns = await self._find_working_patterns(description)

        # Step 2: Predict potential issues
        potential_issues = self._predict_issues(description, working_patterns)

        # Step 3: Build constraints to prevent issues
        constraints = self._build_constraints(potential_issues)

        # Step 4: Generate with constraints
        for attempt in range(self.max_attempts):
            print(f"[SELF-HEALING] Generation attempt {attempt + 1}")

            try:
                # Generate code
                if self.llm_service:
                    result = await self.llm_service.generate_ios_app_multi_llm(
                        description=description + "\n\n" + constraints,
                        app_name=app_name
                    )
                else:
                    # Fallback if no LLM service
                    result = self._create_minimal_app(app_name)

                # Validate generated code
                validation_result = self._validate_code(result)

                if validation_result["success"]:
                    print("[SELF-HEALING] ✓ Generated valid code on first try")
                    self._record_success(description, result)
                    return result

                # Apply healing strategies
                print(f"[SELF-HEALING] Validation failed: {validation_result['errors']}")
                healed_result = await self._apply_healing(result, validation_result)

                if healed_result:
                    print("[SELF-HEALING] ✓ Successfully healed code")
                    self._record_healing_success(description, result, healed_result, validation_result)
                    return healed_result

            except Exception as e:
                print(f"[SELF-HEALING] Attempt {attempt + 1} failed: {str(e)}")

        # All attempts failed - return minimal working app
        print("[SELF-HEALING] All attempts failed, returning minimal app")
        return self._create_minimal_app(app_name)

    async def _find_working_patterns(self, description: str) -> List[Dict]:
        """Find similar apps that worked successfully"""

        if not self.rag_kb:
            return []

        # Search for similar successful apps
        similar_apps = self.rag_kb.search(description, k=5)

        working_patterns = []
        for app in similar_apps:
            # Only use successful patterns
            if app.get('severity') == 'info' and 'success' in app.get('tags', []):
                working_patterns.append({
                    'description': app.get('title', ''),
                    'patterns': self._extract_patterns_from_content(app.get('content', ''))
                })

        return working_patterns

    def _extract_patterns_from_content(self, content: str) -> Dict:
        """Extract useful patterns from successful app content"""

        patterns = {
            'uses_stateobject': '@StateObject' in content,
            'uses_observable': 'ObservableObject' in content or '@Observable' in content,
            'uses_navigation_stack': 'NavigationStack' in content,
            'file_count': content.count('struct') + content.count('class'),
            'has_view_model': 'ViewModel' in content,
            'is_simple_app': content.count('struct') < 5
        }

        return patterns

    def _predict_issues(self, description: str, working_patterns: List[Dict]) -> List[str]:
        """Predict potential issues based on description and patterns"""

        predicted_issues = []

        # Analyze description for complexity indicators
        description_lower = description.lower()

        # Check for indicators that might lead to phantom dependencies
        if any(word in description_lower for word in ['api', 'service', 'fetch', 'load', 'download']):
            predicted_issues.append("phantom_dependency")

        # Check for task-related functionality
        if any(word in description_lower for word in ['task', 'todo', 'list', 'item']):
            predicted_issues.append("reserved_type")

        # Check for navigation needs
        if any(word in description_lower for word in ['navigate', 'page', 'screen', 'view']):
            predicted_issues.append("environment_issue")

        # Always predict missing imports - this is our main issue
        predicted_issues.append("missing_import")

        # Learn from past failures
        for failure in self.failure_history[-10:]:  # Last 10 failures
            if failure['issue'] not in predicted_issues:
                predicted_issues.append(failure['issue'])

        return predicted_issues

    def _build_constraints(self, predicted_issues: List[str]) -> str:
        """Build constraint instructions based on predicted issues"""

        constraints = ["ADDITIONAL CONSTRAINTS TO PREVENT ERRORS:"]

        if "phantom_dependency" in predicted_issues:
            constraints.append("- DO NOT create any Service classes or external dependencies")
            constraints.append("- Implement all functionality inline with @State and @StateObject")

        if "reserved_type" in predicted_issues:
            constraints.append("- Use 'TodoItem' instead of 'Task' for any task-related structs")
            constraints.append("- Use 'AppState' instead of 'State' for state management")

        if "environment_issue" in predicted_issues:
            constraints.append("- Use @Environment(\\.dismiss) for iOS 16+ dismissal")
            constraints.append("- Use NavigationStack instead of NavigationView")

        # CRITICAL: Always add import constraints
        if "missing_import" in predicted_issues:
            constraints.append("- ALWAYS start EVERY Swift file with necessary imports")
            constraints.append("- If using ANY SwiftUI components, start with 'import SwiftUI'")
            constraints.append("- If using ObservableObject or @Published, also import Combine")
            constraints.append("- ViewModels that use SwiftUI types MUST import SwiftUI")

        return "\n".join(constraints)

    def _validate_code(self, result: Dict) -> Dict:
        """Validate generated code for common issues"""

        validation_result = {
            "success": True,
            "errors": [],
            "warnings": []
        }

        if not result or "files" not in result:
            validation_result["success"] = False
            validation_result["errors"].append({
                "type": "no_files",
                "description": "No files generated"
            })
            return validation_result

        # Check each file
        for file in result.get("files", []):
            content = file.get("content", "")
            path = file.get("path", "")

            # CRITICAL: Check for missing imports FIRST
            missing_imports = self._check_missing_imports(content, path)
            if missing_imports:
                validation_result["success"] = False
                for imp in missing_imports:
                    validation_result["errors"].append({
                        "type": "missing_import",
                        "description": f"{path}: Missing {imp} import",
                        "file": path,
                        "missing_import": imp
                    })

            # Check each known failure pattern
            for issue_type, pattern_info in self.known_failure_patterns.items():
                if re.search(pattern_info["pattern"], content):
                    validation_result["success"] = False
                    validation_result["errors"].append({
                        "type": issue_type,
                        "description": pattern_info["description"],
                        "pattern": pattern_info["pattern"],
                        "file": path
                    })

        # Additional validation checks
        if not any("@main" in f.get("content", "") for f in result.get("files", [])):
            validation_result["success"] = False
            validation_result["errors"].append({
                "type": "missing_main",
                "description": "Missing @main app entry point"
            })

        return validation_result

    def _check_missing_imports(self, content: str, path: str) -> List[str]:
        """Check for missing imports in a file"""
        missing_imports = []

        # Check what's needed
        needs_swiftui = any(keyword in content for keyword in [
            'View', 'Text', 'Button', '@State', '@Binding', '@Published',
            '@ObservedObject', '@StateObject', '@Environment', 'VStack', 'HStack',
            'List', 'ForEach', 'NavigationStack', 'NavigationView', 'Sheet',
            'Alert', 'Toggle', 'TextField', 'Image', 'Color', '@Observable',
            'some View', 'body:', '.padding', '.frame', '.foregroundColor',
            'ObservableObject'  # ViewModels often need this
        ])

        # Special check for View protocol conformance
        if re.search(r'struct\s+\w+\s*:\s*View', content):
            needs_swiftui = True

        # Special check for ViewModel files
        if 'ViewModel' in path and ('ObservableObject' in content or '@Published' in content):
            needs_swiftui = True

        needs_foundation = any(keyword in content for keyword in [
            'UUID', 'Date', 'URL', 'Data', 'JSONEncoder', 'JSONDecoder'
        ])

        needs_combine = any(keyword in content for keyword in [
            '@Published', 'ObservableObject', 'PassthroughSubject', 'Cancellable'
        ])

        # Check what's already imported
        if needs_swiftui and 'import SwiftUI' not in content:
            missing_imports.append('SwiftUI')

        if needs_foundation and 'import Foundation' not in content:
            missing_imports.append('Foundation')

        if needs_combine and 'import Combine' not in content:
            missing_imports.append('Combine')

        return missing_imports

    async def _apply_healing(self, result: Dict, validation_result: Dict) -> Optional[Dict]:
        """Apply healing strategies to fix validation errors - FIXED VERSION"""

        if not validation_result.get("errors"):
            return result

        # Create a deep copy of the result
        healed_result = {
            "files": [f.copy() for f in result.get("files", [])],
            "bundle_id": result.get("bundle_id", ""),
            "app_name": result.get("app_name", "App"),
            "features": result.get("features", []),
            "self_healed": True
        }

        # First pass: Apply reserved type fixes to ALL files if any reserved type error exists
        has_reserved_type_error = any(error.get("type") == "reserved_type" for error in validation_result["errors"])
        if has_reserved_type_error:
            print("[SELF-HEALING] Fixing reserved type conflicts in all files")
            for file in healed_result["files"]:
                self._fix_reserved_types(file)

        # Apply fixes for each error
        for error in validation_result["errors"]:
            error_type = error.get("type", "")
            file_path = error.get("file", "")

            # Find the file to fix
            for file in healed_result["files"]:
                if file.get("path", "") == file_path or error_type in ["missing_main", "no_files"]:
                    if error_type in self.known_failure_patterns and error_type != "reserved_type":  # Skip reserved_type as we already fixed it
                        fix_function = self.known_failure_patterns[error_type]["fix"]
                        # Apply fix to specific file
                        fix_function(file)
                    elif error_type == "missing_import":
                        # Special handling for missing imports
                        self._fix_missing_imports(file)

        # Re-validate after healing
        re_validation = self._validate_code(healed_result)

        if re_validation["success"]:
            return healed_result

        # If still failing, try more aggressive healing
        if self.llm_service and hasattr(self.llm_service, '_self_heal_generation'):
            return await self.llm_service._self_heal_generation(
                healed_result,
                [e["description"] for e in re_validation["errors"]],
                healed_result.get("bundle_id", "")
            )

        return None

    def _fix_phantom_dependencies(self, file: Dict) -> None:
        """Fix phantom dependency issues in a specific file"""
        content = file.get("content", "")

        # Remove service imports and dependencies
        content = re.sub(r'import\s+\w+Service\n', '', content)
        content = re.sub(r'private\s+let\s+\w+Service:\s*\w+Service', '', content)
        content = re.sub(r'init\([^)]*Service[^)]*\)', 'init()', content)

        # Replace service calls with inline implementations
        content = re.sub(r'\w+Service\.\w+\([^)]*\)', '[]', content)  # Return empty array
        content = re.sub(r'try\s+await\s+\w+Service\.\w+\([^)]*\)', '[]', content)

        file["content"] = content

    def _fix_reserved_types(self, file: Dict) -> None:
        """Fix reserved type conflicts in a specific file"""
        content = file.get("content", "")
        path = file.get("path", "")
        
        # Log what we're fixing
        if "Task" in content and not "Task<" in content:
            print(f"[SELF-HEALING] Fixing reserved type 'Task' in {path}")

        # First, fix type definitions
        replacements = {
            "struct Task": "struct TodoItem",
            "class Task": "class TodoItem",
            "enum Task": "enum TodoItem",
            "struct State": "struct AppState",
            "class State": "class AppState",
            "struct Action": "struct AppAction",
            "enum Action": "enum AppAction"
        }

        for old, new in replacements.items():
            if old in content:
                content = content.replace(old, new)
                print(f"[SELF-HEALING] Replaced '{old}' with '{new}'")

        # Fix all Task references (more comprehensive)
        # Type annotations
        content = re.sub(r'\bTask\s*:', 'TodoItem:', content)
        content = re.sub(r':\s*Task\b', ': TodoItem', content)
        content = re.sub(r':\s*\[Task\]', ': [TodoItem]', content)
        content = re.sub(r'<Task>', '<TodoItem>', content)
        
        # Array/Collection references
        content = re.sub(r'\[Task\]', '[TodoItem]', content)
        content = re.sub(r'Array<Task>', 'Array<TodoItem>', content)
        
        # Property declarations
        content = re.sub(r'\blet\s+\w+:\s*Task\b', lambda m: m.group(0).replace('Task', 'TodoItem'), content)
        content = re.sub(r'\bvar\s+\w+:\s*Task\b', lambda m: m.group(0).replace('Task', 'TodoItem'), content)
        
        # Function parameters and returns
        content = re.sub(r'\(\s*task:\s*Task\s*\)', '(task: TodoItem)', content)
        content = re.sub(r'->\s*Task\b', '-> TodoItem', content)
        content = re.sub(r'->\s*\[Task\]', '-> [TodoItem]', content)
        
        # ForEach and other SwiftUI constructs
        content = re.sub(r'ForEach\(.*?,\s*id:\s*\\\..*?\)\s*{\s*task\s+in', 
                        lambda m: m.group(0).replace('task in', 'todoItem in'), content)
        
        # Variable names (be careful not to break things)
        content = re.sub(r'\btask\b(?=\s*:)', 'todoItem', content)  # task: before type
        content = re.sub(r'\btasks\b(?=\s*:)', 'todoItems', content)  # tasks: before type

        file["content"] = content

    def _fix_missing_imports(self, file: Dict) -> None:
        """Fix missing import statements in a specific file - CRITICAL FIX"""
        content = file.get("content", "")
        path = file.get("path", "")

        # Check what's needed
        missing_imports = self._check_missing_imports(content, path)

        if missing_imports:
            # Build import statements
            import_statements = []
            for imp in missing_imports:
                import_statements.append(f"import {imp}")

            # Add imports at the beginning of the file
            if import_statements:
                imports_text = '\n'.join(import_statements) + '\n\n'
                # Remove any existing empty lines at the start
                content = content.lstrip()
                file["content"] = imports_text + content

    def _fix_string_literals(self, file: Dict) -> None:
        """Fix string literal issues in a specific file"""
        content = file.get("content", "")

        # Fix single quotes to double quotes
        lines = content.split('\n')
        fixed_lines = []

        for line in lines:
            if not line.strip().startswith('//'):
                line = re.sub(r"'([^']*)'", r'"\1"', line)
            fixed_lines.append(line)

        file["content"] = '\n'.join(fixed_lines)

    def _fix_environment_usage(self, file: Dict) -> None:
        """Fix deprecated environment usage in a specific file"""
        content = file.get("content", "")

        # Fix presentationMode
        content = re.sub(
            r'@Environment\(\\.presentationMode\)\s+var\s+presentationMode',
            '@Environment(\\.dismiss) private var dismiss',
            content
        )
        content = content.replace('presentationMode.wrappedValue.dismiss()', 'dismiss()')

        # Fix NavigationView
        content = content.replace('NavigationView', 'NavigationStack')

        file["content"] = content

    def _create_minimal_app(self, app_name: str) -> Dict:
        """Create a minimal working app as last resort"""

        safe_name = app_name.replace(" ", "")

        return {
            "app_name": app_name,
            "bundle_id": f"com.swiftgen.{safe_name.lower()[:20]}",
            "files": [
                {
                    "path": "Sources/App.swift",
                    "content": f"""import SwiftUI

@main
struct {safe_name}App: App {{
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
    @State private var welcomeText = "Welcome to {app_name}!"
    
    var body: some View {{
        NavigationStack {{
            VStack(spacing: 20) {{
                Image(systemName: "checkmark.circle.fill")
                    .font(.system(size: 60))
                    .foregroundColor(.green)
                
                Text(welcomeText)
                    .font(.title)
                    .multilineTextAlignment(.center)
                
                Button("Get Started") {{
                    welcomeText = "Let's build something amazing!"
                }}
                .buttonStyle(.borderedProminent)
            }}
            .padding()
            .navigationTitle("{app_name}")
        }}
    }}
}}"""
                }
            ],
            "features": ["Minimal working app", "Self-healed"],
            "generated_by_llm": "self-healing"
        }

    def _record_success(self, description: str, result: Dict):
        """Record successful generation for learning"""

        self.success_patterns.append({
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "file_count": len(result.get("files", [])),
            "features": result.get("features", [])
        })

        # Keep only last 100 successes
        if len(self.success_patterns) > 100:
            self.success_patterns = self.success_patterns[-100:]

    def _record_healing_success(self, description: str, original: Dict, healed: Dict, validation: Dict):
        """Record successful healing for learning"""

        healing_record = {
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "errors_fixed": [e["type"] for e in validation.get("errors", [])],
            "healing_applied": True
        }

        # Update RAG knowledge base if available
        if self.rag_kb:
            for error in validation.get("errors", []):
                error_type = error["type"]
                self.rag_kb.add_learned_solution(
                    f"Fixed {error_type} in {description}",
                    f"Applied {error_type} fix successfully",
                    True
                )

    def _record_failure(self, description: str, issue: str):
        """Record failure for future prevention"""

        self.failure_history.append({
            "description": description,
            "issue": issue,
            "timestamp": datetime.now().isoformat()
        })

        # Keep only last 50 failures
        if len(self.failure_history) > 50:
            self.failure_history = self.failure_history[-50:]