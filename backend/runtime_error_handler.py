import re
from typing import Dict, List, Optional

class RuntimeErrorHandler:
    """Handles runtime errors from user-provided crash logs and automatic detection"""

    def __init__(self, llm_service):
        self.llm_service = llm_service
        # Enhanced with SwiftUI-specific patterns
        self.swiftui_crash_patterns = {
            "environment_keypath": {
                "indicators": [
                    "KeyPath._projectReadOnly",
                    "EnvironmentBox.update",
                    "swift_getAtKeyPath",
                    "closure #1 in EnvironmentBox"
                ],
                "common_causes": [
                    "@Environment(\\.dismiss) on iOS < 15",
                    "Accessing undefined environment values",
                    "Missing environment objects",
                    "Incorrect environment key paths"
                ],
                "fixes": [
                    "Add iOS version checks",
                    "Provide default environment values",
                    "Use @EnvironmentObject correctly",
                    "Fix environment key path syntax"
                ]
            }
        }

    async def analyze_crash_log(self, crash_log: str, project_files: List[Dict]) -> Dict:
        """Analyze crash log and suggest fixes"""

        # Parse crash information
        crash_info = self._parse_crash_log(crash_log)

        # Find the problematic file
        problematic_files = []
        for file in project_files:
            if any(hint in file["path"].lower() for hint in crash_info["file_hints"]):
                problematic_files.append(file)

        if not problematic_files:
            # If no specific file found, include all files for analysis
            problematic_files = project_files

        # Create context for the LLM
        return {
            "crash_type": crash_info["type"],
            "error_message": crash_info["error"],
            "suggested_fix": crash_info["suggested_fix"],
            "files_to_modify": problematic_files,
            "stack_frames": crash_info.get("stack_frames", [])
        }

    def _parse_crash_log(self, crash_log: str) -> Dict:
        """Parse crash log to extract useful information"""

        info = {
            "error": "",
            "location": "",
            "type": "unknown",
            "file_hints": [],
            "suggested_fix": "",
            "stack_frames": []
        }

        crash_lower = crash_log.lower()

        # Check for SwiftUI Environment crashes first (highest priority)
        if "KeyPath._projectReadOnly" in crash_log and "EnvironmentBox" in crash_log:
            info["type"] = "swiftui_environment"
            info["error"] = "SwiftUI Environment KeyPath crash - accessing invalid environment value"
            info["suggested_fix"] = "Check @Environment usage, ensure iOS compatibility, and verify environment keys"

            # Extract stack frames to identify which views are affected
            stack_pattern = r'(\d+)\s+(\S+)\s+0x[0-9a-fA-F]+\s+(.+)'
            matches = re.findall(stack_pattern, crash_log)

            for match in matches:
                frame_info = match[2]
                info["stack_frames"].append(frame_info)

                # Look for specific view names
                if "ContentView" in frame_info:
                    info["file_hints"].append("contentview")
                elif "App" in frame_info and "@main" in crash_log:
                    info["file_hints"].append("app")

            return info

        # Common crash patterns (existing)
        if "unexpectedly found nil" in crash_lower:
            info["type"] = "nil_unwrap"
            info["error"] = "Force unwrapping nil value"
            info["suggested_fix"] = "Use optional binding or nil-coalescing operator"

        elif "unrecognized selector" in crash_lower:
            info["type"] = "missing_method"
            info["error"] = "Method not found"
            info["suggested_fix"] = "Implement the missing method or check method name"

        elif "index out of range" in crash_lower:
            info["type"] = "array_bounds"
            info["error"] = "Array index out of bounds"
            info["suggested_fix"] = "Add bounds checking before array access"

        elif "startofmonth" in crash_lower or "date." in crash_lower:
            info["type"] = "missing_extension"
            info["error"] = "Missing Date extension method"
            info["file_hints"] = ["date", "extension", "contentview"]
            info["suggested_fix"] = "Add Date extension with required computed properties"

        elif "precondition failed" in crash_lower:
            info["type"] = "assertion_failure"
            info["error"] = "Precondition or assertion failed"
            info["suggested_fix"] = "Check the condition that's failing"

        elif "deadlock" in crash_lower or "thread" in crash_lower:
            info["type"] = "threading_issue"
            info["error"] = "Threading or deadlock issue"
            info["suggested_fix"] = "Ensure UI updates happen on main thread"

        # Extract file information
        file_patterns = [
            r'(\w+\.swift):(\d+)',  # FileName.swift:123
            r'in\s+(\w+\.swift)',   # in FileName.swift
            r'(\w+View)\.swift',    # ContentView.swift
        ]

        for pattern in file_patterns:
            matches = re.findall(pattern, crash_log, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    info["file_hints"].append(match[0].lower())
                else:
                    info["file_hints"].append(match.lower())

        # Extract the actual error message
        error_lines = crash_log.split('\n')
        for line in error_lines:
            if 'error:' in line.lower() or 'exception:' in line.lower():
                info["error"] = line.strip()
                break

        return info

    def detect_runtime_error_in_message(self, message: str) -> bool:
        """Check if a message contains a runtime error/crash log"""

        error_indicators = [
            "thread", "crash", "exception", "error:",
            "unexpectedly found nil", "unrecognized selector",
            "index out of range", "precondition failed",
            "fatal error", "terminated", "sigabrt",
            "exc_bad_access", "segmentation fault",
            "KeyPath._projectReadOnly", "EnvironmentBox"  # Add SwiftUI crashes
        ]

        message_lower = message.lower()
        return any(indicator in message_lower for indicator in error_indicators)

    async def generate_swiftui_environment_fix(self, files: List[Dict]) -> List[Dict]:
        """Generate fixes for SwiftUI environment crashes"""

        fixed_files = []

        for file in files:
            content = file["content"]
            original_content = content

            # Fix 1: Replace @Environment(\.dismiss) with iOS 16+ compatible code
            if "@Environment(\\.presentationMode)" in content:
                # Replace with modern iOS 16+ version
                content = re.sub(
                r'@Environment\(\\.presentationMode\)\s+(?:private\s+)?var\s+\w+',
                '@Environment(\\.dismiss) private var dismiss',
                content
                )

                # Fix all dismiss calls
                content = re.sub(
                    r'presentationMode\.wrappedValue\.dismiss\(\)',
                    'dismiss()',
                    content
                )

            # Fix 2: Check for NavigationView and replace with NavigationStack
            if "NavigationView" in content:
                content = content.replace("NavigationView", "NavigationStack")

            # Fix 3: Check for custom environment values without proper setup
            env_pattern = r'@Environment\(\\\.(\w+)\)\s+(?:private\s+)?var\s+(\w+)'
            matches = re.findall(env_pattern, content)

            for env_key, var_name in matches:
                # List of valid built-in environment values for iOS 16+
                valid_keys = [
                    "dismiss", "colorScheme", "locale", "dynamicTypeSize",
                    "sizeCategory", "managedObjectContext", "openURL",
                    "refresh", "scenePhase", "accessibilityEnabled",
                    "horizontalSizeClass", "verticalSizeClass", "displayScale",
                    "isSearching", "searchScopes", "dismissSearch"
                ]

                if env_key not in valid_keys:
                    # This is likely a custom environment value - comment it out
                    old_line = f"@Environment(\\.{env_key})"
                    new_line = f"// TODO: Fix custom environment - {old_line}"
                    content = content.replace(old_line, new_line)

            # Fix 4: Add proper imports if missing
            if "@Environment" in content and "import SwiftUI" not in content:
                content = "import SwiftUI\n\n" + content

            # Fix 5: Ensure main app struct has proper structure for iOS 16+
            if "@main" in content and "WindowGroup" in content:
                # Make sure the app structure is correct
                app_pattern = r'@main\s+struct\s+(\w+):\s*App\s*{'
                match = re.search(app_pattern, content)
                if match:
                    app_name = match.group(1)
                    # Ensure body property exists with proper Scene type
                    if "var body: some Scene" not in content:
                        # Add it after the struct declaration
                        insert_pos = match.end()
                        body_code = "\n    var body: some Scene {\n        WindowGroup {\n            ContentView()\n        }\n    }\n"
                        content = content[:insert_pos] + body_code + content[insert_pos:]

            # Fix 6: Add iOS 16 availability if using modern features
            if "@Environment(\\.dismiss)" in content and "@available" not in content:
                # Check if this is a View struct
                view_pattern = r'struct\s+(\w+)\s*:\s*View\s*{'
                match = re.search(view_pattern, content)
                if match:
                    # Add availability attribute before struct
                    content = re.sub(
                        r'(struct\s+' + match.group(1) + r'\s*:\s*View\s*{)',
                        r'@available(iOS 16.0, *)\n\1',
                        content
                    )

            if content != original_content:
                fixed_files.append({
                    "path": file["path"],
                    "content": content
                })
            else:
                fixed_files.append(file)

        return fixed_files