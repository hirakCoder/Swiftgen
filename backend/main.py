from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
import uuid
import os
import sys
import json  # IMPORTANT: This is the json module import - never use 'json' as a variable name
import re
from datetime import datetime
from fastapi.responses import FileResponse, HTMLResponse
from typing import Optional, Dict, List
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all services
from enhanced_claude_service import EnhancedClaudeService
from build_service import BuildService
from project_manager import ProjectManager
from models import GenerateRequest, BuildStatus, ProjectStatus
from self_healing_generator import SelfHealingGenerator
from quality_assurance_pipeline import QualityAssurancePipeline
from advanced_app_generator import AdvancedAppGenerator

# Get the absolute path to the frontend directory
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
STATIC_DIR = FRONTEND_DIR / "static"

# Try to import optional services
try:
    from simulator_service import SimulatorService
    simulator_service = SimulatorService()
except ImportError:
    print("Warning: simulator_service.py not found. Simulator launch functionality will be disabled.")
    simulator_service = None

try:
    from runtime_error_handler import RuntimeErrorHandler
    runtime_handler = RuntimeErrorHandler(None)
except ImportError:
    print("Warning: runtime_error_handler.py not found. Advanced crash log parsing disabled.")
    runtime_handler = None

# Initialize RAG Knowledge Base
rag_knowledge_base = None
try:
    from rag_knowledge_base import RAGKnowledgeBase
    rag_knowledge_base = RAGKnowledgeBase()
    print("✓ RAG Knowledge Base initialized")
except Exception as e:
    print(f"Warning: RAG Knowledge Base not available: {e}")

# Initialize app
app = FastAPI(title="SwiftGen AI - World-Class iOS App Generator")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files correctly
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Initialize services with new architecture
enhanced_service = EnhancedClaudeService()
project_manager = ProjectManager()

# Initialize build service with enhanced recovery
build_service = BuildService()

# CRITICAL: Share the enhanced service with error recovery system
if hasattr(build_service, 'error_recovery_system') and build_service.error_recovery_system:
    build_service.error_recovery_system.claude_service = enhanced_service
    print("✓ Connected enhanced Claude service to error recovery system")

# Initialize new services
self_healing_generator = SelfHealingGenerator(
    rag_kb=rag_knowledge_base,
    llm_service=enhanced_service
)

qa_pipeline = QualityAssurancePipeline(
    rag_kb=rag_knowledge_base
)

advanced_generator = AdvancedAppGenerator(
    llm_service=enhanced_service
)

# Store active connections and project contexts
active_connections: dict = {}
project_contexts: dict = {}
project_state: dict = {}

# Generation statistics
generation_stats = {
    "total_attempts": 0,
    "successful_generations": 0,
    "self_healed_generations": 0,
    "failed_generations": 0,
    "validation_failures": 0,
    "unique_variations": 0,
    "llm_distribution": {
        "claude": 0,
        "gpt4": 0,
        "xai": 0,
        "fallback": 0
    }
}

class ModifyRequest(BaseModel):
    project_id: str
    modification: str
    context: Optional[Dict] = None

def extract_app_name_from_description(description: str, fallback: str = None) -> str:
    """Extract app name from user description using intelligent parsing"""
    patterns = [
        # Look for "app AppName" pattern first
        r"(?:app|application)\s+([A-Z][a-zA-Z]+)(?:\s|$)",
        # Then standard patterns
        r"(?:create|build|make)\s+(?:a|an)?\s*(?:app|application)?\s*(.+?)(?:\s+that|\s+to|\s+for|$)",
        r"(?:create|build|make)\s+(.+?)(?:\.|,|$)",
        r"^(.+?)\s*(?:app|application)",
        r"(?:called|named)\s+[\"']?(.+?)[\"']?(?:\s|$)",
    ]

    description_lower = description.lower()

    # First check for capitalized app name pattern in original description
    cap_pattern = r"(?:app|application)\s+([A-Z][a-zA-Z]+)"
    match = re.search(cap_pattern, description)
    if match:
        return match.group(1)
    
    # Then check other patterns
    for pattern in patterns[1:]:  # Skip the first pattern since we already checked it
        match = re.search(pattern, description_lower, re.IGNORECASE)
        if match:
            potential_name = match.group(1).strip()

            # Clean up
            stop_words = ['a', 'an', 'the', 'app', 'application', 'for', 'that', 'with', 'to', 'using']
            words = potential_name.split()

            while words and words[0] in stop_words:
                words.pop(0)

            if words:
                app_name = ' '.join(word.capitalize() for word in words)

                if len(app_name) > 30:
                    app_name = app_name[:30].rsplit(' ', 1)[0]

                return app_name

    # Keyword-based fallback
    app_keywords = {
        'calculator': 'Calculator',
        'todo': 'Todo List',
        'weather': 'Weather',
        'timer': 'Timer',
        'notes': 'Notes',
        'game': 'Game',
        'tracker': 'Tracker',
        'reminder': 'Reminder',
        'fitness': 'Fitness',
        'recipe': 'Recipe',
        'budget': 'Budget',
        'journal': 'Journal',
    }

    for keyword, default_name in app_keywords.items():
        if keyword in description_lower:
            # Add variation to make it unique
            import random
            variations = ['Pro', 'Plus', 'X', 'Ultimate', 'Smart', 'Quick', 'Easy', 'My']
            variation = random.choice(variations)
            return f"{variation} {default_name}"

    return fallback or "Custom App"

