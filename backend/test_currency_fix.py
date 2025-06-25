"""
Test that currency converter SSL fix works
"""
from quick_ssl_fix import ensure_currency_api_works


def test_currency_ssl_fix():
    """Test SSL fix for currency converter"""
    
    # Simulate files from a currency converter app
    test_files = [
        {
            'path': 'Sources/CurrencyService.swift',
            'content': '''import Foundation

class CurrencyService {
    let apiURL = "https://api.exchangerate-api.com/v4/latest/USD"
    
    func fetchRates() async throws -> ExchangeRates {
        guard let url = URL(string: apiURL) else { throw APIError.invalidURL }
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode(ExchangeRates.self, from: data)
    }
}'''
        },
        {
            'path': 'Sources/ContentView.swift', 
            'content': 'import SwiftUI\n\nstruct ContentView: View { var body: some View { Text("Currency Converter") } }'
        }
    ]
    
    # Apply fix
    fixed_files = ensure_currency_api_works(test_files)
    
    # Check that Info.plist was added
    info_plist = None
    for file in fixed_files:
        if file['path'] == 'Info.plist':
            info_plist = file
            break
    
    assert info_plist is not None, "Info.plist should be created"
    assert 'NSAppTransportSecurity' in info_plist['content'], "Should have ATS config"
    assert 'api.exchangerate-api.com' in info_plist['content'], "Should have API domain"
    
    print("✅ Currency SSL fix test passed!")
    print(f"Created Info.plist with {len(info_plist['content'])} bytes")
    
    # Check if common domains are included
    common_domains = ['exchangerate-api.com', 'frankfurter.app']
    for domain in common_domains:
        if domain in info_plist['content']:
            print(f"  ✓ {domain} configured")


if __name__ == "__main__":
    test_currency_ssl_fix()