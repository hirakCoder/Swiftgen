#!/usr/bin/env python3
"""Debug script to test simulator launch after build"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simulator_service import SimulatorService
from build_service import BuildService

async def test_simulator_launch():
    """Test simulator launch functionality"""
    
    print("=== Testing Simulator Service ===")
    
    # Initialize services
    simulator_service = SimulatorService()
    build_service = BuildService()
    
    # Test 1: Check if simulator service is initialized
    print("\n1. Checking simulator service initialization...")
    if build_service.simulator_service:
        print("✓ Simulator service initialized in build service")
    else:
        print("✗ Simulator service NOT initialized in build service")
        return
    
    # Test 2: List available devices
    print("\n2. Listing available simulator devices...")
    try:
        devices = await simulator_service.list_available_devices()
        print(f"✓ Found {len(devices)} simulator devices")
        for device in devices[:3]:
            print(f"  - {device.name} ({device.state.value})")
    except Exception as e:
        print(f"✗ Error listing devices: {e}")
        return
    
    # Test 3: Check for .app bundles in recent projects
    print("\n3. Checking for .app bundles in recent projects...")
    workspaces_dir = Path(__file__).parent.parent / "workspaces"
    app_bundles_found = []
    
    if workspaces_dir.exists():
        for project_dir in sorted(workspaces_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
            if project_dir.is_dir():
                app_path = build_service._find_app_bundle(str(project_dir))
                if app_path:
                    app_bundles_found.append((project_dir.name, app_path))
                    print(f"✓ Found app bundle in {project_dir.name}: {os.path.basename(app_path)}")
                else:
                    # Check if build directory exists
                    build_dir = project_dir / "build" / "Build" / "Products"
                    if build_dir.exists():
                        print(f"✗ Build dir exists but no .app found in {project_dir.name}")
                        # List what's in the build directory
                        for item in build_dir.rglob("*"):
                            if item.is_dir() and item.name.endswith('.app'):
                                print(f"  Found: {item}")
                    else:
                        print(f"✗ No build directory in {project_dir.name}")
    
    # Test 4: Try to launch an app if found
    if app_bundles_found:
        print(f"\n4. Testing app launch with first found bundle...")
        project_name, app_path = app_bundles_found[0]
        
        # Get bundle ID from project.json
        project_dir = workspaces_dir / project_name
        project_json = project_dir / "project.json"
        bundle_id = "com.example.app"  # default
        
        if project_json.exists():
            import json
            with open(project_json) as f:
                data = json.load(f)
                bundle_id = data.get("bundle_id", bundle_id)
        
        print(f"  App path: {app_path}")
        print(f"  Bundle ID: {bundle_id}")
        
        # Test launch
        try:
            launch_success, launch_message = await simulator_service.install_and_launch_app(
                app_path,
                bundle_id,
                lambda msg: print(f"  Status: {msg}")
            )
            
            if launch_success:
                print(f"✓ App launched successfully: {launch_message}")
            else:
                print(f"✗ App launch failed: {launch_message}")
        except Exception as e:
            print(f"✗ Error during launch: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n4. No app bundles found to test launch")
    
    # Test 5: Check build_service integration
    print("\n5. Testing build_service simulator integration...")
    
    # Create a mock build result
    mock_build_result = {
        "success": True,
        "app_path": app_bundles_found[0][1] if app_bundles_found else None
    }
    
    if mock_build_result["app_path"]:
        print(f"  Simulating successful build with app_path: {mock_build_result['app_path']}")
        print(f"  build_service.simulator_service is: {build_service.simulator_service}")
        print(f"  app_path in result: {mock_build_result.get('app_path')}")
        
        # Check the condition that triggers simulator launch
        if build_service.simulator_service and mock_build_result.get("app_path"):
            print("✓ Conditions met for simulator launch")
        else:
            print("✗ Conditions NOT met for simulator launch")
    
    print("\n=== Debug Complete ===")

if __name__ == "__main__":
    asyncio.run(test_simulator_launch())