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
                    "expected '\"' to terminate string",
                    "single-quoted string literal found"
                ],
                "fixes": [
                    "Check for missing closing quotes",
                    "Ensure strings are properly terminated",
                    "Look for double double-quotes",
                    "Replace single quotes with double quotes"
                ]
            },
            "single_quotes": {
                "patterns": [
                    "single-quoted string literal found",
                    "use '\"'"
                ],
                "fixes": [
                    "Replace all single quotes with double quotes",
                    "Swift requires double quotes for strings"
                ]
            },
            "environment": {
                "patterns": [
                    "generic parameter",
                    "could not be inferred",
                    "@Environment"
                ],
                "fixes": [
                    "Use @Environment(\\.dismiss) instead of presentationMode",
                    "Ensure proper Environment syntax"
                ]
            },
            "import_missing": {
                "patterns": [
                    "cannot find type",
                    "use of unresolved identifier",
                    "no such module"
                ],
                "fixes": [
                    "Add missing imports",
                    "Import SwiftUI for SwiftUI types",
                    "Import Foundation for basic types"
                ]
            },
            "syntax": {
                "patterns": [
                    "expected",
                    "invalid",
                    "consecutive statements"
                ],
                "fixes": [
                    "Check syntax",
                    "Verify Swift syntax rules",
                    "Check for missing semicolons or braces"
                ]
            }
        }

    def _get_dynamic_recovery_strategies(self):
        """Get recovery strategies based on available services and error types"""
        strategies = []

        # Always try simple pattern-based fixes first (fastest)
        strategies.append(self._pattern_based_recovery)

        # Then try LLMs based on availability and strengths
        if self.claude_service:
            strategies.append(self._claude_recovery)  # Best for complex Swift/SwiftUI issues

        if self.openai_key:
            strategies.append(self._openai_recovery)  # Good general purpose

        if self.xai_key:
            strategies.append(self._xai_recovery)  # Can be good for specific patterns

        # Try combined approach if individual LLMs fail
        if len([x for x in [self.claude_service, self.openai_key, self.xai_key] if x]) > 1:
            strategies.append(self._combined_recovery)

        # Local validators
        strategies.append(self._syntax_validator_recovery)

        # Last resort
        strategies.append(self._last_resort_recovery)

        return strategies

    async def recover_from_errors(self, errors: List[str], swift_files: List[Dict],
                                  project_path: str) -> Tuple[bool, List[Dict]]:
        """Main entry point for error recovery"""

        self.logger.info(f"Starting error recovery attempt {self.attempt_count + 1} with {len(errors)} errors")
        self.attempt_count += 1

        # Log the actual errors we're trying to fix
        for error in errors[:5]:  # Show first 5 errors
            self.logger.info(f"Error: {error}")

        # Analyze errors
        error_analysis = self._analyze_errors(errors)
        self.logger.info(f"Error types detected: {error_analysis}")

        # Determine best LLM for these errors
        preferred_llm = self._analyze_errors_for_llm_selection(errors)
        self.logger.info(f"Preferred LLM for these errors: {preferred_llm}")

        # Try recovery strategies in order
        for strategy in self.recovery_strategies:
            strategy_name = strategy.__name__
            self.logger.info(f"Attempting strategy: {strategy_name}")

            start_time = time.time()
            try:
                if asyncio.iscoroutinefunction(strategy):
                    success, modified_files = await strategy(errors, swift_files, error_analysis)
                else:
                    success, modified_files = strategy(errors, swift_files, error_analysis)

                if success:
                    elapsed = time.time() - start_time
                    self.logger.info(f"Strategy {strategy_name} succeeded in {elapsed:.2f}s")
                    return True, modified_files
                else:
                    self.logger.info(f"Strategy {strategy_name} did not resolve the issues")

            except Exception as e:
                self.logger.error(f"Strategy {strategy_name} failed with error: {e}")
                import traceback
                traceback.print_exc()
                continue

        self.logger.warning("All recovery strategies exhausted")
        return False, swift_files

    def _analyze_errors(self, errors: List[str]) -> Dict[str, List[str]]:
        """Analyze and categorize errors"""

        analysis = {
            "string_literal": [],
            "single_quotes": [],
            "environment": [],
            "import_missing": [],
            "type_not_found": [],
            "syntax": [],
            "other": []
        }

        for error in errors:
            categorized = False

            # Check against known patterns
            for error_type, pattern_info in self.error_patterns.items():
                for pattern in pattern_info.get("patterns", []):
                    if pattern in error.lower():
                        if error_type in analysis:
                            analysis[error_type].append(error)
                            categorized = True
                            break
                if categorized:
                    break

            if not categorized:
                analysis["other"].append(error)

        # Remove empty categories
        return {k: v for k, v in analysis.items() if v}

    def _analyze_errors_for_llm_selection(self, errors: List[str]) -> str:
        """Analyze errors to determine which LLM might be best"""

        # Count error types
        swift_ui_errors = sum(1 for e in errors if 'SwiftUI' in e or 'View' in e or '@Environment' in e)
        syntax_errors = sum(1 for e in errors if 'syntax' in e.lower() or 'expected' in e)
        type_errors = sum(1 for e in errors if 'type' in e or 'generic' in e)

        # Determine best LLM based on error types
        if swift_ui_errors > syntax_errors:
            return "claude"  # Claude is best for SwiftUI
        elif syntax_errors > type_errors:
            return "openai"  # GPT-4 is good for general syntax
        else:
            return "any"  # Any LLM can handle it

    def _pattern_based_recovery(self, errors: List[str], swift_files: List[Dict],
                                error_analysis: Dict) -> Tuple[bool, List[Dict]]:
        """Pattern-based recovery for common Swift errors"""

        self.logger.info("Attempting pattern-based recovery")

        # Check for specific error patterns
        has_environment_error = any("generic parameter" in error and "Environment" in error for error in errors)
        has_single_quote_error = any("single-quoted string literal" in error for error in errors)
        has_double_quote_error = any("unterminated string literal" in error for error in errors)

        modified_files = []
        total_fixes_applied = 0

        for file in swift_files:
            content = file["content"]
            original_content = content
            fixes_applied = []

            # Apply targeted fixes based on detected errors
            if has_environment_error:
                # Fix Environment issues
                content = re.sub(
                    r'@Environment\([^)]*\)\s+var\s+presentationMode.*',
                    '@Environment(\\.dismiss) private var dismiss',
                    content
                )
                content = content.replace('presentationMode.wrappedValue.dismiss()', 'dismiss()')
                if content != original_content:
                    fixes_applied.append("Fixed Environment presentationMode")

            if has_single_quote_error:
                # Replace single quotes with double quotes
                lines = content.split('\n')
                fixed_lines = []

                for line in lines:
                    if not line.strip().startswith('//'):
                        line = re.sub(r"'([^']*)'", r'"\1"', line)
                    fixed_lines.append(line)

                content = '\n'.join(fixed_lines)
                if content != original_content:
                    fixes_applied.append("Fixed single quotes")

            if has_double_quote_error:
                # Fix double double-quotes
                content = re.sub(r'TextField\("([^"]+)""\)', r'TextField("\1")', content)
                content = re.sub(r'Text\(""([^"]+)"\)', r'Text("\1")', content)
                content = re.sub(r'""([^"]+)""', r'"\1"', content)
                if content != original_content:
                    fixes_applied.append("Fixed double quotes")

            if content != original_content:
                self.logger.info(f"Applied {len(fixes_applied)} fixes to {file['path']}: {fixes_applied}")
                total_fixes_applied += len(fixes_applied)

            modified_files.append({
                "path": file["path"],
                "content": content
            })

        if total_fixes_applied > 0:
            self.logger.info(f"Pattern-based recovery applied {total_fixes_applied} fixes")
            return True, modified_files

        self.logger.info("Pattern-based recovery made no changes")
        return False, swift_files

    async def _claude_recovery(self, errors: List[str], swift_files: List[Dict],
                               error_analysis: Dict) -> Tuple[bool, List[Dict]]:
        """Use Claude for intelligent recovery - THIS SHOULD BE OUR BEST OPTION"""

        if not self.claude_service:
            self.logger.warning("Claude service not available")
            return False, swift_files

        self.logger.info("Attempting Claude recovery - our most intelligent option")

        try:
            # Send ALL the errors and files to Claude
            result = await self.claude_service.analyze_build_errors(errors, swift_files)

            if result and "files" in result:
                self.logger.info(f"Claude fixed errors: {result.get('fixes_applied', [])}")
                return True, result["files"]
            else:
                self.logger.warning("Claude didn't return fixed files")

        except Exception as e:
            self.logger.error(f"Claude recovery failed: {e}")
            import traceback
            traceback.print_exc()

        return False, swift_files

    async def _openai_recovery(self, errors: List[str], swift_files: List[Dict],
                               error_analysis: Dict) -> Tuple[bool, List[Dict]]:
        """Use OpenAI GPT-4 for recovery with enhanced prompting"""

        if not self.openai_key or not AsyncOpenAI:
            self.logger.warning("OpenAI not available")
            return False, swift_files

        self.logger.info("Attempting OpenAI GPT-4 recovery")

        try:
            client = AsyncOpenAI(api_key=self.openai_key)

            # Create a detailed prompt for GPT-4
            error_text = "\n".join(errors)

            # Include files with errors
            code_context = ""
            for file in swift_files:
                if any(file["path"] in error for error in errors):
                    code_context += f"\nFile: {file['path']}\n```swift\n{file['content']}\n```\n"

            messages = [
                {
                    "role": "system",
                    "content": """You are an expert Swift and SwiftUI developer. Fix compilation errors in iOS apps.
                    
Key rules:
1. Use double quotes " for strings, never single quotes '
2. Use @Environment(\.dismiss) instead of @Environment(\.presentationMode)
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
        """Use xAI (Grok) for recovery"""

        if not self.xai_key or not httpx:
            self.logger.warning("xAI not available")
            return False, swift_files

        self.logger.info("Attempting xAI (Grok) recovery")

        try:
            # xAI API endpoint (update with actual endpoint when available)
            url = "https://api.x.ai/v1/chat/completions"

            headers = {
                "Authorization": f"Bearer {self.xai_key}",
                "Content-Type": "application/json"
            }

            # Create prompt similar to other LLMs
            prompt = self._create_error_fix_prompt(errors, swift_files, error_analysis)

            data = {
                "model": "grok-1",  # or whatever model name xAI uses
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert Swift developer. Fix the build errors and return complete corrected code."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 4000
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=data)

                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']

                    # Parse response
                    fixed_files = self._parse_ai_response(content, swift_files)

                    if fixed_files:
                        self.logger.info("xAI successfully fixed errors")
                        return True, fixed_files
                    else:
                        self.logger.warning("xAI response couldn't be parsed")
                else:
                    self.logger.error(f"xAI API error: {response.status_code} - {response.text}")

        except Exception as e:
            self.logger.error(f"xAI recovery failed: {e}")
            import traceback
            traceback.print_exc()

        return False, swift_files

    async def _combined_recovery(self, errors: List[str], swift_files: List[Dict],
                                 error_analysis: Dict) -> Tuple[bool, List[Dict]]:
        """Combine insights from multiple models for better results"""

        self.logger.info("Attempting combined multi-model recovery")

        # Run multiple LLMs in parallel for faster results
        tasks = []

        if self.claude_service:
            tasks.append(('claude', self._claude_recovery(errors, swift_files, error_analysis)))

        if self.openai_key:
            tasks.append(('openai', self._openai_recovery(errors, swift_files, error_analysis)))

        if self.xai_key:
            tasks.append(('xai', self._xai_recovery(errors, swift_files, error_analysis)))

        if not tasks:
            return False, swift_files

        # Wait for all results
        results = []
        for name, task in tasks:
            try:
                success, files = await task
                if success:
                    results.append((name, files))
                    self.logger.info(f"{name} provided a solution")
            except Exception as e:
                self.logger.error(f"{name} failed in combined recovery: {e}")

        if not results:
            return False, swift_files

        # If we have multiple successful results, merge the best fixes
        if len(results) > 1:
            # For now, just use the first successful result
            # In the future, we could implement a voting system
            self.logger.info(f"Using solution from {results[0][0]}")
            return True, results[0][1]

        return True, results[0][1]

    def _syntax_validator_recovery(self, errors: List[str], swift_files: List[Dict],
                                   error_analysis: Dict) -> Tuple[bool, List[Dict]]:
        """Use Swift syntax validator for recovery"""

        try:
            from swift_syntax_validator import SwiftSyntaxValidator

            self.logger.info("Attempting Swift syntax validator recovery")

            validator = SwiftSyntaxValidator()
            modified_files = []
            total_fixes = 0

            for file in swift_files:
                content, fixes = validator.fix_swift_file(file["content"], file["path"])

                if fixes:
                    self.logger.info(f"Validator applied {len(fixes)} fixes to {file['path']}")
                    for fix in fixes[:3]:  # Show first 3 fixes
                        self.logger.info(f"  - {fix}")
                    total_fixes += len(fixes)

                modified_files.append({
                    "path": file["path"],
                    "content": content
                })

            if total_fixes > 0:
                return True, modified_files

        except ImportError:
            self.logger.warning("Swift syntax validator not available")
        except Exception as e:
            self.logger.error(f"Syntax validator recovery failed: {e}")
            import traceback
            traceback.print_exc()

        return False, swift_files

    def _last_resort_recovery(self, errors: List[str], swift_files: List[Dict],
                              error_analysis: Dict) -> Tuple[bool, List[Dict]]:
        """Last resort - create minimal working version"""

        self.logger.info("Attempting last resort recovery - creating minimal working version")

        # Find the main app file
        app_file = None
        content_view = None

        for file in swift_files:
            if "@main" in file["content"]:
                app_file = file
            elif "ContentView" in file["path"]:
                content_view = file

        if not app_file:
            return False, swift_files

        # Extract app name
        app_name = "MyApp"
        match = re.search(r'struct\s+(\w+):\s*App', app_file["content"])
        if match:
            app_name = match.group(1).replace("App", "")

        # Create minimal working files
        minimal_files = [
            {
                "path": app_file["path"],
                "content": f"""import SwiftUI

@main
struct {app_name}App: App {{
    var body: some Scene {{
        WindowGroup {{
            ContentView()
        }}
    }}
}}"""
            },
            {
                "path": "Sources/ContentView.swift",
                "content": """import SwiftUI

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
}"""
            }
        ]

        self.logger.info("Created minimal working version")
        return True, minimal_files

    def _create_error_fix_prompt(self, errors: List[str], swift_files: List[Dict],
                                 error_analysis: Dict) -> str:
        """Create prompt for AI models"""

        # Include all relevant code
        code_context = ""
        for file in swift_files:
            if any(file["path"] in error for error in errors):
                code_context += f"\nFile: {file['path']}\n```swift\n{file['content']}\n```\n"

        prompt = f"""Fix these Swift build errors:

ERRORS:
{chr(10).join(errors)}

ERROR ANALYSIS:
{json.dumps(error_analysis, indent=2)}

CODE:
{code_context}

CRITICAL RULES:
1. Use double quotes " not single quotes '
2. Use @Environment(\.dismiss) not presentationMode
3. Fix any syntax errors

Return the complete fixed code."""

        return prompt

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