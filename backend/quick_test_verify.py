#!/usr/bin/env python3
"""Quick verification test for SwiftGen"""

import asyncio
import aiohttp
import json
import time

BASE_URL = "http://localhost:8000"

async def test_simple_app():
    """Test a simple app generation"""
    print("🧪 Testing Simple Timer App Generation...")
    
    async with aiohttp.ClientSession() as session:
        # Test health endpoint
        async with session.get(f"{BASE_URL}/health") as response:
            if response.status != 200:
                print("❌ Health check failed")
                return False
            print("✅ Health check passed")
        
        # Generate app
        start = time.time()
        async with session.post(
            f"{BASE_URL}/api/generate",
            json={
                "description": "Create a simple counter app with increment and decrement buttons",
                "app_name": "QuickTestApp"
            }
        ) as response:
            if response.status != 200:
                error = await response.text()
                print(f"❌ Generation failed: {error}")
                return False
            
            result = await response.json()
            project_id = result.get("project_id")
            print(f"✅ Generation started: {project_id}")
            
            # Wait for build
            print("⏳ Waiting for build to complete...")
            await asyncio.sleep(30)  # Give it 30 seconds
            
            # Check status
            async with session.get(f"{BASE_URL}/api/status/{project_id}") as response:
                if response.status == 200:
                    status = await response.json()
                    duration = time.time() - start
                    
                    print(f"\n📊 Results after {duration:.1f}s:")
                    print(f"  Project ID: {project_id}")
                    print(f"  Build Status: {status.get('build_status', 'unknown')}")
                    print(f"  Build Success: {status.get('build_success', False)}")
                    print(f"  Files Created: {len(status.get('files', []))}")
                    
                    if status.get('build_success'):
                        print("\n✅ BUILD SUCCESSFUL! System is working!")
                        return True
                    else:
                        print("\n❌ Build failed")
                        return False
                else:
                    print(f"❌ Could not get status: {response.status}")
                    return False

async def main():
    """Run quick test"""
    print("=" * 50)
    print("🚀 SwiftGen Quick Verification Test")
    print("=" * 50)
    
    success = await test_simple_app()
    
    if success:
        print("\n✅ SYSTEM VERIFIED - Working correctly!")
    else:
        print("\n❌ SYSTEM VERIFICATION FAILED")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())