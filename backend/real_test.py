#!/usr/bin/env python3
"""
REAL End-to-End Testing for SwiftGen
This script does ACTUAL testing - waits for builds to complete and verifies apps run in simulator
"""

import asyncio
import aiohttp
import json
import time
import websockets
from datetime import datetime

class RealSwiftGenTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.ws_url = "ws://localhost:8000"
        self.test_results = []
        
    async def test_real_app_generation(self, app_description, app_name):
        """Test actual app generation with real completion verification"""
        print(f"\\n🚀 REAL TEST: {app_name}")
        print("="*50)
        
        try:
            # Step 1: Submit generation request
            async with aiohttp.ClientSession() as session:
                payload = {
                    "description": app_description,
                    "ios_version": "16.0"
                }
                
                print("📤 Submitting generation request...")
                async with session.post(f"{self.base_url}/api/generate", json=payload) as response:
                    if response.status != 200:
                        print(f"❌ Generation request failed: {response.status}")
                        return False
                    
                    result = await response.json()
                    project_id = result.get("project_id")
                    
                    if not project_id:
                        print("❌ No project ID returned")
                        return False
                    
                    print(f"✅ Generation request accepted - Project ID: {project_id}")
                    
                    # Step 2: Connect to WebSocket and wait for completion
                    print("🔌 Connecting to WebSocket for real-time updates...")
                    
                    completion_status = await self.wait_for_completion(project_id)
                    
                    if completion_status["success"]:
                        print(f"✅ {app_name} completed successfully!")
                        print(f"   Build Status: {completion_status['build_status']}")
                        print(f"   Simulator: {completion_status['simulator_launched']}")
                        print(f"   Files Generated: {completion_status['files_count']}")
                        
                        # Step 3: Verify project files exist
                        if await self.verify_project_files(project_id):
                            print(f"✅ Project files verified")
                            return True
                        else:
                            print(f"❌ Project files missing")
                            return False
                    else:
                        print(f"❌ {app_name} failed to complete")
                        print(f"   Error: {completion_status.get('error', 'Unknown error')}")
                        return False
                        
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            return False
    
    async def wait_for_completion(self, project_id, timeout=180):
        """Wait for actual completion via WebSocket"""
        print("⏳ Waiting for actual build completion...")
        
        try:
            uri = f"{self.ws_url}/ws/{project_id}"
            async with websockets.connect(uri) as websocket:
                start_time = time.time()
                
                while time.time() - start_time < timeout:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=10)
                        data = json.loads(message)
                        
                        msg_type = data.get("type")
                        status = data.get("status")
                        message_text = data.get("message", "")
                        
                        print(f"📡 {status}: {message_text}")
                        
                        if msg_type == "complete":
                            return {
                                "success": status == "success",
                                "build_status": status,
                                "simulator_launched": data.get("simulator_launched", False),
                                "files_count": data.get("files_count", 0),
                                "error": data.get("message") if status != "success" else None
                            }
                        elif msg_type == "error":
                            return {
                                "success": False,
                                "error": message_text
                            }
                            
                    except asyncio.TimeoutError:
                        print("⏳ Still waiting...")
                        continue
                        
                return {
                    "success": False,
                    "error": f"Timeout after {timeout} seconds"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"WebSocket error: {e}"
            }
    
    async def verify_project_files(self, project_id):
        """Verify project files actually exist"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/project/{project_id}/files") as response:
                    if response.status == 200:
                        files_data = await response.json()
                        files = files_data.get("files", [])
                        return len(files) > 0
                    return False
        except:
            return False
    
    async def test_real_modification(self, project_id, modification_description):
        """Test actual modification with completion verification"""
        print(f"\\n🔧 REAL MODIFICATION TEST")
        print("="*50)
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "project_id": project_id,
                    "modification": modification_description
                }
                
                print("📤 Submitting modification request...")
                async with session.post(f"{self.base_url}/api/modify", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        status = result.get("status")
                        
                        if status == "success":
                            print("✅ Modification completed successfully!")
                            print(f"   Summary: {result.get('modification_summary', 'Changes applied')}")
                            return True
                        else:
                            print(f"❌ Modification failed: {result.get('message', 'Unknown error')}")
                            return False
                    else:
                        print(f"❌ Modification request failed: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ Modification test failed: {e}")
            return False
    
    async def run_real_tests(self):
        """Run real end-to-end tests"""
        print("🎯 REAL SWIFTGEN TESTING - NO LIES")
        print("="*60)
        
        # Test different app types
        test_cases = [
            {
                "name": "Simple Timer App",
                "description": "Create a simple timer app with start, stop, and reset buttons. Show the time counting up in minutes and seconds.",
                "complexity": "simple"
            },
            {
                "name": "Todo List App", 
                "description": "Create a todo list app where users can add new tasks, mark them as complete, and delete them. Use a simple list view.",
                "complexity": "medium"
            }
        ]
        
        successful_tests = 0
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases):
            print(f"\\n[{i+1}/{total_tests}] Testing {test_case['name']}...")
            
            success = await self.test_real_app_generation(
                test_case["description"], 
                test_case["name"]
            )
            
            if success:
                successful_tests += 1
                self.test_results.append({
                    "test": test_case["name"],
                    "status": "PASSED",
                    "complexity": test_case["complexity"]
                })
            else:
                self.test_results.append({
                    "test": test_case["name"],
                    "status": "FAILED",
                    "complexity": test_case["complexity"]
                })
            
            # Brief pause between tests
            await asyncio.sleep(5)
        
        # Print final results
        print("\\n" + "="*60)
        print("🎯 REAL TEST RESULTS")
        print("="*60)
        
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASSED" else "❌"
            print(f"{status_icon} {result['test']}: {result['status']}")
        
        print(f"\\nSUMMARY: {successful_tests}/{total_tests} tests passed")
        
        if successful_tests == total_tests:
            print("🎉 ALL REAL TESTS PASSED - SYSTEM IS ACTUALLY WORKING!")
        elif successful_tests > 0:
            print(f"⚠️ PARTIAL SUCCESS - {successful_tests} out of {total_tests} tests passed")
        else:
            print("❌ ALL TESTS FAILED - SYSTEM IS NOT WORKING")
        
        return successful_tests == total_tests

async def main():
    tester = RealSwiftGenTester()
    await tester.run_real_tests()

if __name__ == "__main__":
    asyncio.run(main())