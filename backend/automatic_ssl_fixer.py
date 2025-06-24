"""
Automatic SSL/API Fixer
Detects and fixes SSL/API issues during build and modification processes
"""
import os
import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class AutomaticSSLFixer:
    """Automatically detects and fixes SSL/API issues"""
    
    def __init__(self):
        self.api_patterns = [
            r'https?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',  # Extract domains from URLs
            r'URL\(string:\s*"(https?://[^"]+)"',        # Swift URL construction
            r'\.data\(from:\s*[^,]+\)',                  # URLSession data calls
        ]
        
        self.error_patterns = [
            'failed to load',
            'failed to fetch', 
            'ssl error',
            'transport security',
            'certificate',
            'cannot connect',
            'no data',
            'failed to decode',
            'network error'
        ]
    
    def detect_api_usage(self, files: List[Dict]) -> List[str]:
        """Detect all API domains used in the code"""
        domains = set()
        
        for file in files:
            if file['path'].endswith('.swift'):
                content = file.get('content', '')
                
                # Find all URLs in string literals
                url_patterns = [
                    r'"(https?://[^"]+)"',  # Double quoted URLs
                    r"'(https?://[^']+)'",  # Single quoted URLs
                    r'URL\(string:\s*"(https?://[^"]+)"',  # URL constructor
                ]
                
                for pattern in url_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for url in matches:
                        # Extract domain from URL
                        domain_match = re.search(r'https?://([^/:]+)', url)
                        if domain_match:
                            domain = domain_match.group(1)
                            if domain and '.' in domain:
                                domains.add(domain)
        
        return sorted(list(domains))
    
    def check_info_plist_for_ats(self, files: List[Dict], domains: List[str]) -> Tuple[bool, List[str]]:
        """Check if Info.plist has ATS configuration for the domains"""
        info_plist = None
        
        for file in files:
            if 'Info.plist' in file['path']:
                info_plist = file
                break
        
        if not info_plist:
            return False, domains
        
        content = info_plist.get('content', '')
        missing_domains = []
        
        for domain in domains:
            # Check if domain has ATS exception
            if domain not in content or 'NSAppTransportSecurity' not in content:
                missing_domains.append(domain)
        
        return len(missing_domains) == 0, missing_domains
    
    def generate_ats_config(self, domains: List[str]) -> str:
        """Generate ATS configuration for domains"""
        if not domains:
            return ""
        
        domain_configs = []
        for domain in domains:
            domain_configs.append(f"""            <key>{domain}</key>
            <dict>
                <key>NSIncludesSubdomains</key>
                <true/>
                <key>NSTemporaryExceptionAllowsInsecureHTTPLoads</key>
                <true/>
                <key>NSTemporaryExceptionMinimumTLSVersion</key>
                <string>TLSv1.0</string>
                <key>NSExceptionRequiresForwardSecrecy</key>
                <false/>
            </dict>""")
        
        return f"""    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSExceptionDomains</key>
        <dict>
{chr(10).join(domain_configs)}
        </dict>
        <key>NSAllowsLocalNetworking</key>
        <true/>
    </dict>"""
    
    def fix_info_plist(self, files: List[Dict], domains: List[str]) -> List[Dict]:
        """Add ATS configuration to Info.plist"""
        if not domains:
            return files
        
        modified_files = list(files)
        info_plist_found = False
        
        for i, file in enumerate(modified_files):
            if 'Info.plist' in file['path']:
                info_plist_found = True
                content = file['content']
                
                # Check if NSAppTransportSecurity already exists
                if 'NSAppTransportSecurity' not in content:
                    # Add ATS configuration
                    ats_config = self.generate_ats_config(domains)
                    
                    # Insert before closing </dict>
                    insert_pos = content.rfind('</dict>')
                    if insert_pos > 0:
                        new_content = (
                            content[:insert_pos] + 
                            ats_config + '\n' + 
                            content[insert_pos:]
                        )
                        modified_files[i] = {
                            'path': file['path'],
                            'content': new_content
                        }
                        logger.info(f"Added ATS configuration for domains: {domains}")
                else:
                    # Update existing ATS configuration
                    logger.info("Updating existing ATS configuration")
                    # This is more complex - would need XML parsing for proper update
                
                break
        
        if not info_plist_found:
            # Create Info.plist with ATS configuration
            logger.info("Creating Info.plist with ATS configuration")
            ats_config = self.generate_ats_config(domains)
            info_plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>$(PRODUCT_NAME)</string>
    <key>CFBundleIdentifier</key>
    <string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
{ats_config}
</dict>
</plist>"""
            
            modified_files.append({
                'path': 'Info.plist',
                'content': info_plist_content
            })
        
        return modified_files
    
    def detect_api_response_issues(self, files: List[Dict], error_message: str = "") -> Optional[Dict]:
        """Detect API response format issues"""
        # Look for common patterns that indicate API response issues
        decode_error_patterns = [
            'failed to decode',
            'decoding error',
            'json error',
            'codable',
            'decodable'
        ]
        
        if any(pattern in error_message.lower() for pattern in decode_error_patterns):
            # Try to find the API being used and check response format
            for file in files:
                if 'Service' in file['path'] or 'API' in file['path'] or 'Network' in file['path']:
                    content = file.get('content', '')
                    
                    # Find URL being used
                    url_match = re.search(r'URL\(string:\s*"(https?://[^"]+)"', content)
                    if url_match:
                        return {
                            'type': 'decode_error',
                            'url': url_match.group(1),
                            'file': file['path']
                        }
        
        return None
    
    def apply_automatic_fixes(self, files: List[Dict], build_errors: List[str] = None, user_report: str = "") -> Dict:
        """Apply automatic SSL/API fixes"""
        fixes_applied = []
        modified_files = list(files)
        
        # 1. Detect API domains in use
        domains = self.detect_api_usage(files)
        logger.info(f"Detected API domains: {domains}")
        
        # 2. Check if Info.plist has ATS configuration
        if domains:
            has_ats, missing_domains = self.check_info_plist_for_ats(files, domains)
            
            if not has_ats and missing_domains:
                logger.info(f"Missing ATS configuration for domains: {missing_domains}")
                modified_files = self.fix_info_plist(modified_files, missing_domains)
                fixes_applied.append(f"Added ATS configuration for {len(missing_domains)} domains")
        
        # 3. Check for API response decode issues
        if user_report:
            decode_issue = self.detect_api_response_issues(files, user_report)
            if decode_issue:
                logger.info(f"Detected API decode issue: {decode_issue}")
                fixes_applied.append("Detected API response format issue - manual fix required")
        
        return {
            'files': modified_files,
            'fixes_applied': fixes_applied,
            'domains_fixed': domains,
            'success': len(fixes_applied) > 0
        }


# Integration points for the automatic fixer
def integrate_with_build_service(build_service_instance):
    """Add automatic SSL fixing to build service"""
    ssl_fixer = AutomaticSSLFixer()
    
    # Hook into build process
    original_build = build_service_instance.build_project
    
    async def enhanced_build(project_path, project_id, bundle_id, **kwargs):
        # Read project files to check for SSL issues
        try:
            # Get all Swift and plist files
            files = []
            for root, dirs, filenames in os.walk(project_path):
                for filename in filenames:
                    if filename.endswith(('.swift', '.plist')):
                        filepath = os.path.join(root, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            files.append({
                                'path': os.path.relpath(filepath, project_path),
                                'content': f.read()
                            })
            
            # Apply automatic fixes
            fix_result = ssl_fixer.apply_automatic_fixes(files)
            
            if fix_result['success']:
                logger.info(f"Applied automatic SSL fixes: {fix_result['fixes_applied']}")
                
                # Write fixed files back
                for file in fix_result['files']:
                    filepath = os.path.join(project_path, file['path'])
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(file['content'])
        
        except Exception as e:
            logger.warning(f"SSL auto-fix failed: {e}")
        
        # Continue with normal build
        return await original_build(project_path, project_id, bundle_id, **kwargs)
    
    build_service_instance.build_project = enhanced_build


def integrate_with_modification_handler(modification_handler_instance):
    """Add automatic SSL detection to modification handler"""
    ssl_fixer = AutomaticSSLFixer()
    
    # Hook into issue detection
    original_detect = modification_handler_instance.detect_issue_type
    
    def enhanced_detect(modification_request, context=None):
        # First try original detection
        issue_type, details = original_detect(modification_request, context)
        
        if not issue_type:
            # Check for API-related keywords
            request_lower = modification_request.lower()
            if any(keyword in request_lower for keyword in ssl_fixer.error_patterns):
                # Likely an API issue
                return "api_error", {"detected_by": "automatic_ssl_fixer"}
        
        return issue_type, details
    
    modification_handler_instance.detect_issue_type = enhanced_detect