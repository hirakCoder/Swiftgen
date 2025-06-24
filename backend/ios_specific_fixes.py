"""
iOS Specific Fixes Module

This module contains common iOS issues and their solutions,
including SSL/ATS configuration, network permissions, and other
iOS-specific requirements.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class IssueCategory(Enum):
    """Categories of iOS-specific issues."""
    SECURITY = "security"
    PERMISSIONS = "permissions"
    NETWORKING = "networking"
    UI = "ui"
    BUILD = "build"
    RUNTIME = "runtime"


@dataclass
class IOSFix:
    """Represents a fix for an iOS-specific issue."""
    issue_id: str
    category: IssueCategory
    title: str
    description: str
    detection_patterns: List[str]
    fix_steps: List[Dict[str, Any]]
    verification_steps: List[str]
    notes: Optional[str] = None
    minimum_ios_version: Optional[str] = None


class IOSSpecificFixes:
    """Repository of iOS-specific issues and their solutions."""
    
    def __init__(self):
        self.fixes = self._initialize_fixes()
        
    def _initialize_fixes(self) -> Dict[str, IOSFix]:
        """Initialize the repository of iOS fixes."""
        fixes = {}
        
        # SSL/ATS Issues
        fixes["ats_http_blocked"] = IOSFix(
            issue_id="ats_http_blocked",
            category=IssueCategory.SECURITY,
            title="App Transport Security Blocking HTTP",
            description="iOS blocks cleartext HTTP connections by default",
            detection_patterns=[
                "App Transport Security.*blocked.*cleartext",
                "HTTP load failed.*App Transport Security",
                "Transport security has blocked a cleartext HTTP"
            ],
            fix_steps=[
                {
                    "type": "modify_info_plist",
                    "action": "add_ats_exception",
                    "code": """<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>"""
                },
                {
                    "type": "alternative",
                    "action": "add_domain_exception",
                    "code": """<key>NSAppTransportSecurity</key>
<dict>
    <key>NSExceptionDomains</key>
    <dict>
        <key>yourdomain.com</key>
        <dict>
            <key>NSIncludesSubdomains</key>
            <true/>
            <key>NSTemporaryExceptionAllowsInsecureHTTPLoads</key>
            <true/>
        </dict>
    </dict>
</dict>"""
                }
            ],
            verification_steps=[
                "Check Info.plist contains NSAppTransportSecurity",
                "Verify app can make HTTP requests",
                "Test with actual API endpoint"
            ],
            notes="For production, use HTTPS instead of disabling ATS"
        )
        
        fixes["ssl_certificate_invalid"] = IOSFix(
            issue_id="ssl_certificate_invalid",
            category=IssueCategory.SECURITY,
            title="SSL Certificate Validation Failed",
            description="Server certificate is invalid or self-signed",
            detection_patterns=[
                "certificate.*invalid|untrusted|expired",
                "NSURLErrorServerCertificateUntrusted",
                "SecTrust.*evaluation.*failed"
            ],
            fix_steps=[
                {
                    "type": "code_modification",
                    "action": "implement_cert_bypass",
                    "file": "NetworkManager.swift",
                    "code": """// WARNING: Only for development!
class CertificateBypassDelegate: NSObject, URLSessionDelegate {
    func urlSession(_ session: URLSession, 
                    didReceive challenge: URLAuthenticationChallenge, 
                    completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        if challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust,
           let serverTrust = challenge.protectionSpace.serverTrust {
            let credential = URLCredential(trust: serverTrust)
            completionHandler(.useCredential, credential)
        } else {
            completionHandler(.performDefaultHandling, nil)
        }
    }
}

// Use with URLSession
let session = URLSession(configuration: .default, delegate: CertificateBypassDelegate(), delegateQueue: nil)"""
                }
            ],
            verification_steps=[
                "Verify URLSession uses custom delegate",
                "Test HTTPS connection to problematic server",
                "Ensure certificate errors are bypassed"
            ],
            notes="Never use certificate bypass in production apps"
        )
        
        # Network Permissions
        fixes["local_network_permission"] = IOSFix(
            issue_id="local_network_permission",
            category=IssueCategory.PERMISSIONS,
            title="Local Network Permission Required",
            description="iOS 14+ requires permission for local network access",
            detection_patterns=[
                "local network permission",
                "NSLocalNetworkUsageDescription",
                "requires.*local.*network.*access"
            ],
            fix_steps=[
                {
                    "type": "modify_info_plist",
                    "action": "add_permission",
                    "code": """<key>NSLocalNetworkUsageDescription</key>
