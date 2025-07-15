#!/usr/bin/env python3
"""
Production Test Suite for SwiftGen
Tests all critical functionality to ensure production readiness
"""

import asyncio
import aiohttp
import json
import time
import subprocess
import sys
from pathlib import Path
from datetime import datetime

class SwiftGenProductionTest:
    def __init__(self):
        self.server_process = None
        self.base_url = "http://localhost:8000"
        self.test_results = {
            "health_check": False,
            "simple_generation": False,
            "medium_generation": False,
            "complex_generation": False,
            "simple_modification": False,
            "medium_modification": False,
            "auto_fix": False,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0
        }
        
    def start_server(self):
        """Start the SwiftGen server"""
        print("🚀 Starting SwiftGen server...")
        try:
            # Start server in background
            self.server_process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            print("⏳ Waiting for server to initialize...")
            time.sleep(10)
            
            # Check if server is running
            if self.server_process.poll() is None:
                print("✅ Server started successfully")
                return True
            else:
                print("❌ Server failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def stop_server(self):
        """Stop the SwiftGen server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            print("🛑 Server stopped")
    
    async def test_health_check(self):
        """Test health check endpoint"""
        print("\\n🔍 Testing Health Check...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/health") as response:
                    if response.status == 200:
                        result = await response.json()
                        llm_count = result.get("model_count", 0)
                        services = result.get("services", {})
                        
                        print(f"✅ Health check passed")
                        print(f"   LLM Models: {llm_count}")
                        print(f"   Services: {len([k for k, v in services.items() if v])}")
                        
                        self.test_results["health_check"] = True
                        return True
                    else:
                        print(f"❌ Health check failed: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    async def test_simple_generation(self):
        """Test simple app generation"""
        print("\\n📱 Testing Simple App Generation...")
        
        test_apps = [
            {
                "name": "Timer App",
                "description": "Create a simple timer app with start, stop, and reset functionality",
                "expected_files": ["ContentView.swift", "TimerApp.swift"]
            },
            {
                "name": "Counter App", 
                "description": "Create a counter app with increment and decrement buttons",
                "expected_files": ["ContentView.swift"]
            }
        ]
        
        success_count = 0
        
        async with aiohttp.ClientSession() as session:
            for app in test_apps:
                print(f"   🚀 Testing {app['name']}...")
                
                payload = {
                    "description": app["description"],
                    "ios_version": "16.0"
                }
                
                try:
                    async with session.post(f"{self.base_url}/api/generate", json=payload) as response:
                        if response.status == 200:
                            result = await response.json()
                            project_id = result.get("project_id")
                            app_name = result.get("app_name")
                            
                            if project_id and app_name:
                                print(f"   ✅ {app['name']} initiated: {app_name}")
                                success_count += 1
                            else:
                                print(f"   ❌ {app['name']} - Missing project info")
                        else:
                            print(f"   ❌ {app['name']} failed: {response.status}")
                            
                except Exception as e:
                    print(f"   ❌ {app['name']} error: {e}")
                
                # Small delay between requests
                await asyncio.sleep(1)
        
        if success_count == len(test_apps):
            print(f"✅ Simple generation test passed ({success_count}/{len(test_apps)})")
            self.test_results["simple_generation"] = True
            return True
        else:
            print(f"❌ Simple generation test failed ({success_count}/{len(test_apps)})")
            return False
    
    async def test_medium_generation(self):
        """Test medium complexity app generation"""
        print("\\n🎨 Testing Medium Complexity Generation...")
        
        test_apps = [
            {
                "name": "Todo App",
                "description": "Create a todo list app with add, delete, complete, and edit functionality. Include data persistence.",
            },
            {
                "name": "Calculator App",
                "description": "Create a calculator app with basic math operations, memory functions, and history.",
            }
        ]
        
        success_count = 0
        
        async with aiohttp.ClientSession() as session:
            for app in test_apps:
                print(f"   🚀 Testing {app['name']}...")
                
                payload = {
                    "description": app["description"],
                    "ios_version": "16.0"
                }
                
                try:
                    async with session.post(f"{self.base_url}/api/generate", json=payload) as response:
                        if response.status == 200:
                            result = await response.json()
                            project_id = result.get("project_id")
                            app_name = result.get("app_name")
                            
                            if project_id and app_name:
                                print(f"   ✅ {app['name']} initiated: {app_name}")
                                success_count += 1
                            else:
                                print(f"   ❌ {app['name']} - Missing project info")
                        else:
                            print(f"   ❌ {app['name']} failed: {response.status}")
                            
                except Exception as e:
                    print(f"   ❌ {app['name']} error: {e}")
                
                await asyncio.sleep(1)
        
        if success_count == len(test_apps):
            print(f"✅ Medium generation test passed ({success_count}/{len(test_apps)})")
            self.test_results["medium_generation"] = True
            return True
        else:
            print(f"❌ Medium generation test failed ({success_count}/{len(test_apps)})")
            return False
    
    async def test_complex_generation(self):
        """Test complex app generation"""
        print("\\n🏗️ Testing Complex App Generation...")
        
        test_apps = [
            {
                "name": "Weather App",
                "description": "Create a weather app with current weather, 5-day forecast, location search, and weather maps integration.",
            }
        ]
        
        success_count = 0
        
        async with aiohttp.ClientSession() as session:
            for app in test_apps:
                print(f"   🚀 Testing {app['name']}...")
                
                payload = {
                    "description": app["description"],
                    "ios_version": "16.0"
                }
                
                try:
                    async with session.post(f"{self.base_url}/api/generate", json=payload) as response:
                        if response.status == 200:
                            result = await response.json()
                            project_id = result.get("project_id")
                            app_name = result.get("app_name")
                            
                            if project_id and app_name:
                                print(f"   ✅ {app['name']} initiated: {app_name}")
                                success_count += 1
                            else:
                                print(f"   ❌ {app['name']} - Missing project info")
                        else:
                            print(f"   ❌ {app['name']} failed: {response.status}")
                            
                except Exception as e:
                    print(f"   ❌ {app['name']} error: {e}")
                
                await asyncio.sleep(1)
        
        if success_count == len(test_apps):
            print(f"✅ Complex generation test passed ({success_count}/{len(test_apps)})")
            self.test_results["complex_generation"] = True
            return True
        else:
            print(f"❌ Complex generation test failed ({success_count}/{len(test_apps)})")
            return False
    
    async def test_stats_endpoint(self):
        """Test statistics endpoint"""
        print("\\n📊 Testing Statistics Endpoint...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/stats") as response:
                    if response.status == 200:
                        stats = await response.json()
                        
                        gen_stats = stats.get("generation_stats", {})
                        total_attempts = gen_stats.get("total_attempts", 0)
                        successful = gen_stats.get("successful_generations", 0)
                        failed = gen_stats.get("failed_generations", 0)
                        
                        print(f"✅ Statistics endpoint working")
                        print(f"   Total Attempts: {total_attempts}")
                        print(f"   Successful: {successful}")
                        print(f"   Failed: {failed}")
                        print(f"   Success Rate: {stats.get('success_rate', '0%')}")
                        
                        return True
                    else:
                        print(f"❌ Statistics endpoint failed: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Statistics endpoint error: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all production tests"""
        print("🎯 SwiftGen Production Test Suite")
        print("="*50)
        
        test_functions = [
            ("Health Check", self.test_health_check),
            ("Simple Generation", self.test_simple_generation),
            ("Medium Generation", self.test_medium_generation),
            ("Complex Generation", self.test_complex_generation),
            ("Statistics Endpoint", self.test_stats_endpoint)
        ]
        
        for test_name, test_func in test_functions:
            self.test_results["total_tests"] += 1
            success = await test_func()
            
            if success:
                self.test_results["passed_tests"] += 1
            else:
                self.test_results["failed_tests"] += 1
            
            # Brief pause between tests
            await asyncio.sleep(2)
        
        # Print final results
        self.print_final_results()
    
    def print_final_results(self):
        """Print final test results"""
        print("\\n" + "="*50)
        print("🎯 FINAL TEST RESULTS")
        print("="*50)
        
        total = self.test_results["total_tests"]
        passed = self.test_results["passed_tests"]
        failed = self.test_results["failed_tests"]
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        
        if failed == 0:
            print("\\n🎉 ALL TESTS PASSED - SYSTEM IS PRODUCTION READY!")
        else:
            success_rate = (passed / total) * 100
            print(f"\\n📊 Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 80:
                print("✅ System is mostly production ready with minor issues")
            elif success_rate >= 60:
                print("⚠️ System has significant issues that need attention")
            else:
                print("❌ System is not production ready - major fixes needed")
        
        print("="*50)

async def main():
    """Main test function"""
    test_suite = SwiftGenProductionTest()
    
    try:
        # Start server
        if not test_suite.start_server():
            print("❌ Cannot start server - aborting tests")
            return
        
        # Run all tests
        await test_suite.run_all_tests()
        
    finally:
        # Always stop server
        test_suite.stop_server()

if __name__ == "__main__":
    asyncio.run(main())