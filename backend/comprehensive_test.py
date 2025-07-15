#!/usr/bin/env python3
"""
Comprehensive test of SwiftGen system with different complexity levels
"""

import requests
import json
import time
import sys
import os
from pathlib import Path

# API endpoint
API_BASE = "http://localhost:8000/api"

def check_server_health():
    """Check if server is running"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_app_generation(name, description, expected_complexity="simple"):
    """Test generating a single app"""
    print(f"\n🧪 Testing: {name}")
    print(f"Description: {description}")
    print(f"Expected complexity: {expected_complexity}")
    
    try:
        # Generate app
        response = requests.post(f"{API_BASE}/generate", json={
            "description": description,
            "app_name": name
        }, timeout=120)
        
        if response.status_code != 200:
            print(f"❌ Generation failed: {response.status_code} - {response.text}")
            return False, None
        
        data = response.json()
        project_id = data.get("project_id")
        
        if not project_id:
            print(f"❌ No project ID returned")
            return False, None
        
        print(f"✅ Generation successful! Project ID: {project_id}")
        
        # Check if files were created
        project_path = Path(f"../workspaces/{project_id}")
        if not project_path.exists():
            print(f"❌ Project directory not found: {project_path}")
            return False, project_id
        
        sources_path = project_path / "Sources"
        if not sources_path.exists():
            print(f"❌ Sources directory not found")
            return False, project_id
        
        swift_files = list(sources_path.glob("**/*.swift"))
        print(f"📁 Created {len(swift_files)} Swift files:")
        for file in swift_files:
            rel_path = file.relative_to(project_path)
            size = file.stat().st_size
            print(f"   - {rel_path} ({size} bytes)")
        
        # Check for duplicates
        file_names = [f.name for f in swift_files]
        duplicates = [name for name in file_names if file_names.count(name) > 1]
        if duplicates:
            print(f"❌ Found duplicate files: {duplicates}")
            return False, project_id
        
        # Check minimum files exist
        if len(swift_files) < 2:
            print(f"❌ Too few files generated: {len(swift_files)} (expected at least 2)")
            return False, project_id
        
        # Check for required files
        required_files = ["App.swift", "ContentView.swift"]
        existing_names = [f.name for f in swift_files]
        missing = [req for req in required_files if req not in existing_names]
        if missing:
            print(f"❌ Missing required files: {missing}")
            return False, project_id
        
        print(f"✅ All checks passed for {name}")
        return True, project_id
        
    except Exception as e:
        print(f"❌ Exception during generation: {e}")
        return False, None

def test_app_modification(project_id, modification_description):
    """Test modifying an existing app"""
    print(f"\n🔧 Testing modification: {modification_description}")
    
    try:
        response = requests.post(f"{API_BASE}/modify", json={
            "project_id": project_id,
            "description": modification_description
        }, timeout=120)
        
        if response.status_code != 200:
            print(f"❌ Modification failed: {response.status_code} - {response.text}")
            return False
        
        data = response.json()
        if not data.get("success"):
            print(f"❌ Modification reported failure: {data.get('error', 'Unknown error')}")
            return False
        
        print(f"✅ Modification successful")
        
        # Check if project still exists and has files
        project_path = Path(f"../workspaces/{project_id}")
        if not project_path.exists():
            print(f"❌ Project directory missing after modification")
            return False
        
        sources_path = project_path / "Sources"
        swift_files = list(sources_path.glob("**/*.swift"))
        print(f"📁 Files after modification: {len(swift_files)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception during modification: {e}")
        return False

def run_comprehensive_tests():
    """Run comprehensive tests"""
    print("🚀 SwiftGen Comprehensive Test Suite")
    print("=" * 60)
    
    if not check_server_health():
        print("❌ Server is not running. Please start it first.")
        return False
    
    print("✅ Server is running")
    
    # Test cases for different complexity levels
    test_cases = [
        # Simple apps
        {
            "name": "Note Keeper",
            "description": "Create a simple note-taking app where users can add, edit, and delete notes",
            "complexity": "simple",
            "modifications": [
                "Add a search feature to find notes by title",
                "Add the ability to mark notes as favorites"
            ]
        },
        {
            "name": "BMI Calculator",
            "description": "Create a BMI calculator app with height and weight inputs",
            "complexity": "simple", 
            "modifications": [
                "Add BMI categories (underweight, normal, overweight, obese)",
                "Add a history of previous calculations"
            ]
        },
        
        # Medium complexity apps
        {
            "name": "Expense Tracker",
            "description": "Create an expense tracking app with categories, amounts, and date tracking. Include charts to visualize spending patterns.",
            "complexity": "medium",
            "modifications": [
                "Add monthly budget limits with notifications",
                "Add export functionality to CSV"
            ]
        },
        {
            "name": "Recipe Manager",
            "description": "Create a recipe management app with ingredients, instructions, cooking time, and difficulty ratings. Include search and filtering.",
            "complexity": "medium",
            "modifications": [
                "Add shopping list generation from recipes",
                "Add recipe sharing functionality"
            ]
        },
        
        # Complex apps
        {
            "name": "Fitness Tracker Pro",
            "description": "Create a comprehensive fitness tracking app with workout logging, progress tracking, exercise library, meal planning, and social features. Include data visualization and goal setting.",
            "complexity": "complex",
            "modifications": [
                "Add integration with health data",
                "Add workout plan recommendations based on user goals"
            ]
        },
        {
            "name": "Task Management Suite",
            "description": "Create a professional task management app with projects, team collaboration, file attachments, time tracking, reporting, and notifications. Include offline sync and multi-device support.",
            "complexity": "complex",
            "modifications": [
                "Add Kanban board view for project management",
                "Add time tracking with detailed reports"
            ]
        }
    ]
    
    results = {
        "total_tests": 0,
        "passed_generations": 0,
        "passed_modifications": 0,
        "failed_tests": [],
        "by_complexity": {"simple": 0, "medium": 0, "complex": 0}
    }
    
    for test_case in test_cases:
        results["total_tests"] += 1
        
        # Test app generation
        success, project_id = test_app_generation(
            test_case["name"],
            test_case["description"],
            test_case["complexity"]
        )
        
        if success:
            results["passed_generations"] += 1
            results["by_complexity"][test_case["complexity"]] += 1
            
            # Test modifications if generation succeeded
            for modification in test_case["modifications"]:
                results["total_tests"] += 1
                if test_app_modification(project_id, modification):
                    results["passed_modifications"] += 1
                else:
                    results["failed_tests"].append(f"{test_case['name']} - {modification}")
        else:
            results["failed_tests"].append(f"{test_case['name']} - Generation failed")
        
        # Small delay between tests
        time.sleep(3)
    
    # Print comprehensive results
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    
    total_attempted = results["total_tests"]
    total_passed = results["passed_generations"] + results["passed_modifications"]
    success_rate = (total_passed / total_attempted * 100) if total_attempted > 0 else 0
    
    print(f"Overall Results:")
    print(f"  🎯 Total Tests: {total_attempted}")
    print(f"  ✅ Passed: {total_passed}")
    print(f"  ❌ Failed: {len(results['failed_tests'])}")
    print(f"  📈 Success Rate: {success_rate:.1f}%")
    
    print(f"\nBreakdown:")
    print(f"  📱 App Generations: {results['passed_generations']}/{len(test_cases)}")
    print(f"  🔧 Modifications: {results['passed_modifications']}/{len(test_cases) * 2}")
    
    print(f"\nBy Complexity:")
    for complexity, count in results["by_complexity"].items():
        expected = len([t for t in test_cases if t["complexity"] == complexity])
        print(f"  {complexity.capitalize()}: {count}/{expected}")
    
    if results["failed_tests"]:
        print(f"\n❌ Failed Tests:")
        for failure in results["failed_tests"]:
            print(f"  - {failure}")
    
    # Determine if system is production ready
    generation_success = results["passed_generations"] / len(test_cases) * 100
    modification_success = results["passed_modifications"] / (len(test_cases) * 2) * 100 if len(test_cases) > 0 else 0
    
    print(f"\n🏆 PRODUCTION READINESS ASSESSMENT:")
    print(f"  Generation Success Rate: {generation_success:.1f}%")
    print(f"  Modification Success Rate: {modification_success:.1f}%")
    
    if generation_success >= 80 and modification_success >= 70:
        print("  ✅ SYSTEM IS PRODUCTION READY")
        return True
    else:
        print("  ❌ SYSTEM IS NOT PRODUCTION READY")
        print("  📋 Requirements: 80%+ generation success, 70%+ modification success")
        return False

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)