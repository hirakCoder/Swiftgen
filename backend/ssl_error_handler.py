"""
SSL Error Handler for iOS Applications

This module detects SSL-related errors in iOS build logs and user requests,
provides appropriate fixes, and verifies if fixes were applied successfully.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class SSLErrorHandler:
    """Handles SSL/TLS errors specific to iOS applications."""
    
    # Common SSL error patterns in iOS
    SSL_ERROR_PATTERNS = [
        # NSURLErrorDomain errors
        r"NSURLErrorDomain.*code\s*=\s*-1200",  # NSURLErrorSecureConnectionFailed
        r"NSURLErrorDomain.*code\s*=\s*-1202",  # NSURLErrorServerCertificateUntrusted
        r"NSURLErrorDomain.*code\s*=\s*-1004",  # NSURLErrorCannotConnectToHost (often SSL)
        
        # App Transport Security errors
        r"App Transport Security.*blocked.*cleartext",
        r"ATS.*blocked.*HTTP.*resource",
        r"NSAppTransportSecurity.*required",
        r"Transport security.*blocked.*insecure",
        
        # Certificate errors
        r"certificate.*invalid|untrusted|expired",
        r"SSL.*handshake.*failed",
        r"TLS.*connection.*failed",
        r"SecTrust.*evaluation.*failed",
        
        # Common error messages
        r"The certificate for this server is invalid",
        r"An SSL error has occurred",
        r"Could not establish a secure connection",
        r"HTTP load failed.*App Transport Security",
        
        # URLSession errors
        r"URLSession.*SSL.*error",
        r"dataTask.*SSL.*failed",
        r"URLError.*SSL",
    ]
    
    # Info.plist ATS configuration template
    INFO_PLIST_ATS_TEMPLATE = """    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSAllowsArbitraryLoads</key>
        <true/>
        <key>NSExceptionDomains</key>
        <dict>
            <key>{domain}</key>
            <dict>
                <key>NSIncludesSubdomains</key>
                <true/>
                <key>NSTemporaryExceptionAllowsInsecureHTTPLoads</key>
                <true/>
                <key>NSTemporaryExceptionMinimumTLSVersion</key>
                <string>TLSv1.0</string>
            </dict>
        </dict>
    </dict>"""
    
    def __init__(self):
        self.attempted_fixes = []
        self.successful_fixes = []
        
    def detect_ssl_error(self, content: str) -> Tuple[bool, List[str]]:
        """
        Detect SSL errors in build logs or error messages.
        
        Returns:
            Tuple of (has_ssl_error, list_of_matched_patterns)
        """
        matched_patterns = []
        content_lower = content.lower()
        
        for pattern in self.SSL_ERROR_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                matched_patterns.append(pattern)
                
        # Also check for common SSL-related terms
        ssl_keywords = ['ssl', 'tls', 'https', 'certificate', 'transport security', 'ats']
        if any(keyword in content_lower for keyword in ssl_keywords):
            if 'error' in content_lower or 'failed' in content_lower or 'blocked' in content_lower:
                matched_patterns.append("SSL/TLS keyword with error indicator")
                
        return len(matched_patterns) > 0, matched_patterns
    
    def analyze_ssl_issue(self, content: str, project_path: str) -> Dict[str, any]:
        """
        Analyze the SSL issue and determine the best fix approach.
        
        Returns:
            Dictionary with analysis results and recommended fixes
        """
        has_error, patterns = self.detect_ssl_error(content)
        
        if not has_error:
            return {
                "has_ssl_error": False,
                "patterns": [],
                "recommended_fixes": []
            }
            
        # Extract domain if possible
        domain = self._extract_domain(content)
        
        # Check current Info.plist status
        info_plist_status = self._check_info_plist(project_path)
        
        # Determine recommended fixes based on the error type
        recommended_fixes = []
        
        # Check if it's an HTTP vs HTTPS issue
        if any('cleartext' in p.lower() or 'http' in p.lower() for p in patterns):
            recommended_fixes.append({
                "type": "upgrade_to_https",
                "description": "Upgrade HTTP URLs to HTTPS",
                "priority": 1
            })
            
        # Check if it's an ATS issue
        if any('transport security' in p.lower() or 'ats' in p.lower() for p in patterns):
            if not info_plist_status["has_ats_config"]:
                recommended_fixes.append({
                    "type": "add_ats_exception",
                    "description": "Add App Transport Security exception to Info.plist",
                    "priority": 2,
                    "domain": domain
                })
            else:
                recommended_fixes.append({
                    "type": "modify_ats_config",
                    "description": "Modify existing ATS configuration",
                    "priority": 2,
                    "domain": domain
                })
                
        # Check if it's a certificate issue
        if any('certificate' in p.lower() or 'trust' in p.lower() for p in patterns):
            recommended_fixes.append({
                "type": "implement_cert_validation",
                "description": "Implement custom certificate validation",
                "priority": 3
            })
            
        return {
            "has_ssl_error": True,
            "patterns": patterns,
            "domain": domain,
            "info_plist_status": info_plist_status,
            "recommended_fixes": sorted(recommended_fixes, key=lambda x: x["priority"])
        }
    
    def _extract_domain(self, content: str) -> Optional[str]:
        """Extract domain from error message or URL."""
        # Try to find URLs
        url_pattern = r'https?://([^/\s]+)'
        matches = re.findall(url_pattern, content, re.IGNORECASE)
        if matches:
            return matches[0]
            
        # Try to find domain mentions
        domain_pattern = r'domain[:\s]+([^\s,]+)'
        matches = re.findall(domain_pattern, content, re.IGNORECASE)
        if matches:
            return matches[0]
            
        return None
    
    def _check_info_plist(self, project_path: str) -> Dict[str, any]:
        """Check the current state of Info.plist."""
        info_plist_path = Path(project_path) / "Info.plist"
        
        if not info_plist_path.exists():
            # Try alternative locations
            for alt_path in ["*/Info.plist", "*/*/Info.plist", "*/*/*/Info.plist"]:
                found_paths = list(Path(project_path).glob(alt_path))
                if found_paths:
                    info_plist_path = found_paths[0]
                    break
                    
        result = {
            "exists": info_plist_path.exists() if info_plist_path else False,
            "path": str(info_plist_path) if info_plist_path else None,
            "has_ats_config": False,
            "has_arbitrary_loads": False,
            "exception_domains": []
        }
        
        if result["exists"] and info_plist_path:
            try:
                content = info_plist_path.read_text()
                result["has_ats_config"] = "NSAppTransportSecurity" in content
                result["has_arbitrary_loads"] = "NSAllowsArbitraryLoads" in content and "<true/>" in content
                
                # Extract exception domains
                domain_pattern = r'<key>([^<]+)</key>\s*<dict>.*?NSTemporaryExceptionAllowsInsecureHTTPLoads'
                matches = re.findall(domain_pattern, content, re.DOTALL)
                result["exception_domains"] = matches
                
            except Exception as e:
                logger.error(f"Error reading Info.plist: {e}")
                
        return result
    
    def generate_fix_code(self, fix_type: str, **kwargs) -> Dict[str, str]:
        """Generate code for different types of SSL fixes."""
        fixes = {}
        
        if fix_type == "add_ats_exception":
            domain = kwargs.get("domain", "example.com")
            fixes["info_plist_modification"] = self.INFO_PLIST_ATS_TEMPLATE.format(domain=domain)
            fixes["description"] = f"Add App Transport Security exception for {domain}"
            
        elif fix_type == "upgrade_to_https":
            fixes["code_pattern"] = {
                "search": r'http://([^"\s]+)',
                "replace": r'https://\1',
                "description": "Replace HTTP URLs with HTTPS"
            }
            
        elif fix_type == "implement_cert_validation":
            fixes["swift_code"] = """
