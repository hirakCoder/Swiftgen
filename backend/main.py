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
from typing import Optional, Dict, List

# Add current directory to Python path to ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from claude_service import ClaudeService
from build_service import BuildService
from project_manager import ProjectManager
from models import GenerateRequest, BuildStatus, ProjectStatus

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
async def root():
    return {"message": "SwiftGen MVP API", "version": "0.2.0"}

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
            "message": "Generating Swift code...",
            "status": "generating"
        })

        # Generate code using Claude
        generated_code = await claude_service.generate_ios_app(
            request.description,
            request.app_name or "MyApp"
        )

        # Store project context for future modifications
        project_contexts[project_id] = {
            "app_name": request.app_name or "MyApp",
            "description": request.description,
            "generated_files": generated_code.get("files", []),
            "features": [],
            "modifications": []
        }

        await notify_clients(project_id, {
            "type": "status",
            "message": "Creating project structure...",
            "status": "creating"
        })

        # Create project structure
        project_path = await project_manager.create_project(
            project_id,
            generated_code,
            request.app_name or "MyApp"
        )

        await notify_clients(project_id, {
            "type": "status",
            "message": "Building app...",
            "status": "building"
        })

        # Build the project
        bundle_id = generated_code.get("bundle_id")

        # Check if build_service has the new method signature
        if 'bundle_id' in build_service.build_project.__code__.co_varnames:
            build_result = await build_service.build_project(project_path, project_id, bundle_id)
        else:
            build_result = await build_service.build_project(project_path, project_id)

        if build_result.success:
            simulator_launched = getattr(build_result, 'simulator_launched', False)
            if simulator_launched:
                await notify_clients(project_id, {
                    "type": "complete",
                    "message": "App built and launched in simulator!",
                    "status": "success",
                    "project_id": project_id,
                    "simulator_launched": True
                })
            else:
                await notify_clients(project_id, {
                    "type": "complete",
                    "message": "App built successfully!",
                    "status": "success",
                    "project_id": project_id,
                    "simulator_launched": False,
                    "warnings": build_result.warnings
                })
        else:
            await notify_clients(project_id, {
                "type": "error",
                "message": "Build failed",
                "status": "failed",
                "errors": build_result.errors
            })

        return {
            "project_id": project_id,
            "status": "success" if build_result.success else "failed",
            "build_result": build_result.model_dump(),
            "generated_files": generated_code.get("files", []),
            "simulator_launched": getattr(build_result, 'simulator_launched', False) if build_result.success else False
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/modify")
async def modify_app(request: ModifyRequest):
    """Modify an existing app based on user request"""
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

        # Generate modified code using Claude
        modified_code = await claude_service.modify_ios_app(
            context.get("app_name", "MyApp"),
            context.get("description", ""),
            request.modification,
            context.get("edited_files", context.get("generated_files", [])) if context.get("manual_edit") else context.get("generated_files", [])
        )

        # Update project context
        context["modifications"].append({
            "request": request.modification,
            "timestamp": datetime.now().isoformat()
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

        # Rebuild the project
        bundle_id = context.get("bundle_id", f"com.swiftgen.{context.get('app_name', 'app').lower()}")

        if 'bundle_id' in build_service.build_project.__code__.co_varnames:
            build_result = await build_service.build_project(project_path, project_id, bundle_id)
        else:
            build_result = await build_service.build_project(project_path, project_id)

        if build_result.success:
            await notify_clients(project_id, {
                "type": "complete",
                "message": "App modified and relaunched successfully!",
                "status": "success",
                "project_id": project_id,
                "simulator_launched": getattr(build_result, 'simulator_launched', False)
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
            "status": "success" if build_result.success else "failed",
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
    status = await project_manager.get_project_status(project_id)
    bundle_id = status.get('bundle_id') if status else None

    # Create status update callback
    async def send_status_update(message: str):
        await notify_clients(project_id, {
            "type": "status",
            "message": message,
            "status": "rebuilding"
        })

    if hasattr(build_service, 'set_status_callback'):
        build_service.set_status_callback(send_status_update)

    # Check if build_service has the new method signature
    if 'bundle_id' in build_service.build_project.__code__.co_varnames:
        build_result = await build_service.build_project(project_path, project_id, bundle_id)
    else:
        build_result = await build_service.build_project(project_path, project_id)

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