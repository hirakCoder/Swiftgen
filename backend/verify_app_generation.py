#!/usr/bin/env python3
"""
Verify app generation works by checking recent logs and generated files
"""
import os
import json
import re
from datetime import datetime, timedelta


def check_recent_apps():
    """Check recently generated apps for issues"""
    
    workspaces_dir = "/Users/hirakbanerjee/Desktop/SwiftGen/swiftgen-mvp/workspaces"
    
    if not os.path.exists(workspaces_dir):
        print("❌ No workspaces directory found")
        return False
    
    # Get recent project directories (last 24 hours)
    recent_projects = []
    cutoff_time = datetime.now() - timedelta(hours=24)
    
    for project_dir in os.listdir(workspaces_dir):
        project_path = os.path.join(workspaces_dir, project_dir)
        if os.path.isdir(project_path) and project_dir.startswith("proj_"):
            stat = os.stat(project_path)
            mod_time = datetime.fromtimestamp(stat.st_mtime)
            if mod_time > cutoff_time:
                recent_projects.append((project_dir, project_path, mod_time))
    
    if not recent_projects:
        print("No recent projects found (last 24 hours)")
        return True
    
    print(f"Found {len(recent_projects)} recent projects")
    print("="*60)
    
    issues = []
    
    for project_id, project_path, mod_time in sorted(recent_projects, key=lambda x: x[2], reverse=True)[:5]:
        print(f"\nChecking {project_id} (created {mod_time.strftime('%Y-%m-%d %H:%M')})")
        
        # Check project.json
        project_json_path = os.path.join(project_path, "project.json")
        if os.path.exists(project_json_path):
            with open(project_json_path, 'r') as f:
                project_data = json.load(f)
            
            app_name = project_data.get('product_name', 'Unknown')
            bundle_id = project_data.get('bundle_id', '')
            
            print(f"  App: {app_name}")
            print(f"  Bundle ID: {bundle_id}")
            
            # Check for currency/API apps
            is_api_app = any(keyword in app_name.lower() for keyword in ['currency', 'weather', 'quote', 'api'])
            
            if is_api_app:
                print("  Type: API-based app")
                
                # Check Info.plist
                info_plist_path = os.path.join(project_path, "Info.plist")
                if os.path.exists(info_plist_path):
                    with open(info_plist_path, 'r') as f:
                        plist_content = f.read()
                    
                    has_ssl = 'NSAppTransportSecurity' in plist_content
                    print(f"  SSL Config: {'✅' if has_ssl else '❌ MISSING'}")
                    
                    if not has_ssl:
                        issues.append(f"{project_id}: Missing SSL configuration")
                else:
                    print("  Info.plist: ❌ MISSING")
                    issues.append(f"{project_id}: Missing Info.plist")
                
                # Check for service file
                service_files = []
                sources_dir = os.path.join(project_path, "Sources")
                if os.path.exists(sources_dir):
                    for root, _, files in os.walk(sources_dir):
                        for file in files:
                            if 'service' in file.lower() and file.endswith('.swift'):
                                service_files.append(os.path.join(root, file))
                
                if service_files:
                    # Check JSON decoding
                    for service_file in service_files:
                        with open(service_file, 'r') as f:
                            content = f.read()
                        
                        # Check for proper JSON structures
                        has_codable = 'Codable' in content or 'Decodable' in content
                        has_response_struct = 'Response' in content and 'struct' in content
                        has_json_decoder = 'JSONDecoder' in content
                        
                        print(f"  JSON Decoding: ", end="")
                        if has_codable and has_json_decoder:
                            print("✅")
                        else:
                            print("⚠️  May have issues")
                            if 'currency' in app_name.lower():
                                # Check for the specific issue
                                if '[String: [String: Double]]' in content:
                                    print("    ❌ Wrong JSON format for currency API")
                                    issues.append(f"{project_id}: Wrong currency API JSON format")
            else:
                print("  Type: Simple app")
        else:
            print("  ❌ No project.json found")
            issues.append(f"{project_id}: Missing project.json")
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if issues:
        print(f"❌ Found {len(issues)} issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ All recent apps appear to be correctly configured")
        return True


def check_specific_patterns():
    """Check for specific known issues"""
    
    print("\nChecking for known issues...")
    
    # Check if EMERGENCY_CURRENCY_FIX is being applied
    main_py = "/Users/hirakbanerjee/Desktop/SwiftGen/swiftgen-mvp/backend/main.py"
    with open(main_py, 'r') as f:
        main_content = f.read()
    
    checks = {
        "SSL fix after project creation": "EMERGENCY_CURRENCY_FIX" in main_content,
        "Simple app detection": "simple_apps = [" in main_content,
        "Complexity detection fix": "simple_apps" in main_content and "currency converter" in main_content,
        "SSL keywords check": "['currency', 'converter', 'exchange rate', 'api', 'weather', 'quote']" in main_content
    }
    
    all_good = True
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
        if not passed:
            all_good = False
    
    return all_good


if __name__ == "__main__":
    print("🔍 Verifying App Generation")
    print("="*60)
    
    # Check recent apps
    apps_ok = check_recent_apps()
    
    # Check code patterns
    patterns_ok = check_specific_patterns()
    
    print("\n" + "="*60)
    if apps_ok and patterns_ok:
        print("✅ App generation appears to be working correctly")
    else:
        print("⚠️  Issues detected - simple apps may be broken")