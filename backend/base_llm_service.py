import json
import re
import os
from typing import Dict, List, Optional, Tuple
import hashlib
from datetime import datetime
import random

class BaseLLMService:
    """Base class for all LLM services with common functionality"""

    def __init__(self):
        self.common_prefixes = [
            "Here is", "Here's", "I'll", "Let me", "I've", "Fixed",
            "Created", "Modified", "Updated", "Generated"
        ]

    def _create_safe_bundle_id(self, app_name: str) -> str:
        """Create a safe bundle ID from app name - NO SPACES ALLOWED"""
        # Remove all non-alphanumeric characters and convert to lowercase
        safe_name = re.sub(r'[^a-zA-Z0-9]', '', app_name).lower()

        # Ensure it starts with a letter
        if safe_name and not safe_name[0].isalpha():
            safe_name = 'app' + safe_name

        # Fallback if empty
        if not safe_name:
            safe_name = 'myapp'

        # Ensure reasonable length
        safe_name = safe_name[:20]

        return f"com.swiftgen.{safe_name}"

    def _extract_json_from_response(self, content: str) -> Optional[Dict]:
        """Extract and parse JSON from LLM response - UNIVERSAL VERSION"""

        # Remove any text before the JSON
        content = content.strip()

        # Method 1: Direct parse (if response is pure JSON)
        try:
            return json.loads(content)
        except Exception as e:
            print(f"Direct JSON parse failed: {e}")

        # Method 2: Find JSON after common prefixes
        for prefix in self.common_prefixes:
            if any(content.lower().startswith(p.lower()) for p in [prefix, f"{prefix} "]):
                # Find the first { after the prefix
                json_start = content.find('{')
                if json_start > 0:
                    try:
                        json_end = self._find_matching_brace(content, json_start)
                        if json_end > json_start:
                            json_str = content[json_start:json_end + 1]
                            return json.loads(json_str)
                    except Exception as e:
                        print(f"JSON parse after prefix '{prefix}' failed: {e}")

        # Method 3: Find JSON in markdown
        try:
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                if json_end > json_start:
                    json_str = content[json_start:json_end].strip()
                    return json.loads(json_str)
        except Exception as e:
            print(f"Markdown JSON parse failed: {e}")

        # Method 4: Find raw JSON object with proper brace matching
        try:
            json_start = content.find('{')
            if json_start >= 0:
                json_end = self._find_matching_brace(content, json_start)
                if json_end > json_start:
                    json_str = content[json_start:json_end + 1]
                    result = json.loads(json_str)

                    # Validate it has the expected structure
                    if "files" in result and isinstance(result["files"], list):
                        return result
        except Exception as e:
            print(f"Raw JSON parse with brace matching failed: {e}")

        # Method 5: Try to find JSON by looking for "files" array pattern
        try:
            files_pattern = r'"files"\s*:\s*\['
            match = re.search(files_pattern, content)
            if match:
                # Backtrack to find the opening brace
                for i in range(match.start(), -1, -1):
                    if content[i] == '{':
                        json_start = i
                        json_end = self._find_matching_brace(content, json_start)
                        if json_end > json_start:
                            json_str = content[json_start:json_end + 1]
                            return json.loads(json_str)
        except Exception as e:
            print(f"Pattern-based JSON parse failed: {e}")

        return None

    def _find_matching_brace(self, content: str, start_pos: int) -> int:
        """Find the matching closing brace for an opening brace"""
        if start_pos >= len(content) or content[start_pos] != '{':
            return -1

        brace_count = 0
        in_string = False
        escape_next = False

        for i in range(start_pos, len(content)):
            char = content[i]

            if escape_next:
                escape_next = False
                continue

            if char == '\\':
                escape_next = True
                continue

            if char == '"' and not in_string:
                in_string = True
            elif char == '"' and in_string:
                in_string = False
            elif not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        return i

        return -1

    def _ensure_file_has_content(self, file: Dict, app_name: str) -> Dict:
        """Ensure a single file has actual content"""
        if not file.get("content") or not file["content"].strip():
            # Generate default content based on file path
            path = file.get("path", "")

            if "App.swift" in path:
                safe_app_name = app_name.replace(" ", "")
                file["content"] = f"""import SwiftUI

@main
struct {safe_app_name}App: App {{
    var body: some Scene {{
        WindowGroup {{
            ContentView()
        }}
    }}
}}"""
            elif "ContentView.swift" in path:
                file["content"] = """import SwiftUI

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
            else:
                # Generic Swift file content
                struct_name = os.path.basename(path).replace('.swift', '')
                file["content"] = f"""import SwiftUI

