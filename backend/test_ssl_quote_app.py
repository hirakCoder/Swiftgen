#!/usr/bin/env python3
"""
Test SSL issue with motivational quote app
"""

import requests
import json
import time

def test_motivational_quote_app():
    """Test generating a motivational quote app that uses HTTPS API"""
    
    # API endpoint
    url = "http://localhost:8000/api/generate"
    
    # Request for motivational quote app
    data = {
        "description": """Create a motivational quote app that:
        - Fetches daily quotes from https://api.quotable.io/random
        - Shows the quote and author in a beautiful card
        - Has a refresh button to get new quotes
        - Saves favorite quotes locally
        - Uses modern SwiftUI design with gradients""",
        "app_name": "DailyMotivation",
        "target_ios_version": "16.0"
    }
    
    print("🚀 Testing Motivational Quote App Generation...")
    print(f"App Name: {data['app_name']}")
    print(f"Description: {data['description'][:100]}...")
    
    try:
        # Send request
        response = requests.post(url, json=data, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            project_id = result.get('project_id')
            print(f"✅ Generation started: Project ID = {project_id}")
            
            # Wait a bit and check project status
            time.sleep(5)
            
            # Check project logs
            logs_url = f"http://localhost:8000/api/monitoring/project/{project_id}"
            logs_response = requests.get(logs_url)
            
            if logs_response.status_code == 200:
                logs = logs_response.json()
                print(f"\n📋 Project logs: {len(logs.get('logs', []))} entries")
                
                # Look for SSL errors
                ssl_errors = [log for log in logs.get('logs', []) 
                             if 'SSL' in log.get('message', '') or 
                                'certificate' in log.get('message', '').lower() or
                                'SSL' in log.get('details', {}).get('error', '')]
                
                if ssl_errors:
                    print("\n⚠️ SSL Errors found:")
                    for error in ssl_errors:
                        print(f"  - {error['message']}")
                        if error.get('details'):
                            print(f"    Details: {error['details']}")
            
            return project_id
            
        else:
            print(f"❌ Generation failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def check_ssl_in_generated_code(project_id):
    """Check if SSL handling was added to the generated code"""
    import os
    
    project_path = f"../workspaces/{project_id}"
    
    if not os.path.exists(project_path):
        print(f"❌ Project directory not found: {project_path}")
        return
    
    print(f"\n🔍 Checking generated code for SSL handling...")
    
    # Check Info.plist for ATS settings
    info_plist_path = os.path.join(project_path, "Info.plist")
    if os.path.exists(info_plist_path):
        with open(info_plist_path, 'r') as f:
            content = f.read()
            if "NSAppTransportSecurity" in content:
                print("✅ Info.plist has ATS configuration")
            else:
                print("❌ Info.plist missing ATS configuration")
    
    # Check for SSL handling in Swift files
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if file.endswith('.swift'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                    if "URLSession" in content and ("certificate" in content.lower() or "SSL" in content):
                        print(f"✅ Found SSL handling in {file}")
                    elif "https://" in content and "URLSession" in content:
                        print(f"⚠️ {file} uses HTTPS but may lack SSL handling")

if __name__ == "__main__":
    print("=" * 60)
    print("Testing SSL Issues with Motivational Quote App")
    print("=" * 60)
    
    # Test generation
    project_id = test_motivational_quote_app()
    
    if project_id:
        # Wait for build to complete
        print("\n⏳ Waiting for build to complete...")
        time.sleep(30)
        
        # Check the generated code
        check_ssl_in_generated_code(project_id)
    
    print("\n" + "=" * 60)