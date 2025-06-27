#!/usr/bin/env python3
"""
Test app generation and build process with SSL fixes
"""

import os
import sys
import json
import time
import asyncio
import subprocess
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import initialize_app, generate_app, build_app, test_app_in_simulator

async def test_app_generation(app_description, project_name):
    """Test generating and building an app"""
    print(f"\n{'='*60}")
    print(f"Testing: {app_description}")
    print(f"Project: {project_name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    results = {
        'description': app_description,
        'project_name': project_name,
        'generation': {'success': False, 'files': 0},
        'build': {'success': False, 'errors': []},
        'ssl_fix': {'applied': False, 'domains': []},
        'simulator': {'success': False}
    }
    
    try:
        # Step 1: Generate app
        print("\n1. Generating app...")
        workspace_dir = "../workspaces"
        project_path = os.path.join(workspace_dir, project_name)
        
        # Clean up existing project
        if os.path.exists(project_path):
            import shutil
            shutil.rmtree(project_path)
        
        # Initialize app (this sets up all services)
        app = initialize_app()
        
        # Generate the app
        result = await generate_app(app_description, project_name)
        
        if result and 'project_path' in result:
            results['generation']['success'] = True
            
            # Count generated files
            file_count = 0
            for root, dirs, files in os.walk(project_path):
                file_count += len([f for f in files if f.endswith('.swift')])
            results['generation']['files'] = file_count
            
            print(f"✅ Generated {file_count} Swift files")
            
            # Check for Info.plist
            info_plist_path = os.path.join(project_path, 'Info.plist')
            if os.path.exists(info_plist_path):
                with open(info_plist_path, 'r') as f:
                    content = f.read()
                    if 'NSAppTransportSecurity' in content:
                        results['ssl_fix']['applied'] = True
                        print("✅ SSL configuration applied to Info.plist")
                    else:
                        print("❌ No SSL configuration in Info.plist")
            else:
                print("❌ Info.plist not found")
            
            # Check for API domains
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if file.endswith('.swift'):
                        filepath = os.path.join(root, file)
                        with open(filepath, 'r') as f:
                            content = f.read()
                            import re
                            urls = re.findall(r'https?://([^/"]+)', content)
                            results['ssl_fix']['domains'].extend(urls)
            
            if results['ssl_fix']['domains']:
                print(f"✅ Found API domains: {list(set(results['ssl_fix']['domains']))}")
        
        else:
            print("❌ App generation failed")
            return results
        
        # Step 2: Build app
        print("\n2. Building app...")
        build_result = await build_app(project_name)
        
        if build_result and build_result.get('success'):
            results['build']['success'] = True
            print("✅ Build successful")
            
            # Step 3: Test in simulator
            print("\n3. Testing in simulator...")
            sim_result = await test_app_in_simulator(project_name)
            
            if sim_result and sim_result.get('success'):
                results['simulator']['success'] = True
                print("✅ App launched in simulator")
            else:
                print("❌ Simulator launch failed")
        else:
            results['build']['errors'] = build_result.get('errors', [])
            print(f"❌ Build failed: {len(results['build']['errors'])} errors")
            for error in results['build']['errors'][:3]:
                print(f"   - {error}")
    
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
    
    results['duration'] = time.time() - start_time
    return results

async def main():
    """Run tests for different app types"""
    
    test_cases = [
        # Simple apps
        ("Create a simple calculator app", "test_calc_ssl"),
        ("Create a currency converter app with real-time exchange rates", "test_currency_ssl"),
        
        # API apps
        ("Create a weather app that shows current weather", "test_weather_ssl"),
        ("Create a quote of the day app", "test_quote_ssl"),
    ]
    
    results = []
    
    print(f"\nSwiftGen SSL Test Suite")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nRunning {len(test_cases)} tests...\n")
    
    for description, project_name in test_cases:
        result = await test_app_generation(description, project_name)
        results.append(result)
        
        # Small delay between tests
        await asyncio.sleep(2)
    
    # Summary
    print(f"\n\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    successful_generations = sum(1 for r in results if r['generation']['success'])
    successful_builds = sum(1 for r in results if r['build']['success'])
    successful_sims = sum(1 for r in results if r['simulator']['success'])
    ssl_fixes = sum(1 for r in results if r['ssl_fix']['applied'])
    
    print(f"\nGeneration: {successful_generations}/{len(results)} successful")
    print(f"Build:      {successful_builds}/{len(results)} successful")
    print(f"Simulator:  {successful_sims}/{len(results)} successful")
    print(f"SSL Fixes:  {ssl_fixes}/{len(results)} applied")
    
    print("\nDetailed Results:")
    for r in results:
        print(f"\n{r['description']}:")
        print(f"  - Generation: {'✅' if r['generation']['success'] else '❌'} ({r['generation']['files']} files)")
        print(f"  - SSL Fix:    {'✅' if r['ssl_fix']['applied'] else '❌'}")
        if r['ssl_fix']['domains']:
            print(f"    Domains: {list(set(r['ssl_fix']['domains']))}")
        print(f"  - Build:      {'✅' if r['build']['success'] else '❌'}")
        if not r['build']['success'] and r['build']['errors']:
            print(f"    First error: {r['build']['errors'][0]}")
        print(f"  - Simulator:  {'✅' if r['simulator']['success'] else '❌'}")
        print(f"  - Duration:   {r['duration']:.2f}s")
    
    # Save results
    with open('test_results_ssl.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n\nResults saved to test_results_ssl.json")

if __name__ == "__main__":
    asyncio.run(main())