struct {struct_name}: View {{
    var body: some View {{
        Text("{struct_name}")
    }}
}}"""

        return file

    def _normalize_file_structure(self, parsed_json: Dict, safe_bundle_id: str) -> Dict:
        """Normalize different file structure formats from various LLMs"""

        normalized = {
            "bundle_id": safe_bundle_id,  # ALWAYS use the safe bundle ID
            "app_name": parsed_json.get("app_name", "MyApp"),
            "features": parsed_json.get("features", []),
            "unique_aspects": parsed_json.get("unique_aspects", ""),
            "files": []
        }

        # Handle different file formats
        if "files" in parsed_json:
            for file in parsed_json["files"]:
                # Skip non-Swift files
                if not file.get("path", "").endswith(".swift"):
                    continue

                # Handle both formats: {path, content} and {name, contents}
                if "path" in file and "content" in file:
                    # Standard format
                    # CRITICAL: Ensure file has content
                    file = self._ensure_file_has_content(file, normalized["app_name"])
                    normalized["files"].append({
                        "path": file["path"],
                        "content": file["content"]
                    })
                elif "name" in file and ("contents" in file or "content" in file):
                    # Alternative format from some LLMs
                    filename = file["name"]
                    content = file.get("contents", file.get("content", ""))

                    # Determine path based on filename
                    if filename.endswith('.swift'):
                        if '@main' in content or 'App:' in content:
                            path = "Sources/App.swift"
                        else:
                            # Use filename without extension for path
                            path = f"Sources/{filename}"
                    else:
                        path = f"Sources/{filename}.swift"

                    # Create file dict and ensure content
                    file_dict = {"path": path, "content": content}
                    file_dict = self._ensure_file_has_content(file_dict, normalized["app_name"])

                    normalized["files"].append({
                        "path": file_dict["path"],
                        "content": file_dict["content"]
                    })
                else:
                    print(f"Warning: Unknown file format: {file}")

        # Ensure we have at least the main files
        self._ensure_required_files(normalized)

        # CRITICAL: Log what bundle ID we're using
        print(f"BaseLLMService normalized with bundle ID: {normalized['bundle_id']}")
        print(f"Number of files after normalization: {len(normalized['files'])}")

        # Log file details
        for i, file in enumerate(normalized['files']):
            print(f"  File {i+1}: {file['path']} ({len(file.get('content', ''))} chars)")

        return normalized

    def _ensure_required_files(self, normalized: Dict):
        """Ensure we have the required files for an iOS app"""

        # Check if we have an app main file
        has_main = any('@main' in f.get('content', '') for f in normalized['files'])

        if not has_main and normalized['files']:
            # Find the first file and make it the main app file
            app_name = normalized['app_name'].replace(' ', '')
            main_content = f"""import SwiftUI

