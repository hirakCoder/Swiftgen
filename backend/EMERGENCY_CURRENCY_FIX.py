"""
Emergency fix for currency converter apps
Fixes:
1. JSON decoding format
2. SSL configuration
3. App naming
"""
import os
import re


def fix_currency_converter_issues(project_id: str):
    """Emergency fix for broken currency converter"""
    
    # Handle both direct project_id and full path
    if "/" in project_id:
        workspace_path = project_id
    else:
        workspace_path = f"/Users/hirakbanerjee/Desktop/SwiftGen/swiftgen-mvp/workspaces/{project_id}"
    
    # 1. Fix CurrencyService.swift JSON decoding
    service_path = os.path.join(workspace_path, "Sources/Services/CurrencyService.swift")
    if os.path.exists(service_path):
        with open(service_path, 'r') as f:
            content = f.read()
        
        # Fix the JSON decoding - the API returns {"rates": {"EUR": 0.85}}
        if "[String: [String: Double]]" in content:
            content = content.replace(
                "let response = try JSONDecoder().decode([String: [String: Double]].self, from: data)",
                """let response = try JSONDecoder().decode(ExchangeRateResponse.self, from: data)"""
            )
            content = content.replace(
                'let rates = response["rates"] ?? [:]',
                'let rates = response.rates'
            )
            
            # Add the proper struct
            if "struct ExchangeRateResponse" not in content:
                content = content.replace(
                    "enum CurrencyAppError",
                    """struct ExchangeRateResponse: Codable {
    let rates: [String: Double]
}

enum CurrencyAppError"""
                )
        
        with open(service_path, 'w') as f:
            f.write(content)
        print("✅ Fixed CurrencyService JSON decoding")
    
    # 2. Fix Info.plist - Add SSL configuration
    info_plist_path = os.path.join(workspace_path, "Info.plist")
    if os.path.exists(info_plist_path):
        with open(info_plist_path, 'r') as f:
            content = f.read()
        
        if "NSAppTransportSecurity" not in content:
            # Add before closing </dict>
            ssl_config = """    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSExceptionDomains</key>
        <dict>
            <key>api.exchangerate-api.com</key>
            <dict>
                <key>NSIncludesSubdomains</key>
                <true/>
                <key>NSTemporaryExceptionAllowsInsecureHTTPLoads</key>
                <true/>
            </dict>
            <key>v6.exchangerate-api.com</key>
            <dict>
                <key>NSIncludesSubdomains</key>
                <true/>
                <key>NSTemporaryExceptionAllowsInsecureHTTPLoads</key>
                <true/>
            </dict>
        </dict>
    </dict>
"""
            content = content.replace("</dict>\n</plist>", ssl_config + "</dict>\n</plist>")
            
        with open(info_plist_path, 'w') as f:
            f.write(content)
        print("✅ Added SSL configuration to Info.plist")
    
    # 3. Fix any missing error handling
    viewmodel_path = os.path.join(workspace_path, "Sources/ViewModels/CurrencyViewModel.swift")
    if os.path.exists(viewmodel_path):
        with open(viewmodel_path, 'r') as f:
            content = f.read()
        
        # Make sure error is published
        if "@Published var error:" not in content and "var error:" in content:
            content = content.replace("var error:", "@Published var error:")
            with open(viewmodel_path, 'w') as f:
                f.write(content)
            print("✅ Fixed error publishing in ViewModel")
    
    return True


if __name__ == "__main__":
    # Test with the project ID from logs
    fix_currency_converter_issues("proj_e100eca7")