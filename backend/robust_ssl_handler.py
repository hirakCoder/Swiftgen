#!/usr/bin/env python3
"""
Robust SSL/Certificate Handler for SwiftGen
Comprehensive solution for handling SSL/certificate errors in iOS app generation
"""

import os
import re
import ssl
import certifi
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import subprocess


class RobustSSLHandler:
    """Handles SSL/Certificate errors for iOS app generation"""
    
    def __init__(self):
        """Initialize SSL handler with comprehensive error patterns"""
        self.logger = logging.getLogger(__name__)
        
        # SSL error patterns and solutions
        self.ssl_error_patterns = {
            # Certificate verification errors
            r"certificate verify failed": {
                "type": "cert_verification",
                "solutions": [
                    self._add_ats_exception,
                    self._add_certificate_pinning_bypass,
                    self._update_info_plist_security
                ]
            },
            # Self-signed certificate errors
            r"self(-|\s)?signed certificate": {
                "type": "self_signed",
                "solutions": [
                    self._allow_self_signed_certificates,
                    self._add_local_development_exception
                ]
            },
            # SSL handshake errors
            r"SSL handshake failed|SSLError": {
                "type": "handshake",
                "solutions": [
                    self._update_tls_version,
                    self._add_custom_ssl_context
                ]
            },
            # Certificate expired
            r"certificate.*expired": {
                "type": "expired",
                "solutions": [
                    self._bypass_certificate_validation,
                    self._add_date_bypass
                ]
            },
            # Hostname mismatch
            r"hostname.*doesn't match": {
                "type": "hostname",
                "solutions": [
                    self._disable_hostname_verification,
                    self._add_custom_hostname_validation
                ]
            },
            # ATS (App Transport Security) errors
            r"App Transport Security|ATS|NSURLSession.*error": {
                "type": "ats",
                "solutions": [
                    self._configure_ats_exceptions,
                    self._add_domain_exceptions
                ]
            }
        }
        
        # Track attempted fixes
        self.attempted_fixes = set()
        
        # iOS minimum version for features
        self.ios_min_version = "16.0"
    
    def detect_ssl_error(self, error_message: str) -> Optional[Dict]:
        """Detect SSL/certificate errors in build output"""
        for pattern, info in self.ssl_error_patterns.items():
            if re.search(pattern, error_message, re.IGNORECASE):
                self.logger.info(f"Detected SSL error type: {info['type']}")
                return info
        return None
    
    def fix_ssl_error(self, project_path: str, error_message: str, files: Dict[str, str]) -> Tuple[bool, Dict[str, str]]:
        """Apply SSL/certificate fixes to the project"""
        error_info = self.detect_ssl_error(error_message)
        if not error_info:
            return False, files
        
        self.logger.info(f"Attempting to fix SSL error type: {error_info['type']}")
        
        # Try each solution for this error type
        for solution in error_info['solutions']:
            fix_id = f"{error_info['type']}_{solution.__name__}"
            if fix_id in self.attempted_fixes:
                continue
            
            self.attempted_fixes.add(fix_id)
            
            try:
                success, updated_files = solution(project_path, files, error_message)
                if success:
                    self.logger.info(f"Successfully applied fix: {solution.__name__}")
                    return True, updated_files
            except Exception as e:
                self.logger.warning(f"Failed to apply {solution.__name__}: {e}")
        
        return False, files
    
    def _add_ats_exception(self, project_path: str, files: Dict[str, str], error_message: str) -> Tuple[bool, Dict[str, str]]:
        """Add App Transport Security exceptions to Info.plist"""
        info_plist_path = f"{project_path}/Info.plist"
        
        if info_plist_path not in files:
            return False, files
        
        # Check if we already have ATS exceptions
        if "NSAppTransportSecurity" in files[info_plist_path]:
            return False, files
        
        # Add comprehensive ATS exceptions
        ats_config = """
	<key>NSAppTransportSecurity</key>
	<dict>
		<key>NSAllowsArbitraryLoads</key>
		<true/>
		<key>NSAllowsArbitraryLoadsForMedia</key>
		<true/>
		<key>NSAllowsArbitraryLoadsInWebContent</key>
		<true/>
		<key>NSAllowsLocalNetworking</key>
		<true/>
		<key>NSExceptionDomains</key>
		<dict>
			<key>localhost</key>
			<dict>
				<key>NSExceptionAllowsInsecureHTTPLoads</key>
				<true/>
			</dict>
		</dict>
	</dict>"""
        
        # Insert before closing </dict>
        updated_plist = files[info_plist_path].replace(
            "</dict>\n</plist>",
            f"{ats_config}\n</dict>\n</plist>"
        )
        
        files[info_plist_path] = updated_plist
        return True, files
    
    def _add_certificate_pinning_bypass(self, project_path: str, files: Dict[str, str], error_message: str) -> Tuple[bool, Dict[str, str]]:
        """Add certificate pinning bypass for development"""
        # Find the main networking file
        networking_files = [f for f in files if "Network" in f or "API" in f]
        
        if not networking_files:
            return False, files
        
        target_file = networking_files[0]
        content = files[target_file]
        
        # Add URLSession delegate for certificate handling
        cert_bypass_code = """
    // MARK: - SSL Certificate Bypass for Development
    extension URLSession {
        static var allowingSelfSignedCertificate: URLSession {
            let configuration = URLSessionConfiguration.default
            let delegate = SelfSignedCertificateDelegate()
            return URLSession(configuration: configuration, delegate: delegate, delegateQueue: nil)
        }
    }
    
    class SelfSignedCertificateDelegate: NSObject, URLSessionDelegate {
        func urlSession(_ session: URLSession, didReceive challenge: URLAuthenticationChallenge, 
                       completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
            if challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust {
                if let serverTrust = challenge.protectionSpace.serverTrust {
                    let credential = URLCredential(trust: serverTrust)
                    completionHandler(.useCredential, credential)
                    return
                }
            }
            completionHandler(.performDefaultHandling, nil)
        }
    }
"""
        
        # Add if not already present
        if "SelfSignedCertificateDelegate" not in content:
            files[target_file] = content + cert_bypass_code
            return True, files
        
        return False, files
    
    def _update_info_plist_security(self, project_path: str, files: Dict[str, str], error_message: str) -> Tuple[bool, Dict[str, str]]:
        """Update Info.plist with comprehensive security settings"""
        info_plist_path = f"{project_path}/Info.plist"
        
        if info_plist_path not in files:
            return False, files
        
        content = files[info_plist_path]
        
        # Extract domain from error if possible
        domain_match = re.search(r'https?://([^/]+)', error_message)
        domain = domain_match.group(1) if domain_match else "api.example.com"
        
        # Add specific domain exception
        domain_exception = f"""
		<key>{domain}</key>
		<dict>
			<key>NSIncludesSubdomains</key>
			<true/>
			<key>NSExceptionAllowsInsecureHTTPLoads</key>
			<true/>
			<key>NSExceptionRequiresForwardSecrecy</key>
			<false/>
			<key>NSExceptionMinimumTLSVersion</key>
			<string>TLSv1.0</string>
		</dict>"""
        
        # Check if we need to add this domain
        if domain not in content and "NSExceptionDomains" in content:
            # Insert new domain into existing NSExceptionDomains
            content = content.replace(
                "<key>NSExceptionDomains</key>\n\t\t<dict>",
                f"<key>NSExceptionDomains</key>\n\t\t<dict>{domain_exception}"
            )
            files[info_plist_path] = content
            return True, files
        
        return False, files
    
    def _allow_self_signed_certificates(self, project_path: str, files: Dict[str, str], error_message: str) -> Tuple[bool, Dict[str, str]]:
        """Configure URLSession to allow self-signed certificates"""
        # Find ContentView or main app file
        app_files = [f for f in files if "ContentView" in f or "App.swift" in f]
        
        if not app_files:
            return False, files
        
        target_file = app_files[0]
        content = files[target_file]
        
        # Add URLSession configuration
        ssl_config = """
    // Configure URLSession for development
    private func configureURLSession() {
        URLSession.shared.configuration.urlCache = URLCache.shared
        URLSession.shared.configuration.requestCachePolicy = .reloadIgnoringLocalCacheData
        
        // Allow self-signed certificates in DEBUG mode
        #if DEBUG
        URLSession.shared.configuration.tlsMinimumSupportedProtocolVersion = .TLSv10
        #endif
    }
"""
        
        # Add if not present
        if "configureURLSession" not in content:
            # Find a good insertion point
            if "struct ContentView" in content:
                content = content.replace(
                    "struct ContentView: View {",
                    f"struct ContentView: View {{{ssl_config}"
                )
                files[target_file] = content
                return True, files
        
        return False, files
    
    def _add_local_development_exception(self, project_path: str, files: Dict[str, str], error_message: str) -> Tuple[bool, Dict[str, str]]:
        """Add exceptions for local development servers"""
        info_plist_path = f"{project_path}/Info.plist"
        
        if info_plist_path not in files:
            return False, files
        
        content = files[info_plist_path]
        
        # Add local development domains
        local_domains = ["localhost", "127.0.0.1", "0.0.0.0", "*.local"]
        
        for domain in local_domains:
            if domain not in content:
                domain_config = f"""
		<key>{domain}</key>
		<dict>
			<key>NSExceptionAllowsInsecureHTTPLoads</key>
			<true/>
			<key>NSIncludesSubdomains</key>
			<true/>
		</dict>"""
                
                if "NSExceptionDomains" in content:
                    content = content.replace(
                        "<key>NSExceptionDomains</key>\n\t\t<dict>",
                        f"<key>NSExceptionDomains</key>\n\t\t<dict>{domain_config}"
                    )
        
        if content != files[info_plist_path]:
            files[info_plist_path] = content
            return True, files
        
        return False, files
    
    def _update_tls_version(self, project_path: str, files: Dict[str, str], error_message: str) -> Tuple[bool, Dict[str, str]]:
        """Update TLS version requirements"""
        info_plist_path = f"{project_path}/Info.plist"
        
        if info_plist_path not in files:
            return False, files
        
        content = files[info_plist_path]
        
        # Update minimum TLS version
        if "NSExceptionMinimumTLSVersion" in content:
            content = re.sub(
                r'<key>NSExceptionMinimumTLSVersion</key>\s*<string>TLSv\d+\.\d+</string>',
                '<key>NSExceptionMinimumTLSVersion</key>\n\t\t\t<string>TLSv1.0</string>',
                content
            )
            files[info_plist_path] = content
            return True, files
        
        return False, files
    
    def _add_custom_ssl_context(self, project_path: str, files: Dict[str, str], error_message: str) -> Tuple[bool, Dict[str, str]]:
        """Add custom SSL context for advanced certificate handling"""
        # Find networking files
        networking_files = [f for f in files if "Network" in f or "API" in f or "Service" in f]
        
        if not networking_files:
            return False, files
        
        target_file = networking_files[0]
        content = files[target_file]
        
        ssl_context = """
    // Custom SSL Context Handler
    class SSLContextHandler {
        static func createTrustAllCertificatesSession() -> URLSession {
            let configuration = URLSessionConfiguration.default
            configuration.timeoutIntervalForRequest = 30.0
            configuration.timeoutIntervalForResource = 60.0
            
            return URLSession(configuration: configuration, delegate: TrustAllCertificatesDelegate(), delegateQueue: nil)
        }
    }
    
    class TrustAllCertificatesDelegate: NSObject, URLSessionDelegate {
        func urlSession(_ session: URLSession, didReceive challenge: URLAuthenticationChallenge, 
                       completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
            guard challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust,
                  let serverTrust = challenge.protectionSpace.serverTrust else {
                completionHandler(.performDefaultHandling, nil)
                return
            }
            
            let credential = URLCredential(trust: serverTrust)
            completionHandler(.useCredential, credential)
        }
    }
"""
        
        if "SSLContextHandler" not in content:
            files[target_file] = content + ssl_context
            return True, files
        
        return False, files
    
    def _bypass_certificate_validation(self, project_path: str, files: Dict[str, str], error_message: str) -> Tuple[bool, Dict[str, str]]:
        """Bypass certificate validation for expired certificates"""
        return self._add_custom_ssl_context(project_path, files, error_message)
    
    def _add_date_bypass(self, project_path: str, files: Dict[str, str], error_message: str) -> Tuple[bool, Dict[str, str]]:
        """Add date bypass for expired certificates"""
        # This is handled by the custom SSL context
        return False, files
    
    def _disable_hostname_verification(self, project_path: str, files: Dict[str, str], error_message: str) -> Tuple[bool, Dict[str, str]]:
        """Disable hostname verification for development"""
        return self._add_custom_ssl_context(project_path, files, error_message)
    
    def _add_custom_hostname_validation(self, project_path: str, files: Dict[str, str], error_message: str) -> Tuple[bool, Dict[str, str]]:
        """Add custom hostname validation logic"""
        # This is handled by the custom SSL context
        return False, files
    
    def _configure_ats_exceptions(self, project_path: str, files: Dict[str, str], error_message: str) -> Tuple[bool, Dict[str, str]]:
        """Configure comprehensive ATS exceptions"""
        return self._add_ats_exception(project_path, files, error_message)
    
    def _add_domain_exceptions(self, project_path: str, files: Dict[str, str], error_message: str) -> Tuple[bool, Dict[str, str]]:
        """Add specific domain exceptions based on error"""
        return self._update_info_plist_security(project_path, files, error_message)
    
    def analyze_and_fix(self, project_path: str, error_message: str, files: Dict[str, str]) -> Tuple[bool, Dict[str, str], str]:
        """Main entry point for SSL error analysis and fixing"""
        self.logger.info("Analyzing SSL/Certificate error...")
        
        # Reset attempted fixes for new error
        self.attempted_fixes.clear()
        
        # Try to fix the error
        success, updated_files = self.fix_ssl_error(project_path, error_message, files)
        
        if success:
            message = "Successfully applied SSL/certificate fix"
            self.logger.info(message)
        else:
            message = "Unable to automatically fix SSL/certificate error"
            self.logger.warning(message)
        
        return success, updated_files, message
    
    def get_ssl_recommendations(self, error_message: str) -> List[str]:
        """Get recommendations for SSL/certificate issues"""
        recommendations = []
        
        error_info = self.detect_ssl_error(error_message)
        if not error_info:
            return recommendations
        
        if error_info['type'] == 'cert_verification':
            recommendations.extend([
                "Add the domain to NSExceptionDomains in Info.plist",
                "Ensure the server certificate is valid and not self-signed",
                "For development, consider using NSAllowsArbitraryLoads temporarily"
            ])
        elif error_info['type'] == 'self_signed':
            recommendations.extend([
                "For production, use a valid SSL certificate",
                "For development, add certificate exception handling",
                "Consider using a local certificate authority for testing"
            ])
        elif error_info['type'] == 'handshake':
            recommendations.extend([
                "Check if the server supports TLS 1.2 or higher",
                "Verify the cipher suites are compatible",
                "Ensure the server certificate chain is complete"
            ])
        elif error_info['type'] == 'expired':
            recommendations.extend([
                "Renew the server certificate",
                "For testing, bypass certificate date validation",
                "Check system date/time settings"
            ])
        elif error_info['type'] == 'hostname':
            recommendations.extend([
                "Ensure the certificate CN or SAN matches the hostname",
                "Use the correct hostname in your API calls",
                "For development, consider using custom hostname validation"
            ])
        elif error_info['type'] == 'ats':
            recommendations.extend([
                "Configure NSAppTransportSecurity in Info.plist",
                "Use HTTPS for all network requests",
                "Add specific domain exceptions rather than NSAllowsArbitraryLoads"
            ])
        
        return recommendations