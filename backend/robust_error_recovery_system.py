#!/usr/bin/env python3
"""
Robust Multi-Model Error Recovery System for SwiftGen
World-class implementation that combines Claude, OpenAI, and xAI for intelligent error recovery
"""

import os
import re
import json
import asyncio
import logging
import time
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime

# Import AI services
try:
    import openai
    from openai import AsyncOpenAI
except ImportError:
    openai = None
    AsyncOpenAI = None

try:
    import httpx
except ImportError:
    httpx = None


class RobustErrorRecoverySystem:
    """Multi-model error recovery system for Swift build errors"""

    def __init__(self, claude_service=None, openai_key=None, xai_key=None):
        """Initialize with multiple AI services"""
        self.claude_service = claude_service
        self.openai_key = openai_key
        self.xai_key = xai_key

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Track recovery attempts
        self.attempt_count = 0
        self.max_attempts = 3

        # Load error patterns
        self.error_patterns = self._load_error_patterns()

        # Define recovery strategies based on available services
        self.recovery_strategies = self._get_dynamic_recovery_strategies()

        self.logger.info("Robust error recovery system initialized")

    def _load_error_patterns(self):
        """Load error patterns from file or use defaults"""
        patterns_file = os.path.join(os.path.dirname(__file__), 'error_patterns.json')

        if os.path.exists(patterns_file):
            try:
                with open(patterns_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load error patterns: {e}")

        # Return default patterns - comprehensive list
        return {
            "string_literal": {
                "patterns": [
                    "unterminated string literal",
                    "cannot find '\"' in scope",
                    "consecutive statements on a line must be separated"
                ],
                "fixes": [
                    "Use double quotes \" for strings, not single quotes '",
                    "Ensure all string literals are properly terminated",
                    "Check for unescaped quotes within strings"
                ]
            },
            "persistence_controller": {
                "patterns": [
                    "cannot find 'PersistenceController' in scope",
                    "cannot find type 'PersistenceController'",
                    "use of unresolved identifier 'PersistenceController'",
                    "cannot find 'managedObjectContext' in scope"
                ],
                "fixes": [
                    "Remove Core Data references if not needed",
                    "Remove PersistenceController property from App",
                    "Remove .environment(\\.managedObjectContext) modifier"
                ]
            },
            "missing_import": {
                "patterns": [
                    "cannot find type .* in scope",
                    "use of unresolved identifier",
                    "no such module"
                ],
                "fixes": [
                    "Add missing import statements",
                    "import SwiftUI for SwiftUI types",
                    "import Foundation for basic types"
                ]
            },
            "syntax_error": {
                "patterns": [
                    "expected",
                    "invalid redeclaration",
                    "consecutive declarations"
                ],
                "fixes": [
                    "Check for missing braces or parentheses",
                    "Ensure proper Swift syntax",
                    "Remove duplicate declarations"
                ]
            },
            "exhaustive_switch": {
                "patterns": [
                    "switch must be exhaustive",
                    "does not have a member"
                ],
                "fixes": [
                    "Add all missing enum cases to switch",
                    "Add default case to handle remaining cases",
                    "Verify enum definition matches usage"
                ]
            },
            "type_not_found": {
                "patterns": [
                    "cannot find .* in scope",
                    "use of undeclared type"
                ],
                "fixes": [
                    "Define missing types or remove references",
                    "Ensure all custom Views are implemented",
                    "Check file names match type names"
                ]
            },
            "protocol_conformance": {
                "patterns": [
                    "conform to 'Decodable'",
                    "conform to 'Encodable'",
                    "conform to 'Codable'",
                    "does not conform to protocol"
                ],
                "fixes": [
                    "Add protocol conformance to types",
                    "For JSON encoding/decoding, add : Codable",
                    "Ensure all required protocol methods are implemented"
                ]
            }
        }

    def _get_dynamic_recovery_strategies(self):
        """Get recovery strategies based on available services"""
        strategies = [
            self._pattern_based_recovery,
            self._swift_syntax_recovery,
            self._dependency_recovery,
            self._llm_based_recovery
        ]

        return strategies

    async def recover_from_errors(self, errors: List[str], swift_files: List[Dict],
                                  bundle_id: str = None) -> Tuple[bool, List[Dict], List[str]]:
        """Main recovery method that tries multiple strategies"""

        self.logger.info(f"Starting error recovery with {len(errors)} errors")
        # Don't use persistent attempt count - each recovery call should be independent
        # The build service already handles attempt limiting
        
        # Reset attempt count for each recovery session
        # This allows the recovery system to work on each build attempt
        # self.attempt_count += 1
        
        # Remove the max attempts check here - let build service handle it
        # if self.attempt_count > self.max_attempts:
        #     self.logger.warning("Max recovery attempts reached")
        #     return False, swift_files, []

        # Analyze errors
        error_analysis = self._analyze_errors(errors)
        fixes_applied = []

        # Try each recovery strategy
        for strategy in self.recovery_strategies:
            try:
                self.logger.info(f"Attempting recovery strategy: {strategy.__name__}")
                success, modified_files = await strategy(errors, swift_files, error_analysis)

                if success:
                    self.logger.info(f"Recovery strategy {strategy.__name__} succeeded")

                    # Track what was fixed
                    if strategy.__name__ == "_pattern_based_recovery":
                        fixes_applied.append("Applied pattern-based syntax fixes")
                    elif strategy.__name__ == "_llm_based_recovery":
                        fixes_applied.append("Applied AI-powered fixes")

                    return True, modified_files, fixes_applied

            except Exception as e:
                self.logger.error(f"Strategy {strategy.__name__} failed: {e}")
                continue

        # If all strategies fail, try last resort
        return await self._last_resort_recovery(errors, swift_files, error_analysis)

    def _analyze_errors(self, errors: List[str]) -> Dict[str, List[str]]:
        """Analyze errors to categorize them"""
        analysis = {
            "string_literal_errors": [],
            "missing_imports": [],
            "syntax_errors": [],
            "exhaustive_switch_errors": [],
            "type_not_found_errors": [],
            "protocol_conformance_errors": [],
            "persistence_controller_errors": [],
            "other_errors": []
        }

        for error in errors:
            categorized = False

            # Check each error pattern
            for error_type, pattern_info in self.error_patterns.items():
                for pattern in pattern_info["patterns"]:
                    if re.search(pattern, error, re.IGNORECASE):
                        if error_type == "string_literal":
                            analysis["string_literal_errors"].append(error)
                        elif error_type == "missing_import":
                            analysis["missing_imports"].append(error)
                        elif error_type == "syntax_error":
                            analysis["syntax_errors"].append(error)
                        elif error_type == "exhaustive_switch":
                            analysis["exhaustive_switch_errors"].append(error)
                        elif error_type == "type_not_found":
                            analysis["type_not_found_errors"].append(error)
                        elif error_type == "protocol_conformance":
                            analysis["protocol_conformance_errors"].append(error)
                        elif error_type == "persistence_controller":
                            analysis["persistence_controller_errors"].append(error)
                        categorized = True
                        break
                if categorized:
                    break

            if not categorized:
                analysis["other_errors"].append(error)

        return analysis

    async def _pattern_based_recovery(self, errors: List[str], swift_files: List[Dict],
                                      error_analysis: Dict) -> Tuple[bool, List[Dict]]:
        """Pattern-based recovery for common errors"""

        # Check for PersistenceController errors
        has_persistence_error = bool(error_analysis.get("persistence_controller_errors")) or \
                              any("PersistenceController" in error or "managedObjectContext" in error for error in errors)
        
        # Check for protocol conformance errors
        has_codable_error = bool(error_analysis.get("protocol_conformance_errors"))
        
        if not (error_analysis.get("string_literal_errors") or 
                error_analysis.get("syntax_errors") or 
                has_persistence_error or 
                has_codable_error):
            return False, swift_files

        modified_files = []
        changes_made = False

        for file in swift_files:
            content = file["content"]
            original_content = content

            # Fix PersistenceController errors by removing Core Data references
            if has_persistence_error:
                # Remove from any file that has these references
                if "PersistenceController" in content or "managedObjectContext" in content or "CoreData" in content:
                    # Remove Core Data import
                    content = re.sub(r'import CoreData\s*\n', '', content)
                    
                    # Remove PersistenceController property declarations
                    content = re.sub(r'(private\s+)?let\s+persistenceController\s*=\s*PersistenceController[^\n]*\n', '', content)
                    
                    # Remove .environment modifiers with managedObjectContext
                    content = re.sub(r'\.environment\(\\\.managedObjectContext[^)]*\)\s*', '', content)
                    
                    # Remove @Environment property wrappers for managedObjectContext
                    content = re.sub(r'@Environment\(\\\.managedObjectContext\)\s*(?:private\s+)?var\s+\w+\s*:\s*NSManagedObjectContext\s*\n', '', content)
                    
                    # Remove @FetchRequest property wrappers
                    content = re.sub(r'@FetchRequest\([^}]*\}\s*(?:private\s+)?var\s+\w+\s*:[^\n]*\n', '', content)
                    
                    # Remove PersistenceController references in preview providers
                    content = re.sub(r'\.environment\(\\\.managedObjectContext[^)]*PersistenceController[^)]*\)', '', content)
                    
                    changes_made = True

            # Fix string literal errors
            if error_analysis.get("string_literal_errors"):
                # Fix line by line for better control
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    original_line = line
                    
                    # Replace single quotes with double quotes for string literals
                    # But be careful not to replace character literals or within strings
                    # Look for patterns like = 'text' or ('text' or Text('text')
                    line = re.sub(r"(=\s*)'([^']*)'(?!\w)", r'\1"\2"', line)
                    line = re.sub(r"\('([^']*)'\)", r'("\1")', line)
                    line = re.sub(r"Text\('([^']*)'\)", r'Text("\1")', line)
                    line = re.sub(r"Button\('([^']*)'\)", r'Button("\1")', line)
                    line = re.sub(r"\b'([^']+)'\b", r'"\1"', line)
                    
                    # Fix fancy quotes
                    line = line.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
                    
                    # Count quotes to check for unterminated strings
                    # Skip escaped quotes when counting
                    temp_line = line.replace('\\"', '')
                    quote_count = temp_line.count('"')
                    
                    # If odd number of quotes, likely unterminated
                    if quote_count % 2 != 0:
                        # Look for common patterns of unterminated strings
                        if re.search(r'=\s*"[^"]*$', line):  # Assignment ending with open quote
                            line = line.rstrip() + '"'
                        elif re.search(r'\("[^"]*$', line):  # Function call with open quote
                            line = line.rstrip() + '"'
                        elif re.search(r'Text\("[^"]*$', line):  # Text view with open quote
                            line = line.rstrip() + '")'
                        elif re.search(r'print\("[^"]*$', line):  # Print with open quote
                            line = line.rstrip() + '"'
                        else:
                            # Generic fix - add closing quote
                            line = line.rstrip() + '"'
                    
                    lines[i] = line
                    if line != original_line:
                        changes_made = True
                
                content = '\n'.join(lines)

            # Fix Codable conformance errors
            if has_codable_error:
                for error in error_analysis.get("protocol_conformance_errors", []):
                    # Extract type name that needs Codable
                    match = re.search(r"type '(\w+)' does not conform to protocol '(Codable|Decodable|Encodable)'", error)
                    if match:
                        type_name = match.group(1)
                        protocol_name = match.group(2)
                        
                        # Find the type definition
                        # Look for struct or class definition
                        struct_pattern = rf'(struct\s+{type_name}(?:\s*:\s*([^{{]+))?\s*{{)'
                        class_pattern = rf'(class\s+{type_name}(?:\s*:\s*([^{{]+))?\s*{{)'
                        
                        for pattern in [struct_pattern, class_pattern]:
                            match = re.search(pattern, content)
                            if match:
                                full_match = match.group(0)
                                existing_conformances = match.group(2) if match.group(2) else ""
                                
                                if "Codable" not in existing_conformances and protocol_name not in existing_conformances:
                                    if existing_conformances:
                                        # Add to existing conformances
                                        new_conformances = existing_conformances.strip() + ", Codable"
                                        new_declaration = full_match.replace(existing_conformances, new_conformances)
                                    else:
                                        # Add conformance
                                        type_keyword = "struct" if "struct" in full_match else "class"
                                        new_declaration = full_match.replace(
                                            f"{type_keyword} {type_name}",
                                            f"{type_keyword} {type_name}: Codable"
                                        )
                                    
                                    content = content.replace(full_match, new_declaration)
                                    changes_made = True
                                    break
            
            # Fix common syntax errors
            content = re.sub(r'\.presentationMode', '.dismiss', content)
            content = re.sub(r'@Environment\(\\\.presentationMode\)', '@Environment(\\.dismiss)', content)

            if content != original_content:
                changes_made = True

            modified_files.append({
                "path": file["path"],
                "content": content
            })

        return changes_made, modified_files

    async def _swift_syntax_recovery(self, errors: List[str], swift_files: List[Dict],
                                     error_analysis: Dict) -> Tuple[bool, List[Dict]]:
        """Swift-specific syntax recovery"""

        modified_files = []
        changes_made = False

        for file in swift_files:
            content = file["content"]
            original_content = content

            # Ensure proper imports
            if "@main" in content and "import SwiftUI" not in content:
                content = "import SwiftUI\n" + content
                changes_made = True

            if "Date()" in content and "import Foundation" not in content:
                content = "import Foundation\n" + content
                changes_made = True

            modified_files.append({
                "path": file["path"],
                "content": content
            })

        return changes_made, modified_files

    async def _dependency_recovery(self, errors: List[str], swift_files: List[Dict],
                                   error_analysis: Dict) -> Tuple[bool, List[Dict]]:
        """Fix missing dependencies"""

        if not error_analysis["missing_imports"]:
            return False, swift_files

        modified_files = []
        changes_made = False

        # Extract missing types from errors
        missing_types = set()
        for error in error_analysis["missing_imports"]:
            match = re.search(r"cannot find type '([^']+)' in scope", error)
            if match:
                missing_types.add(match.group(1))

        # Map types to imports
        type_to_import = {
            "Color": "SwiftUI",
            "View": "SwiftUI",
            "Text": "SwiftUI",
            "Button": "SwiftUI",
            "VStack": "SwiftUI",
            "HStack": "SwiftUI",
            "List": "SwiftUI",
            "NavigationView": "SwiftUI",
            "NavigationStack": "SwiftUI",
            "Date": "Foundation",
            "DateFormatter": "Foundation",
            "UUID": "Foundation",
            "URL": "Foundation"
        }

        for file in swift_files:
            content = file["content"]
            imports_to_add = set()

            # Check which imports are needed
            for missing_type in missing_types:
                if missing_type in type_to_import and missing_type in content:
                    import_module = type_to_import[missing_type]
                    if f"import {import_module}" not in content:
                        imports_to_add.add(import_module)

            # Add missing imports
            if imports_to_add:
                import_statements = "\n".join(f"import {module}" for module in sorted(imports_to_add))
                content = import_statements + "\n" + content
                changes_made = True

            modified_files.append({
                "path": file["path"],
                "content": content
            })

        return changes_made, modified_files

    async def _llm_based_recovery(self, errors: List[str], swift_files: List[Dict],
                                  error_analysis: Dict) -> Tuple[bool, List[Dict]]:
        """Use LLMs to fix errors"""

        # Try Claude first if available - FIXED METHOD CALL
        if self.claude_service:
            try:
                # Check which methods are available
                if hasattr(self.claude_service, 'generate_ios_app'):
                    # Use the modification approach
                    fix_prompt = self._create_error_fix_prompt(errors, swift_files, error_analysis)

                    # Create a modification request that fixes the errors
                    modification_request = f"Fix these build errors:\n{chr(10).join(errors[:5])}"

                    # Use modify_ios_app if available
                    if hasattr(self.claude_service, 'modify_ios_app'):
                        result = await self.claude_service.modify_ios_app(
                            app_name="App",
                            description="Fix build errors",
                            modification=modification_request,
                            files=swift_files
                        )

                        if result and "files" in result:
                            return True, result["files"]

                    # Fall back to generate_text
                    elif hasattr(self.claude_service, 'generate_text'):
                        result = self.claude_service.generate_text(fix_prompt)
                        if result["success"]:
                            fixed_files = self._parse_ai_response(result["text"], swift_files)
                            if fixed_files:
                                return True, fixed_files

            except Exception as e:
                self.logger.error(f"Claude recovery failed: {e}")

        # Try OpenAI if available
        if self.openai_key:
            success, files = await self._openai_recovery(errors, swift_files, error_analysis)
            if success:
                return success, files

        # Try xAI if available
        if self.xai_key:
            success, files = await self._xai_recovery(errors, swift_files, error_analysis)
            if success:
                return success, files

        return False, swift_files

    async def _openai_recovery(self, errors: List[str], swift_files: List[Dict],
                               error_analysis: Dict) -> Tuple[bool, List[Dict]]:
        """Use OpenAI for recovery"""

        if not openai or not AsyncOpenAI:
            self.logger.warning("OpenAI not available")
            return False, swift_files

        try:
            client = AsyncOpenAI(api_key=self.openai_key)

            # Create context
            error_text = "\n".join(errors[:10])  # Limit to first 10 errors
            code_context = "\n---\n".join([
                f"File: {f['path']}\n{f['content'][:500]}..."
                for f in swift_files[:3]
            ])

            messages = [
                {
                    "role": "system",
                    "content": """You are an expert Swift developer. Fix compilation errors in iOS apps.
                    
Key rules:
1. Use double quotes " for strings, never single quotes '
2. Use @Environment(\\.dismiss) instead of @Environment(\\.presentationMode)
3. Ensure all Swift syntax is correct
4. Return complete fixed code, not snippets"""
                },
                {
                    "role": "user",
                    "content": f"""Fix these Swift build errors:

ERRORS:
{error_text}

CURRENT CODE:
{code_context}

Return a JSON object with this structure:
{{
    "files": [
        {{
            "path": "Sources/FileName.swift",
            "content": "// COMPLETE fixed Swift code here"
        }}
    ],
    "fixes_applied": ["List of fixes made"]
}}"""
                }
            ]

            response = await client.chat.completions.create(
                model="gpt-4-turbo-preview",  # or "gpt-4" or "gpt-3.5-turbo"
                messages=messages,
                temperature=0.3,
                max_tokens=4000,
                response_format={"type": "json_object"}  # Force JSON response
            )

            content = response.choices[0].message.content
            self.logger.info("GPT-4 response received")

            # Parse JSON response
            try:
                result = json.loads(content)
                if "files" in result:
                    self.logger.info(f"GPT-4 fixes: {result.get('fixes_applied', [])}")
                    return True, result["files"]
            except json.JSONDecodeError:
                # Try to parse as code blocks
                fixed_files = self._parse_ai_response(content, swift_files)
                if fixed_files:
                    return True, fixed_files

        except Exception as e:
            self.logger.error(f"OpenAI recovery failed: {e}")
            import traceback
            traceback.print_exc()

        return False, swift_files

    async def _xai_recovery(self, errors: List[str], swift_files: List[Dict],
                            error_analysis: Dict) -> Tuple[bool, List[Dict]]:
        """Use xAI (Grok) for recovery - placeholder for now"""
        # xAI implementation would go here when API is available
        return False, swift_files

    def _create_error_fix_prompt(self, errors: List[str], swift_files: List[Dict],
                                 error_analysis: Dict) -> str:
        """Create a prompt for LLMs to fix errors"""

        # Get relevant files with errors
        error_files = set()
        for error in errors:
            # Extract file path from error
            match = re.search(r'(Sources/[^:]+\.swift)', error)
            if match:
                error_files.add(match.group(1))

        # Get the files that have errors
        relevant_files = [f for f in swift_files if f["path"] in error_files]

        # Use newline character instead of chr(10) in f-string
        newline = '\n'
        errors_text = newline.join(errors[:10])
        files_text = newline.join([f"File: {f['path']}\n```swift\n{f['content']}\n```" for f in relevant_files])

        prompt = f"""Fix these Swift compilation errors. Be VERY careful with string literals and quotes.

ERRORS:
{errors_text}

ERROR TYPES DETECTED:
{json.dumps(error_analysis, indent=2)}

FILES WITH ERRORS:
{files_text}

CRITICAL INSTRUCTIONS:
1. For "cannot find type in scope" errors:
   - If it's 'PersistenceController', 'DataController', or similar:
     * These are Core Data controllers - either implement them or remove Core Data references
     * For simple apps, you can remove these and use @State/@StateObject instead
   - If it's a custom View or Model:
     * Add the missing type definition
     * Or remove references if not needed
   - Ensure all referenced types have complete implementations

2. For "switch must be exhaustive" errors:
   - Add ALL missing cases to the switch statement
   - Or add a default case: default: break
   - Check the enum definition for all cases

3. For string literal errors:
   - Use regular double quotes " not fancy quotes " " or ' '
   - Fix: Text("Hello") not Text("Hello") or Text('Hello')
   - Ensure all strings are properly terminated

4. For import errors:
   - Add missing imports at the top of files
   - SwiftUI apps need: import SwiftUI
   - Core Data apps need: import CoreData

5. For Codable/Encodable/Decodable errors:
   - Add ": Codable" to struct/class declarations that need JSON encoding
   - Import Foundation if not already imported
   - Example: struct TodoItem: Identifiable, Codable { ... }

6. For '@StateObject' requires property wrapper errors:
   - Ensure the class conforms to ObservableObject
   - Use @Published for properties that should trigger UI updates

7. For missing initializer errors:
   - Add required init methods
   - Or provide default values for all properties

8. IMPORTANT: 
   - Fix the ROOT CAUSE, not just symptoms
   - If Core Data is causing issues and not essential, remove it
   - Keep the app functional even if simplified
   - Return COMPLETE, WORKING code for ALL files

Return JSON with the fixed files:
{{
    "files": [
        {{
            "path": "Sources/FileName.swift",
            "content": "// Complete FIXED code here"
        }}
    ],
    "fixes_applied": ["List of fixes"]
}}"""

        return prompt

    async def _last_resort_recovery(self, errors: List[str], swift_files: List[Dict],
                                    error_analysis: Dict) -> Tuple[bool, List[Dict], List[str]]:
        """Last resort - create minimal working version"""

        self.logger.info("Applying last resort recovery")

        # Find the main app file
        app_file = None
        other_files = []

        for file in swift_files:
            if "@main" in file["content"]:
                app_file = file
            else:
                other_files.append(file)

        if not app_file:
            return False, swift_files, []

        # Create minimal working versions
        modified_files = []

        # Fix app file
        app_name = "MyApp"
        match = re.search(r'struct\s+(\w+):\s*App', app_file["content"])
        if match:
            app_name = match.group(1)

        minimal_app = f"""import SwiftUI

@main
struct {app_name}: App {{
    var body: some Scene {{
        WindowGroup {{
            ContentView()
        }}
    }}
}}"""

        modified_files.append({
            "path": app_file["path"],
            "content": minimal_app
        })

        # Create minimal ContentView
        content_view = """import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack {
            Image(systemName: "globe")
                .imageScale(.large)
                .foregroundStyle(.tint)
            Text("Hello, world!")
        }
        .padding()
    }
}

#Preview {
    ContentView()
}"""

        # Find ContentView file or create one
        content_view_file = None
        for file in other_files:
            if "ContentView" in file["path"]:
                content_view_file = file
                break

        if content_view_file:
            modified_files.append({
                "path": content_view_file["path"],
                "content": content_view
            })
        else:
            modified_files.append({
                "path": "Sources/ContentView.swift",
                "content": content_view
            })

        return True, modified_files, ["Applied minimal working template"]

    def _parse_ai_response(self, response: str, original_files: List[Dict]) -> List[Dict]:
        """Parse AI response to extract fixed files"""

        # Try to parse as JSON first
        try:
            result = json.loads(response)
            if "files" in result:
                return result["files"]
        except json.JSONDecodeError:
            pass

        # Try to extract Swift code blocks
        swift_blocks = re.findall(r'```swift(.*?)```', response, re.DOTALL)

        if swift_blocks:
            # Match blocks to original files
            fixed_files = []
            for file in original_files:
                # Try to find corresponding code block
                for block in swift_blocks:
                    # Simple heuristic: check if file contains key identifiers
                    if "@main" in file["content"] and "@main" in block:
                        fixed_files.append({
                            "path": file["path"],
                            "content": block.strip()
                        })
                        break
                    elif "ContentView" in file["path"] and "ContentView" in block:
                        fixed_files.append({
                            "path": file["path"],
                            "content": block.strip()
                        })
                        break

            if fixed_files:
                return fixed_files

        return None


def create_intelligent_recovery_system(claude_service=None, openai_key=None, xai_key=None):
    """Factory function to create recovery system"""
    return RobustErrorRecoverySystem(
        claude_service=claude_service,
        openai_key=openai_key,
        xai_key=xai_key
    )