@main
struct {app_name}App: App {{
    var body: some Scene {{
        WindowGroup {{
            ContentView()
        }}
    }}
}}"""

            normalized['files'].insert(0, {
                "path": "Sources/App.swift",
                "content": main_content
            })

        # Check if we have a ContentView
        has_content_view = any('ContentView' in f.get('content', '') for f in normalized['files'])

        if not has_content_view:
            content_view_content = """import SwiftUI

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

            normalized['files'].append({
                "path": "Sources/ContentView.swift",
                "content": content_view_content
            })

    def _construct_json_from_content(self, content: str) -> Optional[Dict]:
        """Construct JSON from LLM response when JSON parsing fails"""

        files = []

        # Look for Swift code blocks
        swift_blocks = re.findall(r'```swift(.*?)```', content, re.DOTALL)

        print(f"Found {len(swift_blocks)} Swift code blocks")

        if swift_blocks:
            for i, code in enumerate(swift_blocks):
                code = code.strip()

                # Determine file type
                if "@main" in code or "App:" in code:
                    files.append({
                        "path": "Sources/App.swift",
                        "content": code
                    })
                elif "ContentView" in code:
                    files.append({
                        "path": "Sources/ContentView.swift",
                        "content": code
                    })
                else:
                    # Try to get struct name
                    struct_match = re.search(r'struct\s+(\w+)\s*:', code)
                    if struct_match:
                        struct_name = struct_match.group(1)
                        files.append({
                            "path": f"Sources/{struct_name}.swift",
                            "content": code
                        })
                    else:
                        files.append({
                            "path": f"Sources/File{i}.swift",
                            "content": code
                        })

        if not files:
            print("No Swift code blocks found")
            return None

        # Extract app name
        app_name = self._extract_app_name(content)

        return {
            "files": files,
            "features": ["Generated from code blocks"],
            "app_name": app_name,
            "unique_aspects": "AI-generated implementation"
        }

    def _extract_app_name(self, content: str) -> str:
        """Extract app name from content"""

        patterns = [
            r'struct\s+(\w+)App\s*:\s*App',
            r'"app_name":\s*"([^"]+)"',
            r'named?\s+["\']*([A-Za-z][A-Za-z0-9\s]+)["\']*',
            r'called?\s+["\']*([A-Za-z][A-Za-z0-9\s]+)["\']*'
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return "MyApp"

    def _create_unique_seed(self) -> str:
        """Create a unique seed for variation"""
        return hashlib.md5(
            f"{datetime.now().isoformat()}{random.random()}".encode()
        ).hexdigest()[:8]

    async def parse_llm_response(self, content: str, safe_bundle_id: str) -> Dict:
        """Universal method to parse any LLM response"""

        print(f"BaseLLMService parsing response with bundle ID: {safe_bundle_id}")

        # Try to extract JSON
        parsed = self._extract_json_from_response(content)

        if parsed:
            # Normalize the structure
            normalized = self._normalize_file_structure(parsed, safe_bundle_id)

            # Log success
            print(f"Successfully parsed LLM response:")
            print(f"  - Files: {len(normalized['files'])}")
            print(f"  - App Name: {normalized['app_name']}")
            print(f"  - Bundle ID: {normalized['bundle_id']}")

            # CRITICAL: Verify we're returning the correct bundle ID
            if normalized['bundle_id'] != safe_bundle_id:
                print(f"WARNING: Bundle ID mismatch! Expected {safe_bundle_id}, got {normalized['bundle_id']}")
                normalized['bundle_id'] = safe_bundle_id

            # CRITICAL: Verify all files have content
            for i, file in enumerate(normalized['files']):
                if not file.get('content') or not file['content'].strip():
                    print(f"WARNING: File {i+1} ({file.get('path', 'unknown')}) has no content!")
                    file = self._ensure_file_has_content(file, normalized['app_name'])
                    normalized['files'][i] = file

            return normalized
        else:
            # Try to construct from content
            print("Failed to parse as JSON, attempting to extract code...")
            constructed = self._construct_json_from_content(content)

            if constructed:
                normalized = self._normalize_file_structure(constructed, safe_bundle_id)
                print(f"Constructed {len(normalized['files'])} files from content")

                # CRITICAL: Ensure bundle ID is correct
                normalized['bundle_id'] = safe_bundle_id

                # CRITICAL: Ensure all files have content
                for i, file in enumerate(normalized['files']):
                    if not file.get('content') or not file['content'].strip():
                        file = self._ensure_file_has_content(file, normalized['app_name'])
                        normalized['files'][i] = file

                return normalized
            else:
                raise Exception("Could not extract valid app data from response")