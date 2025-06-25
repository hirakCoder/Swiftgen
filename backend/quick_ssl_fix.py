"""
Quick SSL fix for currency converter and API apps
"""
import re


def add_ssl_fix_to_info_plist(content: str) -> str:
    """Add or update NSAppTransportSecurity in Info.plist"""
    
    # Common API domains that need SSL exceptions
    common_domains = [
        "api.exchangerate-api.com",
        "api.exchangeratesapi.io", 
        "api.fixer.io",
        "cdn.jsdelivr.net",
        "api.currencyapi.com",
        "api.frankfurter.app",
        "v6.exchangerate-api.com"
    ]
    
    # Check if NSAppTransportSecurity already exists
    if "NSAppTransportSecurity" in content:
        # Update existing - insert before closing </dict> of NSAppTransportSecurity
        ats_end = content.find("</dict>", content.find("NSAppTransportSecurity"))
        if ats_end > 0:
            # Add exception domains
            domain_entries = []
            for domain in common_domains:
                domain_entries.append(f"""        <key>{domain}</key>
        <dict>
            <key>NSIncludesSubdomains</key>
            <true/>
            <key>NSTemporaryExceptionAllowsInsecureHTTPLoads</key>
            <true/>
            <key>NSTemporaryExceptionMinimumTLSVersion</key>
            <string>TLSv1.0</string>
        </dict>""")
            
            new_content = content[:ats_end] + "\n".join(domain_entries) + "\n    " + content[ats_end:]
            return new_content
    else:
        # Add new NSAppTransportSecurity section before final </dict>
        final_dict = content.rfind("</dict>")
        if final_dict > 0:
            ats_section = """    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSAllowsArbitraryLoads</key>
        <false/>
        <key>NSExceptionDomains</key>
        <dict>"""
            
            for domain in common_domains:
                ats_section += f"""
            <key>{domain}</key>
            <dict>
                <key>NSIncludesSubdomains</key>
                <true/>
                <key>NSTemporaryExceptionAllowsInsecureHTTPLoads</key>
                <true/>
                <key>NSTemporaryExceptionMinimumTLSVersion</key>
                <string>TLSv1.0</string>
            </dict>"""
            
            ats_section += """
        </dict>
    </dict>
"""
            new_content = content[:final_dict] + ats_section + content[final_dict:]
            return new_content
    
    return content


def ensure_currency_api_works(files: list) -> list:
    """Ensure currency converter apps can access APIs"""
    
    modified_files = []
    info_plist_found = False
    
    for file in files:
        if file['path'].endswith('Info.plist'):
            # Fix Info.plist
            file['content'] = add_ssl_fix_to_info_plist(file['content'])
            info_plist_found = True
            modified_files.append(file)
        else:
            modified_files.append(file)
    
    # If no Info.plist, create one
    if not info_plist_found:
        info_plist = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>$(PRODUCT_NAME)</string>
    <key>CFBundleIdentifier</key>
    <string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSAllowsArbitraryLoads</key>
        <false/>
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
            <key>api.frankfurter.app</key>
            <dict>
                <key>NSIncludesSubdomains</key>
                <true/>
                <key>NSTemporaryExceptionAllowsInsecureHTTPLoads</key>
                <true/>
            </dict>
        </dict>
    </dict>
</dict>
</plist>"""
        modified_files.append({
            'path': 'Info.plist',
            'content': info_plist
        })
    
    return modified_files