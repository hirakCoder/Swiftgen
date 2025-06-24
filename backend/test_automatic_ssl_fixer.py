#!/usr/bin/env python3
"""
Test the automatic SSL fixer
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from automatic_ssl_fixer import AutomaticSSLFixer


def test_automatic_ssl_fixer():
    """Test the automatic SSL fixer functionality"""
    
    # Create test files
    test_files = [
        {
            "path": "Info.plist",
            "content": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>TestApp</string>
</dict>
</plist>"""
        },
        {
            "path": "Sources/Services/APIService.swift",
            "content": """import Foundation

class APIService {
    let apiURL = "https://api.example.com/data"
    let quotesURL = URL(string: "https://zenquotes.io/api/random")!
    
    func fetchData() async throws {
        let (data, _) = try await URLSession.shared.data(from: URL(string: apiURL)!)
    }
}"""
        }
    ]
    
    fixer = AutomaticSSLFixer()
    
    # Test domain detection
    print("Testing domain detection...")
    domains = fixer.detect_api_usage(test_files)
    print(f"Detected domains: {domains}")
    assert "api.example.com" in domains
    assert "zenquotes.io" in domains
    
    # Test ATS check
    print("\nTesting ATS configuration check...")
    has_ats, missing = fixer.check_info_plist_for_ats(test_files, domains)
    print(f"Has ATS: {has_ats}, Missing domains: {missing}")
    assert not has_ats
    assert len(missing) == 2
    
    # Test automatic fix
    print("\nTesting automatic fix...")
    result = fixer.apply_automatic_fixes(test_files)
    print(f"Fix result: {result['fixes_applied']}")
    print(f"Domains fixed: {result['domains_fixed']}")
    
    # Verify Info.plist was updated
    info_plist = next(f for f in result['files'] if 'Info.plist' in f['path'])
    print("\nUpdated Info.plist content:")
    print(info_plist['content'])
    
    assert "NSAppTransportSecurity" in info_plist['content']
    assert "api.example.com" in info_plist['content']
    assert "zenquotes.io" in info_plist['content']
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    test_automatic_ssl_fixer()