// Custom certificate validation
extension URLSession {
    static var customSession: URLSession {
        let configuration = URLSessionConfiguration.default
        let session = URLSession(configuration: configuration, delegate: SSLPinningDelegate(), delegateQueue: nil)
        return session
    }
}

class SSLPinningDelegate: NSObject, URLSessionDelegate {
    func urlSession(_ session: URLSession, didReceive challenge: URLAuthenticationChallenge, 
                    completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        if challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust {
            if let serverTrust = challenge.protectionSpace.serverTrust {
                // For development only - accept all certificates
                let credential = URLCredential(trust: serverTrust)
                completionHandler(.useCredential, credential)
                return
            }
        }
        completionHandler(.cancelAuthenticationChallenge, nil)
    }
}"""
            fixes["description"] = "Implement custom certificate validation (development mode)"
            
        return fixes
    
    def verify_fix_applied(self, project_path: str, fix_type: str, original_analysis: Dict) -> Dict[str, any]:
        """Verify if a fix was successfully applied."""
        verification_result = {
            "fix_applied": False,
            "fix_type": fix_type,
            "details": {}
        }
        
        if fix_type in ["add_ats_exception", "modify_ats_config"]:
            current_status = self._check_info_plist(project_path)
            original_status = original_analysis.get("info_plist_status", {})
            
            # Check if ATS was added
            if not original_status.get("has_ats_config") and current_status.get("has_ats_config"):
                verification_result["fix_applied"] = True
                verification_result["details"]["ats_added"] = True
                
            # Check if domain was added
            domain = original_analysis.get("domain")
            if domain and domain in current_status.get("exception_domains", []):
                verification_result["fix_applied"] = True
                verification_result["details"]["domain_added"] = domain
                
        elif fix_type == "upgrade_to_https":
            # Would need to check actual code files for URL changes
            verification_result["details"]["requires_code_analysis"] = True
            
        return verification_result
    
    def get_user_friendly_explanation(self, analysis: Dict) -> str:
        """Generate a user-friendly explanation of the SSL issue and fix."""
        if not analysis.get("has_ssl_error"):
            return "No SSL errors detected."
            
        explanation = ["🔒 SSL/Security Issue Detected\n"]
        
        # Explain the issue
        patterns = analysis.get("patterns", [])
        if any('cleartext' in p.lower() or 'transport security' in p.lower() for p in patterns):
            explanation.append("Your app is trying to connect to a server using HTTP (insecure) instead of HTTPS (secure).")
            explanation.append("iOS blocks insecure connections by default for security reasons.\n")
        elif any('certificate' in p.lower() for p in patterns):
            explanation.append("The server's SSL certificate is not trusted by iOS.")
            explanation.append("This could be because it's self-signed, expired, or from an untrusted authority.\n")
            
        # Explain the recommended fixes
        fixes = analysis.get("recommended_fixes", [])
        if fixes:
            explanation.append("Recommended solutions:")
            for i, fix in enumerate(fixes, 1):
                if fix["type"] == "upgrade_to_https":
                    explanation.append(f"{i}. Change your API URLs from HTTP to HTTPS (most secure)")
                elif fix["type"] == "add_ats_exception":
                    explanation.append(f"{i}. Add a security exception for your domain (temporary fix)")
                elif fix["type"] == "implement_cert_validation":
                    explanation.append(f"{i}. Implement custom certificate validation (for development)")
                    
        return "\n".join(explanation)
    
    def track_fix_attempt(self, fix_type: str, success: bool):
        """Track fix attempts for learning purposes."""
        attempt = {
            "fix_type": fix_type,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        self.attempted_fixes.append(attempt)
        if success:
            self.successful_fixes.append(attempt)
            
    def get_alternative_fixes(self, failed_fix_type: str) -> List[Dict]:
        """Get alternative fixes when the primary fix fails."""
        alternatives = []
        
        if failed_fix_type == "add_ats_exception":
            alternatives.append({
                "type": "allow_arbitrary_loads",
                "description": "Allow all insecure loads (not recommended for production)",
                "warning": "This disables all transport security - use only for development"
            })
            
        elif failed_fix_type == "upgrade_to_https":
            alternatives.append({
                "type": "add_ats_exception",
                "description": "Add security exception instead of upgrading to HTTPS"
            })
            
        return alternatives


# For backward compatibility
from datetime import datetime

def detect_ssl_error(content: str) -> bool:
    """Legacy function for SSL error detection."""
    handler = SSLErrorHandler()
    has_error, _ = handler.detect_ssl_error(content)
    return has_error