import os
import json
import logging
import time
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import anthropic
import requests
from dotenv import load_dotenv

# Import intelligent router
try:
    from intelligent_llm_router import IntelligentLLMRouter, RequestType
except ImportError:
    IntelligentLLMRouter = None
    RequestType = None
    logger.warning("IntelligentLLMRouter not available - using fallback mode")

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LLMModel:
    """Data class for LLM model configuration"""
    name: str
    provider: str
    api_key_env: str
    model_id: str
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 30

class EnhancedClaudeService:
    """Enhanced service for managing multiple LLM providers"""

    def __init__(self):
        """Initialize the enhanced Claude service with all available LLMs"""
        self.models = {}
        self.available_models = []
        self.current_model = None
        self.api_keys = {}
        self._clients = {}
        
        # Initialize intelligent router
        self.router = IntelligentLLMRouter() if IntelligentLLMRouter else None
        self.failure_count = {}  # Track failures per request
        
        # Progress callback for real-time updates
        self.progress_callback = None

        # Define ALL supported models - UPDATED WITH CORRECT MODEL NAMES
        self.supported_models = [
            LLMModel(
                name="Claude 3.5 Sonnet",
                provider="anthropic",
                api_key_env="CLAUDE_API_KEY",
                model_id="claude-3-5-sonnet-20241022",  # Latest Claude model
                max_tokens=8192  # Increased for complete app generation
            ),
            LLMModel(
                name="GPT-4 Turbo",
                provider="openai",
                api_key_env="OPENAI_API_KEY",
                model_id="gpt-4-turbo-preview",
                max_tokens=4096,
                temperature=0.7
            ),
            LLMModel(
                name="xAI Grok",
                provider="xai",
                api_key_env="XAI_API_KEY",
                model_id="grok-3-latest",  # Correct model name confirmed by xAI docs
                max_tokens=4096
            )
        ]

        # Initialize all available models
        self._initialize_models()

        # Log initialization results
        logger.info(f"Initialized {len(self.available_models)} LLM models out of {len(self.supported_models)} supported")
        for model in self.available_models:
            logger.info(f"  - {model.name} ({model.provider}) ✓")

        # Set default model if available
        if self.available_models:
            self.current_model = self.available_models[0]
            logger.info(f"Default model set to: {self.current_model.name}")

    def _initialize_models(self):
        """Initialize all models that have valid API keys"""
        for model in self.supported_models:
            api_key = os.getenv(model.api_key_env, "").strip()
            if api_key:
                self.api_keys[model.provider] = api_key
                self.models[model.provider] = model
                self.available_models.append(model)
                logger.info(f"✓ Initialized {model.name}")
            else:
                logger.warning(f"✗ Skipped {model.name} - No API key found ({model.api_key_env})")

    def _initialize_client(self, provider: str):
        """Initialize API client for the given provider"""
        try:
            if provider == "anthropic" and provider not in self._clients:
                self._clients["anthropic"] = anthropic.Anthropic(
                    api_key=self.api_keys["anthropic"],
                    timeout=30.0,  # 30 second timeout
                    max_retries=2  # Limit retries at the client level
                )
                return True
            elif provider == "openai" and provider not in self._clients:
                from openai import OpenAI
                self._clients["openai"] = OpenAI(
                    api_key=self.api_keys["openai"],
                    timeout=30.0,  # 30 second timeout
                    max_retries=2  # Limit retries at the client level
                )
                return True
            elif provider == "xai" and provider not in self._clients:
                # xAI uses OpenAI-compatible API
                from openai import OpenAI
                self._clients["xai"] = OpenAI(
                    api_key=self.api_keys.get("xai", ""),
                    base_url="https://api.x.ai/v1",
                    timeout=30.0,  # 30 second timeout
                    max_retries=2  # Limit retries at the client level
                )
                return True
            return provider in self._clients
        except Exception as e:
            logger.error(f"Failed to initialize {provider} client: {str(e)}")
            return False

    def get_available_models(self) -> List[LLMModel]:
        """Get list of all available models"""
        return self.available_models

    def set_model(self, provider: str) -> bool:
        """Set the current model by provider name"""
        if provider in self.models:
            self.current_model = self.models[provider]
            logger.info(f"Switched to model: {self.current_model.name}")
            return True
        else:
            logger.error(f"Provider {provider} not available")
            return False
    
    def set_progress_callback(self, callback):
        """Set a callback function for progress updates"""
        self.progress_callback = callback

    async def generate_ios_app(self, description: str, app_name: str = None, retry_count: int = 0) -> Dict[str, Any]:
        """Generate iOS app code using the best available LLM"""
        if not self.available_models:
            raise Exception("No LLM model available")
        
        # Prevent infinite retry loops
        MAX_RETRIES = 3
        if retry_count >= MAX_RETRIES:
            logger.error(f"Maximum retries ({MAX_RETRIES}) reached. Stopping.")
            raise Exception(f"Failed to generate app after {MAX_RETRIES} attempts")
        
        app_name = app_name or "MyApp"
        
        # Check if this is a complex app and use architect if needed
        try:
            from complex_app_architect import ComplexAppArchitect
            architect = ComplexAppArchitect()
            complexity = architect.analyze_complexity(description)
            
            if complexity == "high":
                logger.info(f"[ARCHITECT] Detected high-complexity app. Using architectural planning...")
                # Use architect to create enhanced prompt
                enhanced_description = architect.create_enhanced_prompt(description, app_name)
                # Override the description with the architect's detailed plan
                description = enhanced_description
                logger.info(f"[ARCHITECT] Created detailed architecture plan for {architect.identify_app_type(description)} app")
        except ImportError:
            logger.warning("ComplexAppArchitect not available, using standard generation")
        
        # Use intelligent routing if available
        if self.router:
            available_providers = [model.provider for model in self.available_models]
            selected_provider = self.router.route_initial_request(description, app_type="ios", available_providers=available_providers)
            if selected_provider in self.models:
                self.current_model = self.models[selected_provider]
                logger.info(f"[ROUTER] Selected {self.current_model.name} for app generation")
            else:
                logger.warning(f"[ROUTER] Provider {selected_provider} not available, using default")
                self.current_model = self.available_models[0]
        else:
            # Fallback to first available model
            if not self.current_model:
                self.current_model = self.available_models[0]

        # Create the prompt for iOS app generation
        # Try to use enhanced prompts for better syntax
        try:
            from enhanced_prompts import get_generation_prompts
            system_prompt, user_prompt = get_generation_prompts(app_name or "MyApp", description)
            # Skip the old user_prompt generation
            use_enhanced = True
        except ImportError:
            use_enhanced = False
            system_prompt = """You are SwiftGen AI, an expert iOS developer. Create UNIQUE, production-ready SwiftUI apps.

CRITICAL RULES:
1. Each app must be UNIQUE - use creative approaches, unique UI designs, innovative features
2. Use @Environment(\\.dismiss) NOT @Environment(\\.presentationMode) 
3. ALWAYS use double quotes " for strings, NEVER single quotes '
4. Return ONLY valid JSON - no explanatory text before or after
5. Make apps exceptional, not just functional
6. NEVER use generic names like "MyApp" - always use the actual app name provided
7. Only include actual Swift source files in the files array - no JSON, PDF, or asset files
8. Use the EXACT bundle ID format: com.swiftgen.{app_name_lowercase_no_spaces}
9. ENSURE all files have actual Swift code content - never return empty content strings
10. ALWAYS import SwiftUI in every Swift file
11. ALWAYS import Combine when using @Published or ObservableObject

Focus on: Elegant architecture, smooth animations, thoughtful UX, accessibility."""

        if not use_enhanced:
            user_prompt = f"""Create a complete iOS app with these requirements:
App Name: {app_name or "MyApp"}
Description: {description}

Return a JSON response with this EXACT structure:
{{
    "files": [
        {{
            "path": "Sources/App.swift",
            "content": "// Full Swift code here"
        }},
        {{
            "path": "Sources/ContentView.swift", 
            "content": "// Full Swift code here"
        }}
    ],
    "bundle_id": "com.swiftgen.{app_name.lower().replace(' ', '') if app_name else 'app'}",
    "features": ["Feature 1", "Feature 2"],
    "unique_aspects": "What makes this implementation unique",
    "app_name": "{app_name or 'MyApp'}",
    "product_name": "{app_name.replace(' ', '') if app_name else 'MyApp'}"
}}"""

        try:
            # Send initial progress update
            if self.progress_callback:
                await self.progress_callback(f"🚀 Starting app generation with {self.current_model.name}...")
            
            result = await self._generate_with_current_model(system_prompt, user_prompt)

            # Parse JSON response
            if isinstance(result, str):
                # Clean the response to ensure it's valid JSON
                result = result.strip()
                if result.startswith("```json"):
                    result = result[7:]
                if result.endswith("```"):
                    result = result[:-3]
                result = json.loads(result)
            
            # Check for truncated code
            if "files" in result:
                for file in result["files"]:
                    content = file.get("content", "")
                    if "..." in content and re.search(r'(class|struct|enum)\s+\w+\.\.\.', content):
                        logger.warning(f"Detected truncated code in {file.get('path', 'unknown')}")
                        raise Exception("Generated code appears to be truncated. Retrying with higher token limit...")
            
            # Add LLM provider info to result
            if self.current_model:
                result["generated_by_llm"] = self.current_model.provider

            return result

        except Exception as e:
            logger.error(f"Generation failed with {self.current_model.name}: {str(e)}")
            
            # Track failure
            request_id = f"gen_{app_name}_{description[:20]}"
            self.failure_count[request_id] = self.failure_count.get(request_id, 0) + 1
            
            # Use intelligent fallback if router available
            if self.router and self.current_model:
                request_type = self.router.analyze_request(description)
                next_provider, strategy = self.router.get_fallback_strategy(
                    self.current_model.provider,
                    request_type,
                    self.failure_count[request_id]
                )
                
                if next_provider in self.models:
                    self.current_model = self.models[next_provider]
                    logger.info(f"[ROUTER] Retrying with {self.current_model.name} using {strategy}")
                    
                    # Record failure for learning
                    self.router.record_result(
                        self.current_model.provider,
                        request_type,
                        success=False
                    )
                    
                    try:
                        return await self.generate_ios_app(description, app_name, retry_count + 1)
                    except Exception as e:
                        logger.error(f"Retry with {self.current_model.name} failed: {str(e)}")
                        pass
            
            # Fallback to sequential retry
            for model in self.available_models:
                if model != self.current_model:
                    self.current_model = model
                    logger.info(f"Retrying with {model.name}")
                    try:
                        return await self.generate_ios_app(description, app_name, retry_count + 1)
                    except Exception as e:
                        logger.error(f"Sequential retry with {model.name} failed: {str(e)}")
                        continue

            raise Exception(f"All LLM models failed. Last error: {str(e)}")

    async def _generate_with_current_model(self, system_prompt: str, user_prompt: str) -> str:
        """Generate text using the current model"""
        if self.current_model.provider == "anthropic":
            return await self._generate_claude(system_prompt, user_prompt)
        elif self.current_model.provider == "openai":
            return await self._generate_openai(system_prompt, user_prompt)
        elif self.current_model.provider == "xai":
            return await self._generate_xai(system_prompt, user_prompt)
        else:
            raise Exception(f"Unknown provider: {self.current_model.provider}")

    async def _generate_claude(self, system_prompt: str, user_prompt: str) -> str:
        """Generate text using Claude"""
        import anthropic

        client = anthropic.Anthropic(
            api_key=self.api_keys["anthropic"],
            timeout=30.0,  # 30 second timeout
            max_retries=2  # Limit retries at the client level
        )
        
        # Send progress update before starting
        if self.progress_callback:
            await self.progress_callback("🤖 Claude is analyzing your requirements...")

        message = client.messages.create(
            model=self.current_model.model_id,
            max_tokens=self.current_model.max_tokens,
            temperature=self.current_model.temperature,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Send progress update after generation
        if self.progress_callback:
            await self.progress_callback("✨ Claude has generated the app architecture...")

        return message.content[0].text

    async def _generate_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Generate text using OpenAI"""
        from openai import OpenAI
        
        client = OpenAI(api_key=self.api_keys["openai"])
        
        # Send progress update before starting
        if self.progress_callback:
            await self.progress_callback("🤖 GPT-4 is analyzing your requirements...")
        
        response = client.chat.completions.create(
            model=self.current_model.model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=self.current_model.max_tokens,
            temperature=self.current_model.temperature
        )
        
        # Send progress update after generation
        if self.progress_callback:
            await self.progress_callback("✨ GPT-4 has generated the app architecture...")

        return response.choices[0].message.content

    async def _generate_xai(self, system_prompt: str, user_prompt: str) -> str:
        """Generate text using xAI Grok"""
        try:
            # xAI API is compatible with OpenAI format
            # Use OpenAI SDK with xAI endpoint
            from openai import OpenAI
            
            # Initialize xAI client with custom base URL
            xai_client = OpenAI(
                api_key=self.api_keys.get("xai", ""),
                base_url="https://api.x.ai/v1"
            )
            
            # Send progress update before starting
            if self.progress_callback:
                await self.progress_callback("🤖 xAI Grok is analyzing your requirements...")
            
            # Create chat completion using Grok
            response = xai_client.chat.completions.create(
                model=self.current_model.model_id,  # grok-3-latest
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.current_model.max_tokens,
                temperature=self.current_model.temperature
            )
            
            # Send progress update after generation
            if self.progress_callback:
                await self.progress_callback("✨ xAI Grok has generated the app architecture...")
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"xAI generation failed: {str(e)}")
            
            # Fallback to Claude only if xAI actually fails
            logger.warning("xAI request failed, falling back to Claude")
            if "anthropic" in self.models:
                self.current_model = self.models["anthropic"]
                return await self._generate_claude(system_prompt, user_prompt)
            elif "openai" in self.models:
                self.current_model = self.models["openai"]
                return await self._generate_openai(system_prompt, user_prompt)
            else:
                raise Exception(f"xAI generation failed and no fallback available: {str(e)}")

    def generate_text(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Synchronous wrapper for compatibility"""
        import asyncio

        async def _async_generate():
            result = await self._generate_with_current_model("You are a helpful assistant.", prompt)
            return {"success": True, "text": result}

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(_async_generate())
        except Exception as e:
            return {"success": False, "error": str(e), "text": ""}
        finally:
            loop.close()
    
    async def get_completion(self, system_prompt: str, user_prompt: str, max_tokens: int = 4096, temperature: float = 0.7) -> str:
        """Get completion from current LLM model - for chat handler compatibility"""
        try:
            # Use the current model with provided prompts
            response = await self._generate_with_current_model(system_prompt, user_prompt)
            return response
        except Exception as e:
            print(f"Error in get_completion: {e}")
            raise
    
    async def extract_app_name(self, description: str) -> str:
        """Use LLM to extract a proper app name from description"""
        prompt = f"""Given this iOS app description, provide a proper app name.

Description: {description}

Requirements:
- The name should be 1-4 words maximum
- It should be descriptive and memorable
- Avoid generic names like "MyApp" or "App"
- Don't include "iOS" or "App" in the name unless essential
- Make it suitable for the App Store

Return ONLY the app name, nothing else. No explanation or quotes."""

        try:
            # Use a low temperature for consistent naming
            response = await self._generate_with_current_model("You are an app naming expert.", prompt)
            if response:
                app_name = response.strip().strip('"').strip("'")
                # Limit length
                if len(app_name) > 30:
                    app_name = app_name[:30].rsplit(' ', 1)[0]
                return app_name
            else:
                return None
        except Exception as e:
            print(f"[LLM] Failed to extract app name: {e}")
            return None

    # Optional: Add these methods if your main.py expects them
    async def generate_ios_app_multi_llm(self, description: str, app_name: str = None) -> Dict[str, Any]:
        """Alias for compatibility"""
        return await self.generate_ios_app(description, app_name)

    async def modify_ios_app(self, app_name: str, description: str, modification: str,
                             files: List[Dict], existing_bundle_id: str = None,
                             project_tracking_id: str = None) -> Dict[str, Any]:
        """Modify an existing iOS app with intelligent modification handling"""
        
        # Import modification handler
        try:
            from modification_handler import ModificationHandler
            mod_handler = ModificationHandler()
        except:
            mod_handler = None
        
        # Use intelligent routing for modifications
        if self.router:
            # Analyze modification to determine best LLM
            available_providers = [model.provider for model in self.available_models]
            # CRITICAL: Pass is_modification=True to prevent router from thinking this is app creation
            selected_provider = self.router.route_initial_request(modification, available_providers=available_providers, is_modification=True)
            if selected_provider in self.models:
                self.current_model = self.models[selected_provider]
                logger.info(f"[ROUTER] Selected {self.current_model.name} for modification: {modification[:50]}...")
            
            # Create specialized prompt if router available
            strategy = "standard approach"
            if self.router:
                # CRITICAL: Pass modification_history to indicate this is a modification
                request_type = self.router.analyze_request(modification, modification_history=[{"type": "modification"}])
                specialized_prompt = self.router.create_specialized_prompt(
                    self.current_model.provider,
                    strategy,
                    modification,
                    []  # No previous failures yet
                )
                logger.info(f"[ROUTER] Using specialized prompt for {request_type.value}")
        
        # Analyze modification request
        modification_type = self._analyze_modification_type(modification)
        
        system_prompt = f"""You are SwiftGen AI, an expert iOS developer. 
{modification_type['guidance']}

IMPORTANT RULES:
1. ONLY modify what is requested - do NOT rebuild the entire app
2. Keep all existing functionality unless explicitly asked to change it
3. Maintain the same app structure and architecture
4. Return ALL files with their complete content (modified or unchanged)
5. Do NOT change the app name or bundle ID
6. If fixing "cannot find X in scope" errors, CREATE the missing file/type
7. When creating new files, add them to the files array in your response

CRITICAL iOS VERSION CONSTRAINTS (HIGHEST PRIORITY):
- Target iOS: 16.0 ONLY - This is NON-NEGOTIABLE
- FORBIDDEN iOS 17+ features that MUST NOT be used:
  * NO .symbolEffect() → use .scaleEffect or .opacity animations instead
  * NO .bounce effects → use .animation(.spring()) instead
  * NO @Observable macro → use ObservableObject + @Published
  * NO .scrollBounceBehavior modifier → remove it entirely
  * NO .contentTransition modifier → use regular transitions
  * NO ContentUnavailableView → create custom empty state views
  * NO AnyShapeStyle → use concrete types like Color or LinearGradient
  * NO NavigationStack with complex path → use NavigationView for simple navigation
  * NO .scrollTargetBehavior → not available in iOS 16
  * NO .scrollPosition → use ScrollViewReader instead
  * NO .scrollClipDisabled → not available in iOS 16
  * NO .sensoryFeedback → use UIKit haptics if needed
- ALWAYS check iOS availability before using ANY modifier
- When in doubt, use the iOS 15/16 compatible approach

MODERN SWIFT PATTERNS (MANDATORY):
1. Navigation: Use NavigationStack for iOS 16+ (simple cases only), NavigationView as fallback
2. State Management: ObservableObject + @Published for iOS 16
3. Async/Await: ALWAYS use async/await, NEVER completion handlers
4. UI Updates: Mark UI classes/methods with @MainActor
5. Modifiers: Use .foregroundStyle NOT .foregroundColor
6. Concurrency: NEVER use DispatchSemaphore with async/await

MODULE IMPORT RULES - CRITICAL FOR SWIFTUI:
- NEVER import local folders: NO import Components, Views, Models, ViewModels, Services
- ONLY import system frameworks: import SwiftUI, Foundation, Combine, CoreData, etc.
- SwiftUI uses direct type references, NOT module imports
- Access types directly: ContentView NOT Components.ContentView
- WRONG: import Components; Components.MyView()
- RIGHT: MyView() // direct reference"""

        # Use modification handler if available
        if mod_handler:
            user_prompt = mod_handler.prepare_modification_prompt(app_name, modification, files)
        else:
            # Fallback to simpler prompt
            user_prompt = f"""Current iOS App: {app_name}
Modification Request: {modification}

CRITICAL: Return ALL {len(files)} files, even if unchanged.
Only modify files that need to change for: "{modification}"

Current files:
"""
            for file in files:
                user_prompt += f"\n--- {file['path']} ---\n{file['content'][:500]}...\n"
            
            user_prompt += f"""

Return JSON with ALL {len(files)} files:
{{
    "files": [ALL {len(files)} files with path and content],
    "bundle_id": "{existing_bundle_id}",
    "modification_summary": "Brief summary of what changed",
    "changes_made": [
        "SPECIFIC change 1 (e.g., Added dark mode toggle to settings)",
        "SPECIFIC change 2 (e.g., Updated color scheme to support dark theme)",
        "SPECIFIC change 3 (e.g., Added UserDefaults to persist theme preference)",
        "List each concrete change made to implement the modification"
    ],
    "files_modified": ["List of files that were actually modified"]
}}

IMPORTANT: The "changes_made" array must contain SPECIFIC, CONCRETE changes you made to the code, not generic statements."""

        # Try generation with intelligent error handling
        request_id = f"mod_{app_name}_{modification[:20]}"
        self.failure_count[request_id] = self.failure_count.get(request_id, 0)
        
        try:
            result = await self._generate_with_current_model(system_prompt, user_prompt)
        except Exception as gen_error:
            logger.error(f"[ROUTER] Modification generation failed: {gen_error}")
            
            # Intelligent fallback for modifications
            if self.router and self.current_model:
                self.failure_count[request_id] += 1
                # CRITICAL: Pass modification_history to indicate this is a modification
                request_type = self.router.analyze_request(modification, modification_history=[{"type": "modification"}])
                
                # Get fallback strategy
                next_provider, strategy = self.router.get_fallback_strategy(
                    self.current_model.provider,
                    request_type,
                    self.failure_count[request_id]
                )
                
                if next_provider in self.models:
                    logger.info(f"[ROUTER] Falling back to {next_provider} with {strategy}")
                    self.current_model = self.models[next_provider]
                    
                    # Create specialized prompt for fallback
                    if self.router:
                        specialized_user_prompt = self.router.create_specialized_prompt(
                            next_provider,
                            strategy,
                            modification,
                            [str(gen_error)]
                        )
                        # Append existing context
                        specialized_user_prompt += "\n\n" + user_prompt.split("Current files:")[1] if "Current files:" in user_prompt else user_prompt
                        user_prompt = specialized_user_prompt
                    
                    # Retry with fallback
                    result = await self._generate_with_current_model(system_prompt, user_prompt)
                else:
                    raise gen_error
            else:
                raise gen_error

        if isinstance(result, str):
            result = result.strip()
            if result.startswith("```json"):
                result = result[7:]
            if result.endswith("```"):
                result = result[:-3]
            
            # Clean up common JSON issues before parsing
            try:
                # First attempt - direct parsing
                result = json.loads(result)
            except json.JSONDecodeError as e:
                print(f"[ERROR] Initial JSON parse failed: {e}")
                print(f"[ERROR] Error at position: {e.pos if hasattr(e, 'pos') else 'unknown'}")
                
                # Use modification handler to fix JSON if available
                if mod_handler:
                    fixed_result = mod_handler.fix_json_response(result)
                    if fixed_result:
                        result = fixed_result
                    else:
                        # Create minimal modification response
                        result = mod_handler.create_minimal_modification(files, modification)
                else:
                    # Fallback parsing attempts
                    try:
                        # Extract JSON object
                        json_match = re.search(r'\{[\s\S]*\}', result)
                        if json_match:
                            result = json.loads(json_match.group(0))
                        else:
                            raise ValueError("No JSON object found")
                    except Exception as e3:
                        print(f"[ERROR] All JSON parsing failed: {e3}")
                        # Return minimal response
                        return {
                            "app_name": app_name,
                            "bundle_id": existing_bundle_id,
                            "files": files,  # Return original files unchanged
                            "modification_summary": f"Failed to apply: {modification}",
                            "changes_made": ["Error: Could not parse LLM response"],
                            "modified_by_llm": self.current_model.provider if self.current_model else "claude"
                        }
                    else:
                        print("[ERROR] No JSON object found in response")
                        return {
                            "app_name": app_name,
                            "bundle_id": existing_bundle_id,
                            "files": [],  # Empty files = clear failure signal
                            "modification_summary": "Failed to parse modification response",
                            "changes_made": ["Error: No valid JSON in response"],
                            "modified_by_llm": self.current_model.provider if self.current_model else "claude"
                        }

        # Record success if using router
        if self.router and isinstance(result, dict):
            # CRITICAL: Pass modification_history to indicate this is a modification
            request_type = self.router.analyze_request(modification, modification_history=[{"type": "modification"}])
            self.router.record_result(
                self.current_model.provider,
                request_type,
                success=True
            )
            logger.info(f"[ROUTER] Recorded success for {self.current_model.provider} on {request_type.value}")
        
        # Ensure consistency
        if isinstance(result, dict):
            # Validate the modification response
            if mod_handler:
                is_valid, issues = mod_handler.validate_modification_response(result, files)
                if not is_valid:
                    print(f"[ERROR] Modification response validation failed: {issues}")
                    # Try to fix by ensuring all files are present
                    if 'files' not in result or len(result.get('files', [])) != len(files):
                        print(f"[WARNING] Fixing incomplete file list - ensuring all {len(files)} files are included")
                        # Create a mapping of returned files
                        returned_files = {f['path']: f for f in result.get('files', [])}
                        # Fill in missing files with originals
                        complete_files = []
                        for orig_file in files:
                            if orig_file['path'] in returned_files:
                                complete_files.append(returned_files[orig_file['path']])
                            else:
                                print(f"[WARNING] File {orig_file['path']} was missing - including original")
                                complete_files.append(orig_file)
                        result['files'] = complete_files
            
            result["bundle_id"] = existing_bundle_id
            result["app_name"] = app_name
            result["modified_by_llm"] = self.current_model.provider if self.current_model else "claude"
            
            # Ensure we have modification summary
            if "modification_summary" not in result:
                result["modification_summary"] = modification[:100]
            
            # Ensure we have specific changes listed
            if "changes_made" not in result or not result.get("changes_made") or result.get("changes_made") == ["Changes applied as requested"]:
                # Try to infer changes from modification request
                inferred_changes = []
                mod_lower = modification.lower()
                
                # Common modification patterns
                if "dark mode" in mod_lower or "dark theme" in mod_lower:
                    inferred_changes.extend([
                        "Added dark mode support to the app",
                        "Updated color scheme for dark theme compatibility",
                        "Added theme toggle functionality"
                    ])
                elif "color" in mod_lower:
                    inferred_changes.append(f"Updated color scheme as requested: {modification[:80]}")
                elif "add" in mod_lower:
                    inferred_changes.append(f"Added new functionality: {modification[:80]}")
                elif "fix" in mod_lower:
                    inferred_changes.append(f"Fixed issue: {modification[:80]}")
                elif "update" in mod_lower or "change" in mod_lower:
                    inferred_changes.append(f"Updated: {modification[:80]}")
                else:
                    inferred_changes.append(f"Applied modification: {modification[:80]}")
                
                # Add file count info
                files_modified = result.get("files_modified", [])
                if files_modified:
                    inferred_changes.append(f"Modified {len(files_modified)} files: {', '.join(files_modified[:3])}")
                elif "files" in result:
                    inferred_changes.append(f"Updated {len(result['files'])} files")
                
                result["changes_made"] = inferred_changes
                
        else:
            # If result is not a dict at this point, something went wrong
            print(f"[ERROR] Result is not a dict: {type(result)}")
            return {
                "app_name": app_name,
                "bundle_id": existing_bundle_id,
                "files": files,  # Return original files
                "modification_summary": "Failed to process modification",
                "changes_made": ["Error: Invalid response format"],
                "modified_by_llm": self.current_model.provider if self.current_model else "claude"
            }
        
        # Post-process to remove iOS 17 features before returning
        if isinstance(result, dict) and "files" in result:
            for file in result["files"]:
                if "content" in file:
                    file["content"] = self._remove_ios17_features_from_content(file["content"])
        
        return result

    async def modify_ios_app_multi_llm(self, *args, **kwargs):
        """Alias for compatibility"""
        return await self.modify_ios_app(*args, **kwargs)
    
    def _analyze_modification_type(self, modification: str) -> Dict[str, str]:
        """Analyze the modification request to provide better guidance"""
        mod_lower = modification.lower()
        
        if any(word in mod_lower for word in ["theme", "dark", "color", "style"]):
            return {
                "type": "ui_theme",
                "guidance": "You're modifying UI theme/colors. Focus on Color assets, view modifiers, and appearance settings. Do NOT change app functionality."
            }
        elif any(word in mod_lower for word in ["add button", "add feature", "new screen"]):
            return {
                "type": "feature_addition",
                "guidance": "You're adding a new feature. Integrate it smoothly with existing code without disrupting current functionality."
            }
        elif any(word in mod_lower for word in ["fix", "bug", "error", "crash"]):
            return {
                "type": "bug_fix",
                "guidance": "You're fixing a bug. Focus on the specific issue without changing unrelated code."
            }
        elif any(word in mod_lower for word in ["improve", "enhance", "optimize"]):
            return {
                "type": "enhancement",
                "guidance": "You're enhancing existing functionality. Make targeted improvements without rebuilding."
            }
        else:
            return {
                "type": "general",
                "guidance": "Make the requested modification while preserving all existing functionality."
            }
    
    def _remove_ios17_features_from_content(self, content: str) -> str:
        """Remove or replace iOS 17+ features with iOS 16 alternatives"""
        
        # Replace .symbolEffect with animation alternatives
        content = re.sub(
            r'\.symbolEffect\([^)]*\)',
            '.scaleEffect(1.1).animation(.easeInOut(duration: 0.3), value: true)',
            content
        )
        
        # Replace .bounce with spring animation
        content = re.sub(
            r'\.bounce\b',
            '.animation(.spring())',
            content
        )
        
        # Replace @Observable with ObservableObject
        content = re.sub(
            r'@Observable\s+class\s+(\w+)',
            r'class \1: ObservableObject',
            content
        )
        
        # Remove .scrollBounceBehavior
        content = re.sub(
            r'\.scrollBounceBehavior\([^)]*\)',
            '',
            content
        )
        
        # Remove .contentTransition
        content = re.sub(
            r'\.contentTransition\([^)]*\)',
            '',
            content
        )
        
        # Replace ContentUnavailableView with custom implementation
        if 'ContentUnavailableView' in content:
            content = re.sub(
                r'ContentUnavailableView\([^}]+\}',
                '''VStack(spacing: 16) {
                    Image(systemName: "tray")
                        .font(.system(size: 50))
                        .foregroundColor(.gray)
                    Text("No Content Available")
                        .font(.headline)
                        .foregroundColor(.gray)
                }''',
                content
            )
        
        # Replace AnyShapeStyle with Color
        content = re.sub(
            r':\s*any\s+ShapeStyle|:\s*AnyShapeStyle',
            ': Color',
            content
        )
        
        # Remove .scrollTargetBehavior
        content = re.sub(
            r'\.scrollTargetBehavior\([^)]*\)',
            '',
            content
        )
        
        # Remove .scrollPosition
        content = re.sub(
            r'\.scrollPosition\([^)]*\)',
            '',
            content
        )
        
        # Remove .scrollClipDisabled
        content = re.sub(
            r'\.scrollClipDisabled\([^)]*\)',
            '',
            content
        )
        
        # Remove .sensoryFeedback
        content = re.sub(
            r'\.sensoryFeedback\([^)]*\)',
            '',
            content
        )
        
        # Replace NavigationStack with NavigationView for complex cases
        if 'NavigationStack' in content and 'path:' in content:
            # Complex NavigationStack with path binding - replace with NavigationView
            content = re.sub(
                r'NavigationStack\(path:\s*[^)]+\)\s*\{',
                'NavigationView {',
                content
            )
        
        return content