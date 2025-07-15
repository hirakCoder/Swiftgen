#!/usr/bin/env python3
"""
SSL Integration Module for SwiftGen
Ensures proper SSL/HTTPS handling for generated iOS apps
"""

import re
import logging
from typing import Dict, List, Tuple
from robust_ssl_handler import RobustSSLHandler


class SSLIntegration:
    """Integrates SSL handling into the app generation pipeline"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ssl_handler = RobustSSLHandler()
        
    def analyze_app_for_https(self, files: Dict[str, str]) -> bool:
        """Check if the app uses HTTPS URLs"""
        https_pattern = r'https://[^\s"\']+'
        api_patterns = [
            r'URLSession',
            r'URLRequest',
            r'\.dataTask',
            r'async.*URL',
            r'try await.*URL'
        ]
        
        for filepath, content in files.items():
            if filepath.endswith('.swift'):
                # Check for HTTPS URLs
                if re.search(https_pattern, content):
                    self.logger.info(f"Found HTTPS URL in {filepath}")
                    return True
                    
                # Check for networking code
                for pattern in api_patterns:
                    if re.search(pattern, content):
                        self.logger.info(f"Found networking code in {filepath}")
                        return True
                        
        return False
    
    def preemptively_add_ssl_support(self, files: Dict[str, str]) -> Dict[str, str]:
        """Add SSL support before any errors occur"""
        
        # Always add ATS configuration for apps with networking
        if self.analyze_app_for_https(files):
            self.logger.info("App uses HTTPS, adding SSL support preemptively")
            
            # Update Info.plist
            info_plist_path = None
            for filepath in files:
                if filepath.endswith('Info.plist'):
                    info_plist_path = filepath
                    break
                    
            if info_plist_path:
                # Add comprehensive ATS settings
                ats_config = """
	<key>NSAppTransportSecurity</key>
	<dict>
		<key>NSAllowsArbitraryLoads</key>
		<false/>
		<key>NSAllowsArbitraryLoadsForMedia</key>
		<false/>
		<key>NSAllowsArbitraryLoadsInWebContent</key>
		<false/>
		<key>NSAllowsLocalNetworking</key>
		<true/>
		<key>NSExceptionDomains</key>
		<dict>
			<key>localhost</key>
			<dict>
				<key>NSExceptionAllowsInsecureHTTPLoads</key>
				<true/>
			</dict>
			<key>api.quotable.io</key>
			<dict>
				<key>NSIncludesSubdomains</key>
				<true/>
				<key>NSExceptionRequiresForwardSecrecy</key>
				<false/>
				<key>NSExceptionMinimumTLSVersion</key>
				<string>TLSv1.2</string>
			</dict>
			<key>api.github.com</key>
			<dict>
				<key>NSIncludesSubdomains</key>
				<true/>
				<key>NSExceptionRequiresForwardSecrecy</key>
				<false/>
			</dict>
		</dict>
	</dict>"""
                
                # Only add if not already present
                if "NSAppTransportSecurity" not in files[info_plist_path]:
                    files[info_plist_path] = files[info_plist_path].replace(
                        "</dict>\n</plist>",
                        f"{ats_config}\n</dict>\n</plist>"
                    )
                    self.logger.info("Added ATS configuration to Info.plist")
                    
            # Add SSL session configuration to networking files
            self._add_ssl_session_configuration(files)
                    
        return files
    
    def _add_ssl_session_configuration(self, files: Dict[str, str]) -> None:
        """Add proper SSL session configuration to networking code"""
        
        for filepath, content in files.items():
            if filepath.endswith('.swift') and ('URLSession' in content or 'https://' in content):
                
                # Check if we need to add SSL configuration
                if 'URLSession.shared' in content and 'URLSessionConfiguration' not in content:
                    
                    # Add a properly configured URLSession
                    ssl_session_code = """
    // MARK: - SSL Configured URLSession
    private let sslConfiguredSession: URLSession = {
        let configuration = URLSessionConfiguration.default
        configuration.timeoutIntervalForRequest = 30.0
        configuration.timeoutIntervalForResource = 60.0
        configuration.waitsForConnectivity = true
        configuration.allowsCellularAccess = true
        configuration.httpShouldSetCookies = true
        configuration.httpCookieAcceptPolicy = .always
        
        // Enable HTTP/2
        configuration.multipathServiceType = .none
        
        // Cache policy
        configuration.requestCachePolicy = .useProtocolCachePolicy
        configuration.urlCache = URLCache.shared
        
        return URLSession(configuration: configuration)
    }()
"""
                    
                    # Replace URLSession.shared with our configured session
                    updated_content = content.replace('URLSession.shared', 'sslConfiguredSession')
                    
                    # Add the session configuration before the first use
                    if 'sslConfiguredSession' in updated_content and ssl_session_code not in updated_content:
                        # Find a good insertion point (after imports, before first class/struct)
                        lines = updated_content.split('\n')
                        insert_index = 0
                        
                        for i, line in enumerate(lines):
                            if line.strip().startswith('import '):
                                insert_index = i + 1
                            elif line.strip().startswith('class ') or line.strip().startswith('struct '):
                                break
                                
                        lines.insert(insert_index, ssl_session_code)
                        updated_content = '\n'.join(lines)
                        files[filepath] = updated_content
                        self.logger.info(f"Added SSL session configuration to {filepath}")
    
    def handle_ssl_error(self, error_message: str, files: Dict[str, str], project_path: str) -> Tuple[bool, Dict[str, str]]:
        """Handle SSL errors during build or runtime"""
        
        # Use the robust SSL handler
        success, updated_files, message = self.ssl_handler.analyze_and_fix(
            project_path, error_message, files
        )
        
        if success:
            self.logger.info(f"SSL error fixed: {message}")
        else:
            self.logger.warning(f"Unable to fix SSL error: {message}")
            
        return success, updated_files
    
    def get_ssl_recommendations(self, app_description: str) -> List[str]:
        """Get SSL recommendations based on app description"""
        recommendations = []
        
        # Check for API usage patterns
        api_keywords = ['api', 'fetch', 'download', 'web service', 'rest', 'json', 'quote', 'weather', 'news']
        
        if any(keyword in app_description.lower() for keyword in api_keywords):
            recommendations.extend([
                "Configure NSAppTransportSecurity in Info.plist",
                "Use HTTPS for all API calls",
                "Handle SSL certificate validation properly",
                "Consider certificate pinning for sensitive data"
            ])
            
        return recommendations


# Singleton instance
ssl_integration = SSLIntegration()