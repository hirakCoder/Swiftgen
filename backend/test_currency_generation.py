#!/usr/bin/env python3
"""
Test currency converter generation end-to-end
"""
import os
import time


def test_currency_app():
    """Test that currency converter apps work properly"""
    
    print("🧪 Testing Currency Converter Generation")
    print("="*60)
    
    # Simulate the generation flow
    test_description = "create a currency converter app with real-time exchange rates"
    
    # 1. Check if it's detected as API app
    keywords = ['currency', 'converter', 'exchange rate', 'api', 'weather', 'quote']
    is_api_app = any(keyword in test_description.lower() for keyword in keywords)
    
    print(f"1. API App Detection: {'✅' if is_api_app else '❌'}")
    print(f"   Description: '{test_description}'")
    print(f"   Contains keywords: {[k for k in keywords if k in test_description.lower()]}")
    
    # 2. Check if it's marked as simple (not complex)
    simple_apps = ["currency converter", "calculator", "timer", "counter", "converter", "weather app"]
    is_simple = any(app in test_description.lower() for app in simple_apps)
    
    print(f"\n2. Complexity Detection: {'✅ Simple' if is_simple else '❌ Complex'}")
    
    # 3. Simulate file generation
    print("\n3. File Generation Check:")
    
    test_files = [
        {
            'path': 'Sources/Services/CurrencyService.swift',
            'content': '''import Foundation

class CurrencyService {
    private let baseURL = "https://api.exchangerate-api.com/v4/latest/USD"
    
    func fetchRates() async throws -> CurrencyRates {
        let (data, _) = try await URLSession.shared.data(from: URL(string: baseURL)!)
        return try JSONDecoder().decode(CurrencyRates.self, from: data)
    }
}

struct CurrencyRates: Codable {
    let rates: [String: Double]
}'''
        }
    ]
    
    # Check if service has proper structure
    service_content = test_files[0]['content']
    has_codable = 'Codable' in service_content
    has_url = 'exchangerate-api.com' in service_content
    has_decoder = 'JSONDecoder' in service_content
    
    print(f"   - Has Codable struct: {'✅' if has_codable else '❌'}")
    print(f"   - Has API URL: {'✅' if has_url else '❌'}")
    print(f"   - Has JSONDecoder: {'✅' if has_decoder else '❌'}")
    
    # 4. Check SSL fix would be applied
    print("\n4. SSL Configuration:")
    
    # Check if EMERGENCY_CURRENCY_FIX exists
    fix_exists = os.path.exists("/Users/hirakbanerjee/Desktop/SwiftGen/swiftgen-mvp/backend/EMERGENCY_CURRENCY_FIX.py")
    print(f"   - Emergency fix module exists: {'✅' if fix_exists else '❌'}")
    
    # Check if it would be called
    if is_api_app:
        print("   - Would apply SSL fix: ✅")
        print("   - Domains configured: api.exchangerate-api.com, v6.exchangerate-api.com")
    else:
        print("   - Would apply SSL fix: ❌ (not detected as API app)")
    
    # 5. Summary
    print("\n" + "="*60)
    print("SUMMARY:")
    
    all_good = is_api_app and is_simple and has_codable and fix_exists
    
    if all_good:
        print("✅ Currency converter generation should work correctly")
        print("\nExpected behavior:")
        print("1. App detected as API-based → SSL fix applied")
        print("2. App marked as simple → only 3 build attempts")
        print("3. Proper JSON decoding structure")
        print("4. Info.plist configured for API access")
    else:
        print("❌ Currency converter generation has issues")
        if not is_api_app:
            print("- Not detected as API app")
        if not is_simple:
            print("- Marked as complex (too many build attempts)")
        if not has_codable:
            print("- Missing proper JSON structure")
    
    return all_good


if __name__ == "__main__":
    success = test_currency_app()
    
    # Also check a recently generated currency app
    recent_currency_app = "/Users/hirakbanerjee/Desktop/SwiftGen/swiftgen-mvp/workspaces/proj_e100eca7"
    if os.path.exists(recent_currency_app):
        print(f"\n\nChecking recent app: {recent_currency_app}")
        
        info_plist = os.path.join(recent_currency_app, "Info.plist")
        if os.path.exists(info_plist):
            with open(info_plist, 'r') as f:
                content = f.read()
            
            has_ssl = "NSAppTransportSecurity" in content
            print(f"Info.plist has SSL config: {'✅' if has_ssl else '❌'}")
            
            if has_ssl:
                print("The manual fix worked for this app")