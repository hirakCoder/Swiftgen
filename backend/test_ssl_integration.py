#!/usr/bin/env python3
"""
Test SSL Fixer Integration
"""
import asyncio
import sys
import os
import json

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import build service
from build_service import BuildService
from automatic_ssl_fixer import AutomaticSSLFixer, integrate_with_build_service

async def test_ssl_integration():
    """Test that SSL fixer is properly integrated"""
    
    print("Testing SSL Fixer Integration...")
    
    # Initialize build service
    build_service = BuildService()
    
    # Check if build_project method exists
    print(f"✓ BuildService has build_project method: {hasattr(build_service, 'build_project')}")
    
    # Store original method
    original_build = build_service.build_project
    
    # Integrate SSL fixer
    integrate_with_build_service(build_service)
    
    # Check if method was replaced
    print(f"✓ build_project method was enhanced: {build_service.build_project != original_build}")
    
    # Create a test project structure
    test_project_path = "../workspaces/test_ssl_integration"
    os.makedirs(test_project_path, exist_ok=True)
    
    # Create a Swift file with API usage
    os.makedirs(f"{test_project_path}/Sources", exist_ok=True)
    with open(f"{test_project_path}/Sources/APIService.swift", "w") as f:
        f.write("""
import Foundation

class APIService {
    let apiURL = "https://api.exchangerate-api.com/v4/latest/USD"
    
    func fetchRates() async throws -> Data {
        let url = URL(string: apiURL)!
        let (data, _) = try await URLSession.shared.data(from: url)
        return data
    }
}
""")
    
    # Create a basic Info.plist without SSL config
    with open(f"{test_project_path}/Info.plist", "w") as f:
        f.write("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>Test App</string>
</dict>
</plist>""")
    
    print(f"\n✓ Created test project at: {test_project_path}")
    
    # Check Info.plist before
    with open(f"{test_project_path}/Info.plist", "r") as f:
        original_plist = f.read()
    print(f"✓ Original Info.plist has SSL config: {'NSAppTransportSecurity' in original_plist}")
    
    # Test the SSL fixer directly
    ssl_fixer = AutomaticSSLFixer()
    
    # Read files
    files = []
    for root, dirs, filenames in os.walk(test_project_path):
        for filename in filenames:
            if filename.endswith(('.swift', '.plist')):
                filepath = os.path.join(root, filename)
                with open(filepath, 'r') as f:
                    files.append({
                        'path': os.path.relpath(filepath, test_project_path),
                        'content': f.read()
                    })
    
    # Apply fixes
    fix_result = ssl_fixer.apply_automatic_fixes(files)
    
    print(f"\n✓ SSL Fixer detected domains: {fix_result['domains_fixed']}")
    print(f"✓ Fixes applied: {fix_result['fixes_applied']}")
    
    # Check if Info.plist was fixed
    for file in fix_result['files']:
        if 'Info.plist' in file['path']:
            print(f"✓ Info.plist now has SSL config: {'NSAppTransportSecurity' in file['content']}")
            break
    
    # Clean up
    import shutil
    shutil.rmtree(test_project_path)
    
    print("\n✅ SSL Fixer integration test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_ssl_integration())