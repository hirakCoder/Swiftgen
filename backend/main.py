from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
import uuid
import os
import sys
import json
from datetime import datetime
from fastapi.responses import FileResponse
from typing import Optional, Dict, List

# Add current directory to Python path to ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from claude_service import ClaudeService
from build_service import BuildService
from project_manager import ProjectManager
from models import GenerateRequest, BuildStatus, ProjectStatus

# Import EnhancedClaudeService if available
try:
    # Try both possible naming conventions
    try:
        from enhanced_claude_service import EnhancedClaudeService
    except ImportError:
        from enhancedClaudeService import EnhancedClaudeService

    enhanced_service = EnhancedClaudeService()
    use_enhanced_service = True
    print("Using Enhanced Multi-LLM Service")
except Exception as e:
    enhanced_service = None
    use_enhanced_service = False
    print(f"Enhanced service not available: {str(e)}")
    print("Using standard Claude service")

# Import SimulatorService - we'll handle if it doesn't exist
try:
    from simulator_service import SimulatorService
    simulator_service = SimulatorService()
except ImportError:
    print("Warning: simulator_service.py not found. Simulator launch functionality will be disabled.")
    simulator_service = None

app = FastAPI(title="SwiftGen MVP")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# Initialize services
claude_service = ClaudeService()
build_service = BuildService()
project_manager = ProjectManager()

# Store active connections and project contexts
active_connections: dict = {}
project_contexts: dict = {}

class ModifyRequest(BaseModel):
    project_id: str
    modification: str
    context: Optional[Dict] = None

@app.get("/")
async def serve_index():
    """Serve the main application page"""
    return FileResponse("../frontend/index.html")

@app.get("/editor.html")
async def serve_editor():
    """Serve the code editor page"""
    return FileResponse("../frontend/editor.html")

