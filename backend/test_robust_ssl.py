#!/usr/bin/env python3
"""
Test script for Robust SSL Handler
"""

from robust_ssl_handler import RobustSSLHandler

def test_comprehensive_ssl_fix():
    """Test the comprehensive SSL fix generation"""
    print("Testing Robust SSL Handler...")
    print("=" * 60)
    
    handler = RobustSSLHandler()
    
    # Test with a typical external API domain
    domain = "api.myservice.com"
    
    # Generate comprehensive solution
    solution = handler.generate_comprehensive_ssl_solution(domain, "certificate")
    
    print(f"\nGenerated SSL solution for domain: {domain}")
    print("-" * 40)
    
    # Check Info.plist fix
    if "info_plist_changes" in solution:
        print("\n1. Info.plist Configuration:")
        print(solution["info_plist_changes"]["description"])
        print("Content preview:")
        print(solution["info_plist_changes"]["content"][:300] + "...")
    
    # Check network configuration
    if "network_configuration" in solution:
        print("\n2. Network Configuration:")
        print(f"File: {solution['network_configuration']['filename']}")
        print(solution['network_configuration']['description'])
        print("Code preview:")
        print(solution['network_configuration']['content'][:400] + "...")
    
    # Check URLSession delegate
    if "url_session_delegate" in solution:
        print("\n3. URLSession Delegate:")
        print(f"File: {solution['url_session_delegate']['filename']}")
        print(solution['url_session_delegate']['description'])
    
    # Check Alamofire fix
    if "alamofire_fix" in solution:
        print("\n4. Alamofire Support:")
        print(f"File: {solution['alamofire_fix']['filename']}")
        print(solution['alamofire_fix']['description'])
    
    # Check Combine fix
    if "combine_fix" in solution:
        print("\n5. Combine Framework Support:")
        print(f"File: {solution['combine_fix']['filename']}")
        print(solution['combine_fix']['description'])
    
    print("\n" + "=" * 60)

def test_apply_comprehensive_fix():
    """Test applying comprehensive SSL fix to project files"""
    print("\nTesting Apply Comprehensive Fix...")
    print("=" * 60)
    
    handler = RobustSSLHandler()
    
    # Sample project files
    test_files = [
        {
            "path": "ContentView.swift",
            "content": """import SwiftUI

struct ContentView: View {
    @StateObject private var viewModel = ContentViewModel()
    
    var body: some View {
        VStack {
            Text("API Data")
            Button("Fetch Data") {
                viewModel.fetchData()
            }
        }
    }
}"""
        },
        {
            "path": "ContentViewModel.swift", 
            "content": """import Foundation

class ContentViewModel: ObservableObject {
    @Published var data: [String] = []
    
    func fetchData() {
        guard let url = URL(string: "https://api.example.com/data") else { return }
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            // Handle response
        }.resume()
    }
}"""
        },
        {
            "path": "Info.plist",
            "content": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>MyApp</string>
</dict>
</plist>"""
        }
    ]
    
    # Apply comprehensive fix
    result = handler.apply_comprehensive_ssl_fix(test_files, "api.example.com")
    
    print(f"Files modified: {len(result['files_modified'])}")
    print(f"Changes made: {len(result['changes_made'])}")
    
    print("\nChanges:")
    for change in result['changes_made']:
        print(f"  - {change}")
    
    print("\nSSL Fixes Applied:")
    for fix_type, applied in result['ssl_fixes_applied'].items():
        print(f"  - {fix_type}: {'✅' if applied else '❌'}")
    
    print("\nModified Files:")
    for file_path in result['files_modified']:
        print(f"  - {file_path}")
    
    # Check if Info.plist was updated
    for file in result['files']:
        if 'Info.plist' in file['path']:
            print("\nUpdated Info.plist preview:")
            print(file['content'][:500] + "...")
            break
    
    print("\n" + "=" * 60)

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Robust SSL Handler Test Suite")
    print("=" * 60 + "\n")
    
    test_comprehensive_ssl_fix()
    test_apply_comprehensive_fix()
    
    print("\nAll tests completed!")
    print("\nKey Features:")
    print("✅ Comprehensive Info.plist configuration")
    print("✅ Custom URLSession with SSL handling")
    print("✅ Development mode SSL bypass")
    print("✅ Automatic SSL error recovery")
    print("✅ Support for Alamofire and Combine")
    print("✅ Multiple fallback strategies")

if __name__ == "__main__":
    main()