<string>This app needs to access your local network to discover and connect to devices.</string>"""
                },
                {
                    "type": "code_modification",
                    "action": "add_bonjour_services",
                    "code": """<key>NSBonjourServices</key>
<array>
    <string>_http._tcp</string>
    <string>_yourservice._tcp</string>
</array>"""
                }
            ],
            verification_steps=[
                "Check Info.plist for NSLocalNetworkUsageDescription",
                "Verify permission prompt appears",
                "Test local network connectivity"
            ],
            minimum_ios_version="14.0"
        )
        
        # Camera/Photo Permissions
        fixes["camera_permission"] = IOSFix(
            issue_id="camera_permission",
            category=IssueCategory.PERMISSIONS,
            title="Camera Permission Required",
            description="App needs camera usage description",
            detection_patterns=[
                "NSCameraUsageDescription.*required",
                "This app has crashed because it attempted to access privacy-sensitive data without a usage description",
                "must.*contain.*NSCameraUsageDescription"
            ],
            fix_steps=[
                {
                    "type": "modify_info_plist",
                    "action": "add_permission",
                    "code": """<key>NSCameraUsageDescription</key>
<string>This app needs camera access to take photos and videos.</string>"""
                }
            ],
            verification_steps=[
                "Check Info.plist for NSCameraUsageDescription",
                "Run app and verify camera permission prompt",
                "Test camera functionality"
            ]
        )
        
        fixes["photo_library_permission"] = IOSFix(
            issue_id="photo_library_permission",
            category=IssueCategory.PERMISSIONS,
            title="Photo Library Permission Required",
            description="App needs photo library usage description",
            detection_patterns=[
                "NSPhotoLibraryUsageDescription.*required",
                "NSPhotoLibraryAddUsageDescription.*required",
                "must.*contain.*PhotoLibrary.*Description"
            ],
            fix_steps=[
                {
                    "type": "modify_info_plist",
                    "action": "add_permission",
                    "code": """<key>NSPhotoLibraryUsageDescription</key>
<string>This app needs access to your photo library to select photos.</string>
<key>NSPhotoLibraryAddUsageDescription</key>
<string>This app needs permission to save photos to your library.</string>"""
                }
            ],
            verification_steps=[
                "Check Info.plist for photo library descriptions",
                "Verify permission prompts appear",
                "Test photo selection and saving"
            ]
        )
        
        # Location Permissions
        fixes["location_permission"] = IOSFix(
            issue_id="location_permission",
            category=IssueCategory.PERMISSIONS,
            title="Location Permission Required",
            description="App needs location usage description",
            detection_patterns=[
                "NSLocationWhenInUseUsageDescription.*required",
                "NSLocationAlwaysUsageDescription.*required",
                "location.*permission.*required"
            ],
            fix_steps=[
                {
                    "type": "modify_info_plist",
                    "action": "add_permission",
                    "code": """<key>NSLocationWhenInUseUsageDescription</key>
<string>This app needs your location to provide location-based features.</string>
<key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
<string>This app needs your location to provide location-based features even in the background.</string>"""
                }
            ],
            verification_steps=[
                "Check Info.plist for location descriptions",
                "Verify location permission prompt",
                "Test location services"
            ]
        )
        
        # Build Issues
        fixes["bitcode_not_supported"] = IOSFix(
            issue_id="bitcode_not_supported",
            category=IssueCategory.BUILD,
            title="Bitcode Not Supported",
            description="Framework doesn't support bitcode",
            detection_patterns=[
                "does not contain bitcode",
                "bitcode.*not.*supported",
                "ENABLE_BITCODE.*NO"
            ],
            fix_steps=[
                {
                    "type": "build_settings",
                    "action": "disable_bitcode",
                    "settings": {
                        "ENABLE_BITCODE": "NO"
                    },
                    "description": "Disable bitcode in Build Settings"
                }
            ],
            verification_steps=[
                "Check Build Settings for ENABLE_BITCODE = NO",
                "Clean and rebuild project",
                "Verify build succeeds"
            ]
        )
        
        fixes["minimum_deployment_target"] = IOSFix(
            issue_id="minimum_deployment_target",
            category=IssueCategory.BUILD,
            title="Deployment Target Too Low",
            description="API requires higher iOS deployment target",
            detection_patterns=[
                "is only available.*iOS [0-9]+",
                "minimum deployment target",
                "@available.*iOS"
            ],
            fix_steps=[
                {
                    "type": "build_settings",
                    "action": "update_deployment_target",
                    "settings": {
                        "IPHONEOS_DEPLOYMENT_TARGET": "13.0"
                    }
                },
                {
                    "type": "code_modification",
                    "action": "add_availability_check",
                    "code": """if #available(iOS 13.0, *) {
    // Use iOS 13+ API
} else {
    // Fallback for earlier versions
}"""
                }
            ],
            verification_steps=[
                "Check deployment target in project settings",
                "Verify availability checks in code",
                "Test on minimum supported iOS version"
            ]
        )
        
        # UI Issues
        fixes["scene_delegate_missing"] = IOSFix(
            issue_id="scene_delegate_missing",
            category=IssueCategory.UI,
            title="Scene Delegate Configuration Missing",
            description="iOS 13+ scene delegate not configured",
            detection_patterns=[
                "UISceneDelegate",
                "scene.*delegate.*missing",
                "UIApplicationSceneManifest"
            ],
            fix_steps=[
                {
                    "type": "modify_info_plist",
                    "action": "add_scene_manifest",
                    "code": """<key>UIApplicationSceneManifest</key>
