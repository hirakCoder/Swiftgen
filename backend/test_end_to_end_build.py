#!/usr/bin/env python3
"""
End-to-end test that generates and builds apps to verify everything works
"""
import asyncio
import json
import os
import subprocess
import sys
import time
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_claude_service import EnhancedClaudeService
from project_manager import ProjectManager
from build_service import BuildService


async def test_complete_app_flow(app_type: str, description: str):
    """Test complete flow: generate -> create project -> build"""
    print(f"\n{'='*80}")
    print(f"TESTING COMPLETE FLOW: {app_type}")
    print(f"Description: {description}")
    print('='*80)
    
    start_time = time.time()
    success = True
    project_path = None
    
    try:
        # Initialize services
        service = EnhancedClaudeService()
        project_manager = ProjectManager()
        build_service = BuildService()
        
        # 1. Generate app
        print("\n1. GENERATING CODE...")
        result = await service.generate_ios_app(description, app_type)
        
        if not result or 'files' not in result:
            print(f"❌ FAILED: No code generated")
            return False
            
        print(f"✅ Generated {len(result['files'])} files")
        
        # Check critical files
        file_paths = [f['path'] for f in result['files']]
        has_app = any('App.swift' in path for path in file_paths)
        has_content_view = any('ContentView.swift' in path for path in file_paths)
        
        print(f"  - App.swift: {'✅' if has_app else '❌'}")
        print(f"  - ContentView.swift: {'✅' if has_content_view else '❌'}")
        
        # 2. Create project
        project_id = f"test_build_{app_type.replace(' ', '_').lower()}_{datetime.now().strftime('%H%M%S')}"
        print(f"\n2. CREATING PROJECT: {project_id}")
        
        project_path = await project_manager.create_project(
            project_id,
            result,
            app_type
        )
        
        if not os.path.exists(project_path):
            print("❌ FAILED: Project not created")
            return False
            
        print(f"✅ Project created at: {project_path}")
        
        # Check Info.plist for API apps
        if any(keyword in description.lower() for keyword in ['api', 'weather', 'currency', 'quote']):
            info_plist_path = os.path.join(project_path, "Info.plist")
            if os.path.exists(info_plist_path):
                with open(info_plist_path, 'r') as f:
                    plist_content = f.read()
                if 'NSAppTransportSecurity' in plist_content:
                    print("✅ Info.plist has SSL configuration")
                else:
                    print("❌ Info.plist missing SSL configuration")
                    success = False
            else:
                print("❌ Info.plist not found")
                success = False
        
        # Get bundle ID from project.json
        project_json_path = os.path.join(project_path, "project.json")
        bundle_id = "com.swiftgen.testapp"
        if os.path.exists(project_json_path):
            with open(project_json_path, 'r') as f:
                project_data = json.load(f)
                bundle_id = project_data.get('bundle_id', bundle_id)
        
        # 3. Build project
        print(f"\n3. BUILDING PROJECT...")
        build_result = await build_service.build_project(
            project_path=project_path,
            project_id=project_id,
            bundle_id=bundle_id,
            app_complexity="simple",
            is_modification=False
        )
        
        if build_result and build_result.get('success'):
            print("✅ BUILD SUCCESSFUL!")
            if 'app_path' in build_result:
                print(f"  App bundle: {build_result['app_path']}")
            if 'simulator_ready' in build_result:
                print(f"  Simulator ready: {build_result['simulator_ready']}")
        else:
            print("❌ BUILD FAILED!")
            if build_result and 'error' in build_result:
                print(f"  Error: {build_result['error']}")
            
            # Check build log
            build_log_path = os.path.join(os.path.dirname(__file__), 
                                          f"build_logs/proj_{project_id}_build.log")
            if os.path.exists(build_log_path):
                print("\n  Last 50 lines of build log:")
                with open(build_log_path, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-50:]:
                        if 'error:' in line.lower() or 'failed' in line.lower():
                            print(f"    {line.rstrip()}")
            
            success = False
        
        elapsed = time.time() - start_time
        print(f"\n⏱️  Total time: {elapsed:.1f}s")
        
        return success
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        if project_path and os.path.exists(project_path):
            print(f"\nCleaning up: {project_path}")
            os.system(f"rm -rf {project_path}")


async def run_tests():
    """Run end-to-end tests for calculator and currency converter"""
    
    print("🚀 END-TO-END APP GENERATION AND BUILD TESTS")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    test_cases = [
        ("Calculator", "Create a simple calculator app with basic math operations (+, -, *, /)"),
        ("Currency Converter", "Create a currency converter app that shows real-time exchange rates"),
    ]
    
    results = []
    
    for app_type, description in test_cases:
        success = await test_complete_app_flow(app_type, description)
        results.append((app_type, success))
        
        # Small delay between tests
        await asyncio.sleep(2)
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    for app_type, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{app_type:20} {status}")
    
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    
    print(f"\nTotal: {passed}/{len(results)} passed")
    
    if failed > 0:
        print("\n⚠️  CRITICAL: Some apps failed to build!")
        print("Simple app generation is NOT working properly!")
        return False
    else:
        print("\n✅ All apps generated and built successfully!")
        print("Simple app generation is working correctly!")
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
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)