@app.get("/")
async def serve_index():
    """Serve the main application page"""
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        print(f"ERROR: index.html not found at {index_path}")
        print(f"FRONTEND_DIR: {FRONTEND_DIR}")
        print(f"Files in FRONTEND_DIR: {list(FRONTEND_DIR.glob('*'))}")
        raise HTTPException(status_code=404, detail=f"index.html not found at {index_path}")

    # Read and return the HTML file with cache busting
    with open(index_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Add a timestamp to force browser refresh
    timestamp = datetime.now().timestamp()
    html_content = html_content.replace('</head>', f'<meta name="cache-version" content="{timestamp}"></head>')

    return HTMLResponse(
        content=html_content,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )

@app.get("/index.html")
async def serve_index_alt():
    """Alternative route for index.html"""
    return await serve_index()

@app.get("/app.js")
async def serve_app_js():
    """Serve the app.js file"""
    app_js_path = FRONTEND_DIR / "app.js"
    if not app_js_path.exists():
        raise HTTPException(status_code=404, detail="app.js not found")
    return FileResponse(app_js_path, media_type="application/javascript")

@app.get("/editor.html")
async def serve_editor():
    """Serve the code editor page"""
    editor_path = FRONTEND_DIR / "editor.html"
    if not editor_path.exists():
        raise HTTPException(status_code=404, detail=f"editor.html not found at {editor_path}")

    with open(editor_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    return HTMLResponse(content=html_content)

def _is_complex_app(description: str) -> bool:
    """Determine if the app requires advanced architecture"""
    description_lower = description.lower()
    
    # Indicators of complex apps
    complex_indicators = [
        # Architecture patterns
        "enterprise", "production", "scalable", "professional",
        "real-world", "commercial", "business",
        # Feature complexity
        "api", "backend", "server", "database", "cloud",
        "authentication", "login", "user accounts",
        "real-time", "chat", "messaging", "notifications",
        "payment", "subscription", "in-app purchase",
        "offline", "sync", "cache",
        "social", "sharing", "collaboration",
        # Specific app types that are complex
        "ecommerce", "e-commerce", "shopping", "marketplace",
        "banking", "finance", "investment", "crypto",
        "healthcare", "medical", "fitness tracker",
        "social media", "social network",
        "uber", "airbnb", "delivery",
        # Technical requirements
        "mvvm", "clean architecture", "coordinator",
        "dependency injection", "unit test",
        "analytics", "crash reporting",
        "multiple screens", "complex navigation"
    ]
    
    # Count matches
    matches = sum(1 for indicator in complex_indicators if indicator in description_lower)
    
    # Also check for explicit mentions of needing many features
    if any(phrase in description_lower for phrase in ["full app", "complete app", "all features"]):
        matches += 2
    
    # Consider complex if 2+ indicators present
    return matches >= 2

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    # Get actual available LLMs from the service
    available_models = []
    if hasattr(enhanced_service, 'get_available_models'):
        available_models = enhanced_service.get_available_models()
        llm_names = [model.provider for model in available_models]
    else:
        llm_names = []

    return {
        "status": "healthy",
        "services": {
            "enhanced_llm": llm_names,
            "rag_kb": rag_knowledge_base is not None,
            "simulator": simulator_service is not None,
            "self_healing": True,
            "qa_pipeline": True,
            "runtime_handler": runtime_handler is not None
        },
        "stats": generation_stats,
        "llm_availability": {
            "claude": "anthropic" in llm_names,
            "gpt4": "openai" in llm_names,
            "xai": "xai" in llm_names
        },
        "model_count": len(available_models),
        "method_check": {
            "has_generate_ios_app_multi_llm": hasattr(enhanced_service, 'generate_ios_app_multi_llm'),
            "has_generate_ios_app": hasattr(enhanced_service, 'generate_ios_app'),
            "has_generate_text": hasattr(enhanced_service, 'generate_text')
        }
    }

async def _generate_app_async(project_id: str, request: GenerateRequest):
    """Async function to generate the app in background"""
    generation_start_time = datetime.now()
    
    try:
        # Extract app name
        if request.app_name and request.app_name != "MyApp":
            app_name = request.app_name
        else:
            app_name = extract_app_name_from_description(request.description)

        print(f"\n[MAIN] Generating UNIQUE app: {app_name}")
        print(f"[MAIN] Description: {request.description}")
        print(f"[MAIN] Using LLM selection for optimal results")

        # Update status with more details
        await notify_clients(project_id, {
            "type": "status",
            "message": f"🤖 Analyzing your request for {app_name}...",
            "status": "analyzing",
            "app_name": app_name,
            "description": request.description[:100] + "..." if len(request.description) > 100 else request.description
        })

        # Step 1: Generate with self-healing and UNIQUENESS
        # Detect if this is a complex app that needs advanced generation
        is_complex_app = _is_complex_app(request.description)
        
        if is_complex_app:
            await notify_clients(project_id, {
                "type": "status",
                "message": "🏗️ Architecting enterprise-grade app structure...",
                "status": "generating"
            })
        else:
            await notify_clients(project_id, {
                "type": "status",
                "message": "🧬 Creating unique implementation with AI...",
                "status": "generating"
            })

        # Use advanced generator for complex apps
        if is_complex_app:
            generated_code = await advanced_generator.generate_advanced_app(
                description=request.description,
                app_name=app_name
            )
        elif hasattr(enhanced_service, 'generate_ios_app_multi_llm'):
            generated_code = await enhanced_service.generate_ios_app_multi_llm(
                description=request.description,
                app_name=app_name
            )
        elif hasattr(enhanced_service, 'generate_ios_app'):
            generated_code = await enhanced_service.generate_ios_app(
                description=request.description,
                app_name=app_name
            )
        else:
            # Fall back to using the generate_text method with a proper prompt
            prompt = f"""Generate a complete iOS app with the following requirements:
App Name: {app_name}
Description: {request.description}

Return a JSON response with:
1. files: array of Swift source files with path and content
2. bundle_id: the app bundle identifier
3. features: array of implemented features
4. unique_aspects: what makes this implementation unique

Important: Return ONLY valid JSON, no explanatory text."""

            result = enhanced_service.generate_text(prompt)
            if result["success"]:
                # Parse the JSON response
                generated_code = json.loads(result["text"])
            else:
                raise Exception(f"Generation failed: {result.get('error', 'Unknown error')}")

        # Track which LLM was used
        llm_used = generated_code.get("generated_by_llm", "unknown")
        if llm_used in generation_stats["llm_distribution"]:
            generation_stats["llm_distribution"][llm_used] += 1

        # Track uniqueness
        if generated_code.get("unique_aspects"):
            generation_stats["unique_variations"] += 1

        # Send generation complete status with details
        files_count = len(generated_code.get("files", []))
        features = generated_code.get("features", [])
        features_preview = ', '.join(features[:3]) + ('...' if len(features) > 3 else '') if features else "standard features"
        
        await notify_clients(project_id, {
            "type": "status",
            "message": f"✨ Generated {files_count} Swift files with {features_preview}",
            "status": "generated",
            "files_count": files_count,
            "features": features
        })

        # Step 2: Run quality assurance
        await notify_clients(project_id, {
            "type": "status",
            "message": "🔍 Validating code quality and best practices...",
            "status": "validating"
        })

        validation_result = await qa_pipeline.validate(generated_code)

        if not validation_result.success:
            print(f"[MAIN] Validation failed: {validation_result.errors}")
            generation_stats["validation_failures"] += 1

            # Try to heal validation errors on existing code
            await notify_clients(project_id, {
                "type": "status",
                "message": "🔧 Applying AI fixes to resolve issues...",
                "status": "healing"
            })

            # Convert validation errors to the format expected by healing
            validation_dict = {
                "success": False,
                "errors": [
                    {
                        "type": "reserved_type" if "Reserved type conflict" in err else 
                                "missing_import" if "Missing" in err and "import" in err else
                                "naming_conflict" if "conflict" in err else "unknown",
                        "description": err,
                        "file": err.split(":")[0].strip() if ":" in err else "Sources/ContentView.swift"
                    }
                    for err in validation_result.errors
                ]
            }

            # Apply healing to existing code instead of regenerating
            healed_code = await self_healing_generator._apply_healing(
                generated_code,
                validation_dict
            )

            if healed_code:
                generated_code = healed_code
                generation_stats["self_healed_generations"] += 1

                # Re-validate
                validation_result = await qa_pipeline.validate(generated_code)

        if validation_result.warnings:
            print(f"[MAIN] Validation warnings: {validation_result.warnings[:3]}")

        # Step 2.5: Pre-build Swift code validation
        try:
            from swift_code_validator import SwiftCodeValidator
            
            # Validate and fix Swift code
            is_valid, swift_errors, fixed_files = SwiftCodeValidator.validate_files(
                generated_code.get("files", [])
            )
            
            if swift_errors:
                print(f"[MAIN] Swift validation found {len(swift_errors)} issues, attempting fixes...")
                for error in swift_errors[:5]:  # Show first 5 errors
                    print(f"  - {error}")
                
                # Use fixed files
                generated_code["files"] = fixed_files
                
        except Exception as e:
            print(f"[MAIN] Swift validation error: {e}")

        # Step 3: Create project
        await notify_clients(project_id, {
            "type": "status",
            "message": f"📁 Building {app_name} project structure...",
            "status": "creating"
        })

        project_path = await project_manager.create_project(
            project_id,
            generated_code,
            app_name
        )

        # Get project metadata - FIXED: Don't shadow the json module
        project_metadata_path = os.path.join(project_path, "project.json")
        with open(project_metadata_path, 'r') as f:
            project_metadata = json.load(f)  # Using json module correctly

        bundle_id = project_metadata['bundle_id']
        product_name = project_metadata['product_name']

        # Store project context
        project_contexts[project_id] = {
            "app_name": app_name,
            "description": request.description,
            "bundle_id": bundle_id,
            "product_name": product_name,
            "generated_files": generated_code.get("files", []),
            "features": generated_code.get("features", []),
            "generated_by_llm": llm_used,
            "unique_aspects": generated_code.get("unique_aspects", ""),
            "self_healed": generated_code.get("self_healed", False),
            "validation_warnings": validation_result.warnings,
            "modifications": [],
            "generation_timestamp": datetime.now().isoformat()
        }

        # Store initial state
        project_state[project_id] = {
            "current_files": generated_code.get("files", []).copy(),
            "version": 1
        }

        # Step 4: Build project with enhanced error recovery
        await notify_clients(project_id, {
            "type": "status",
            "message": f"🏗️ Compiling {app_name}...",
            "status": "building"
        })

        # Set build status callback
        async def build_status_callback(message: str):
            # Ensure we send proper JSON messages
            if message and not message.startswith('['):  # Skip log-style messages
                await notify_clients(project_id, {
                    "type": "status",
                    "message": message,
                    "status": "building"
                })

        build_service.set_status_callback(build_status_callback)
        
        print(f"[MAIN] Starting build for {project_id} at {project_path}")
        print(f"[MAIN] Bundle ID: {bundle_id}")
        print(f"[MAIN] Build service error recovery: {hasattr(build_service, 'error_recovery_system')}")
        
        try:
            build_result = await build_service.build_project(project_path, project_id, bundle_id)
            print(f"[MAIN] Build completed with success={build_result.success}")
            print(f"[MAIN] Build errors: {len(build_result.errors) if build_result.errors else 0}")
            print(f"[MAIN] Build warnings: {len(build_result.warnings) if build_result.warnings else 0}")
            
            if hasattr(build_result, 'simulator_launched'):
                print(f"[MAIN] Simulator launched: {build_result.simulator_launched}")
        except Exception as e:
            print(f"[MAIN] Build exception: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

        # Handle build result
        if build_result.success:
            generation_stats["successful_generations"] += 1

            simulator_launched = getattr(build_result, 'simulator_launched', False)

            # Create success message with unique aspects
            unique_info = generated_code.get("unique_aspects", "")
            features_text = ', '.join(generated_code.get('features', [])[:3])

            # Calculate total generation time
            total_time = (datetime.now() - generation_start_time).total_seconds()
            time_display = f"{int(total_time)}s" if total_time < 60 else f"{int(total_time/60)}m {int(total_time%60)}s"
            
            success_message = f"""✅ {app_name} has been created successfully!

🎨 Unique Implementation: {unique_info}
✨ Features: {features_text}
🤖 Generated by: {llm_used.upper()}
📊 Quality Score: {_calculate_quality_score(validation_result)}%
⏱️ Total Time: {time_display}"""

            await notify_clients(project_id, {
                "type": "complete",
                "message": success_message + ("\n\n📱 The app is now running in the iOS Simulator!" if simulator_launched else ""),
                "status": "success",
                "project_id": project_id,
                "simulator_launched": simulator_launched,
                "app_name": app_name,
                "features": generated_code.get("features", []),
                "unique_aspects": unique_info,
                "quality_score": _calculate_quality_score(validation_result),
                "generated_by_llm": llm_used,
                "files_count": len(generated_code.get("files", [])),
                "total_time": total_time,
                "time_display": time_display
            })

            # Send the generated files to the frontend
            await notify_clients(project_id, {
                "type": "code_generated",
                "files": generated_code.get("files", []),
                "project_id": project_id
            })

            # Background task doesn't return - all communication via WebSocket
            print(f"[MAIN] Generation completed successfully for {project_id}")
        else:
            generation_stats["failed_generations"] += 1
            
            print(f"[MAIN] Build failed, sending failure response")
            print(f"[MAIN] Error count: {len(build_result.errors)}")

            await notify_clients(project_id, {
                "type": "complete",  # Use complete type so UI handles it properly
                "message": "Build failed - but don't worry, we're learning from this! Please try again or describe what changes you'd like.",
                "status": "failed",
                "errors": build_result.errors,
                "app_name": app_name
            })

            # Learn from failure
            if rag_knowledge_base:
                for error in build_result.errors[:3]:
                    rag_knowledge_base.add_learned_solution(
                        f"Build failure for {app_name}",
                        error,
                        False
                    )

            # Send failure via WebSocket
            print(f"[MAIN] Build failed for {project_id}")

    except Exception as e:
        generation_stats["failed_generations"] += 1

        import traceback
        traceback.print_exc()

        await notify_clients(project_id, {
            "type": "error",
            "message": f"Failed to create app: {str(e)}",
            "status": "failed",
            "app_name": request.app_name or "App"
        })
        
        print(f"[MAIN] Exception in generation for {project_id}: {str(e)}")

@app.post("/api/generate")
async def generate_app(request: GenerateRequest, background_tasks: BackgroundTasks):
    """Generate iOS app with self-healing and quality assurance"""
    # Use provided project_id or generate a new one
    project_id = request.project_id if request.project_id else f"proj_{uuid.uuid4().hex[:8]}"
    generation_stats["total_attempts"] += 1
    
    # Extract app name for immediate response
    if request.app_name and request.app_name != "MyApp":
        app_name = request.app_name
    else:
        app_name = extract_app_name_from_description(request.description)
    
    # Start generation in background
    background_tasks.add_task(_generate_app_async, project_id, request)
    
    # Return immediately so frontend can connect WebSocket
    return {
        "project_id": project_id,
        "app_name": app_name,
        "status": "started",
        "message": "Generation started"
    }

@app.post("/api/modify")
async def modify_app(request: ModifyRequest):
    """Modify an existing app with AI-powered enhancements"""
    try:
        project_id = request.project_id

        # Check if project exists
        project_path = await project_manager.get_project_path(project_id)
        if not project_path:
            raise HTTPException(status_code=404, detail="Project not found")

        # Get project context
        context = project_contexts.get(project_id, {})
        current_state = project_state.get(project_id, {})

        if request.context:
            context.update(request.context)

        # Get project metadata - FIXED: Don't shadow the json module
        project_metadata_path = os.path.join(project_path, "project.json")
        with open(project_metadata_path, 'r') as f:
            project_metadata = json.load(f)  # Using json module correctly

        bundle_id = project_metadata.get('bundle_id')
        app_name = project_metadata.get('app_name', context.get("app_name", "MyApp"))

        # Use current state files
        files_to_modify = current_state.get("current_files", context.get("generated_files", []))

        await notify_clients(project_id, {
            "type": "status",
            "message": "🔍 AI is analyzing your modification request...",
            "status": "analyzing",
            "app_name": app_name
        })

        # Generate modified code with INTELLIGENCE
        try:
            # Check if the method exists, otherwise fall back
            if hasattr(enhanced_service, 'modify_ios_app_multi_llm'):
                modified_code = await enhanced_service.modify_ios_app_multi_llm(
                    app_name,
                    context.get("description", ""),
                    request.modification,
                    files_to_modify,
                    existing_bundle_id=bundle_id,
                    project_tracking_id=context.get("project_tracking_id", None)
                )
            elif hasattr(enhanced_service, 'modify_ios_app'):
                modified_code = await enhanced_service.modify_ios_app(
                    app_name,
                    context.get("description", ""),
                    request.modification,
                    files_to_modify
                )
            else:
                # Fall back to using generate_text with modification prompt
                prompt = f"""Modify the existing iOS app with these details:
App Name: {app_name}
Current Description: {context.get("description", "")}
Modification Request: {request.modification}
Bundle ID: {bundle_id}

Current files to modify:
{json.dumps([{"path": f["path"], "content_preview": f["content"][:200] + "..."} for f in files_to_modify[:3]], indent=2)}

Return a JSON response with the modified files and changes made."""

                result = enhanced_service.generate_text(prompt)
                if result["success"]:
                    modified_code = json.loads(result["text"])  # Using json module correctly
                else:
                    raise Exception(f"Modification failed: {result.get('error', 'Unknown error')}")
        
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON parsing error in modification: {e}")
            await notify_clients(project_id, {
                "type": "error",
                "message": "❌ Failed to parse modification response",
                "status": "error"
            })
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to parse modification response: {str(e)}"}
            )
        except Exception as e:
            print(f"[ERROR] Modification error: {e}")
            await notify_clients(project_id, {
                "type": "error", 
                "message": f"❌ Modification failed: {str(e)}",
                "status": "error"
            })
            return JSONResponse(
                status_code=500,
                content={"error": f"Modification failed: {str(e)}"}
            )

        # Check if parsing actually succeeded
        parsing_failed = (
            not modified_code.get("files") or 
            len(modified_code.get("files", [])) == 0 or
            any("Error:" in str(change) for change in modified_code.get("changes_made", []))
        )

        if parsing_failed:
            print("[ERROR] Parsing failed - no files or error in changes")
            await notify_clients(project_id, {
                "type": "error",
                "message": "❌ Failed to parse modification response. Please try rephrasing your request.",
                "status": "error"
            })
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to parse modification response. The AI couldn't understand the request format."}
            )

        # Track which LLM was used for modification
        llm_used = modified_code.get("modified_by_llm", "unknown")

        # Validate modifications
        await notify_clients(project_id, {
            "type": "status",
            "message": "🔍 Ensuring modification quality...",
            "status": "validating"
        })

        validation_result = await qa_pipeline.validate(modified_code)

        if not validation_result.success:
            # Try to fix with self-healing
            # Convert validation errors to expected format
            validation_errors = []
            for error in validation_result.errors:
                if isinstance(error, str):
                    # Parse the error string to extract type
                    error_type = "other"
                    if "DependencyValidator" in error:
                        error_type = "phantom_dependency"
                    elif "NamingConflictValidator" in error:
                        error_type = "reserved_type"
                    elif "BuildabilityValidator" in error:
                        error_type = "syntax"

                    validation_errors.append({
                        "type": error_type,
                        "description": error
                    })
                else:
                    validation_errors.append(error)

            # Create proper validation result format
            validation_dict = {
                "success": False,
                "errors": validation_errors
            }

            healed = await self_healing_generator._apply_healing(
                modified_code,
                validation_dict
            )

            if healed:
                modified_code = healed
                validation_result = await qa_pipeline.validate(modified_code)

        # Update project state
        project_state[project_id]["current_files"] = modified_code.get("files", []).copy()
        project_state[project_id]["version"] += 1

        # Update context
        if "modifications" not in context:
            context["modifications"] = []
            
        context["modifications"].append({
            "request": request.modification,
            "timestamp": datetime.now().isoformat(),
            "validation_warnings": validation_result.warnings,
            "modified_by_llm": llm_used,
            "version": project_state[project_id]["version"]
        })

        project_contexts[project_id] = context

        # Update files
        await notify_clients(project_id, {
            "type": "status",
            "message": "📝 Applying intelligent modifications...",
            "status": "updating"
        })

        await project_manager.update_project_files(
            project_id,
            modified_code.get("files", [])
        )

        # Rebuild
        await notify_clients(project_id, {
            "type": "status",
            "message": "🏗️ Rebuilding with your changes...",
            "status": "rebuilding"
        })

        # Set build status callback
        async def build_status_callback(message: str):
            # Ensure we send proper JSON messages
            if message and not message.startswith('['):  # Skip log-style messages
                await notify_clients(project_id, {
                    "type": "status",
                    "message": message,
                    "status": "building"
                })

        build_service.set_status_callback(build_status_callback)
        build_result = await build_service.build_project(project_path, project_id, bundle_id)

        if build_result.success:
            modification_summary = modified_code.get("modification_summary", "Changes applied")

            # Create detailed modification message
            changes_detail = modified_code.get("changes_made", [])
            changes_text = '\n'.join(f"• {change}" for change in changes_detail[:5]) if changes_detail else modification_summary
            
            detailed_message = f"""✅ {app_name} has been modified successfully!

📝 Changes Applied:
{changes_text}

🤖 Modified by: {llm_used.upper()}
📊 Quality Score: {_calculate_quality_score(validation_result)}%
📁 Files Updated: {len(modified_code.get("files", []))}"""

            await notify_clients(project_id, {
                "type": "complete",
                "message": detailed_message,
                "status": "success",
                "project_id": project_id,
                "app_name": app_name,
                "modification_summary": modification_summary,
                "changes_made": changes_detail,
                "modified_by_llm": llm_used,
                "files_updated": len(modified_code.get("files", [])),
                "quality_score": _calculate_quality_score(validation_result)
            })

            # Send updated files to frontend
            await notify_clients(project_id, {
                "type": "code_generated",
                "files": modified_code.get("files", []),
                "project_id": project_id
            })

            return {
                "project_id": project_id,
                "bundle_id": bundle_id,
                "app_name": app_name,
                "status": "success",
                "build_result": build_result.model_dump(),
                "modified_files": modified_code.get("files", []),
                "files": modified_code.get("files", []),  # Include for frontend
                "modification_summary": modification_summary,
                "modified_by_llm": llm_used,
                "quality_score": _calculate_quality_score(validation_result)
            }
        else:
            await notify_clients(project_id, {
                "type": "error",
                "message": "Build failed after modification",
                "status": "failed",
                "errors": build_result.errors,
                "app_name": app_name
            })

            # Return error response instead of throwing exception
            return {
                "project_id": project_id,
                "status": "failed",
                "message": "Build failed after modification",
                "errors": build_result.errors,
                "app_name": app_name
            }

    except Exception as e:
        import traceback
        traceback.print_exc()
        
        # Return error response instead of throwing exception
        return {
            "project_id": project_id,
            "status": "failed", 
            "message": f"Modification failed: {str(e)}",
            "error": str(e)
        }

@app.get("/api/stats")
async def get_generation_stats():
    """Get generation statistics and quality metrics"""
    qa_stats = qa_pipeline.get_validation_stats()

    success_rate = 0
    if generation_stats["total_attempts"] > 0:
        success_rate = (generation_stats["successful_generations"] / generation_stats["total_attempts"]) * 100

    # Calculate LLM usage percentages
    total_llm_uses = sum(generation_stats["llm_distribution"].values())
    llm_percentages = {}
    if total_llm_uses > 0:
        for llm, count in generation_stats["llm_distribution"].items():
            llm_percentages[llm] = f"{(count / total_llm_uses * 100):.1f}%"

    # Get error recovery stats if available
    recovery_stats = {}
    if hasattr(build_service, 'error_recovery_system') and build_service.error_recovery_system:
        if hasattr(build_service.error_recovery_system, 'get_recovery_metrics'):
            recovery_stats = build_service.error_recovery_system.get_recovery_metrics()

    # Get available models info
    available_models = []
    if hasattr(enhanced_service, 'get_available_models'):
        available_models = enhanced_service.get_available_models()

    llm_info = {
        "count": len(available_models),
        "providers": [model.provider for model in available_models] if available_models else [],
        "models": [{"name": model.name, "provider": model.provider} for model in available_models] if available_models else []
    }

    return {
        "generation_stats": generation_stats,
        "success_rate": f"{success_rate:.1f}%",
        "qa_stats": qa_stats,
        "llm_info": llm_info,
        "llm_usage": llm_percentages,
        "recovery_stats": recovery_stats,
        "rag_documents": len(rag_knowledge_base.metadata) if rag_knowledge_base else 0,
        "unique_apps_created": generation_stats["unique_variations"],
        "learning_enabled": rag_knowledge_base is not None
    }

@app.get("/api/projects")
async def list_projects():
    """List all projects with enhanced metadata"""
    projects = await project_manager.list_projects()

    # Enhance with context information
    enhanced_projects = []
    for project in projects:
        project_id = project["project_id"]
        if project_id in project_contexts:
            context = project_contexts[project_id]
            project["features"] = context.get("features", [])[:3]
            project["generated_by_llm"] = context.get("generated_by_llm", "unknown")
            project["unique_aspects"] = context.get("unique_aspects", "")
            project["modifications_count"] = len(context.get("modifications", []))

        enhanced_projects.append(project)

    return enhanced_projects

@app.get("/api/project/{project_id}/status")
async def get_project_status(project_id: str):
    """Get current project status with full context"""
    status = await project_manager.get_project_status(project_id)
    if not status:
        raise HTTPException(status_code=404, detail="Project not found")

    if project_id in project_contexts:
        status["context"] = project_contexts[project_id]

    if project_id in project_state:
        status["state_version"] = project_state[project_id].get("version", 1)

    return status

@app.get("/api/project/{project_id}/files")
async def get_project_files(project_id: str):
    """Get project source files"""
    if project_id in project_state:
        current_files = project_state[project_id].get("current_files", [])
        if current_files:
            return {
                "files": current_files,
                "version": project_state[project_id].get("version", 1),
                "context": project_contexts.get(project_id, {})
            }

    files = await project_manager.get_project_files(project_id)
    return {"files": files, "version": 0}

async def handle_chat_message(websocket: WebSocket, project_id: str, message: str):
    """Handle intelligent chat messages with context awareness"""
    try:
        # Get project context
        context = project_contexts.get(project_id, {})
        app_name = context.get('app_name', 'MyApp')
        
        # Analyze message intent with improved NLP
        message_lower = message.lower()
        
        # Check if this is a modification request
        modify_keywords = ['add', 'change', 'modify', 'update', 'remove', 'delete', 'fix', 'improve', 
                          'make', 'can you', 'please', 'want', 'need', 'should', 'would like']
        create_keywords = ['create', 'build', 'make a new', 'develop', 'start a new']
        
        is_modification = any(keyword in message_lower for keyword in modify_keywords)
        is_creation = any(keyword in message_lower for keyword in create_keywords)
        
        # Extract specific UI elements or features mentioned
        ui_elements = ['button', 'label', 'text', 'color', 'font', 'image', 'icon', 'list', 'table',
                       'navigation', 'tab', 'screen', 'view', 'layout', 'animation', 'gesture', 
                       'dark', 'theme', 'mode', 'style']
        mentioned_elements = [elem for elem in ui_elements if elem in message_lower]
        
        # Determine action
        if project_id and project_id != "new":
            # ANY request when a project exists should be treated as modification
            # This prevents accidentally creating new apps
            modification_type = "unknown"
            if mentioned_elements:
                modification_type = f"UI update ({', '.join(mentioned_elements)})"
            elif is_modification:
                modification_type = "feature modification"
            else:
                # Even if no keywords detected, treat as modification
                modification_type = "app update"
            
            await websocket.send_json({
                "type": "chat_response",
                "message": f"I understand you want to modify {app_name}. Processing your {modification_type} request...",
                "action": "modify",
                "project_id": project_id
            })
            
            # Send modification request
            modify_request = {
                "project_id": project_id,
                "modification": message,
                "context": context
            }
            
            # Instead of calling the API directly, send a message to trigger frontend action
            await websocket.send_json({
                "type": "trigger_modification",
                "data": modify_request
            })
            
        elif is_creation and (not project_id or project_id == "new"):
            # New app creation
            await websocket.send_json({
                "type": "chat_response", 
                "message": "I'll help you create a new app. Please describe what you'd like to build.",
                "action": "create"
            })
            
        else:
            # General help or unclear request
            help_message = "I can help you:\n"
            if project_id and project_id != "new":
                help_message += f"• Modify {app_name} - just describe what changes you want\n"
                help_message += "• Add new features like buttons, screens, or functionality\n"
                help_message += "• Change colors, layout, or UI elements\n"
            else:
                help_message += "• Create a new iOS app - describe what you want to build\n"
                help_message += "• Examples: 'Create a todo list app' or 'Build a calculator'\n"
            
            await websocket.send_json({
                "type": "chat_response",
                "message": help_message,
                "action": "help"
            })
            
    except Exception as e:
        print(f"Error handling chat message: {e}")
        await websocket.send_json({
            "type": "error",
            "message": "Sorry, I couldn't process your message. Please try again."
        })

@app.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """WebSocket for real-time updates"""
    try:
        await websocket.accept()

        if project_id not in active_connections:
            active_connections[project_id] = []
        active_connections[project_id].append(websocket)

        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket connected successfully",
            "project_id": project_id
        })

        while True:
            try:
                message = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                if message == "ping":
                    await websocket.send_text("pong")
                else:
                    # Handle chat messages
                    try:
                        msg_data = json.loads(message)
                        if msg_data.get("type") == "chat":
                            await handle_chat_message(websocket, project_id, msg_data.get("content", ""))
                    except json.JSONDecodeError:
                        # If not JSON, treat as plain text chat message
                        await handle_chat_message(websocket, project_id, message)
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "heartbeat", "timestamp": datetime.now().isoformat()})

    except WebSocketDisconnect:
        if project_id in active_connections and websocket in active_connections[project_id]:
            active_connections[project_id].remove(websocket)
            if not active_connections[project_id]:
                del active_connections[project_id]
    except Exception as e:
        print(f"WebSocket error: {e}")
        if project_id in active_connections and websocket in active_connections[project_id]:
            active_connections[project_id].remove(websocket)

