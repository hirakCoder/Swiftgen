#!/usr/bin/env python3
"""Test script to verify the error recovery fixes"""

import asyncio
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from build_service import BuildService

async def test_build():
    """Test building the project with recovery enabled"""
    
    build_service = BuildService()
    
    # Set up a status callback
    def status_callback(status):
        print(f"[STATUS] {status}")
    
    build_service.status_callback = status_callback
    
    # Build the project
    project_path = "/Users/hirakbanerjee/Desktop/SwiftGen/swiftgen-mvp/workspaces/proj_c9borlgu"
    
    print(f"Testing build with error recovery for: {project_path}")
    print("=" * 60)
    
    result = await build_service.build_project(project_path)
    
    print("\n" + "=" * 60)
    print("Build Result:")
    print(f"Success: {result.success}")
    print(f"Build Time: {result.build_time:.2f}s")
    print(f"App Path: {result.app_path}")
    
    if result.errors:
        print(f"\nErrors ({len(result.errors)}):")
        for error in result.errors[:5]:  # Show first 5 errors
            print(f"  - {error}")
    
    if result.warnings:
        print(f"\nWarnings ({len(result.warnings)}):")
        for warning in result.warnings:
            print(f"  - {warning}")
    
    return result.success

if __name__ == "__main__":
    success = asyncio.run(test_build())
    sys.exit(0 if success else 1)