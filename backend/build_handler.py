import asyncio
import json
import os
import time
from typing import Dict, Any, Optional
from fastapi import WebSocket
import logging

from build_service import BuildService, BuildStatus
from simulator_service import SimulatorService
from app_name_sanitizer import AppNameSanitizer

class BuildHandler:
    """Handles build requests through WebSocket with production-ready error handling"""

    def __init__(self, workspace_dir: str, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.build_service = BuildService(workspace_dir, logger=self.logger)
        self.active_builds: Dict[str, asyncio.Task] = {}

    async def handle_build_request(self, websocket: WebSocket, project_id: str,
                                   project_path: str, app_name: str):
        """Handle build request with real-time status updates"""

        # Cancel any existing build for this project
        if project_id in self.active_builds:
            self.active_builds[project_id].cancel()
            await asyncio.sleep(1)  # Let cancellation complete

        # Create build task
        build_task = asyncio.create_task(
            self._execute_build(websocket, project_id, project_path, app_name)
        )
        self.active_builds[project_id] = build_task

        try:
            await build_task
        finally:
            # Clean up
            if project_id in self.active_builds:
                del self.active_builds[project_id]

    async def _execute_build(self, websocket: WebSocket, project_id: str,
                             project_path: str, app_name: str):
        """Execute build with status updates"""

        try:
            # Fix naming consistency issues first
            await self._fix_project_naming(project_path, app_name)

            # Subscribe to build status updates
            status_queue = asyncio.Queue()

            async def status_callback(status: BuildStatus, message: str):
                await status_queue.put((status, message))

            # Start build in background
            build_future = asyncio.create_task(
                self.build_service.build_and_run(project_path)
            )

            # Send status updates while building
            last_status = None
            while not build_future.done():
                try:
                    # Wait for status update or timeout
                    status, message = await asyncio.wait_for(
                        status_queue.get(),
                        timeout=0.5
                    )

                    if status != last_status:
                        await self._send_status(websocket, project_id, status, message)
                        last_status = status

                except asyncio.TimeoutError:
                    # Send heartbeat
                    if last_status:
                        await self._send_heartbeat(websocket, project_id)
                    continue

            # Get build result
            build_result = await build_future

            # Send final result
            await self._send_build_result(websocket, project_id, build_result)

            # If successful, send screenshot
            if build_result.success and build_result.simulator_screenshot:
                await self._send_screenshot(websocket, project_id,
                                            build_result.simulator_screenshot)

        except asyncio.CancelledError:
            await self._send_status(
                websocket, project_id, BuildStatus.FAILED,
                "Build cancelled by user"
            )
            raise
        except Exception as e:
            self.logger.error(f"Build failed for {project_id}: {e}", exc_info=True)
            await self._send_error(websocket, project_id, str(e))

    async def _fix_project_naming(self, project_path: str, app_name: str):
        """Fix any naming inconsistencies in the project"""
        try:
            import yaml

            # Read project.yml
            project_yml_path = os.path.join(project_path, "project.yml")
            with open(project_yml_path, 'r') as f:
                project_config = yaml.safe_load(f)

            # Apply consistent naming
            from app_name_sanitizer import apply_consistent_naming
            fixed_config = apply_consistent_naming(project_config, app_name)

            # Write back
            with open(project_yml_path, 'w') as f:
                yaml.dump(fixed_config, f, default_flow_style=False, sort_keys=False)

            self.logger.info(f"Fixed naming consistency for: {app_name}")

        except Exception as e:
            self.logger.warning(f"Failed to fix naming: {e}")

    async def _send_status(self, websocket: WebSocket, project_id: str,
                           status: BuildStatus, message: str):
        """Send build status update"""
        try:
            await websocket.send_json({
                "type": "build_status",
                "projectId": project_id,
                "status": status.value,
                "message": message,
                "timestamp": time.time()
            })
        except Exception as e:
            self.logger.error(f"Failed to send status: {e}")

    async def _send_heartbeat(self, websocket: WebSocket, project_id: str):
        """Send heartbeat to keep connection alive"""
        try:
            await websocket.send_json({
                "type": "heartbeat",
                "projectId": project_id,
                "timestamp": time.time()
            })
        except Exception:
            pass

    async def _send_build_result(self, websocket: WebSocket, project_id: str,
                                 build_result):
        """Send final build result"""
        try:
            result_data = {
                "type": "build_result",
                "projectId": project_id,
                "success": build_result.success,
                "status": build_result.status.value,
                "message": build_result.message,
                "timestamp": time.time()
            }

            if build_result.app_path:
                result_data["appPath"] = build_result.app_path
            if build_result.bundle_id:
                result_data["bundleId"] = build_result.bundle_id
            if build_result.errors:
                result_data["errors"] = build_result.errors

            await websocket.send_json(result_data)

        except Exception as e:
            self.logger.error(f"Failed to send build result: {e}")

    async def _send_screenshot(self, websocket: WebSocket, project_id: str,
                               screenshot_path: str):
        """Send simulator screenshot"""
        try:
            import base64

            with open(screenshot_path, 'rb') as f:
                screenshot_data = base64.b64encode(f.read()).decode('utf-8')

            await websocket.send_json({
                "type": "screenshot",
                "projectId": project_id,
                "data": screenshot_data,
                "timestamp": time.time()
            })

        except Exception as e:
            self.logger.error(f"Failed to send screenshot: {e}")

    async def _send_error(self, websocket: WebSocket, project_id: str, error: str):
        """Send error message"""
        try:
            await websocket.send_json({
                "type": "error",
                "projectId": project_id,
                "error": error,
                "timestamp": time.time()
            })
        except Exception as e:
            self.logger.error(f"Failed to send error: {e}")

    async def cancel_build(self, project_id: str):
        """Cancel an active build"""
        if project_id in self.active_builds:
            self.active_builds[project_id].cancel()
            return True
        return False

    async def get_build_logs(self, project_id: str, project_path: str) -> Dict[str, Any]:
        """Get build logs for a project"""
        try:
            logs = await self.build_service.get_build_logs(project_path)

            # Also get app logs if available
            bundle_id = self._get_last_bundle_id(project_path)
            app_logs = ""

            if bundle_id:
                app_logs = await self.build_service.simulator_service.get_app_logs(
                    bundle_id, lines=200
                )

            return {
                "buildLogs": logs,
                "appLogs": app_logs,
                "timestamp": time.time()
            }

        except Exception as e:
            self.logger.error(f"Failed to get logs: {e}")
            return {
                "error": str(e),
                "timestamp": time.time()
            }

    def _get_last_bundle_id(self, project_path: str) -> Optional[str]:
        """Get the last built app's bundle ID"""
        try:
            # Check for a build metadata file
            metadata_path = os.path.join(project_path, ".build_metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    return metadata.get("bundle_id")
        except Exception:
            pass
        return None

    async def cleanup(self):
        """Clean up resources"""
        # Cancel all active builds
        for task in self.active_builds.values():
            task.cancel()

        # Wait for cancellations
        if self.active_builds:
            await asyncio.gather(*self.active_builds.values(), return_exceptions=True)

        # Clean up services
        await self.build_service.cleanup()


# WebSocket endpoint integration
async def websocket_build_endpoint(websocket: WebSocket, project_id: str):
    """WebSocket endpoint for build operations"""
    await websocket.accept()

    build_handler = BuildHandler(workspace_dir="./workspaces")

    try:
        while True:
            data = await websocket.receive_json()

            if data["type"] == "build":
                await build_handler.handle_build_request(
                    websocket,
                    project_id,
                    data["projectPath"],
                    data["appName"]
                )

            elif data["type"] == "cancel":
                success = await build_handler.cancel_build(project_id)
                await websocket.send_json({
                    "type": "cancel_result",
                    "success": success
                })

            elif data["type"] == "get_logs":
                logs = await build_handler.get_build_logs(
                    project_id,
                    data["projectPath"]
                )
                await websocket.send_json({
                    "type": "logs",
                    **logs
                })

    except Exception as e:
        logging.error(f"WebSocket error: {e}")
    finally:
        await build_handler.cleanup()
        await websocket.close()