async def notify_clients(project_id: str, message: dict):
    """Send message to all connected clients for a project"""
    if project_id in project_contexts and 'app_name' not in message:
        context = project_contexts[project_id]
        message['app_name'] = context.get('app_name', 'App')

    # Ensure project_id is in the message
    message['project_id'] = project_id
    
    # Debug logging
    print(f"[NOTIFY] Sending to {project_id}: type={message.get('type')}, status={message.get('status')}")

    if project_id in active_connections:
        disconnected = []
        for connection in active_connections[project_id]:
            try:
                await connection.send_json(message)
                print(f"[NOTIFY] Sent successfully to connection")
            except Exception as e:
                print(f"[NOTIFY] Failed to send: {str(e)}")
                disconnected.append(connection)

        for conn in disconnected:
            active_connections[project_id].remove(conn)
    else:
        print(f"[NOTIFY] No active connections for {project_id}")

def _calculate_quality_score(validation_result) -> int:
    """Calculate a quality score based on validation results"""
    # Start with 100
    score = 100

    # Deduct for errors (should be 0 if we're here)
    score -= len(validation_result.errors) * 20

    # Deduct for warnings
    score -= len(validation_result.warnings) * 5

    # Ensure score is between 0 and 100
    return max(0, min(100, score))

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("\n" + "="*60)
    print("🚀 SwiftGen AI - World-Class iOS App Generator")
    print("="*60)

    # Get available models from enhanced service
    available_models = []
    if hasattr(enhanced_service, 'get_available_models'):
        available_models = enhanced_service.get_available_models()

    print(f"✓ Enhanced Claude Service: {len(available_models)} LLMs available")
    print(f"✓ Self-Healing Generator: Enabled")
    print(f"✓ Quality Assurance Pipeline: Active")
    print(f"✓ RAG Knowledge Base: {'Active' if rag_knowledge_base else 'Disabled'}")
    print(f"✓ Simulator Service: {'Available' if simulator_service else 'Not available'}")
    print(f"✓ Runtime Error Handler: {'Available' if runtime_handler else 'Not available'}")
    print("="*60)

    # Show which LLMs are available
    if available_models:
        print("Available LLMs:")
        for model in available_models:
            print(f"  - {model.name} ({model.provider})")

    print("="*60)
    print("Ready to create unique, world-class iOS apps!")
    print("="*60 + "\n")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)