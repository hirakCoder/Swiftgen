#!/usr/bin/env python3
"""
Full System Test for SwiftGen
Tests all components to ensure production readiness
"""

import asyncio
import aiohttp
import json
import time
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"

class SwiftGenTester:
    def __init__(self):
        self.results = {
            "simple_apps": {"passed": 0, "failed": 0, "details": []},
            "medium_apps": {"passed": 0, "failed": 0, "details": []},
            "complex_apps": {"passed": 0, "failed": 0, "details": []},
            "modifications": {"passed": 0, "failed": 0, "details": []},
            "total_time": 0
        }
        self.start_time = time.time()
    
    async def test_app_generation(self, description, app_name, complexity):
        """Test app generation"""
        print(f"\n🧪 Testing {complexity} app: {app_name}")
        
        start = time.time()
        try:
            async with aiohttp.ClientSession() as session:
                # Generate app
                async with session.post(
                    f"{BASE_URL}/api/generate",
                    json={
                        "description": description,
                        "app_name": app_name
                    }
                ) as response:
                    if response.status != 200:
                        error = await response.text()
                        raise Exception(f"Generation failed: {error}")
                    
                    result = await response.json()
                    project_id = result.get("project_id")
                    
                    if not project_id:
                        raise Exception("No project_id returned")
                    
                    print(f"  ✓ Generation started: {project_id}")
                    
                    # Wait for build to complete
                    build_success = await self.wait_for_build(session, project_id)
                    
                    duration = time.time() - start
                    
                    if build_success:
                        self.results[f"{complexity}_apps"]["passed"] += 1
                        self.results[f"{complexity}_apps"]["details"].append({
                            "app_name": app_name,
                            "status": "✅ SUCCESS",
                            "duration": f"{duration:.1f}s"
                        })
                        print(f"  ✅ Build successful in {duration:.1f}s")
                        return project_id
                    else:
                        raise Exception("Build failed")
                        
        except Exception as e:
            duration = time.time() - start
            self.results[f"{complexity}_apps"]["failed"] += 1
            self.results[f"{complexity}_apps"]["details"].append({
                "app_name": app_name,
                "status": f"❌ FAILED: {str(e)}",
                "duration": f"{duration:.1f}s"
            })
            print(f"  ❌ Failed: {str(e)}")
            return None
    
    async def wait_for_build(self, session, project_id, timeout=120):
        """Wait for build to complete"""
        start = time.time()
        
        while time.time() - start < timeout:
            try:
                async with session.get(f"{BASE_URL}/api/status/{project_id}") as response:
                    if response.status == 200:
                        status = await response.json()
                        
                        if status.get("build_status") == "completed":
                            return status.get("build_success", False)
                        elif status.get("build_status") == "failed":
                            return False
                        
            except:
                pass
            
            await asyncio.sleep(2)
        
        return False
    
    async def test_modification(self, project_id, modification, app_name):
        """Test app modification"""
        print(f"\n🔧 Testing modification: {modification[:50]}...")
        
        start = time.time()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{BASE_URL}/api/modify",
                    json={
                        "project_id": project_id,
                        "modification": modification
                    }
                ) as response:
                    if response.status != 200:
                        error = await response.text()
                        raise Exception(f"Modification failed: {error}")
                    
                    # Wait for modification to complete
                    await asyncio.sleep(15)  # Give it time to process
                    
                    duration = time.time() - start
                    self.results["modifications"]["passed"] += 1
                    self.results["modifications"]["details"].append({
                        "app_name": app_name,
                        "modification": modification[:50] + "...",
                        "status": "✅ SUCCESS",
                        "duration": f"{duration:.1f}s"
                    })
                    print(f"  ✅ Modification successful in {duration:.1f}s")
                    
        except Exception as e:
            duration = time.time() - start
            self.results["modifications"]["failed"] += 1
            self.results["modifications"]["details"].append({
                "app_name": app_name,
                "modification": modification[:50] + "...",
                "status": f"❌ FAILED: {str(e)}",
                "duration": f"{duration:.1f}s"
            })
            print(f"  ❌ Failed: {str(e)}")
    
    async def run_all_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("🚀 SwiftGen Full System Test")
        print("=" * 60)
        
        # Test simple apps
        print("\n📱 Testing Simple Apps...")
        simple_apps = [
            ("Create a simple timer app with start, stop, and reset buttons", "TimerApp"),
            ("Create a counter app with increment and decrement buttons", "CounterApp"),
            ("Create a hello world app with a greeting message", "HelloApp")
        ]
        
        for desc, name in simple_apps:
            await self.test_app_generation(desc, name, "simple")
        
        # Test medium complexity apps
        print("\n📱 Testing Medium Complexity Apps...")
        medium_apps = [
            ("Create a todo list app with add, delete, and mark complete features", "TodoApp"),
            ("Create a calculator app with basic arithmetic operations", "CalculatorApp"),
            ("Create a notes app with create, edit, and delete functionality", "NotesApp")
        ]
        
        for desc, name in medium_apps:
            await self.test_app_generation(desc, name, "medium")
        
        # Test complex apps
        print("\n📱 Testing Complex Apps...")
        complex_apps = [
            ("Create a weather app that shows current temperature and 5-day forecast with location services", "WeatherApp"),
            ("Create a currency converter app with real-time exchange rates and calculator", "CurrencyApp"),
            ("Create a fitness tracker app with workout logging, progress charts, and goals", "FitnessApp")
        ]
        
        for desc, name in complex_apps:
            await self.test_app_generation(desc, name, "complex")
        
        # Test modifications on successful apps
        print("\n🔧 Testing Modifications...")
        
        # Try to modify the first successful simple app
        for detail in self.results["simple_apps"]["details"]:
            if "SUCCESS" in detail["status"]:
                # Generate a new simple app for modification test
                project_id = await self.test_app_generation(
                    "Create a simple counter app", 
                    "ModTestApp", 
                    "simple"
                )
                if project_id:
                    await self.test_modification(
                        project_id,
                        "Add a reset button that sets the counter back to zero",
                        "ModTestApp"
                    )
                break
        
        # Print results
        self.print_results()
    
    def print_results(self):
        """Print test results"""
        self.results["total_time"] = time.time() - self.start_time
        
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS")
        print("=" * 60)
        
        # Summary
        total_passed = sum(cat["passed"] for cat in self.results.values() if isinstance(cat, dict) and "passed" in cat)
        total_failed = sum(cat["failed"] for cat in self.results.values() if isinstance(cat, dict) and "failed" in cat)
        total_tests = total_passed + total_failed
        
        print(f"\n✅ Passed: {total_passed}/{total_tests}")
        print(f"❌ Failed: {total_failed}/{total_tests}")
        print(f"⏱️  Total Time: {self.results['total_time']:.1f}s")
        
        # Detailed results
        for category in ["simple_apps", "medium_apps", "complex_apps", "modifications"]:
            if category in self.results:
                cat_name = category.replace("_", " ").title()
                print(f"\n### {cat_name}")
                print(f"Passed: {self.results[category]['passed']}")
                print(f"Failed: {self.results[category]['failed']}")
                
                for detail in self.results[category]["details"]:
                    print(f"  - {detail['app_name']}: {detail['status']} ({detail['duration']})")
        
        # Save results
        with open("test_results_full.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Results saved to test_results_full.json")
        
        # Return success/failure
        return total_failed == 0

async def main():
    """Main test runner"""
    tester = SwiftGenTester()
    
    # Check if server is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status != 200:
                    print("❌ Server is not running! Start it with:")
                    print("   cd backend && source venv/bin/activate && uvicorn main:app --reload")
                    sys.exit(1)
    except:
        print("❌ Cannot connect to server at http://localhost:8000")
        print("   Make sure the server is running!")
        sys.exit(1)
    
    # Run tests
    success = await tester.run_all_tests()
    
    if success:
        print("\n✅ ALL TESTS PASSED! System is production ready!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please fix the issues.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())