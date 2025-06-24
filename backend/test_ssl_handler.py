#!/usr/bin/env python3
"""
Test script for SSL Error Handler functionality
"""

from ssl_error_handler import SSLErrorHandler
from ios_specific_fixes import IOSSpecificFixes
from modification_handler import ModificationHandler

def test_ssl_detection():
    """Test SSL error detection"""
    print("Testing SSL Error Detection...")
    
    handler = SSLErrorHandler()
    
    # Test cases
    test_errors = [
        "App Transport Security has blocked a cleartext HTTP (http://) resource load since it is insecure.",
        "NSURLErrorDomain Code=-1202 The certificate for this server is invalid",
        "An SSL error has occurred and a secure connection to the server cannot be made.",
        "HTTP load failed (error code: -1022) App Transport Security policy requires HTTPS",
        "The resource could not be loaded because the App Transport Security policy requires the use of a secure connection.",
        "Regular error without SSL issues"
    ]
    
    for error in test_errors:
        has_ssl, patterns = handler.detect_ssl_error(error)
        print(f"\nError: {error[:60]}...")
        print(f"SSL Error Detected: {has_ssl}")
        if patterns:
            print(f"Matched Patterns: {patterns[:2]}")
    
    print("\n" + "="*60 + "\n")

def test_ssl_analysis():
    """Test SSL issue analysis"""
    print("Testing SSL Issue Analysis...")
    
    handler = SSLErrorHandler()
    
    error_msg = """
    2024-12-20 10:30:45.123 MyApp[12345:67890] App Transport Security has blocked a cleartext HTTP (http://api.example.com/data) resource load since it is insecure. Temporary exceptions can be configured via your app's Info.plist file.
    """
    
    analysis = handler.analyze_ssl_issue(error_msg, "/path/to/project")
    
    print(f"Has SSL Error: {analysis['has_ssl_error']}")
    print(f"Domain Extracted: {analysis.get('domain', 'None')}")
    print(f"Recommended Fixes: {len(analysis['recommended_fixes'])}")
    
    for fix in analysis['recommended_fixes']:
        print(f"  - {fix['type']}: {fix['description']}")
    
    # Get user-friendly explanation
    explanation = handler.get_user_friendly_explanation(analysis)
    print(f"\nUser Explanation:\n{explanation}")
    
    print("\n" + "="*60 + "\n")

def test_fix_generation():
    """Test SSL fix code generation"""
    print("Testing SSL Fix Generation...")
    
    handler = SSLErrorHandler()
    
    # Test different fix types
    fix_types = ["add_ats_exception", "upgrade_to_https", "implement_cert_validation"]
    
    for fix_type in fix_types:
        print(f"\nGenerating fix for: {fix_type}")
        fix_code = handler.generate_fix_code(fix_type, domain="api.example.com")
        
        if "description" in fix_code:
            print(f"Description: {fix_code['description']}")
        
        if "info_plist_modification" in fix_code:
            print("Info.plist modification preview:")
            print(fix_code['info_plist_modification'][:200] + "...")
        
        if "swift_code" in fix_code:
            print("Swift code preview:")
            print(fix_code['swift_code'][:200] + "...")
    
    print("\n" + "="*60 + "\n")

def test_ios_fixes():
    """Test iOS-specific fixes"""
    print("Testing iOS Specific Fixes...")
    
    fixes = IOSSpecificFixes()
    
    # Test finding fixes for common issues
    test_issues = [
        "App Transport Security has blocked a cleartext HTTP",
        "This app needs NSCameraUsageDescription",
        "does not contain bitcode",
        "The certificate for this server is invalid"
    ]
    
    for issue in test_issues:
        print(f"\nIssue: {issue}")
        applicable_fixes = fixes.find_fixes_for_issue(issue)
        print(f"Found {len(applicable_fixes)} applicable fixes")
        
        if applicable_fixes:
            fix = applicable_fixes[0]
            print(f"  - {fix.title}")
            print(f"  - Category: {fix.category.value}")
    
    print("\n" + "="*60 + "\n")

def test_modification_handler():
    """Test modification handler with SSL detection"""
    print("Testing Modification Handler Integration...")
    
    handler = ModificationHandler()
    
    # Test issue detection
    ssl_error = "App Transport Security has blocked HTTP access to api.example.com"
    
    detection = handler.detect_and_handle_issue(ssl_error, "/path/to/project")
    
    print(f"Issue Detected: {detection['issue_detected']}")
    print(f"Issue Type: {detection.get('issue_type', 'None')}")
    print(f"Is Repeated: {detection['is_repeated']}")
    print(f"User Message Preview: {detection['user_message'][:100]}...")
    
    # Test SSL fix application
    if detection['issue_detected'] and detection['issue_type'] == 'ssl_error':
        print("\nTesting SSL Fix Application...")
        
        test_files = [
            {"path": "ContentView.swift", "content": "import SwiftUI\n\nstruct ContentView: View {\n    var body: some View {\n        Text(\"Hello\")\n    }\n}"},
            {"path": "Info.plist", "content": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>MyApp</string>
</dict>
</plist>"""}
        ]
        
        result = handler.apply_ssl_fix(test_files, "add_ats_exception", domain="api.example.com")
        
        print(f"Files Modified: {result['files_modified']}")
        print(f"Changes Made: {result['changes_made']}")
        
        # Check if Info.plist was updated
        for file in result['files']:
            if 'Info.plist' in file['path']:
                print("\nUpdated Info.plist preview:")
                print(file['content'][:300] + "...")
    
    print("\n" + "="*60 + "\n")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("SSL Error Handler Test Suite")
    print("="*60 + "\n")
    
    test_ssl_detection()
    test_ssl_analysis()
    test_fix_generation()
    test_ios_fixes()
    test_modification_handler()
    
    print("All tests completed!")

if __name__ == "__main__":
    main()