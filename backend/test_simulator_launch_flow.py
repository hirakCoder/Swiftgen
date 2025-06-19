#!/usr/bin/env python3
"""Test the complete flow from build success to simulator launch"""

import asyncio
import os
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_build_to_simulator_flow():
    """Test the complete flow"""
    
    print("=== Testing Build to Simulator Flow ===\n")
    
    # Find a project with a successful build (has .app bundle)
    workspaces_dir = Path(__file__).parent.parent / "workspaces"
    test_project = None
    
    for project_dir in sorted(workspaces_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
        if project_dir.is_dir():
            # Check for .app bundle
            build_products = project_dir / "build" / "Build" / "Products"
            if build_products.exists():
                for item in build_products.rglob("*.app"):
                    # Skip apps with special characters
                    if '?' not in item.name:
                        test_project = {
                            "path": str(project_dir),
                            "id": project_dir.name,
                            "app_path": str(item)
                        }
                        break
            if test_project:
                break
    
    if not test_project:
        print("❌ No suitable test project found with .app bundle")
        return
    
    print(f"✓ Found test project: {test_project['id']}")
    print(f"  App bundle: {os.path.basename(test_project['app_path'])}")
    
    # Get bundle ID from project.json
    project_json = Path(test_project['path']) / "project.json"
    bundle_id = "com.example.app"
    
    if project_json.exists():
        with open(project_json) as f:
            data = json.load(f)
            bundle_id = data.get("bundle_id", bundle_id)
    
    print(f"  Bundle ID: {bundle_id}")
    
    # Now simulate what build_service.py does after a successful build
    print("\n=== Simulating Build Service Flow ===")
    
    from build_service import BuildService
    from datetime import datetime
    
    build_service = BuildService()
    
    # Create an async status callback
    async def status_callback(message: str):
        print(f"  [Status] {message}")
    
    build_service.set_status_callback(status_callback)
    
    # Simulate the code from build_service.py after a successful build
    print("\n1. Checking if simulator service is available...")
    if build_service.simulator_service:
        print("✓ Simulator service is available")
        
        print("\n2. Simulating successful build result...")
        build_result = {
            "success": True,
            "app_path": test_project['app_path']
        }
        
        print(f"   build_result['success'] = {build_result['success']}")
        print(f"   build_result['app_path'] = {build_result['app_path']}")
        
        print("\n3. Executing simulator launch code (as in build_service.py:410-432)...")
        
        try:
            app_path = build_result.get("app_path")
            if app_path:
                await build_service._update_status("📱 Preparing to launch in iOS Simulator...")
                await build_service._update_status(f"Build completed successfully for {os.path.basename(app_path)}")
                
                # This is the exact call from build_service.py
                launch_success, launch_message = await build_service.simulator_service.install_and_launch_app(
                    app_path,
                    bundle_id,
                    build_service._update_status
                )
                
                if launch_success:
                    await build_service._update_status("🎉 App launched successfully!")
                    print("\n✓ SIMULATOR LAUNCH SUCCESSFUL!")
                else:
                    print(f"\n✗ Simulator launch failed: {launch_message}")
                    await build_service._update_status(f"Simulator launch issue: {launch_message}")
            else:
                print("\n✗ No app_path in build result")
        except Exception as e:
            print(f"\n✗ Exception during simulator launch: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("✗ Simulator service NOT available in build service")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    # Run in the virtual environment
    import subprocess
    venv_python = Path(__file__).parent / "venv" / "bin" / "python"
    
    if venv_python.exists() and sys.executable != str(venv_python):
        # Re-run with venv python
        print("Re-running with virtual environment...")
        subprocess.run([str(venv_python), __file__])
    else:
        # Already in venv or venv doesn't exist
        asyncio.run(test_build_to_simulator_flow())