@app.post("/api/generate")
async def generate_app(request: GenerateRequest):
    """Generate iOS app from natural language description"""
    try:
        # Create project ID
        project_id = f"proj_{uuid.uuid4().hex[:8]}"

        # Create status update callback
        async def send_status_update(message: str):
            await notify_clients(project_id, {
                "type": "status",
                "message": message,
                "status": "building"
            })

        # Set callback for build service if it supports it
        if hasattr(build_service, 'set_status_callback'):
            build_service.set_status_callback(send_status_update)

        # Update connected clients
        await notify_clients(project_id, {
            "type": "status",
            "message": "Analyzing your request...",
            "status": "analyzing"
        })

        # Generate code using enhanced service if available, otherwise use standard
        if use_enhanced_service and enhanced_service:
            print(f"[MAIN] Using enhanced multi-LLM service for generation")
            generated_code = await enhanced_service.generate_ios_app_multi_llm(
                description=request.description,
                app_name=request.app_name
            )
        else:
            print(f"[MAIN] Using standard Claude service for generation")
            generated_code = await claude_service.generate_ios_app(
                description=request.description,
                app_name=request.app_name
            )

        # CRITICAL: Debug what we received
        print(f"\n[MAIN] Generated code structure:")
        print(f"  Type: {type(generated_code)}")
        print(f"  Keys: {generated_code.keys() if isinstance(generated_code, dict) else 'Not a dict'}")
        print(f"  Number of files: {len(generated_code.get('files', []))}")

        # Log file details
        if "files" in generated_code:
            for i, file in enumerate(generated_code["files"]):
                print(f"  File {i+1}: {file.get('path', 'unknown')} ({len(file.get('content', ''))} chars)")

        # Get the actual app name from the response
        actual_app_name = generated_code.get("app_name", request.app_name or "MyApp")

        # CRITICAL FIX: Create project with the generated code AS IS
        await notify_clients(project_id, {
            "type": "status",
            "message": f"Creating {actual_app_name} with unique features...",
            "status": "creating"
        })

        # Create project structure - pass the ENTIRE generated_code dict
        print(f"\n[MAIN] Passing generated_code to project_manager.create_project")
        project_path = await project_manager.create_project(
            project_id,
            generated_code,  # Pass the entire dict with files
            actual_app_name
        )

        # CRITICAL: Get the actual bundle ID from the project metadata
        project_metadata_path = os.path.join(project_path, "project.json")
        with open(project_metadata_path, 'r') as f:
            project_metadata = json.load(f)

        # Use the CORRECT bundle ID from project manager
        correct_bundle_id = project_metadata['bundle_id']
        correct_product_name = project_metadata['product_name']

        print(f"[MAIN] Using CORRECT bundle ID: {correct_bundle_id} (not {generated_code.get('bundle_id', 'none')})")

        # Log which LLM was used if multi-LLM
        if generated_code.get("multi_llm_generated"):
            print(f"[MAIN] App generated using multiple LLMs")

        # Store project context for future modifications with CORRECT bundle ID
        project_contexts[project_id] = {
            "app_name": actual_app_name,
            "description": request.description,
            "bundle_id": correct_bundle_id,  # Use the CORRECT bundle ID
            "product_name": correct_product_name,
            "generated_files": generated_code.get("files", []),
            "features": generated_code.get("features", []),
            "unique_aspects": generated_code.get("unique_aspects", ""),
            "modifications": [],
            "generated_by_llm": generated_code.get("generated_by_llm", "claude")
        }

        await notify_clients(project_id, {
            "type": "status",
            "message": "Building your unique app...",
            "status": "building"
        })

        # Build the project with the CORRECT bundle ID
        build_result = await build_service.build_project(project_path, project_id, correct_bundle_id)

        # Determine final status based on build and launch results
        final_status = "failed"
        status_type = "error"

        if build_result.success:
            simulator_launched = getattr(build_result, 'simulator_launched', False)

            if simulator_launched:
                final_status = "success"
                status_type = "complete"
            else:
                # Build succeeded but launch failed
                final_status = "warning"
                status_type = "complete"

            unique_message = f"""✅ {actual_app_name} has been created successfully!

Unique features: {', '.join(generated_code.get('features', [])[:3])}

{generated_code.get('unique_aspects', '')}"""

            if simulator_launched:
                await notify_clients(project_id, {
                    "type": status_type,
                    "message": unique_message + "\n\n📱 The app is now running in the iOS Simulator!",
                    "status": "success",
                    "project_id": project_id,
                    "simulator_launched": True,
                    "app_name": actual_app_name
                })
            else:
                # Check if it's a launch failure
                launch_failed = any("Failed to launch app" in w for w in build_result.warnings)
                if launch_failed:
                    await notify_clients(project_id, {
                        "type": status_type,
                        "message": unique_message + "\n\n⚠️ App built successfully but couldn't launch in simulator. You can manually open it from Xcode.",
                        "status": "warning",
                        "project_id": project_id,
                        "simulator_launched": False,
                        "warnings": build_result.warnings,
                        "app_name": actual_app_name
                    })
                else:
                    await notify_clients(project_id, {
                        "type": status_type,
                        "message": unique_message,
                        "status": "success",
                        "project_id": project_id,
                        "simulator_launched": False,
                        "warnings": build_result.warnings,
                        "app_name": actual_app_name
                    })
        else:
            await notify_clients(project_id, {
                "type": "error",
                "message": "Build failed - attempting automatic fixes...",
                "status": "failed",
                "errors": build_result.errors
            })

        return {
            "project_id": project_id,
            "app_name": actual_app_name,
            "bundle_id": correct_bundle_id,  # Return the CORRECT bundle ID
            "product_name": correct_product_name,
            "status": final_status,  # success, warning, or failed
            "build_result": build_result.model_dump(),
            "generated_files": generated_code.get("files", []),
            "features": generated_code.get("features", []),
            "unique_aspects": generated_code.get("unique_aspects", ""),
            "simulator_launched": getattr(build_result, 'simulator_launched', False) if build_result.success else False
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/modify")
async def modify_app(request: ModifyRequest):
    """Modify an existing app based on user request"""
    print(f"[MODIFY API] Received request: {request.modification}")
    print(f"[MODIFY API] Project ID: {request.project_id}")
    print(f"[MODIFY API] Context: {request.context}")

    try:
        project_id = request.project_id

        # Check if project exists
        project_path = await project_manager.get_project_path(project_id)
        if not project_path:
            raise HTTPException(status_code=404, detail="Project not found")

        # Get project context
        context = project_contexts.get(project_id, {})
        if request.context:
            context.update(request.context)

        # CRITICAL: Get the bundle ID from project metadata, not from context
        project_metadata_path = os.path.join(project_path, "project.json")
        if os.path.exists(project_metadata_path):
            with open(project_metadata_path, 'r') as f:
                project_metadata = json.load(f)
                bundle_id = project_metadata.get('bundle_id')
                product_name = project_metadata.get('product_name')
        else:
            # Fallback to context
            bundle_id = context.get("bundle_id")
            product_name = context.get("product_name")

        if not bundle_id:
            # Last resort: generate safe bundle ID
            from claude_service import ClaudeService
            temp_service = ClaudeService()
            bundle_id = temp_service._create_safe_bundle_id(context.get("app_name", "app"))

        print(f"[MAIN] Modifying app with bundle ID: {bundle_id}")

        # Create status update callback
        async def send_status_update(message: str):
            await notify_clients(project_id, {
                "type": "status",
                "message": message,
                "status": "modifying"
            })

        if hasattr(build_service, 'set_status_callback'):
            build_service.set_status_callback(send_status_update)

        await notify_clients(project_id, {
            "type": "status",
            "message": "Analyzing modification request...",
            "status": "analyzing"
        })

        # Generate modified code using enhanced service if available
        if use_enhanced_service and enhanced_service:
            print(f"[MAIN] Using enhanced multi-LLM service for modification")
            modified_code = await enhanced_service.modify_ios_app_multi_llm(
                context.get("app_name", "MyApp"),
                context.get("description", ""),
                request.modification,
                context.get("edited_files", context.get("generated_files", [])) if context.get("manual_edit") else context.get("generated_files", []),
                existing_bundle_id=bundle_id
            )
        else:
            print(f"[MAIN] Using standard Claude service for modification")
            modified_code = await claude_service.modify_ios_app(
                context.get("app_name", "MyApp"),
                context.get("description", ""),
                request.modification,
                context.get("edited_files", context.get("generated_files", [])) if context.get("manual_edit") else context.get("generated_files", []),
                existing_bundle_id=bundle_id
            )

        # CRITICAL: Ensure the bundle ID remains the same
        modified_code["bundle_id"] = bundle_id

        # Update project context
        context["modifications"].append({
            "request": request.modification,
            "timestamp": datetime.now().isoformat(),
            "modified_by_llm": modified_code.get("modified_by_llm", "claude")
        })
        if "features" in modified_code:
            context["features"].extend(modified_code["features"])
        project_contexts[project_id] = context

        await notify_clients(project_id, {
            "type": "status",
            "message": "Updating project files...",
            "status": "updating"
        })

        # Update project files
        await project_manager.update_project_files(
            project_id,
            modified_code.get("files", [])
        )

        await notify_clients(project_id, {
            "type": "status",
            "message": "Rebuilding app with changes...",
            "status": "rebuilding"
        })

        # Rebuild the project with the same bundle ID
        build_result = await build_service.build_project(project_path, project_id, bundle_id)

        # Determine final status
        final_status = "failed"
        status_type = "error"

        if build_result.success:
            simulator_launched = getattr(build_result, 'simulator_launched', False)

            if simulator_launched:
                final_status = "success"
                status_type = "complete"
            else:
                final_status = "warning"
                status_type = "complete"

            if simulator_launched:
                await notify_clients(project_id, {
                    "type": status_type,
                    "message": "✅ App modified and relaunched successfully!",
                    "status": "success",
                    "project_id": project_id,
                    "simulator_launched": True
                })
            else:
                # Check if it's a launch failure
                launch_failed = any("Failed to launch app" in w for w in build_result.warnings)
                if launch_failed:
                    await notify_clients(project_id, {
                        "type": status_type,
                        "message": "✅ App modified successfully!\n\n⚠️ The build succeeded but couldn't relaunch in simulator. The app has been updated - you may need to manually launch it.",
                        "status": "warning",
                        "project_id": project_id,
                        "simulator_launched": False,
                        "warnings": build_result.warnings
                    })
                else:
                    await notify_clients(project_id, {
                        "type": status_type,
                        "message": "✅ App modified successfully!",
                        "status": "success",
                        "project_id": project_id,
                        "simulator_launched": False
                    })
        else:
            await notify_clients(project_id, {
                "type": "error",
                "message": "Build failed after modification",
                "status": "failed",
                "errors": build_result.errors
            })

        return {
            "project_id": project_id,
            "bundle_id": bundle_id,
            "product_name": product_name,
            "status": final_status,  # success, warning, or failed
            "build_result": build_result.model_dump(),
            "modified_files": modified_code.get("files", []),
            "features_added": modified_code.get("features", [])
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects")
async def list_projects():
    """List all projects"""
    projects = await project_manager.list_projects()
    return projects

@app.get("/api/project/{project_id}/status")
async def get_project_status(project_id: str):
    """Get current project status"""
    status = await project_manager.get_project_status(project_id)
    if not status:
        raise HTTPException(status_code=404, detail="Project not found")

    # Add context information if available
    if project_id in project_contexts:
        status["context"] = project_contexts[project_id]

    return status

@app.get("/api/project/{project_id}/files")
async def get_project_files(project_id: str):
    """Get project source files"""
    files = await project_manager.get_project_files(project_id)
    return {"files": files}

@app.post("/api/project/{project_id}/rebuild")
async def rebuild_project(project_id: str):
    """Rebuild an existing project"""
    project_path = await project_manager.get_project_path(project_id)
    if not project_path:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get project metadata for bundle ID
    project_metadata_path = os.path.join(project_path, "project.json")
    bundle_id = None

    if os.path.exists(project_metadata_path):
        with open(project_metadata_path, 'r') as f:
            metadata = json.load(f)
            bundle_id = metadata.get('bundle_id')

    # Create status update callback
    async def send_status_update(message: str):
        await notify_clients(project_id, {
            "type": "status",
            "message": message,
            "status": "rebuilding"
        })

    if hasattr(build_service, 'set_status_callback'):
        build_service.set_status_callback(send_status_update)

    # Always pass bundle_id to build_project
    build_result = await build_service.build_project(project_path, project_id, bundle_id)

    return {"build_result": build_result.model_dump()}

@app.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """WebSocket for real-time updates"""
    await websocket.accept()

    if project_id not in active_connections:
        active_connections[project_id] = []
    active_connections[project_id].append(websocket)

    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections[project_id].remove(websocket)
        if not active_connections[project_id]:
            del active_connections[project_id]

async def notify_clients(project_id: str, message: dict):
    """Send message to all connected clients for a project"""
    if project_id in active_connections:
        disconnected = []
        for connection in active_connections[project_id]:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)

        # Remove disconnected clients
        for conn in disconnected:
            active_connections[project_id].remove(conn)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)