#!/usr/bin/env python3
"""
Test script for UI Quality Improvements
Tests generation quality for different app types
"""

import json
import asyncio
import os
import sys
import re
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import necessary modules
from enhanced_claude_service import EnhancedClaudeService
from ui_quality_validator import UIQualityValidator
from modification_handler import ModificationHandler

async def test_app_generation(claude_service, app_type, description):
    """Test app generation and validate UI quality"""
    print(f"\n{'='*60}")
    print(f"Testing {app_type} App Generation")
    print(f"{'='*60}")
    
    try:
        # Generate app
        print(f"Generating {app_type} app...")
        result = await claude_service.generate_ios_app(
            description=description,
            app_name=f"Test{app_type}"
        )
        
        if result.get("success"):
            print(f"✅ Generation successful!")
            
            # Validate UI quality
            validator = UIQualityValidator()
            is_valid, issues, score = validator.validate_ui_quality(result.get("files", []))
            
            print(f"\n📊 UI Quality Score: {score}/100")
            print(f"✅ Valid: {is_valid}")
            
            if issues:
                print("\n⚠️  Issues found:")
                for issue in issues[:5]:  # Show first 5 issues
                    print(f"  - {issue}")
            
            # Check for anti-patterns
            check_antipatterns(result.get("files", []))
            
            return result
        else:
            print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        return None

def check_antipatterns(files):
    """Check for specific anti-patterns in generated code"""
    print("\n🔍 Checking for anti-patterns:")
    
    antipatterns = {
        "Multiple gradients": r'(Linear|Radial|Angular)Gradient.*?(Linear|Radial|Angular)Gradient',
        "Gradient on text": r'Text\([^)]+\)[\s\n]*\.foregroundStyle\([^)]*Gradient',
        "Custom colors": r'Color\(red:|Color\(#|Color\(hex:',
        "Complex animations": r'\.animation\(|\.transition\(|withAnimation',
        "Missing foregroundColor": r'Text\([^)]+\)(?!.*foregroundColor)(?!.*foregroundStyle)',
    }
    
    found_issues = False
    for file in files:
        if file['path'].endswith('.swift'):
            content = file['content']
            for pattern_name, pattern in antipatterns.items():
                matches = len(re.findall(pattern, content, re.DOTALL))
                if matches > 0:
                    if pattern_name == "Complex animations" and matches <= 3:
                        continue  # Allow up to 3 animations
                    print(f"  ❌ {pattern_name}: {matches} occurrences in {file['path']}")
                    found_issues = True
    
    if not found_issues:
        print("  ✅ No anti-patterns detected!")

async def test_modification(claude_service, app_files, modification_request):
    """Test app modification"""
    print(f"\n{'='*60}")
    print(f"Testing Modification: {modification_request}")
    print(f"{'='*60}")
    
    try:
        # Use modification handler
        mod_handler = ModificationHandler()
        
        # Modify app
        print("Applying modification...")
        result = await claude_service.modify_ios_app(
            app_name="TestApp",
            description="Test app",
            modification=modification_request,
            files=app_files
        )
        
        if result.get("files"):
            print("✅ Modification successful!")
            
            # Check what changed
            modified_files = result.get("files_modified", [])
            changes = result.get("changes_made", [])
            
            print(f"\n📝 Files modified: {len(modified_files)}")
            for file in modified_files[:3]:
                print(f"  - {file}")
            
            print(f"\n🔧 Changes made:")
            for change in changes[:5]:
                print(f"  - {change}")
            
            # Validate UI quality after modification
            validator = UIQualityValidator()
            is_valid, issues, score = validator.validate_ui_quality(result.get("files", []))
            
            print(f"\n📊 UI Quality Score after modification: {score}/100")
            
            return result
        else:
            print(f"❌ Modification failed")
            return None
            
    except Exception as e:
        print(f"❌ Error during modification: {e}")
        return None

async def main():
    """Run all tests"""
    print("🧪 Testing UI Quality Improvements")
    print("="*60)
    
    # Initialize Claude service
    claude_service = EnhancedClaudeService()
    
    # Test different app types
    test_apps = [
        ("Timer", "Create a simple timer app with start, pause, and reset functionality. Display the time in MM:SS format."),
        ("Todo", "Create a todo list app where users can add, complete, and delete tasks. Use a simple list interface."),
        ("Calculator", "Create a basic calculator app with number buttons 0-9 and basic operations (+, -, *, /)."),
    ]
    
    results = {}
    
    for app_type, description in test_apps:
        result = await test_app_generation(claude_service, app_type, description)
        if result:
            results[app_type] = result
    
    # Test modifications
    if "Timer" in results:
        print("\n" + "="*60)
        print("TESTING MODIFICATIONS")
        print("="*60)
        
        timer_files = results["Timer"].get("files", [])
        
        # Test dark mode addition
        await test_modification(
            claude_service, 
            timer_files,
            "Add a dark mode toggle to the timer app"
        )
        
        # Test UI enhancement
        await test_modification(
            claude_service,
            timer_files, 
            "Make the timer display larger and more prominent"
        )
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for app_type, result in results.items():
        validator = UIQualityValidator()
        _, _, score = validator.validate_ui_quality(result.get("files", []))
        print(f"{app_type}: Quality Score = {score}/100")

if __name__ == "__main__":
    asyncio.run(main())