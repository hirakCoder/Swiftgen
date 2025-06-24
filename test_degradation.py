#!/usr/bin/env python3
"""
Script to reproduce the modification degradation issue.
Tests making multiple consecutive modifications to identify when failures start.
"""

import asyncio
import json
import time
from datetime import datetime
import httpx
import websockets
from typing import Dict, List, Optional

BASE_URL = "http://localhost:8002"
WS_URL = "ws://localhost:8002/ws"

class ModificationTester:
    def __init__(self):
        self.project_id: Optional[str] = None
        self.results: List[Dict] = []
        self.ws_connection = None
        
    async def create_test_app(self) -> str:
        """Create a fresh test app"""
        print("\n🚀 Creating fresh test app...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{BASE_URL}/api/generate",
                json={
                    "app_name": f"TestApp_{int(time.time())}",
                    "description": "A simple todo app for testing modifications",
                    "features": ["Add tasks", "Mark complete", "Delete tasks"],
                    "ui_framework": "SwiftUI"
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to create app: {response.text}")
                
            data = response.json()
            self.project_id = data["project_id"]
            print(f"✅ Created app with project_id: {self.project_id}")
            return self.project_id
    
    async def connect_websocket(self):
        """Connect to WebSocket for real-time updates"""
        try:
            self.ws_connection = await websockets.connect(f"{WS_URL}/{self.project_id}")
            print("✅ WebSocket connected")
        except Exception as e:
            print(f"❌ WebSocket connection failed: {e}")
    
    async def make_modification(self, modification: str, mod_number: int) -> Dict:
        """Make a single modification and track results"""
        print(f"\n📝 Modification #{mod_number}: {modification}")
        start_time = time.time()
        
        result = {
            "number": mod_number,
            "modification": modification,
            "start_time": datetime.now().isoformat(),
            "success": False,
            "error": None,
            "duration": 0,
            "ws_messages": []
        }
        
        # Listen for WebSocket messages
        ws_task = None
        if self.ws_connection:
            ws_task = asyncio.create_task(self.listen_websocket(result))
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{BASE_URL}/api/modify",
                    json={
                        "project_id": self.project_id,
                        "modification": modification
                    }
                )
                
                result["status_code"] = response.status_code
                result["response_body"] = response.text[:500]  # First 500 chars
                
                if response.status_code == 200:
                    data = response.json()
                    result["success"] = data.get("success", False)
                    result["modified_files"] = len(data.get("modified_files", []))
                    print(f"✅ Modification successful: {result['modified_files']} files modified")
                else:
                    result["error"] = f"HTTP {response.status_code}: {response.text}"
                    print(f"❌ Modification failed: {result['error']}")
                    
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ Exception during modification: {e}")
        
        result["duration"] = time.time() - start_time
        
        # Cancel WebSocket listener
        if ws_task:
            ws_task.cancel()
            
        self.results.append(result)
        return result
    
    async def listen_websocket(self, result: Dict):
        """Listen for WebSocket messages during modification"""
        try:
            while True:
                message = await asyncio.wait_for(self.ws_connection.recv(), timeout=1.0)
                msg_data = json.loads(message)
                result["ws_messages"].append({
                    "type": msg_data.get("type"),
                    "time": datetime.now().isoformat()
                })
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            result["ws_error"] = str(e)
    
    async def run_test_sequence(self):
        """Run a sequence of modifications to reproduce degradation"""
        modifications = [
            "Change the app title to 'My Awesome Tasks'",
            "Add a dark mode toggle in settings",
            "Change the add button color to blue",
            "Add a counter showing total tasks",
            "Make completed tasks show with strikethrough",
            "Add a clear all button",
            "Change font to SF Pro Display",
            "Add task priority levels",
            "Enable task editing",
            "Add task categories"
        ]
        
        await self.create_test_app()
        await self.connect_websocket()
        
        print(f"\n🧪 Testing {len(modifications)} consecutive modifications...")
        
        for i, mod in enumerate(modifications, 1):
            result = await self.make_modification(mod, i)
            
            # Short delay between modifications
            await asyncio.sleep(2)
            
            # Stop if we hit failures
            if not result["success"] and i > 3:
                print(f"\n⚠️  Degradation detected at modification #{i}")
                break
        
        # Analyze results
        self.analyze_results()
    
    def analyze_results(self):
        """Analyze test results to identify patterns"""
        print("\n📊 Test Results Analysis:")
        print("=" * 60)
        
        success_count = sum(1 for r in self.results if r["success"])
        print(f"Total modifications: {len(self.results)}")
        print(f"Successful: {success_count}")
        print(f"Failed: {len(self.results) - success_count}")
        
        # Find where failures start
        first_failure = None
        for i, result in enumerate(self.results):
            if not result["success"]:
                first_failure = i + 1
                break
        
        if first_failure:
            print(f"\n🔴 First failure at modification #{first_failure}")
            if first_failure > 2:
                print("✅ Confirmed: Degradation occurs after initial success")
        
        # Show detailed results
        print("\nDetailed Results:")
        for r in self.results:
            status = "✅" if r["success"] else "❌"
            print(f"{status} Mod #{r['number']}: {r['modification'][:50]}...")
            if r["error"]:
                print(f"   Error: {r['error'][:100]}...")
            print(f"   Duration: {r['duration']:.2f}s")
            print(f"   WS Messages: {len(r['ws_messages'])}")
        
        # Save results
        with open("degradation_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Full results saved to degradation_test_results.json")

async def main():
    tester = ModificationTester()
    try:
        await tester.run_test_sequence()
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
    finally:
        if tester.ws_connection:
            await tester.ws_connection.close()

if __name__ == "__main__":
    print("🔬 SwiftGen Modification Degradation Test")
    print("This will create a test app and make multiple modifications")
    print("to reproduce the degradation issue.")
    
    asyncio.run(main())