<dict>
    <key>UIApplicationSupportsMultipleScenes</key>
    <false/>
    <key>UISceneConfigurations</key>
    <dict>
        <key>UIWindowSceneSessionRoleApplication</key>
        <array>
            <dict>
                <key>UISceneConfigurationName</key>
                <string>Default Configuration</string>
                <key>UISceneDelegateClassName</key>
                <string>$(PRODUCT_MODULE_NAME).SceneDelegate</string>
            </dict>
        </array>
    </dict>
</dict>"""
                }
            ],
            verification_steps=[
                "Check Info.plist for UIApplicationSceneManifest",
                "Verify SceneDelegate.swift exists",
                "Test app launch on iOS 13+"
            ],
            minimum_ios_version="13.0"
        )
        
        return fixes
    
    def find_fixes_for_issue(self, error_message: str) -> List[IOSFix]:
        """Find applicable fixes based on error message."""
        applicable_fixes = []
        error_lower = error_message.lower()
        
        for fix_id, fix in self.fixes.items():
            # Check detection patterns
            for pattern in fix.detection_patterns:
                if pattern.lower() in error_lower:
                    applicable_fixes.append(fix)
                    break
                    
        return applicable_fixes
    
    def get_fix_by_id(self, fix_id: str) -> Optional[IOSFix]:
        """Get a specific fix by its ID."""
        return self.fixes.get(fix_id)
    
    def get_fixes_by_category(self, category: IssueCategory) -> List[IOSFix]:
        """Get all fixes in a specific category."""
        return [fix for fix in self.fixes.values() if fix.category == category]
    
    def generate_fix_instructions(self, fix: IOSFix) -> str:
        """Generate human-readable instructions for applying a fix."""
        instructions = [f"## {fix.title}\n"]
        instructions.append(f"**Issue:** {fix.description}\n")
        
        if fix.minimum_ios_version:
            instructions.append(f"**Minimum iOS Version:** {fix.minimum_ios_version}\n")
            
        instructions.append("### Steps to Fix:\n")
        
        for i, step in enumerate(fix.fix_steps, 1):
            step_type = step.get("type", "")
            action = step.get("action", "")
            
            if step_type == "modify_info_plist":
                instructions.append(f"{i}. Add to Info.plist:")
                instructions.append("```xml")
                instructions.append(step.get("code", ""))
                instructions.append("```\n")
                
            elif step_type == "code_modification":
                file = step.get("file", "your code")
                instructions.append(f"{i}. Add to {file}:")
                instructions.append("```swift")
                instructions.append(step.get("code", ""))
                instructions.append("```\n")
                
            elif step_type == "build_settings":
                instructions.append(f"{i}. Update Build Settings:")
                settings = step.get("settings", {})
                for key, value in settings.items():
                    instructions.append(f"   - Set {key} to {value}")
                instructions.append("")
                
        instructions.append("### Verification Steps:\n")
        for step in fix.verification_steps:
            instructions.append(f"- {step}")
            
        if fix.notes:
            instructions.append(f"\n**Note:** {fix.notes}")
            
        return "\n".join(instructions)
    
    def get_all_permission_fixes(self) -> List[IOSFix]:
        """Get all permission-related fixes."""
        return self.get_fixes_by_category(IssueCategory.PERMISSIONS)
    
    def get_security_fixes(self) -> List[IOSFix]:
        """Get all security-related fixes."""
        return self.get_fixes_by_category(IssueCategory.SECURITY)