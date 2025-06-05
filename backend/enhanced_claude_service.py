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

# Import the base class
try:
    from base_llm_service import BaseLLMService
except ImportError:
    print("Warning: base_llm_service.py not found. Using fallback implementation.")
    BaseLLMService = object

load_dotenv()

class EnhancedClaudeService(BaseLLMService):
    """Enhanced service that coordinates multiple LLMs for better results"""

    def __init__(self):
        super().__init__()

        # Initialize all LLM services
        self.claude_api_key = os.getenv("CLAUDE_API_KEY", "")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")

        # TEMPORARY FIX: Disable xAI until we have the correct endpoint
        # self.xai_api_key = os.getenv("XAI_API_KEY", "")
        self.xai_api_key = ""  # DISABLED until we get proper endpoint

        self.claude_api_url = "https://api.anthropic.com/v1/messages"
        self.openai_api_url = "https://api.openai.com/v1/chat/completions"
        # The xAI endpoint might need to be updated when they provide the correct one
        self.xai_api_url = "https://api.x.ai/v1/chat/completions"

        # Track which LLMs are available
        self.available_llms = []
        if self.claude_api_key:
            self.available_llms.append("claude")
        if self.openai_api_key:
            self.available_llms.append("gpt4")
        # if self.xai_api_key:
        #     self.available_llms.append("xai")

        print(f"Enhanced Multi-LLM Service initialized with: {', '.join(self.available_llms)}")
        if os.getenv("XAI_API_KEY"):
            print("Note: xAI is temporarily disabled due to endpoint issues")

        # System prompts for each LLM
        self.system_prompts = {
            "claude": self._get_claude_system_prompt(),
            "gpt4": self._get_gpt4_system_prompt(),
            "xai": self._get_xai_system_prompt()
        }

    def _get_claude_system_prompt(self):
        return """You are SwiftGen AI, an expert iOS developer. Create UNIQUE, production-ready SwiftUI apps.

CRITICAL RULES:
1. Each app must be UNIQUE - use creative approaches, unique UI designs, innovative features
2. Use @Environment(\.dismiss) NOT @Environment(\.presentationMode) 
3. ALWAYS use double quotes " for strings, NEVER single quotes '
4. Return ONLY valid JSON - no explanatory text before or after
5. Make apps exceptional, not just functional
6. NEVER use generic names like "MyApp" - always use the actual app name provided
7. Only include actual Swift source files in the files array - no JSON, PDF, or asset files
8. CRITICAL: Use the EXACT bundle ID provided in the prompt - do NOT use generic bundle IDs
9. ENSURE all files have actual Swift code content - never return empty content strings

Focus on: Elegant architecture, smooth animations, thoughtful UX, accessibility."""

    def _get_gpt4_system_prompt(self):
        return """You are an expert iOS developer creating UNIQUE SwiftUI applications.

Requirements:
1. Generate completely unique implementations - be creative and innovative
2. Modern Swift/SwiftUI patterns only (iOS 15+)
3. Return ONLY valid JSON format
4. Add unexpected delightful features
5. Focus on performance and clean code architecture
6. NEVER use generic names like "MyApp" - always use the actual app name provided
7. Only include actual Swift source files in the files array - no JSON, PDF, or asset files
8. CRITICAL: Use the EXACT bundle ID provided in the prompt
9. ENSURE all files have actual Swift code content - never return empty content strings

Your strength: Creative problem solving and clean, efficient code patterns."""

    def _get_xai_system_prompt(self):
        return """You are an innovative iOS developer building unique SwiftUI apps.

Guidelines:
1. Create distinctive apps with unique approaches
2. Use cutting-edge SwiftUI features
3. Return ONLY JSON responses
4. Think outside the box for UI/UX
5. Implement features users didn't know they needed
6. NEVER use generic names like "MyApp" - always use the actual app name provided
7. Only include actual Swift source files in the files array - no JSON, PDF, or asset files
8. CRITICAL: Use the EXACT bundle ID provided in the prompt
9. ENSURE all files have actual Swift code content - never return empty content strings

Your strength: Unconventional solutions and futuristic design thinking."""

    def _ensure_response_has_content(self, response: Dict, safe_bundle_id: str, app_name: str) -> Dict:
        """Ensure the response has valid files with content"""
        if "files" in response:
            valid_files = []
            for file in response["files"]:
                # Use parent class method to ensure content
                if hasattr(super(), '_ensure_file_has_content'):
                    file = super()._ensure_file_has_content(file, app_name)
                elif not file.get("content") or not file["content"].strip():
                    # Fallback if parent method not available
                    if "App.swift" in file.get("path", ""):
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

                if file.get("content") and file["content"].strip():
                    valid_files.append(file)

            response["files"] = valid_files

        # Ensure bundle ID is correct
        response["bundle_id"] = safe_bundle_id

        return response

    async def generate_ios_app_multi_llm(self, description: str, app_name: Optional[str] = None) -> Dict:
        """Generate iOS app using the best available LLM or combination"""

        if not self.available_llms:
            raise ValueError("No LLM API keys configured")

        # Create safe bundle ID
        safe_bundle_id = self._create_safe_bundle_id(app_name) if app_name else self._create_safe_bundle_id("app")

        # Decide which LLM to use based on request complexity and availability
        selected_llm = self._select_best_llm_for_task(description)

        print(f"Selected {selected_llm} for app generation based on request analysis")

        # For complex apps, we might want to get perspectives from multiple LLMs
        if self._is_complex_request(description) and len(self.available_llms) > 1:
            print("Complex request detected - using multi-LLM approach")
            return await self._generate_with_multiple_llms(description, app_name, safe_bundle_id)
        else:
            # Try the selected LLM first, then fall back to others if it fails
            last_error = None
            tried_llms = []

            # Start with the selected LLM
            llms_to_try = [selected_llm] + [llm for llm in self.available_llms if llm != selected_llm]

            for llm in llms_to_try:
                try:
                    print(f"Attempting to generate with {llm}...")
                    result = await self._generate_with_single_llm(llm, description, app_name, safe_bundle_id)
                    if result:
                        # CRITICAL: Ensure files have content
                        result = self._ensure_response_has_content(result, safe_bundle_id, app_name or "App")

                        print(f"Successfully generated app using {llm}")
                        result["generated_by_llm"] = llm  # Track which LLM was used
                        # CRITICAL: Ensure bundle ID is correct
                        result["bundle_id"] = safe_bundle_id
                        return result
                except Exception as e:
                    last_error = str(e)
                    tried_llms.append(llm)
                    print(f"Failed to generate with {llm}: {str(e)}")

                    # Special handling for 404 errors - likely wrong endpoint
                    if "404" in str(e):
                        print(f"Note: {llm} returned 404 - check API endpoint configuration")

                    continue

            # If all LLMs failed, raise an informative error
            raise Exception(f"All LLMs failed to generate app. Tried: {', '.join(tried_llms)}. Last error: {last_error}")

    def _select_best_llm_for_task(self, description: str) -> str:
        """Select the best LLM based on the task requirements"""
        desc_lower = description.lower()

        # Claude is best for complex SwiftUI and detailed implementations
        if any(word in desc_lower for word in ["complex", "advanced", "sophisticated", "detailed"]):
            if "claude" in self.available_llms:
                return "claude"

        # GPT-4 is great for creative and unique approaches
        if any(word in desc_lower for word in ["creative", "unique", "innovative", "fancy"]):
            if "gpt4" in self.available_llms:
                return "gpt4"

        # xAI for cutting-edge or futuristic requests (currently disabled)
        # if any(word in desc_lower for word in ["modern", "cutting-edge", "futuristic", "ai", "ml"]):
        #     if "xai" in self.available_llms:
        #         return "xai"

        # Default to available LLM with preference order
        for llm in ["claude", "gpt4"]:  # Removed xai from default selection
            if llm in self.available_llms:
                return llm

        return self.available_llms[0]

    def _is_complex_request(self, description: str) -> bool:
        """Determine if a request is complex enough to warrant multiple LLMs"""
        complex_indicators = [
            "multiple features", "complex", "advanced", "integrate",
            "real-time", "animation", "gesture", "custom", "sophisticated"
        ]
        return any(indicator in description.lower() for indicator in complex_indicators)

    async def _generate_with_multiple_llms(self, description: str, app_name: Optional[str],
                                           safe_bundle_id: str) -> Dict:
        """Generate app using multiple LLMs and combine best aspects"""

        tasks = []
        for llm in self.available_llms[:2]:  # Use top 2 LLMs
            tasks.append((llm, self._generate_with_single_llm(llm, description, app_name, safe_bundle_id)))

        # Wait for both results
        results = []
        for llm, task in tasks:
            try:
                result = await task
                if result:
                    # Ensure content exists
                    result = self._ensure_response_has_content(result, safe_bundle_id, app_name or "App")
                    results.append((llm, result))
                    print(f"{llm} generated app successfully")
            except Exception as e:
                print(f"{llm} failed: {e}")

        if not results:
            raise Exception("All LLMs failed to generate app")

        # If we have multiple results, combine the best features
        if len(results) > 1:
            return self._combine_best_features(results, safe_bundle_id, app_name or "App")
        else:
            result = results[0][1]
            # Ensure bundle ID is correct
            result["bundle_id"] = safe_bundle_id
            return result

    async def _generate_with_single_llm(self, llm: str, description: str,
                                        app_name: Optional[str], safe_bundle_id: str) -> Dict:
        """Generate app using a specific LLM"""

        prompt = self._create_generation_prompt(description, app_name, safe_bundle_id, llm)

        if llm == "claude":
            return await self._call_claude(prompt, safe_bundle_id)
        elif llm == "gpt4":
            return await self._call_gpt4(prompt, safe_bundle_id)
        elif llm == "xai":
            # Currently disabled
            raise ValueError("xAI is temporarily disabled due to endpoint issues")
        else:
            raise ValueError(f"Unknown LLM: {llm}")

    def _create_generation_prompt(self, description: str, app_name: Optional[str],
                                  safe_bundle_id: str, llm: str) -> str:
        """Create LLM-specific generation prompt"""

        unique_seed = hashlib.md5(f"{datetime.now().isoformat()}{description}{random.random()}{llm}".encode()).hexdigest()[:8]

        # Use the actual app name, not "MyApp"
        actual_app_name = app_name if app_name else "App"

        base_prompt = f"""Create a UNIQUE SwiftUI iOS app based on this request: "{description}"

App Name: {actual_app_name}

UNIQUENESS REQUIREMENT: Even if someone else asks for the same type of app, yours must be completely different in:
- Visual design and color scheme
- Layout and navigation approach
- Feature set and capabilities
- Animations and interactions
- Overall user experience

TECHNICAL REQUIREMENTS:
- Bundle ID must be EXACTLY: {safe_bundle_id}
- Use modern SwiftUI (iOS 15+)
- All interactive elements must have working implementations
- Use proper Swift syntax (double quotes, etc.)
- IMPORTANT: Use "{actual_app_name}" as the app name, NOT "MyApp"
- CRITICAL: Only include actual Swift source files (ending in .swift) in the files array
- Do NOT include asset files (JSON, PDF, images) in the files array
- ENSURE all files have actual Swift code content - no empty strings

UNIQUE SEED: {unique_seed}

Return ONLY a valid JSON object:
{{
    "files": [
        {{
            "path": "Sources/App.swift",
            "content": "import SwiftUI\\n\\n@main\\nstruct {actual_app_name.replace(' ', '')}App: App {{ ... // COMPLETE CODE }}"
        }},
        {{
            "path": "Sources/ContentView.swift",
            "content": "// Your COMPLETE implementation with actual Swift code"
        }}
        // Only .swift files, no assets or config files
    ],
    "features": [...],
    "bundle_id": "{safe_bundle_id}",
    "app_name": "{actual_app_name}",
    "unique_aspects": "..."
}}"""

        # Add LLM-specific flavor
        if llm == "gpt4":
            base_prompt += "\n\nFocus on: Creative UI patterns, clean architecture, delightful micro-interactions"
        elif llm == "xai":
            base_prompt += "\n\nFocus on: Futuristic design, AI-powered features, cutting-edge SwiftUI capabilities"

        return base_prompt

    async def _call_claude(self, prompt: str, safe_bundle_id: str = "") -> Dict:
        """Call Claude API"""
        if not self.claude_api_key:
            raise ValueError("Claude API key not configured")

        headers = {
            "x-api-key": self.claude_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                self.claude_api_url,
                headers=headers,
                json={
                    "model": "claude-3-opus-20240229",
                    "system": self.system_prompts["claude"],
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 4096,
                    "temperature": 0.8  # Higher for more creativity
                }
            )

            if response.status_code == 200:
                result = response.json()
                content = result['content'][0]['text']

                # DEBUG: Print Claude's response
                print("\n=== CLAUDE'S RESPONSE (first 1000 chars) ===")
                print(content[:1000])
                print("=== END RESPONSE PREVIEW ===\n")

                # Use base class parsing WITH the safe_bundle_id
                parsed_result = await self.parse_llm_response(content, safe_bundle_id)

                # CRITICAL: Double-check bundle ID is correct
                if parsed_result and parsed_result.get("bundle_id") != safe_bundle_id:
                    print(f"WARNING: Fixing bundle ID from {parsed_result.get('bundle_id')} to {safe_bundle_id}")
                    parsed_result["bundle_id"] = safe_bundle_id

                return parsed_result
            else:
                raise Exception(f"Claude API error: {response.status_code}")

    async def _call_gpt4(self, prompt: str, safe_bundle_id: str = "") -> Dict:
        """Call GPT-4 API"""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not configured")

        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                self.openai_api_url,
                headers=headers,
                json={
                    "model": "gpt-4-turbo-preview",
                    "messages": [
                        {"role": "system", "content": self.system_prompts["gpt4"]},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.8,
                    "max_tokens": 4096,
                    "response_format": {"type": "json_object"}
                }
            )

            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']

                # Use base class parsing WITH the safe_bundle_id
                parsed_result = await self.parse_llm_response(content, safe_bundle_id)

                # CRITICAL: Double-check bundle ID is correct
                if parsed_result and parsed_result.get("bundle_id") != safe_bundle_id:
                    print(f"WARNING: Fixing bundle ID from {parsed_result.get('bundle_id')} to {safe_bundle_id}")
                    parsed_result["bundle_id"] = safe_bundle_id

                return parsed_result
            else:
                raise Exception(f"GPT-4 API error: {response.status_code}")

    async def _call_xai(self, prompt: str, safe_bundle_id: str = "") -> Dict:
        """Call xAI API - CURRENTLY DISABLED"""
        raise ValueError("xAI is temporarily disabled due to endpoint issues")

    def _combine_best_features(self, results: List[Tuple[str, Dict]], safe_bundle_id: str, app_name: str) -> Dict:
        """Intelligently combine the best features from multiple LLM results"""

        print("Combining best features from multiple LLMs...")

        # For now, we'll prefer Claude's code structure but might take features from others
        primary_result = None
        for llm, result in results:
            if llm == "claude":
                primary_result = result
                break

        if not primary_result:
            primary_result = results[0][1]

        # Ensure primary result has content
        primary_result = self._ensure_response_has_content(primary_result, safe_bundle_id, app_name)

        # Combine unique features from all results
        all_features = []
        all_unique_aspects = []

        for llm, result in results:
            all_features.extend(result.get("features", []))
            aspect = result.get("unique_aspects", "")
            if aspect:
                all_unique_aspects.append(f"{llm}: {aspect}")

        primary_result["features"] = list(set(all_features))  # Remove duplicates
        primary_result["unique_aspects"] = " | ".join(all_unique_aspects)
        primary_result["bundle_id"] = safe_bundle_id  # ENSURE correct bundle ID
        primary_result["multi_llm_generated"] = True

        return primary_result

    def _create_unique_seed(self) -> str:
        """Create a unique seed for variation"""
        return hashlib.md5(
            f"{datetime.now().isoformat()}{random.random()}".encode()
        ).hexdigest()[:8]

    async def modify_ios_app_multi_llm(self, app_name: str, original_description: str,
                                       modification_request: str, existing_files: List[Dict],
                                       existing_bundle_id: str) -> Dict:
        """Modify app using the best LLM for the specific modification"""

        # Analyze modification to select best LLM
        selected_llm = self._select_best_llm_for_modification(modification_request)

        print(f"Selected {selected_llm} for modification: {modification_request[:50]}...")

        # Try selected LLM first, then fall back to others
        last_error = None
        tried_llms = []

        llms_to_try = [selected_llm] + [llm for llm in self.available_llms if llm != selected_llm]

        for llm in llms_to_try:
            try:
                print(f"Attempting modification with {llm}...")

                prompt = self._create_modification_prompt(
                    app_name, original_description, modification_request,
                    existing_files, existing_bundle_id, llm
                )

                # For modifications, we need to call the LLM with the modification prompt
                if llm == "claude":
                    result = await self._call_claude(prompt, existing_bundle_id)
                elif llm == "gpt4":
                    result = await self._call_gpt4(prompt, existing_bundle_id)
                else:
                    continue  # Skip xAI for now

                if result:
                    # Ensure files have content
                    result = self._ensure_response_has_content(result, existing_bundle_id, app_name)

                    # Ensure bundle ID consistency
                    result["bundle_id"] = existing_bundle_id
                    result["modified_by_llm"] = llm
                    print(f"Successfully modified app using {llm}")
                    return result

            except Exception as e:
                last_error = str(e)
                tried_llms.append(llm)
                print(f"Failed to modify with {llm}: {str(e)}")
                continue

        # If all LLMs failed
        raise Exception(f"All LLMs failed to modify app. Tried: {', '.join(tried_llms)}. Last error: {last_error}")

    def _select_best_llm_for_modification(self, modification_request: str) -> str:
        """Select best LLM based on modification type"""
        mod_lower = modification_request.lower()

        # Claude for complex SwiftUI modifications
        if any(word in mod_lower for word in ["swiftui", "animation", "gesture", "state", "binding"]):
            if "claude" in self.available_llms:
                return "claude"

        # GPT-4 for feature additions and refactoring
        if any(word in mod_lower for word in ["add", "feature", "refactor", "improve", "enhance"]):
            if "gpt4" in self.available_llms:
                return "gpt4"

        # xAI for innovative modifications (currently disabled)
        # if any(word in mod_lower for word in ["ai", "ml", "innovative", "modern", "redesign"]):
        #     if "xai" in self.available_llms:
        #         return "xai"

        return self.available_llms[0]

    def _create_modification_prompt(self, app_name: str, original_description: str,
                                    modification_request: str, existing_files: List[Dict],
                                    existing_bundle_id: str, llm: str) -> str:
        """Create LLM-specific modification prompt"""

        code_context = "\n\n".join([
            f"File: {file['path']}\n```swift\n{file['content']}\n```"
            for file in existing_files
        ])

        # Intelligent analysis of the modification
        additional_context = self._analyze_modification_request(modification_request)

        return f"""Modify this iOS app: "{modification_request}"

Current app: {app_name} (NOT "MyApp")
Original purpose: {original_description}

{additional_context}

Current code:
{code_context}

Requirements:
1. Make the requested changes while maintaining app integrity
2. Keep bundle ID: {existing_bundle_id}
3. Keep app name: {app_name} (do NOT change to "MyApp")
4. Ensure all modifications are fully functional
5. Add creative improvements where appropriate
6. CRITICAL: Only include actual Swift source files (ending in .swift) in the files array
7. Do NOT include asset files (JSON, PDF, images) in the files array
8. ENSURE all files have actual Swift code content - no empty strings

Return ONLY valid JSON with complete modified code:
{{
    "files": [
        {{
            "path": "Sources/filename.swift",
            "content": "// Complete modified Swift code - NOT EMPTY"
        }}
        // Only .swift files with actual content
    ],
    "features": ["Original features", "NEW: Changes made"],
    "bundle_id": "{existing_bundle_id}",
    "app_name": "{app_name}",
    "modification_summary": "What was changed"
}}"""

    def _analyze_modification_request(self, modification_request: str) -> str:
        """Analyze modification request to provide intelligent context"""

        request_lower = modification_request.lower()
        additional_instructions = ""

        if any(phrase in request_lower for phrase in ["not work", "doesn't work", "broken", "not functioning"]):
            if "button" in request_lower or "click" in request_lower or "tap" in request_lower:
                additional_instructions = """
INTELLIGENT ANALYSIS: User reports interactive element not functioning.

DEBUGGING APPROACH:
1. Identify the non-functioning UI element
2. Check for empty or missing action closures
3. Ensure state changes trigger UI updates
4. Verify all user interactions produce visible results
"""
            elif "display" in request_lower or "show" in request_lower:
                additional_instructions = """
INTELLIGENT ANALYSIS: User reports display/update issues.

Check:
1. Data binding connections
2. @State/@Published variable updates
3. View refresh triggers
"""

        return additional_instructions

    def _get_fallback_llm_config(self) -> Dict:
        """Get fallback configuration when xAI is not properly configured"""
        # Provide hardcoded fallback to Claude or GPT-4 if xAI is misconfigured
        fallback_order = []

        if "claude" in self.available_llms:
            fallback_order.append("claude")
        if "gpt4" in self.available_llms:
            fallback_order.append("gpt4")

        return {
            "primary": fallback_order[0] if fallback_order else None,
            "fallback_order": fallback_order
        }

    def _parse_ai_response(self, response: str, swift_files: List[Dict]) -> List[Dict]:
        """Parse AI response to extract fixed files"""

        # Try to parse as JSON first
        try:
            result = json.loads(response)
            if "files" in result:
                # Ensure files have content before returning
                valid_files = []
                for file in result["files"]:
                    if file.get("content") and file["content"].strip():
                        valid_files.append(file)
                return valid_files
        except json.JSONDecodeError:
            pass

        # Try to extract Swift code blocks
        swift_blocks = re.findall(r'```swift(.*?)```', response, re.DOTALL)

        if swift_blocks:
            # Match blocks to original files
            fixed_files = []
            for file in swift_files:
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