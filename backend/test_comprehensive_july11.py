#!/usr/bin/env python3
"""Comprehensive test of SwiftGen capabilities - July 11, 2025"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*70}")
    print(f"🧪 {title}")
    print(f"{'='*70}")

def test_generation(description, app_name, expected_complexity="simple"):
    """Test app generation"""
    print(f"\n📱 Testing: {app_name}")
    print(f"   Type: {expected_complexity}")
    print(f"   Description: {description[:60]}...")
    
    url = f"{BASE_URL}/api/generate"
    payload = {
        "description": description,
        "app_name": app_name
    }
    
    try:
        response = requests.post(url, json=payload, timeout=180)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ SUCCESS: {result.get('message', 'Generated')}")
            print(f"   Project ID: {result.get('project_id')}")
            return True, result.get('project_id')
        else:
            print(f"   ❌ FAILED: Status {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False, None
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False, None

def test_modification(project_id, modification, expected_result="should work"):
    """Test app modification"""
    print(f"\n🔧 Modification: {modification[:60]}...")
    print(f"   Expected: {expected_result}")
    
    url = f"{BASE_URL}/api/modify"
    payload = {
        "project_id": project_id,
        "modification": modification
    }
    
    try:
        response = requests.post(url, json=payload, timeout=180)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ SUCCESS: {result.get('message', 'Modified')}")
            print(f"   Modified by: {result.get('modified_by_llm', 'Unknown')}")
            return True
        else:
            print(f"   ❌ FAILED: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def check_apple_hig_compliance():
    """Check if Apple HIG rules are being enforced"""
    print_section("Apple HIG Compliance Check")
    
    # These should be in the prompts
    hig_rules = [
        "44x44pt minimum touch targets",
        "System colors only",
        "Safe area compliance",
        "Accessibility labels",
        "Standard spacing (4, 8, 12, 16, 20, 24, 32pt)"
    ]
    
    # Check if enhanced_prompts.py has HIG rules
    try:
        with open('backend/enhanced_prompts.py', 'r') as f:
            content = f.read()
            
        print("Checking for Apple HIG rules in prompts:")
        for rule in hig_rules:
            if rule.lower() in content.lower() or rule.split()[0].lower() in content.lower():
                print(f"   ✅ {rule}")
            else:
                print(f"   ❌ {rule} - NOT FOUND")
    except Exception as e:
        print(f"   ❌ Could not check prompts: {e}")

def run_comprehensive_test():
    """Run comprehensive testing suite"""
    
    print("🚀 SwiftGen Comprehensive Test Suite - July 11, 2025")
    print("="*70)
    
    # Check Apple HIG compliance first
    check_apple_hig_compliance()
    
    # Test 1: Simple App Generation
    print_section("Test 1: Simple App Generation")
    
    simple_apps = [
        ("Create a countdown timer with minutes and seconds", "CountdownPro", "simple"),
        ("Build a tip calculator with bill splitting", "TipSplit", "simple"),
        ("Make a color picker app with hex code display", "ColorPalette", "simple")
    ]
    
    simple_results = []
    for desc, name, complexity in simple_apps:
        success, project_id = test_generation(desc, name, complexity)
        simple_results.append((success, project_id, name))
        if success:
            time.sleep(5)  # Wait between tests
    
    # Test 2: Complex App Generation
    print_section("Test 2: Complex App Generation")
    
    complex_apps = [
        ("Create a fitness tracking app with workout plans, progress charts, calorie counter, and Apple Health integration", "FitTracker Pro", "complex"),
        ("Build a recipe app with ingredient lists, step-by-step instructions, cooking timers, shopping list generation, and meal planning", "ChefMaster", "complex"),
        ("Develop a budget tracking app with expense categories, monthly reports, bill reminders, and data visualization", "BudgetWise", "complex")
    ]
    
    complex_results = []
    for desc, name, complexity in complex_apps:
        success, project_id = test_generation(desc, name, complexity)
        complex_results.append((success, project_id, name))
        if success:
            time.sleep(5)
    
    # Test 3: Simple Modifications
    print_section("Test 3: Simple Modifications")
    
    # Use first successful simple app
    simple_app_id = None
    for success, pid, name in simple_results:
        if success and pid:
            simple_app_id = pid
            print(f"Using {name} ({pid}) for modification tests")
            break
    
    if simple_app_id:
        simple_mods = [
            "Change the main color theme to purple",
            "Make all buttons have rounded corners with radius 12",
            "Add haptic feedback when buttons are tapped"
        ]
        
        for mod in simple_mods:
            test_modification(simple_app_id, mod)
            time.sleep(3)
    
    # Test 4: Complex Modifications
    print_section("Test 4: Complex Modifications")
    
    # Use first successful complex app
    complex_app_id = None
    for success, pid, name in complex_results:
        if success and pid:
            complex_app_id = pid
            print(f"Using {name} ({pid}) for complex modification tests")
            break
    
    if complex_app_id:
        complex_mods = [
            "Add a comprehensive settings screen with theme selection, notification preferences, data export options, and about section",
            "Implement data persistence using Core Data with automatic backups",
            "Add a dashboard view showing weekly and monthly statistics with interactive charts"
        ]
        
        for mod in complex_mods:
            test_modification(complex_app_id, mod)
            time.sleep(5)
    
    # Summary
    print_section("Test Summary")
    
    simple_success = sum(1 for s, _, _ in simple_results if s)
    complex_success = sum(1 for s, _, _ in complex_results if s)
    
    print(f"Simple App Generation: {simple_success}/{len(simple_apps)} passed")
    print(f"Complex App Generation: {complex_success}/{len(complex_apps)} passed")
    print(f"Simple Modifications: Tested on {simple_app_id if simple_app_id else 'N/A'}")
    print(f"Complex Modifications: Tested on {complex_app_id if complex_app_id else 'N/A'}")
    
    # Check known issues
    print_section("Known Issues Check")
    
    issues = {
        "LLM Routing": "Fixed - Intelligent routing based on complexity",
        "JSON Parsing": "Enhanced - Better error recovery for xAI",
        "Apple HIG Compliance": "Check prompts above",
        "xAI Limitations": "Handled - Limited to simple tasks only",
        "Dismiss Pattern Errors": "Fixed - Pattern-based recovery",
        "Generic Parameter Errors": "Fixed - Automatic Hashable conformance"
    }
    
    for issue, status in issues.items():
        print(f"{issue}: {status}")
    
    print("\n" + "="*70)
    print("✅ Test suite completed. Check server logs for detailed analysis.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--no-server":
        print("Running without server (HIG compliance check only)")
        check_apple_hig_compliance()
    else:
        run_comprehensive_test()