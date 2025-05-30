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

        # System prompt that makes Claude understand its role
        self.system_prompt = """You are SwiftGen AI, the world's most creative iOS app developer. You have deep expertise in:
- Swift 5.9 and SwiftUI
- Creating UNIQUE, beautiful iOS apps that stand out
- Understanding user intent perfectly
- Apple's Human Interface Guidelines
- Modern app design trends and animations

Your goal is to create iOS apps that are:
1. EXACTLY what the user asked for (not generic templates)
2. UNIQUE - even if two users ask for "timer app", they should get completely different implementations
3. Production-ready with proper error handling
4. Visually stunning with thoughtful animations
5. Following iOS best practices

You think creatively and never produce cookie-cutter solutions. Each app you create should feel special and crafted with care."""

    async def generate_ios_app(self, description: str, app_name: Optional[str] = None) -> Dict:
        """Generate iOS app using Claude's full intelligence"""

        # Let Claude handle EVERYTHING - app name extraction, understanding, generation
        if not self.api_key or self.api_key == "YOUR_CLAUDE_API_KEY_HERE":
            raise ValueError("Claude API key is required. Please set CLAUDE_API_KEY in .env file")

        try:
            # Create a prompt that lets Claude shine
            prompt = self._create_intelligent_generation_prompt(description, app_name)

            # Call Claude API
            response = await self._call_claude_api(prompt)

            if response and "files" in response:
                print(f"Claude generated: {response.get('app_name')} with features: {response.get('features', [])}")
                return response
            else:
                raise Exception("Failed to generate app. Please try with a clearer description.")

        except Exception as e:
            print(f"Error in app generation: {str(e)}")
            raise

    async def modify_ios_app(self, app_name: str, original_description: str,
                           modification_request: str, existing_files: List[Dict]) -> Dict:
        """Let Claude intelligently modify the app"""

        # Handle manual edits
        if isinstance(existing_files, dict) and existing_files.get('manual_edit'):
            return {
                "files": existing_files.get('edited_files', []),
                "features": ["Manual code edit applied"],
                "bundle_id": f"com.swiftgen.{app_name.lower().replace(' ', '')}",
                "app_name": app_name
            }

        if not self.api_key or self.api_key == "YOUR_CLAUDE_API_KEY_HERE":
            raise ValueError("Claude API key is required for modifications")

        try:
            # Let Claude understand and apply the modifications
            prompt = self._create_intelligent_modification_prompt(
                app_name, original_description, modification_request, existing_files
            )

            response = await self._call_claude_api(prompt)

            if response:
                # Ensure the response has the correct structure
                validated_response = self._validate_modification_response(response, existing_files, app_name)

                if validated_response and "files" in validated_response:
                    print(f"Claude applied modifications: {validated_response.get('modification_summary', 'Changes applied')}")
                    return validated_response
                else:
                    raise Exception("Invalid modification response from Claude")
            else:
                raise Exception("Failed to get modification response from Claude")

        except Exception as e:
            print(f"Error in app modification: {str(e)}")
            raise

    def _validate_modification_response(self, response: Dict, existing_files: List[Dict], app_name: str) -> Dict:
        """Validate and fix the modification response structure"""

        # Ensure we have a files array
        if "files" not in response:
            print("Warning: No 'files' key in response, attempting to construct from existing files")
            response["files"] = existing_files

        # Validate each file has required fields
        validated_files = []

        for file in response.get("files", []):
            # Check if it's a properly structured file
            if isinstance(file, dict):
                # Ensure it has both path and content
                if "path" in file and "content" in file:
                    validated_files.append(file)
                elif "content" in file:
                    # Try to infer path from existing files
                    print(f"Warning: File missing 'path', attempting to match by content")
                    matched = False
                    for existing_file in existing_files:
                        # Simple matching - in production, this could be more sophisticated
                        if len(file["content"]) > 100 and existing_file["path"].endswith(".swift"):
                            file["path"] = existing_file["path"]
                            validated_files.append(file)
                            matched = True
                            break

                    if not matched:
                        # Default path
                        file["path"] = "Sources/ModifiedFile.swift"
                        validated_files.append(file)
                else:
                    print(f"Warning: Invalid file structure: {file}")
            else:
                print(f"Warning: File is not a dictionary: {file}")

        # If no valid files were found, use existing files
        if not validated_files:
            print("Warning: No valid files in response, using existing files")
            validated_files = existing_files

        # Ensure other required fields
        if "bundle_id" not in response:
            response["bundle_id"] = f"com.swiftgen.{app_name.lower().replace(' ', '')}"

        if "app_name" not in response:
            response["app_name"] = app_name

        if "features" not in response:
            response["features"] = ["Modifications applied"]

        response["files"] = validated_files

        return response

    def _create_intelligent_generation_prompt(self, description: str, app_name: Optional[str]) -> str:
        """Create a prompt that unleashes Claude's creativity with better understanding"""

        # Generate uniqueness factors
        time_context = datetime.now()
        unique_seed = hashlib.md5(f"{time_context.isoformat()}{description}{random.random()}".encode()).hexdigest()[:8]

        # Time-based creativity hints
        hour = time_context.hour
        if hour < 6:
            time_hint = "late night creative energy - think outside the box"
        elif hour < 12:
            time_hint = "morning freshness - bright and energizing"
        elif hour < 17:
            time_hint = "afternoon productivity - focused and efficient"
        elif hour < 21:
            time_hint = "evening relaxation - smooth and calming"
        else:
            time_hint = "night time sophistication - elegant and refined"

        # Random design inspiration
        design_inspirations = [
            "Apple's latest iOS design language with subtle depth",
            "Minimalist Japanese design principles",
            "Bold Memphis design with geometric shapes",
            "Organic, nature-inspired interfaces",
            "Retro-futuristic cyberpunk aesthetics",
            "Swiss design with perfect typography",
            "Playful material design with delightful animations",
            "Luxury brand design language",
            "Video game-inspired interactive elements",
            "Magazine editorial layouts"
        ]

        design_inspiration = random.choice(design_inspirations)

        # Color mood
        color_moods = [
            "vibrant gradients that catch the eye",
            "sophisticated monochrome with accent colors",
            "nature-inspired earth tones",
            "bold contrasting colors",
            "soft pastels with gentle transitions",
            "deep, rich jewel tones",
            "tech-inspired neon accents",
            "calming ocean palette"
        ]

        color_mood = random.choice(color_moods)

        # Analyze the request to understand intent better
        desc_lower = description.lower()
        clarification = ""

        # Check for theme/style references
        if "theme" in desc_lower or "style" in desc_lower or "like" in desc_lower:
            clarification = """
IMPORTANT CLARIFICATION:
If the user mentions "X theme" or "X style" or "like X", they usually mean:
- Create the type of app they explicitly mentioned (menu, calculator, timer, etc.)
- Style it visually similar to X (colors, layout, design patterns)
- NOT create a clone of X

For example:
- "menu app with Uber Eats theme" = Restaurant menu app that looks like Uber Eats UI
- "calculator with Apple style" = Calculator app with Apple's design aesthetics
- "timer like Spotify" = Timer app with Spotify's visual style
"""

        prompt = f"""Create a UNIQUE iOS app based on this request:

USER REQUEST: "{description}"
{"APP NAME: " + app_name if app_name else "APP NAME: Extract from the request or create a creative name"}
{clarification}

UNDERSTANDING THE REQUEST:
1. First, identify the CORE APP TYPE the user wants:
   - Is it explicitly mentioned? (menu, calculator, timer, todo, etc.)
   - What is the primary functionality they need?

2. Then identify any STYLE/THEME references:
   - Are they asking for a specific visual style?
   - Do they reference another app for design inspiration?

3. Be careful not to confuse:
   - "X theme/style" = visual design like X
   - "app like X" = functionality similar to X
   - "X app" = the type of app is X

UNIQUENESS REQUIREMENTS:
- Unique Seed: {unique_seed}
- Time Context: {time_hint}
- Design Inspiration: {design_inspiration}
- Color Mood: {color_mood}
- Random Factor: {random.randint(1, 1000)}

CRITICAL TECHNICAL REQUIREMENTS:
1. ALWAYS import SwiftUI at the top of EVERY Swift file
2. Ensure @main struct conforms to App protocol
3. Include all necessary imports (Foundation, Combine, etc.)
4. Use proper Swift syntax and iOS 16+ features
5. Make sure ALL code compiles without errors

CREATIVE REQUIREMENTS:
1. Generate a COMPLETELY UNIQUE implementation
2. Add unexpected delightful features
3. Use smooth animations and transitions
4. Make it feel premium and polished
5. Include at least ONE surprising feature

Return a JSON object with this EXACT structure:
{{
    "files": [
        {{
            "path": "Sources/AppMain.swift",
            "content": "import SwiftUI\n\n@main\nstruct AppNameApp: App {{\n    var body: some Scene {{\n        WindowGroup {{\n            ContentView()\n        }}\n    }}\n}}"
        }},
        {{
            "path": "Sources/ContentView.swift",
            "content": "import SwiftUI\n\n// Your unique implementation here"
        }},
        // Add more files if needed
    ],
    "features": [
        "Specific feature 1 that you implemented",
        "Specific feature 2 that you implemented"
    ],
    "bundle_id": "com.swiftgen.{{app_name_lowercase}}",
    "app_name": "{{AppName}}",
    "unique_aspects": "What makes this implementation special",
    "design_notes": "Design decisions you made"
}}

Remember:
- ALWAYS import SwiftUI in EVERY Swift file
- Two users asking for the same type of app should get COMPLETELY DIFFERENT implementations
- Understand what TYPE of app they want vs what STYLE they want"""

        return prompt

    def _create_intelligent_modification_prompt(self, app_name: str, original_description: str,
                                              modification_request: str, existing_files: List[Dict]) -> str:
        """Create a prompt for intelligent modifications"""

        # Prepare existing code
        code_context = "\n\n".join([
            f"File: {file['path']}\n```swift\n{file['content']}\n```"
            for file in existing_files
        ])

        # Generate modification context
        mod_seed = hashlib.md5(f"{modification_request}{datetime.now().isoformat()}".encode()).hexdigest()[:8]

        prompt = f"""You need to modify an existing iOS app based on a user request.

CURRENT APP:
- App Name: {app_name}
- Original Purpose: {original_description}

USER'S MODIFICATION REQUEST: "{modification_request}"

EXISTING CODE:
{code_context}

MODIFICATION REQUIREMENTS:
1. UNDERSTAND the modification request:
   - What exactly does the user want to change?
   - Is it visual? Functional? Bug fix? New feature?
   - What's the intent behind the request?

2. MAKE REAL CHANGES:
   - Don't just return the same code
   - Actually implement what the user asked for
   - If they say "add dark mode", add real dark mode support
   - If they say "make buttons bigger", make them bigger
   - If they say "add animation", add actual animations

3. PRESERVE & ENHANCE:
   - Keep all existing functionality working
   - Maintain the app's unique character
   - Add smooth transitions for any UI changes
   - Improve code quality where possible

4. BE CREATIVE:
   - Modification Seed: {mod_seed}
   - Don't just do the minimum - exceed expectations
   - Add related improvements that make sense

CRITICAL: Return a properly formatted JSON object with this EXACT structure:
{{
    "files": [
        {{
            "path": "Sources/AppMain.swift",
            "content": "// The complete modified AppMain.swift code"
        }},
        {{
            "path": "Sources/ContentView.swift",
            "content": "// The complete modified ContentView.swift code"
        }}
        // Include ALL files, both modified and unmodified
        // Each file MUST have both "path" and "content" keys
    ],
    "features": [
        "Specific change 1 that was made",
        "Specific change 2 that was made"
    ],
    "bundle_id": "{f"com.swiftgen.{app_name.lower().replace(' ', '')}"}",
    "app_name": "{app_name}",
    "modification_summary": "Clear explanation of what was changed and why"
}}

IMPORTANT FORMATTING RULES:
- Each file object MUST have "path" and "content" keys
- The "path" must match the original file paths exactly
- Include the COMPLETE file content, not snippets
- Return ALL files from the app, whether modified or not
- Ensure the JSON is properly formatted without syntax errors

The user wants their app modified. Make sure you actually change the code based on their request!"""

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
                        "temperature": 0.8  # Higher temperature for more creativity
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result['content'][0]['text']

                    # Extract and parse JSON from response
                    parsed = self._extract_json_from_response(content)

                    if parsed and "files" in parsed and len(parsed["files"]) > 0:
                        return parsed
                    else:
                        print("Invalid response structure from Claude")
                        return None

                else:
                    print(f"Claude API error: {response.status_code}")
                    print(f"Response: {response.text}")

                    # Handle rate limits
                    if response.status_code == 429:
                        print("Rate limited. Please wait before trying again.")
                    elif response.status_code == 401:
                        print("Invalid API key. Please check your CLAUDE_API_KEY.")

                    return None

            except httpx.TimeoutException:
                print("Request to Claude timed out. The request might be too complex.")
                return None
            except Exception as e:
                print(f"Error calling Claude API: {str(e)}")
                return None

    def _extract_json_from_response(self, content: str) -> Optional[Dict]:
        """Extract and parse JSON from Claude's response, handling various formats"""

        try:
            # Method 1: Try to parse the entire content as JSON
            return json.loads(content)
        except:
            pass

        try:
            # Method 2: Look for JSON wrapped in ```json blocks
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                if json_end > json_start:
                    json_str = content[json_start:json_end].strip()
                    return json.loads(json_str)
        except:
            pass

        try:
            # Method 3: Find JSON by looking for { and }
            json_start = content.find('{')
            json_end = content.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
        except:
            pass

        # Method 4: Try to extract code blocks and construct JSON manually
        try:
            return self._construct_json_from_content(content)
        except Exception as e:
            print(f"Failed to extract JSON from response: {e}")
            return None

    def _construct_json_from_content(self, content: str) -> Dict:
        """Construct JSON from Claude's response when it's not properly formatted"""

        # This handles cases where Claude returns Swift code outside of proper JSON
        files = []

        # Look for file paths and their content
        lines = content.split('\n')
        current_file = None
        current_content = []
        in_code_block = False

        for line in lines:
            # Check for file path indicators
            if '"path":' in line:
                # Save previous file if exists
                if current_file and current_content:
                    files.append({
                        "path": current_file,
                        "content": '\n'.join(current_content).strip()
                    })
                    current_content = []

                # Extract file path
                try:
                    path_match = re.search(r'"path":\s*"([^"]+)"', line)
                    if path_match:
                        current_file = path_match.group(1)
                except:
                    pass

            # Check for content start
            elif '"content":' in line:
                in_code_block = True
                # Try to extract content from the same line if it's there
                try:
                    content_match = re.search(r'"content":\s*"(.+)"', line)
                    if content_match:
                        # Single line content
                        content_str = content_match.group(1)
                        # Unescape the content
                        content_str = content_str.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
                        if current_file:
                            files.append({
                                "path": current_file,
                                "content": content_str
                            })
                            current_file = None
                            in_code_block = False
                except:
                    pass

            # Collect code content
            elif in_code_block and current_file:
                # Look for the end of content
                if '"}' in line or '"},' in line:
                    # Extract content before the closing
                    content_part = line.split('"}')[0].split('"},')[0]
                    if content_part.strip():
                        current_content.append(content_part)

                    # Save the file
                    if current_content:
                        content_str = '\n'.join(current_content)
                        # Unescape the content
                        content_str = content_str.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
                        files.append({
                            "path": current_file,
                            "content": content_str.strip()
                        })

                    current_file = None
                    current_content = []
                    in_code_block = False
                else:
                    current_content.append(line)

        # Handle any remaining file
        if current_file and current_content:
            content_str = '\n'.join(current_content)
            content_str = content_str.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
            files.append({
                "path": current_file,
                "content": content_str.strip()
            })

        # Extract other fields
        app_name = "MyApp"
        features = []

        # Try to find app name
        app_name_match = re.search(r'"app_name":\s*"([^"]+)"', content)
        if app_name_match:
            app_name = app_name_match.group(1)

        # Try to find features
        if '"features"' in content:
            features_match = re.search(r'"features":\s*\[(.*?)\]', content, re.DOTALL)
            if features_match:
                features_str = features_match.group(1)
                # Extract individual features
                feature_matches = re.findall(r'"([^"]+)"', features_str)
                features = feature_matches

        # If we found files, construct a valid response
        if files:
            return {
                "files": files,
                "features": features if features else ["Generated from Claude response"],
                "bundle_id": f"com.swiftgen.{app_name.lower().replace(' ', '')}",
                "app_name": app_name,
                "unique_aspects": "AI-generated unique implementation"
            }

        # Last resort: Look for Swift code blocks and create files from them
        swift_blocks = re.findall(r'```swift(.*?)```', content, re.DOTALL)
        if swift_blocks:
            for i, code in enumerate(swift_blocks):
                # Determine file name based on content
                if "@main" in code:
                    files.append({
                        "path": "Sources/AppMain.swift",
                        "content": code.strip()
                    })
                elif "ContentView" in code:
                    files.append({
                        "path": "Sources/ContentView.swift",
                        "content": code.strip()
                    })
                else:
                    files.append({
                        "path": f"Sources/File{i}.swift",
                        "content": code.strip()
                    })

            if files:
                return {
                    "files": files,
                    "features": ["Generated from Swift code blocks"],
                    "bundle_id": f"com.swiftgen.app",
                    "app_name": "Generated App",
                    "unique_aspects": "AI-generated implementation"
                }

        raise Exception("Could not extract valid app data from response")

    async def analyze_build_errors(self, errors: List[str], project_files: List[Dict]) -> Dict:
        """Let Claude analyze and fix build errors"""

        if not self.api_key:
            raise ValueError("Claude API key required for error analysis")

        error_text = "\n".join(errors)
        code_context = "\n\n".join([
            f"File: {file['path']}\n```swift\n{file['content']}\n```"
            for file in project_files
        ])

        prompt = f"""Analyze these iOS build errors and provide fixes:

BUILD ERRORS:
{error_text}

CURRENT CODE:
{code_context}

Analyze the errors and provide corrected code. Focus on:
1. Understanding the root cause of each error
2. Providing minimal, targeted fixes
3. Ensuring the fixes don't break other functionality
4. Following Swift best practices

Return a JSON object with corrected files:
{{
    "files": [
        {{
            "path": "Sources/filename.swift",
            "content": "// Corrected Swift code"
        }}
    ],
    "fixes_applied": [
        "Description of each fix"
    ],
    "root_causes": [
        "Root cause analysis"
    ]
}}"""

        response = await self._call_claude_api(prompt)
        return response if response else {"files": project_files, "fixes_applied": ["Unable to analyze errors"]}