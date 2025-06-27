#!/usr/bin/env python3
"""
Test SSL integration and build process
"""

import os
import json
import time
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_app_generation(description, expected_type="simple"):
    """Test generating an app and check SSL configuration"""
    
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Expected type: {expected_type}")
    print(f"{'='*60}")
    
    # Generate app
    print("\n1. Generating app...")
    response = requests.post(f"{BASE_URL}/api/generate", json={
        "description": description
    })
    
    if response.status_code != 200:
        print(f"❌ Generation failed: {response.status_code}")
        return None
    
    data = response.json()
    project_id = data.get('project_id')
    print(f"✅ Generated project: {project_id}")
    
    # Wait for generation to complete
    print("\n2. Waiting for generation to complete...")
    time.sleep(10)  # Give it time to generate and apply SSL fixes
    
    # Check project files
    project_path = f"../workspaces/{project_id}"
    results = {
        'project_id': project_id,
        'description': description,
        'files_generated': 0,
        'has_info_plist': False,
        'has_ssl_config': False,
        'api_domains': [],
        'build_success': False
    }
    
    if os.path.exists(project_path):
        # Count Swift files
        for root, dirs, files in os.walk(project_path):
            results['files_generated'] += len([f for f in files if f.endswith('.swift')])
        
        # Check Info.plist
        info_plist_path = os.path.join(project_path, 'Info.plist')
        if os.path.exists(info_plist_path):
            results['has_info_plist'] = True
            with open(info_plist_path, 'r') as f:
                content = f.read()
                if 'NSAppTransportSecurity' in content:
                    results['has_ssl_config'] = True
                    print("✅ SSL configuration found in Info.plist")
                else:
                    print("❌ No SSL configuration in Info.plist")
        else:
            print("❌ Info.plist not found")
        
        # Check for API usage
        import re
        for root, dirs, files in os.walk(os.path.join(project_path, 'Sources')):
            for file in files:
                if file.endswith('.swift'):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r') as f:
                        content = f.read()
                        urls = re.findall(r'https?://([^/"]+)', content)
                        results['api_domains'].extend(urls)
        
        results['api_domains'] = list(set(results['api_domains']))
        
        if results['api_domains']:
            print(f"✅ Found API domains: {results['api_domains']}")
        
        # Check build
        print("\n3. Checking build status...")
        build_path = os.path.join(project_path, 'build/Build/Products/Debug-iphonesimulator')
        if os.path.exists(build_path):
            apps = [d for d in os.listdir(build_path) if d.endswith('.app')]
            if apps:
                results['build_success'] = True
                print(f"✅ Build successful: {apps[0]}")
            else:
                print("❌ No .app bundle found")
        else:
            print("❌ Build directory not found")
    
    return results

def main():
    """Run SSL integration tests"""
    
    print("SwiftGen SSL Integration Test")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Server not running. Please start the server first.")
            return
    except:
        print("❌ Cannot connect to server at http://localhost:8000")
        print("Please start the server with: python3 main.py")
        return
    
    # Test cases
    test_cases = [
        # Simple app (no SSL needed)
        ("Create a simple calculator app", "simple"),
        
        # API apps (SSL needed)
        ("Create a currency converter app with real-time exchange rates", "api"),
        ("Create a weather app that shows current weather for any city", "api"),
        ("Create a quote of the day app", "api"),
    ]
    
    results = []
    
    for description, expected_type in test_cases:
        result = test_app_generation(description, expected_type)
        if result:
            results.append(result)
        time.sleep(5)  # Delay between tests
    
    # Summary
    print(f"\n\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    total = len(results)
    generated = sum(1 for r in results if r['files_generated'] > 0)
    has_plist = sum(1 for r in results if r['has_info_plist'])
    has_ssl = sum(1 for r in results if r['has_ssl_config'])
    needs_ssl = sum(1 for r in results if r['api_domains'])
    correct_ssl = sum(1 for r in results if (r['api_domains'] and r['has_ssl_config']) or (not r['api_domains'] and not r['has_ssl_config']))
    built = sum(1 for r in results if r['build_success'])
    
    print(f"\nGeneration:     {generated}/{total} successful")
    print(f"Info.plist:     {has_plist}/{total} have Info.plist")
    print(f"SSL Config:     {has_ssl}/{needs_ssl} API apps have SSL config")
    print(f"SSL Correct:    {correct_ssl}/{total} have correct SSL setup")
    print(f"Build Success:  {built}/{total} built successfully")
    
    print("\nDetailed Results:")
    for r in results:
        print(f"\n{r['description']}:")
        print(f"  Project ID:    {r['project_id']}")
        print(f"  Files:         {r['files_generated']} Swift files")
        print(f"  Info.plist:    {'✅' if r['has_info_plist'] else '❌'}")
        print(f"  SSL Config:    {'✅' if r['has_ssl_config'] else '❌'}")
        print(f"  API Domains:   {r['api_domains'] if r['api_domains'] else 'None'}")
        print(f"  Build:         {'✅' if r['build_success'] else '❌'}")
        
        # Check if SSL is correctly applied
        if r['api_domains'] and not r['has_ssl_config']:
            print(f"  ⚠️  WARNING: App uses APIs but missing SSL config!")
        elif not r['api_domains'] and r['has_ssl_config']:
            print(f"  ⚠️  WARNING: App has SSL config but doesn't use APIs")
    
    # Save results
    with open('ssl_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n\nResults saved to ssl_test_results.json")

if __name__ == "__main__":
    main()