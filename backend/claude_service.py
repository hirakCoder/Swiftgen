import os
import json
import httpx
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import asyncio
from datetime import datetime
import random
import hashlib
import re

load_dotenv()

class ClaudeService:
    def __init__(self):
        self.api_key = os.getenv("CLAUDE_API_KEY", "")
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-opus-20240229"
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        self.system_prompt = """You are SwiftGen AI, an expert iOS developer. Create production-ready SwiftUI apps.

CRITICAL RULES - FOLLOW EXACTLY:
1. Use @Environment(\.dismiss) NOT @Environment(\.presentationMode) for iOS 15+
2. ALWAYS use double quotes " for strings, NEVER single quotes '
3. For dismiss functionality use: dismiss() NOT presentationMode.wrappedValue.dismiss()
4. Never use double double-quotes like "" at the start/end of strings
5. Import SwiftUI at the top of every file
6. Bundle IDs must not contain spaces - only lowercase letters, numbers, and dots
7. ALWAYS return ONLY valid JSON - no explanatory text before or after the JSON
8. CRITICAL: Use the EXACT bundle ID provided in the prompt - do NOT use generic IDs
9. ENSURE all files have actual content - never return empty content strings

MODERN SWIFTUI PATTERNS:
✅ CORRECT: @Environment(\.dismiss) private var dismiss
❌ WRONG: @Environment(\.presentationMode) var presentationMode

✅ CORRECT: Button("Back") { dismiss() }
❌ WRONG: Button("Back") { presentationMode.wrappedValue.dismiss() }

✅ CORRECT: Text("Hello World")
❌ WRONG: Text('Hello World') or Text(""Hello World"")

CRITICAL: Return ONLY the JSON object. Do NOT include any explanatory text like "Here is the code" or "I've fixed the issue". Start your response with { and end with }."""

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

    def _ensure_files_have_content(self, response: Dict) -> Dict:
        """Ensure all files have actual content"""
        if "files" in response:
            for file in response["files"]:
                if not file.get("content") or not file["content"].strip():
                    # Generate default content based on file path
                    if "App.swift" in file.get("path", ""):
                        app_name = response.get("app_name", "MyApp").replace(" ", "")
                        file["content"] = f"""import SwiftUI

@main
struct {app_name}App: App {{
    var body: some Scene {{
        WindowGroup {{
            ContentView()
        }}
    }}
}}"""
                    elif "ContentView.swift" in file.get("path", ""):
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
        return response

    async def generate_ios_app(self, description: str, app_name: Optional[str] = None) -> Dict:
        """Generate iOS app using Claude's full intelligence"""

        if not self.api_key:
            raise ValueError("Claude API key is required")

        try:
            # Generate safe bundle ID
            safe_bundle_id = self._create_safe_bundle_id(app_name) if app_name else self._create_safe_bundle_id("app")

            print(f"[CLAUDE SERVICE] Generating app with bundle ID: {safe_bundle_id}")

            prompt = self._create_intelligent_generation_prompt(description, app_name, safe_bundle_id)

            # Call Claude API with retry
            max_retries = 3
            last_error = None

            for attempt in range(max_retries):
                try:
                    response = await self._call_claude_api(prompt)

                    if response and "files" in response:
                        # CRITICAL FIX: Ensure files have content
                        response = self._ensure_files_have_content(response)

                        # CRITICAL FIX: ALWAYS override bundle ID to ensure it's correct
                        response["bundle_id"] = safe_bundle_id

                        # Let Claude determine the app name from context
                        actual_app_name = response.get("app_name", app_name or "App")

                        print(f"[CLAUDE SERVICE] Generated response structure:")
                        print(f"  - App name: {actual_app_name}")
                        print(f"  - Bundle ID: {safe_bundle_id}")
                        print(f"  - Number of files: {len(response.get('files', []))}")

                        # Log file details
                        for i, file in enumerate(response.get("files", [])):
                            print(f"  - File {i+1}: {file.get('path', 'unknown')} ({len(file.get('content', ''))} chars)")

                        # CRITICAL: Validate the response doesn't have generic bundle ID
                        if response.get("bundle_id") == "com.swiftgen.myapp" and app_name and app_name.lower() != "myapp":
                            print(f"WARNING: Claude returned generic bundle ID, overriding with: {safe_bundle_id}")
                            response["bundle_id"] = safe_bundle_id

                        return response

                except Exception as e:
                    last_error = str(e)
                    if attempt < max_retries - 1:
                        print(f"Attempt {attempt + 1} failed: {str(e)}, retrying...")
                        await asyncio.sleep(2)
                        continue

            raise Exception(f"Failed to generate app after {max_retries} attempts. Last error: {last_error}")

        except Exception as e:
            print(f"Error in app generation: {str(e)}")
            raise

    async def modify_ios_app(self, app_name: str, original_description: str,
                             modification_request: str, existing_files: List[Dict],
                             existing_bundle_id: Optional[str] = None) -> Dict:
        """Let Claude intelligently modify the app"""

        # Handle manual edits
        if isinstance(existing_files, dict) and existing_files.get('manual_edit'):
            edited_files = existing_files.get('edited_files', [])

            # Use existing bundle ID or create safe one
            safe_bundle_id = existing_bundle_id or self._create_safe_bundle_id(app_name)

            return {
                "files": edited_files,
                "features": ["Manual code edit applied"],
                "bundle_id": safe_bundle_id,
                "app_name": app_name
            }

        if not self.api_key:
            raise ValueError("Claude API key is required for modifications")

        try:
            # Use existing bundle ID or create safe one
            safe_bundle_id = existing_bundle_id or self._create_safe_bundle_id(app_name)

            prompt = self._create_intelligent_modification_prompt(
                app_name, original_description, modification_request, existing_files, safe_bundle_id
            )

            response = await self._call_claude_api(prompt)

            if response:
                # Ensure files have content
                response = self._ensure_files_have_content(response)

                # Ensure the response has the correct structure
                validated_response = self._validate_modification_response(response, existing_files, app_name, safe_bundle_id)

                if validated_response and "files" in validated_response:
                    print(f"Claude applied modifications: {validated_response.get('modification_summary', 'Changes applied')}")
                    print(f"Using bundle ID: {validated_response['bundle_id']}")
                    return validated_response
                else:
                    raise Exception("Invalid modification response from Claude")
            else:
                raise Exception("Failed to get modification response from Claude")

        except Exception as e:
            print(f"Error in app modification: {str(e)}")
            raise

    def _validate_modification_response(self, response: Dict, existing_files: List[Dict],
                                        app_name: str, safe_bundle_id: str) -> Dict:
        """Validate and fix the modification response structure"""

        if "files" not in response:
            response["files"] = existing_files

        # ALWAYS use the safe bundle ID
        response["bundle_id"] = safe_bundle_id

        if "app_name" not in response:
            response["app_name"] = app_name

        if "features" not in response:
            response["features"] = ["Modifications applied"]

        return response

    def _create_intelligent_generation_prompt(self, description: str, app_name: Optional[str],
                                              safe_bundle_id: str) -> str:
        """Create a prompt that unleashes Claude's creativity with proper string formatting"""

        unique_seed = hashlib.md5(f"{datetime.now().isoformat()}{description}{random.random()}".encode()).hexdigest()[:8]

        prompt = f"""Create a UNIQUE SwiftUI iOS app based on this request: "{description}"

CRITICAL REQUIREMENTS:
1. Create EXACTLY what the user asked for - analyze their specific needs
2. Make it UNIQUE - even if someone else asks for a similar app, yours should be different
3. Add creative touches, unique features, and thoughtful UX that sets this app apart
4. Use modern SwiftUI patterns (iOS 15+) and best practices
5. Think beyond basic functionality - what would make this app exceptional?
6. CRITICAL: Use EXACTLY this bundle ID: {safe_bundle_id} - DO NOT use "com.swiftgen.myapp"
7. ENSURE all files have actual Swift code content - no empty strings

UNIQUENESS FACTORS TO CONSIDER:
- Visual design and color schemes
- Layout and navigation patterns  
- Additional helpful features the user didn't explicitly ask for
- Smooth animations and transitions
- Thoughtful edge cases handling
- Accessibility features
- Performance optimizations

TECHNICAL REQUIREMENTS:
- @Environment(\.dismiss) private var dismiss (NOT presentationMode)
- Text("Hello") with double quotes (NOT 'Hello' or ""Hello"")
- Ensure all interactive elements (buttons, taps, gestures) have proper implementations
- All calculations and state changes must update the UI
- Every file must have complete, working Swift code

IMPORTANT: Bundle ID must be exactly: {safe_bundle_id}
DO NOT USE: com.swiftgen.myapp

UNIQUE SEED FOR VARIATION: {unique_seed}

Return ONLY a valid JSON object (no explanatory text):
{{
    "files": [
        {{
            "path": "Sources/App.swift",
            "content": "// Your COMPLETE unique implementation with actual Swift code"
        }},
        {{
            "path": "Sources/ContentView.swift", 
            "content": "// Your COMPLETE unique implementation with actual Swift code"
        }}
        // Add more files as needed for your unique architecture
    ],
    "features": ["List of unique features you implemented"],
    "bundle_id": "{safe_bundle_id}",
    "app_name": "{app_name or 'Your chosen app name'}",
    "unique_aspects": "What makes this implementation special and different"
}}"""

        return prompt

    def _create_intelligent_modification_prompt(self, app_name: str, original_description: str,
                                                modification_request: str, existing_files: List[Dict],
                                                safe_bundle_id: str) -> str:
        """Create a prompt for intelligent modifications with proper string formatting"""

        code_context = "\n\n".join([
            f"File: {file['path']}\n```swift\n{file['content']}\n```"
            for file in existing_files
        ])

        # Analyze the modification request to provide intelligent context
        additional_instructions = ""

        # Generic pattern detection for common issues
        request_lower = modification_request.lower()

        if any(phrase in request_lower for phrase in ["not work", "doesn't work", "broken", "not functioning", "nothing happens"]):
            if "button" in request_lower or "click" in request_lower or "tap" in request_lower:
                additional_instructions = """
INTELLIGENT ANALYSIS: User reports interactive element not functioning.

GENERIC DEBUGGING APPROACH:
1. Identify the non-functioning UI element in the current code
2. Trace its action/binding to understand what SHOULD happen
3. Common issues to check:
   - Empty or missing action closures
   - Functions that don't modify any @State/@Published variables
   - Missing bindings between UI and data
   - Calculations that don't update display values
   
4. Fix by ensuring:
   - Actions have actual implementation
   - State changes trigger UI updates
   - All user interactions produce visible results
   - Data flow is properly connected

IMPORTANT: Analyze the SPECIFIC app context and fix accordingly. Don't assume app type.
"""
            elif "display" in request_lower or "show" in request_lower or "update" in request_lower:
                additional_instructions = """
INTELLIGENT ANALYSIS: User reports display/update issues.

Investigate:
1. Data binding connections
2. @State/@Published variable updates
3. View refresh triggers
4. Conditional rendering logic
"""
            elif "calculate" in request_lower or "compute" in request_lower:
                additional_instructions = """
INTELLIGENT ANALYSIS: User reports calculation issues.

Ensure:
1. Input validation and conversion
2. Calculation logic correctness
3. Result storage in observable properties
4. UI updates after calculation
"""

        prompt = f"""Modify this iOS app based on the request: "{modification_request}"

Current app: {app_name}
Original purpose: {original_description}

Current code:
{code_context}

{additional_instructions}

Make the requested changes and return the COMPLETE modified code.

CRITICAL SYNTAX RULES:
- Use double quotes " for all strings (NOT single quotes ')
- Use @Environment(\.dismiss) NOT presentationMode
- Fix any syntax errors you see
- Ensure all Button actions actually perform their intended function
- Every file must have complete, working Swift code

IMPORTANT: Keep the EXACT SAME bundle ID: {safe_bundle_id}
NO SPACES IN BUNDLE ID!

Return ONLY a valid JSON object (no explanatory text) with ALL files:
{{
    "files": [
        {{
            "path": "Sources/App.swift",
            "content": "// Complete modified code with PROPER SYNTAX and actual content"
        }},
        {{
            "path": "Sources/ContentView.swift",
            "content": "// Complete modified code with PROPER SYNTAX and actual content"
        }}
    ],
    "features": ["Original features", "NEW: Changes made"],
    "bundle_id": "{safe_bundle_id}",
    "app_name": "{app_name}",
    "modification_summary": "What was changed"
}}"""

        return prompt

    async def _call_claude_api(self, prompt: str) -> Optional[Dict]:
        """Make API call to Claude with improved error handling"""

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "system": self.system_prompt,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "max_tokens": 4096,
                        "temperature": 0.7
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result['content'][0]['text']

                    # DEBUG: Print Claude's response
                    print("\n=== CLAUDE'S RESPONSE (first 1000 chars) ===")
                    print(content[:1000])
                    print("=== END RESPONSE PREVIEW ===\n")

                    # Try to extract JSON
                    parsed = self._extract_json_from_response(content)

                    if parsed and "files" in parsed and len(parsed["files"]) > 0:
                        # Log the actual files we're returning
                        print(f"[CLAUDE SERVICE] Successfully parsed {len(parsed['files'])} files:")
                        for file in parsed["files"]:
                            print(f"  - {file['path']} ({len(file.get('content', ''))} chars)")
                            # Log first 200 chars of content for debugging
                            content_preview = file.get('content', '')[:200].replace('\n', '\\n')
                            print(f"    Preview: {content_preview}...")

                        # Ensure files have content
                        parsed = self._ensure_files_have_content(parsed)

                        return parsed
                    else:
                        # If JSON parsing fails, try to construct from content
                        print("Failed to parse as JSON, attempting to extract code...")
                        constructed = self._construct_json_from_content(content)
                        if constructed and "files" in constructed:
                            print(f"Constructed {len(constructed['files'])} files from content")
                            constructed = self._ensure_files_have_content(constructed)
                            return constructed
                        else:
                            raise Exception("Could not extract valid app data from response")

                else:
                    print(f"Claude API error: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None

            except httpx.TimeoutException:
                print("Request to Claude timed out")
                raise
            except Exception as e:
                print(f"Error calling Claude API: {str(e)}")
                raise

    def _extract_json_from_response(self, content: str) -> Optional[Dict]:
        """Extract and parse JSON from Claude's response - ENHANCED VERSION"""

        # Remove any text before the JSON
        content = content.strip()

        # Method 1: Direct parse (if response is pure JSON)
        try:
            result = json.loads(content)
            # CRITICAL: Validate bundle ID
            if "bundle_id" in result and result["bundle_id"] == "com.swiftgen.myapp":
                print("WARNING: Claude returned generic bundle ID")
            return result
        except Exception as e:
            print(f"Direct JSON parse failed: {e}")

        # Method 2: Find JSON after common prefixes
        # Claude often prefixes with explanatory text
        common_prefixes = [
            "Here is the modified code",
            "Here is the complete modified code",
            "Here's the fixed code",
            "I'll fix",
            "Let me fix",
            "Here is the fixed",
            "Here are the fixed files",
            "Fixed the",
            "I've fixed",
            "Here is a unique",
            "Here's a unique",
            "I'll create",
            "Let me create"
        ]

        for prefix in common_prefixes:
            if content.lower().startswith(prefix.lower()):
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
            # Find the first { that looks like JSON start
            json_start = content.find('{')
            if json_start >= 0:
                # Use proper brace matching to find the end
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

    def _construct_json_from_content(self, content: str) -> Optional[Dict]:
        """Construct JSON from Claude's response when JSON parsing fails"""

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
        app_name = "MyApp"

        # Try to find app name in various ways
        patterns = [
            r'struct\s+(\w+)App\s*:\s*App',
            r'"app_name":\s*"([^"]+)"',
            r'named?\s+["\']*([A-Za-z][A-Za-z0-9\s]+)["\']*',
            r'called?\s+["\']*([A-Za-z][A-Za-z0-9\s]+)["\']*'
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                app_name = match.group(1).strip()
                break

        # Create safe bundle ID
        safe_bundle_id = self._create_safe_bundle_id(app_name)

        return {
            "files": files,
            "features": ["Generated from Claude response"],
            "bundle_id": safe_bundle_id,
            "app_name": app_name,
            "unique_aspects": "AI-generated implementation"
        }

    async def analyze_build_errors(self, errors: List[str], project_files: List[Dict]) -> Dict:
        """Let Claude analyze and fix build errors - THIS IS THE KEY METHOD"""

        if not self.api_key:
            print("No Claude API key - cannot fix build errors intelligently")
            return {
                "files": project_files,
                "fixes_applied": ["No API key available"]
            }

        # Create a comprehensive prompt for Claude to fix the errors
        error_text = "\n".join(errors)

        # Include ALL files that have errors
        files_with_errors = []
        for file in project_files:
            # Check if this file is mentioned in any error
            if any(file["path"] in error for error in errors):
                files_with_errors.append(file)

        # If no specific files found, include all files
        if not files_with_errors:
            files_with_errors = project_files

        code_context = "\n\n".join([
            f"File: {file['path']}\n```swift\n{file['content']}\n```"
            for file in files_with_errors
        ])

        prompt = f"""You are an expert Swift developer. Fix these Swift compilation errors.

BUILD ERRORS:
{error_text}

CURRENT CODE WITH ERRORS:
{code_context}

ANALYSIS:
1. Look at each error carefully
2. Understand what's causing it
3. Apply the correct fix

COMMON FIXES:
- "generic parameter 'T' could not be inferred @Environment(.presentationMode)" → Use @Environment(\.dismiss) private var dismiss
- "single-quoted string literal found" → Replace ALL single quotes ' with double quotes "
- "unterminated string literal" → Ensure all strings have matching quotes
- TextField("text"", ...) → TextField("text", ...)

Return ONLY a JSON object with ALL the files (fixed) and ensure each file has actual content:
{{
    "files": [
        {{
            "path": "Sources/ContentView.swift",
            "content": "// COMPLETE FIXED CODE HERE - not empty!"
        }}
        // Include ALL files that need fixes
    ],
    "fixes_applied": [
        "Replaced presentationMode with dismiss",
        "Fixed single quotes to double quotes",
        // List each fix you made
    ]
}}

IMPORTANT: Return the COMPLETE fixed code for each file, not just snippets. Every file must have actual Swift code content."""

        try:
            print("Sending errors to Claude for intelligent fixing...")
            response = await self._call_claude_api(prompt)

            if response and "files" in response:
                # Ensure files have content
                response = self._ensure_files_have_content(response)
                print(f"Claude fixed errors: {response.get('fixes_applied', [])}")
                return response
            else:
                print("Claude response didn't contain fixed files")
                return {
                    "files": project_files,
                    "fixes_applied": ["Claude couldn't parse the errors"]
                }
        except Exception as e:
            print(f"Error calling Claude for fixes: {e}")
            return {
                "files": project_files,
                "fixes_applied": [f"Error calling Claude: {str(e)}"]
            }