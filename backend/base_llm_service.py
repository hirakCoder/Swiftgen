"""
Base LLM Service - Foundation for all LLM integrations
Provides common functionality and standards for world-class code generation
"""

import json
import re
import os
from typing import Dict, List, Optional, Tuple
import hashlib
from datetime import datetime
import random

class BaseLLMService:
    """Base class for all LLM services with production-ready functionality"""

    def __init__(self):
        self.common_prefixes = [
            "Here is", "Here's", "I'll", "Let me", "I've", "Fixed",
            "Created", "Modified", "Updated", "Generated"
        ]

        # Track performance metrics
        self.performance_metrics = {
            "total_calls": 0,
            "successful_parses": 0,
            "failed_parses": 0,
            "average_response_time": 0
        }

        # Common Swift patterns to enforce
        self.swift_patterns = {
            "modern_ios": {
                "NavigationStack": "NavigationView",
                "@Environment(\\.dismiss)": "@Environment(\\.presentationMode)",
                "iOS 16": ["iOS 15", "iOS 14"]
            },
            "naming_safety": {
                "TodoItem": "Task",
                "AppState": "State",
                "AppAction": "Action",
                "OperationResult": "Result",
                "AppError": "Error"
            }
        }

    def _create_safe_bundle_id(self, app_name: str) -> str:
        """Create a safe bundle ID from app name"""
        # Remove all non-alphanumeric characters
        safe_name = re.sub(r'[^a-zA-Z0-9]', '', app_name).lower()

        # Ensure it starts with a letter
        if safe_name and not safe_name[0].isalpha():
            safe_name = 'app' + safe_name

        # Fallback if empty
        if not safe_name:
            safe_name = 'myapp'

        # Ensure reasonable length
        safe_name = safe_name[:20]

        # Add timestamp for uniqueness in development
        timestamp = datetime.now().strftime('%H%M')

        return f"com.swiftgen.{safe_name}"

    def _extract_json_from_response(self, content: str) -> Optional[Dict]:
        """Extract and parse JSON from LLM response with enhanced error recovery"""

        self.performance_metrics["total_calls"] += 1
        content = content.strip()

        # Method 1: Direct parse
        try:
            result = json.loads(content)
            self.performance_metrics["successful_parses"] += 1
            return self._validate_and_normalize_result(result)
        except Exception as e:
            pass

        # Method 2: Remove common prefixes
        for prefix in self.common_prefixes:
            for variant in [prefix, f"{prefix} ", f"{prefix}:", f"{prefix}."] :
                if content.lower().startswith(variant.lower()):
                    content = content[len(variant):].strip()
                    break

        # Method 3: Find JSON boundaries
        json_start = content.find('{')
        json_end = content.rfind('}')

        if json_start >= 0 and json_end > json_start:
            try:
                json_str = content[json_start:json_end + 1]
                result = json.loads(json_str)
                self.performance_metrics["successful_parses"] += 1
                return self._validate_and_normalize_result(result)
            except:
                pass

        # Method 4: Extract from markdown
        if "```json" in content:
            try:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                if json_end > json_start:
                    json_str = content[json_start:json_end].strip()
                    result = json.loads(json_str)
                    self.performance_metrics["successful_parses"] += 1
                    return self._validate_and_normalize_result(result)
            except:
                pass

        # Method 5: Try to fix common JSON errors
        if json_start >= 0:
            try:
                # Extract potential JSON
                potential_json = content[json_start:]

                # Fix common issues
                potential_json = self._fix_json_common_errors(potential_json)

                result = json.loads(potential_json)
                self.performance_metrics["successful_parses"] += 1
                return self._validate_and_normalize_result(result)
            except:
                pass

        self.performance_metrics["failed_parses"] += 1
        return None

    def _fix_json_common_errors(self, json_str: str) -> str:
        """Fix common JSON formatting errors"""

        # Remove trailing commas
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)

        # Fix unescaped quotes in strings
        # This is tricky - only fix obvious cases
        json_str = re.sub(r':\s*"([^"]*)"([^",}\]]+)"', r': "\1\2"', json_str)

        # Ensure proper closing
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')
        if open_braces > close_braces:
            json_str += '}' * (open_braces - close_braces)

        return json_str

    def _validate_and_normalize_result(self, result: Dict) -> Dict:
        """Validate and normalize the parsed result"""

        # Ensure required fields
        if "files" not in result:
            return None

        # Normalize file structure
        normalized_files = []
        for file in result.get("files", []):
            if isinstance(file, dict):
                path = file.get("path", "")
                content = file.get("content", "")

                # Skip invalid files
                if not path or not content:
                    continue

                # Ensure proper path format
                if not path.startswith("Sources/"):
                    path = f"Sources/{path}"

                if not path.endswith(".swift"):
                    path = f"{path}.swift"

                normalized_files.append({
                    "path": path,
                    "content": self._apply_swift_patterns(content)
                })

        result["files"] = normalized_files

        # Ensure other required fields
        if "bundle_id" not in result:
            result["bundle_id"] = self._create_safe_bundle_id(result.get("app_name", "App"))

        return result

    def _apply_swift_patterns(self, content: str) -> str:
        """Apply modern Swift patterns and fix common issues"""

        # Apply modern iOS patterns
        for modern, deprecated in self.swift_patterns["modern_ios"].items():
            if isinstance(deprecated, list):
                for dep in deprecated:
                    content = content.replace(dep, modern)
            else:
                content = content.replace(deprecated, modern)

        # Fix naming conflicts
        for safe, reserved in self.swift_patterns["naming_safety"].items():
            # Only replace definitions, not references in strings
            content = re.sub(rf'\b(struct|class|enum)\s+{reserved}\b', f'\\1 {safe}', content)

        # Fix string quotes
        lines = content.split('\n')
        fixed_lines = []
        for line in lines:
            if not line.strip().startswith('//'):
                # Fix single quotes
                line = re.sub(r"'([^']*)'", r'"\1"', line)
            fixed_lines.append(line)
        content = '\n'.join(fixed_lines)

        return content

    def _ensure_ios16_compatibility(self, content: str) -> str:
        """Ensure all code is iOS 16+ compatible"""

        replacements = [
            # Environment
            (r'@Environment\(\\.presentationMode\)\s+(?:private\s+)?var\s+\w+',
             '@Environment(\\.dismiss) private var dismiss'),

            # Dismiss calls  
            (r'presentationMode\.wrappedValue\.dismiss\(\)',
             'dismiss()'),

            # Navigation
            (r'NavigationView\s*{',
             'NavigationStack {'),
        ]

        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)

        return content

    def _create_unique_seed(self) -> str:
        """Create a unique seed for variation"""
        return hashlib.md5(
            f"{datetime.now().isoformat()}{random.random()}".encode()
        ).hexdigest()[:8]

    def _build_system_prompt(self, focus: str = "") -> str:
        """Build a comprehensive system prompt for any LLM"""

        base_prompt = """You are an expert iOS developer creating production-ready SwiftUI apps.

CRITICAL RULES - NEVER VIOLATE:

1. SELF-CONTAINED APPS:
   - NO external services or dependencies (no APIService, NetworkManager, etc.)
   - ALL functionality implemented within generated files
   - Use mock data and local state management only

2. RESERVED TYPE SAFETY:
   - NEVER use: struct/class Task (use TodoItem)
   - NEVER use: struct/class State (use AppState)  
   - NEVER use: struct/class Action (use AppAction)
   - NEVER use: struct/class Result (use OperationResult)
   - NEVER use: struct/class Error (use AppError)

3. MODERN iOS PATTERNS (iOS 16+):
   - Use NavigationStack NOT NavigationView
   - Use @Environment(\.dismiss) NOT presentationMode
   - Use async/await for asynchronous operations
   - Use @StateObject for view-owned objects
   - Use @ObservedObject for injected objects

4. CODE QUALITY:
   - Every file must compile without errors
   - Use proper SwiftUI property wrappers
   - Include all necessary imports
   - Follow Swift naming conventions
   - Add helpful comments for complex logic

5. ARCHITECTURE:
   - Keep it simple - max 5-7 files
   - Use MVVM with ObservableObject
   - No complex dependency injection
   - Clear separation of concerns

Return ONLY valid JSON with complete, working code."""

        if focus:
            base_prompt += f"\n\nADDITIONAL FOCUS: {focus}"

        return base_prompt

    def get_performance_metrics(self) -> Dict:
        """Get performance metrics for monitoring"""

        success_rate = 0
        if self.performance_metrics["total_calls"] > 0:
            success_rate = (self.performance_metrics["successful_parses"] /
                            self.performance_metrics["total_calls"] * 100)

        return {
            "total_calls": self.performance_metrics["total_calls"],
            "success_rate": f"{success_rate:.1f}%",
            "failed_parses": self.performance_metrics["failed_parses"],
            "average_response_time": self.performance_metrics["average_response_time"]
        }

    def _extract_app_name_from_code(self, files: List[Dict]) -> str:
        """Extract the actual app name from Swift code"""

        for file in files:
            content = file.get("content", "")
            if "@main" in content:
                match = re.search(r'struct\s+(\w+)App\s*:\s*App', content)
                if match:
                    app_name = match.group(1)
                    # Convert PascalCase to readable
                    readable = re.sub(r'([A-Z])', r' \1', app_name).strip()
                    return readable

        return "MyApp"

    def _normalize_app_names(self, files: List[Dict], target_name: str) -> List[Dict]:
        """Normalize all app names to be consistent"""

        safe_name = target_name.replace(" ", "")

        for file in files:
            content = file.get("content", "")

            # Update @main struct
            if "@main" in content:
                content = re.sub(
                    r'struct\s+\w+App\s*:\s*App',
                    f'struct {safe_name}App: App',
                    content
                )

            # Update ViewModel references
            content = re.sub(
                r'(\w+)ViewModel',
                f'{safe_name}ViewModel',
                content
            )

            file["content"] = content

        return files

    async def parse_llm_response(self, content: str, safe_bundle_id: str, app_name: str) -> Dict:
        """Universal method to parse any LLM response"""

        start_time = datetime.now()

        # Extract JSON
        parsed = self._extract_json_from_response(content)

        if not parsed:
            # If parsing failed, create minimal structure
            parsed = self._create_minimal_response(app_name, safe_bundle_id)

        # Ensure all required fields
        parsed["bundle_id"] = safe_bundle_id

        if "app_name" not in parsed:
            parsed["app_name"] = app_name

        # Normalize app names
        if "files" in parsed:
            parsed["files"] = self._normalize_app_names(parsed["files"], app_name)

        # Apply iOS 16 compatibility
        for file in parsed.get("files", []):
            file["content"] = self._ensure_ios16_compatibility(file["content"])

        # Update metrics
        elapsed = (datetime.now() - start_time).total_seconds()
        self._update_response_time(elapsed)

        return parsed

    def _create_minimal_response(self, app_name: str, bundle_id: str) -> Dict:
        """Create minimal response when parsing fails"""

        safe_name = app_name.replace(" ", "")

        return {
            "app_name": app_name,
            "bundle_id": bundle_id,
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
    var body: some View {{
        Text("Welcome to {app_name}!")
            .padding()
    }}
}}"""
                }
            ],
            "features": ["Basic app structure"],
            "parsing_failed": True
        }

    def _update_response_time(self, elapsed: float):
        """Update average response time metric"""

        current_avg = self.performance_metrics["average_response_time"]
        total_calls = self.performance_metrics["total_calls"]

        if total_calls == 1:
            self.performance_metrics["average_response_time"] = elapsed
        else:
            # Calculate new average
            new_avg = ((current_avg * (total_calls - 1)) + elapsed) / total_calls
            self.performance_metrics["average_response_time"] = new_avg