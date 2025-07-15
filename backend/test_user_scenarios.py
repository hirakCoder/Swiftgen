#!/usr/bin/env python3
"""Test the system from an end user's perspective"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

class UserTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.current_project_id = None
        self.test_results = []
        
    async def create_app(self, name, description):
        """Create a new app"""
        print(f"\n🚀 Creating app: {name}")
        print(f"   Description: {description}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/api/generate", 
                                  json={"app_name": name, "description": description}) as resp:
                result = await resp.json()
                self.current_project_id = result.get('project_id')
                print(f"   Project ID: {self.current_project_id}")
                return result
    
    async def wait_for_build(self, timeout=60):
        """Wait for app to build"""
        print("   ⏳ Waiting for build...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/projects/{self.current_project_id}/status") as resp:
                    if resp.status == 200:
                        status = await resp.json()
                        if status.get('build_status') == 'success':
                            print("   ✅ Build successful!")
                            return True
                        elif status.get('build_status') == 'failed':
                            print("   ❌ Build failed!")
                            return False
            await asyncio.sleep(2)
        
        print("   ⏱️  Build timeout!")
        return False
    
    async def modify_app(self, modification):
        """Modify the current app"""
        print(f"\n✏️  Modifying app: {modification}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/api/modify", 
                                  json={"project_id": self.current_project_id, 
                                        "modification": modification}) as resp:
                result = await resp.json()
                return result
    
    async def check_modification_result(self, timeout=60):
        """Check modification result via WebSocket monitoring"""
        print("   🔍 Checking modification result...")
        
        # For now, just wait and check build status
        build_success = await self.wait_for_build(timeout)
        
        # Try to get project files to see what changed
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/projects/{self.current_project_id}/files") as resp:
                if resp.status == 200:
                    files = await resp.json()
                    print(f"   📁 Total files: {len(files.get('files', []))}")
        
        return build_success
    
    async def run_test_scenario(self, scenario_name, app_name, app_description, modifications):
        """Run a complete test scenario"""
        print(f"\n{'='*60}")
        print(f"🧪 TEST SCENARIO: {scenario_name}")
        print(f"{'='*60}")
        
        scenario_result = {
            "name": scenario_name,
            "app_name": app_name,
            "creation_success": False,
            "modifications": []
        }
        
        # Create the app
        try:
            await self.create_app(app_name, app_description)
            build_success = await self.wait_for_build()
            scenario_result["creation_success"] = build_success
            
            if not build_success:
                print("   ⚠️  Skipping modifications due to build failure")
                self.test_results.append(scenario_result)
                return
                
        except Exception as e:
            print(f"   ❌ Creation failed: {e}")
            self.test_results.append(scenario_result)
            return
        
        # Try each modification
        for mod in modifications:
            print(f"\n   Modification {len(scenario_result['modifications']) + 1}: {mod}")
            
            mod_result = {
                "request": mod,
                "success": False,
                "feedback_clear": False,
                "build_success": False
            }
            
            try:
                # Make modification
                result = await self.modify_app(mod)
                
                # Wait for build
                build_success = await self.check_modification_result()
                mod_result["build_success"] = build_success
                
                # Check if we got clear feedback (would need WebSocket monitoring)
                mod_result["success"] = build_success
                
                scenario_result["modifications"].append(mod_result)
                
                if not build_success:
                    print("   ⚠️  Modification failed, continuing anyway...")
                    
            except Exception as e:
                print(f"   ❌ Modification error: {e}")
                scenario_result["modifications"].append(mod_result)
        
        self.test_results.append(scenario_result)
    
    async def run_all_tests(self):
        """Run all test scenarios"""
        
        # Scenario 1: Simple Counter App with Basic Modifications
        await self.run_test_scenario(
            "Simple Counter App",
            "TestCounter",
            "Create a simple counter app with increment and decrement buttons",
            [
                "Add a reset button that sets the counter to zero",
                "Add dark mode toggle in the navigation bar",
                "Make the counter text larger and add animation when it changes"
            ]
        )
        
        # Wait between scenarios
        await asyncio.sleep(5)
        
        # Scenario 2: Todo App with List Modifications
        await self.run_test_scenario(
            "Todo List App",
            "TestTodo", 
            "Create a todo list app where users can add and complete tasks",
            [
                "Add swipe to delete functionality for todo items",
                "Add a filter to show only incomplete tasks",
                "Add task priorities with color coding (high=red, medium=yellow, low=green)"
            ]
        )
        
        await asyncio.sleep(5)
        
        # Scenario 3: Weather App with API Integration
        await self.run_test_scenario(
            "Weather App",
            "TestWeather",
            "Create a weather app that shows current temperature and conditions",
            [
                "Add a search bar to look up weather for different cities",
                "Add a 5-day forecast view below current weather",
                "Add pull-to-refresh functionality"
            ]
        )
        
        await asyncio.sleep(5)
        
        # Scenario 4: Calculator App with UI Modifications  
        await self.run_test_scenario(
            "Calculator App",
            "TestCalc",
            "Create a basic calculator app with number buttons and operations",
            [
                "Add a history view that shows previous calculations",
                "Change the color scheme to use blue accent colors",
                "Add haptic feedback when buttons are pressed"
            ]
        )
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n\n{'='*60}")
        print("📊 TEST SUMMARY")
        print(f"{'='*60}")
        
        total_scenarios = len(self.test_results)
        successful_creations = sum(1 for r in self.test_results if r["creation_success"])
        
        total_mods = sum(len(r["modifications"]) for r in self.test_results)
        successful_mods = sum(1 for r in self.test_results 
                            for m in r["modifications"] if m["success"])
        
        print(f"\n🏗️  App Creation:")
        print(f"   Total: {total_scenarios}")
        print(f"   Successful: {successful_creations}")
        print(f"   Success Rate: {(successful_creations/total_scenarios*100):.1f}%")
        
        print(f"\n✏️  Modifications:")
        print(f"   Total: {total_mods}")
        print(f"   Successful: {successful_mods}")
        print(f"   Success Rate: {(successful_mods/total_mods*100 if total_mods > 0 else 0):.1f}%")
        
        print(f"\n📋 Detailed Results:")
        for scenario in self.test_results:
            print(f"\n   {scenario['name']} ({scenario['app_name']}):")
            print(f"   - Creation: {'✅' if scenario['creation_success'] else '❌'}")
            for i, mod in enumerate(scenario['modifications'], 1):
                status = '✅' if mod['success'] else '❌'
                print(f"   - Mod {i}: {status} {mod['request'][:50]}...")

async def main():
    print("🧪 SwiftGen End User Testing")
    print("Starting comprehensive user scenario testing...\n")
    
    tester = UserTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())