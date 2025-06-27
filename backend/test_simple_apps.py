#!/usr/bin/env python3
"""
Test suite to verify simple apps work correctly
Tests common app types that should work without issues
"""
import asyncio
import json
import os
import sys
import time
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_claude_service import EnhancedClaudeService
from project_manager import ProjectManager
from build_service import BuildService


async def test_app_generation(app_type: str, description: str):
    """Test generating a specific app type"""
    print(f"\n{'='*60}")
    print(f"Testing: {app_type}")
    print(f"Description: {description}")
    print('='*60)
    
    start_time = time.time()
    
    try:
        # Initialize services
        service = EnhancedClaudeService()
        project_manager = ProjectManager()
        build_service = BuildService()
        
        # Generate app
        print("1. Generating code...")
        result = await service.generate_ios_app(description, app_type)
        
        if not result or 'files' not in result:
            print(f"❌ FAILED: No code generated")
            return False
            
        print(f"✅ Generated {len(result['files'])} files")
        
        # Check for critical files
        file_paths = [f['path'] for f in result['files']]
        has_app = any('App.swift' in path for path in file_paths)
        has_content_view = any('ContentView.swift' in path for path in file_paths)
        has_info_plist = any('Info.plist' in path for path in file_paths)
        
        print(f"  - App.swift: {'✅' if has_app else '❌'}")
        print(f"  - ContentView.swift: {'✅' if has_content_view else '❌'}")
        print(f"  - Info.plist: {'✅' if has_info_plist else '❌'}")
        
        # Check for SSL configuration if API app
        if any(keyword in description.lower() for keyword in ['api', 'weather', 'currency', 'quote']):
            print("\n2. Checking SSL configuration...")
            info_plist = next((f for f in result['files'] if 'Info.plist' in f['path']), None)
            if info_plist and 'NSAppTransportSecurity' in info_plist.get('content', ''):
                print("✅ SSL configuration present")
            else:
                print("❌ MISSING SSL configuration")
                # Should be fixed by EMERGENCY_CURRENCY_FIX
        
        # Check JSON decoding for currency apps
        if 'currency' in description.lower():
            print("\n3. Checking JSON decoding...")
            service_file = next((f for f in result['files'] if 'Service' in f['path']), None)
            if service_file:
                content = service_file['content']
                if 'ExchangeRateResponse' in content or 'Codable' in content:
                    print("✅ Proper JSON decoding structure")
                else:
                    print("❌ Missing proper JSON decoding")
        
        # Create test project
        project_id = f"test_{app_type.replace(' ', '_')}_{datetime.now().strftime('%H%M%S')}"
        print(f"\n4. Creating project {project_id}...")
        
        project_path = await project_manager.create_project(
            project_id,
            result,
            app_type
        )
        
        # Check if files were written
        if os.path.exists(project_path):
            swift_files = []
            for root, _, files in os.walk(os.path.join(project_path, "Sources")):
                swift_files.extend([f for f in files if f.endswith('.swift')])
            print(f"✅ Project created with {len(swift_files)} Swift files")
            
            # Check Info.plist after creation
            info_plist_path = os.path.join(project_path, "Info.plist")
            if os.path.exists(info_plist_path):
                with open(info_plist_path, 'r') as f:
                    plist_content = f.read()
                if 'NSAppTransportSecurity' in plist_content:
                    print("✅ Info.plist has SSL configuration")
                else:
                    print("⚠️  Info.plist missing SSL configuration")
        else:
            print("❌ FAILED: Project not created")
            return False
        
        elapsed = time.time() - start_time
        print(f"\n✅ {app_type} test completed in {elapsed:.1f}s")
        
        # Cleanup
        os.system(f"rm -rf {project_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run tests for all simple app types"""
    
    test_cases = [
        ("Calculator", "Create a simple calculator app with basic operations"),
        ("Timer", "Create a countdown timer app"),
        ("Counter", "Create a counter app with increment and decrement"),
        ("Todo List", "Create a simple todo list app"),
        ("Currency Converter", "Create a currency converter app that shows real-time exchange rates"),
        ("Weather App", "Create a weather app that shows current weather"),
        ("Quote App", "Create an app that displays random quotes from an API"),
    ]
    
    results = []
    
    print("🧪 TESTING SIMPLE APP GENERATION")
    print(f"Testing {len(test_cases)} app types...")
    
    for app_type, description in test_cases:
        success = await test_app_generation(app_type, description)
        results.append((app_type, success))
        
        # Small delay between tests
        await asyncio.sleep(2)
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    
    for app_type, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{app_type:20} {status}")
    
    print(f"\nTotal: {passed}/{len(results)} passed ({failed} failed)")
    
    if failed > 0:
        print("\n⚠️  CRITICAL: Some simple apps are broken!")
        return False
    else:
        print("\n✅ All simple apps working correctly!")
        return True


if __name__ == "__main__":
    # Check if services are available
    try:
        from enhanced_claude_service import EnhancedClaudeService
        service = EnhancedClaudeService()
        if not service.available_models:
            print("❌ No LLM models available. Check API keys.")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        sys.exit(1)
    
    # Run tests
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)