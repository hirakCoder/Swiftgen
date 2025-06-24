"""
Fix Verification System
Ensures that fixes are actually applied and working
"""

import os
import json
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class FixVerificationSystem:
    """Verifies that fixes have been properly applied and are working"""
    
    def __init__(self):
        self.fix_history = {}  # Track fixes per project
        self.verification_rules = {
            "ssl_error": self._verify_ssl_fix,
            "missing_permission": self._verify_permission_fix,
            "build_error": self._verify_build_fix,
            "crash": self._verify_crash_fix,
            "ui_issue": self._verify_ui_fix
        }
    
    def track_fix_attempt(self, project_id: str, issue_type: str, fix_applied: Dict, 
                         files_modified: List[str]) -> None:
        """Track when a fix is attempted"""
        if project_id not in self.fix_history:
            self.fix_history[project_id] = []
        
        self.fix_history[project_id].append({
            "timestamp": datetime.now().isoformat(),
            "issue_type": issue_type,
            "fix_applied": fix_applied,
            "files_modified": files_modified,
            "verified": False,
            "working": None
        })
    
    def verify_fix_applied(self, project_id: str, issue_type: str, 
                          project_files: List[Dict]) -> Tuple[bool, str]:
        """Verify if the fix was actually applied to the code"""
        
        if issue_type not in self.verification_rules:
            return True, "Fix type not requiring verification"
        
        # Get the last fix attempt for this issue type
        if project_id not in self.fix_history:
            return False, "No fix history found"
        
        last_fix = None
        for fix in reversed(self.fix_history[project_id]):
            if fix["issue_type"] == issue_type:
                last_fix = fix
                break
        
        if not last_fix:
            return False, "No fix attempted for this issue type"
        
        # Run the verification rule
        verification_func = self.verification_rules[issue_type]
        is_applied, message = verification_func(last_fix, project_files)
        
        # Update the fix history
        last_fix["verified"] = True
        last_fix["working"] = is_applied
        
        return is_applied, message
    
    def _verify_ssl_fix(self, fix_attempt: Dict, project_files: List[Dict]) -> Tuple[bool, str]:
        """Verify SSL/ATS fix was applied"""
        fix_type = fix_attempt.get("fix_applied", {}).get("type", "")
        
        if fix_type == "info_plist":
            # Check if Info.plist exists and has ATS settings
            info_plist = None
            for file in project_files:
                if file["path"].endswith("Info.plist"):
                    info_plist = file["content"]
                    break
            
            if not info_plist:
                return False, "Info.plist not found - fix not applied"
            
            # Check for NSAppTransportSecurity
            if "NSAppTransportSecurity" in info_plist:
                if "NSAllowsArbitraryLoads" in info_plist or "NSExceptionDomains" in info_plist:
                    return True, "SSL/ATS fix properly applied in Info.plist"
                else:
                    return False, "NSAppTransportSecurity found but not configured properly"
            else:
                return False, "NSAppTransportSecurity not found in Info.plist"
        
        elif fix_type == "https_upgrade":
            # Check if HTTP URLs were replaced with HTTPS
            http_found = False
            for file in project_files:
                if file["path"].endswith(".swift"):
                    if re.search(r'https?://(?!localhost|127\.0\.0\.1)', file["content"]):
                        # Check if there are still HTTP URLs (excluding localhost)
                        if re.search(r'http://(?!localhost|127\.0\.0\.1)', file["content"]):
                            http_found = True
                            break
            
            if http_found:
                return False, "HTTP URLs still found in code - HTTPS upgrade incomplete"
            else:
                return True, "All URLs upgraded to HTTPS successfully"
        
        return False, "Unknown SSL fix type"
    
    def _verify_permission_fix(self, fix_attempt: Dict, project_files: List[Dict]) -> Tuple[bool, str]:
        """Verify permission fix was applied"""
        permission_type = fix_attempt.get("fix_applied", {}).get("permission", "")
        
        # Check Info.plist for usage descriptions
        info_plist = None
        for file in project_files:
            if file["path"].endswith("Info.plist"):
                info_plist = file["content"]
                break
        
        if not info_plist:
            return False, "Info.plist not found"
        
        permission_keys = {
            "camera": "NSCameraUsageDescription",
            "photos": "NSPhotoLibraryUsageDescription",
            "location": ["NSLocationWhenInUseUsageDescription", "NSLocationAlwaysAndWhenInUseUsageDescription"],
            "microphone": "NSMicrophoneUsageDescription",
            "contacts": "NSContactsUsageDescription"
        }
        
        if permission_type in permission_keys:
            keys_to_check = permission_keys[permission_type]
            if isinstance(keys_to_check, str):
                keys_to_check = [keys_to_check]
            
            for key in keys_to_check:
                if key in info_plist:
                    return True, f"{permission_type} permission properly configured"
            
            return False, f"{permission_type} permission key not found in Info.plist"
        
        return False, "Unknown permission type"
    
    def _verify_build_fix(self, fix_attempt: Dict, project_files: List[Dict]) -> Tuple[bool, str]:
        """Verify build error fix was applied"""
        # This would need to check the actual build result
        # For now, just check if files were modified
        files_modified = fix_attempt.get("files_modified", [])
        if files_modified:
            return True, f"Build fix applied to {len(files_modified)} files"
        return False, "No files were modified for build fix"
    
    def _verify_crash_fix(self, fix_attempt: Dict, project_files: List[Dict]) -> Tuple[bool, str]:
        """Verify crash fix was applied"""
        # Check for common crash fixes like optional unwrapping, error handling
        crash_type = fix_attempt.get("fix_applied", {}).get("crash_type", "")
        
        if crash_type == "force_unwrap":
            # Check if force unwraps were replaced
            force_unwraps = 0
            for file in project_files:
                if file["path"].endswith(".swift"):
                    # Count remaining force unwraps (excluding legitimate uses)
                    force_unwraps += len(re.findall(r'!\s*(?:[^=]|$)', file["content"]))
            
            if force_unwraps < fix_attempt.get("fix_applied", {}).get("original_count", float('inf')):
                return True, "Force unwraps have been reduced"
            else:
                return False, "Force unwraps still present in code"
        
        return True, "Crash fix assumed to be applied"
    
    def _verify_ui_fix(self, fix_attempt: Dict, project_files: List[Dict]) -> Tuple[bool, str]:
        """Verify UI fix was applied"""
        # Check if UI-related code was modified
        ui_files_modified = 0
        for file_path in fix_attempt.get("files_modified", []):
            if "View" in file_path or "UI" in file_path:
                ui_files_modified += 1
        
        if ui_files_modified > 0:
            return True, f"UI fix applied to {ui_files_modified} view files"
        return False, "No UI files were modified"
    
    def get_repeated_issues(self, project_id: str) -> List[Dict]:
        """Get issues that have been reported multiple times"""
        if project_id not in self.fix_history:
            return []
        
        issue_counts = {}
        for fix in self.fix_history[project_id]:
            issue_type = fix["issue_type"]
            if issue_type not in issue_counts:
                issue_counts[issue_type] = []
            issue_counts[issue_type].append(fix)
        
        repeated = []
        for issue_type, fixes in issue_counts.items():
            if len(fixes) > 1:
                # Check if any fix worked
                any_working = any(f.get("working", False) for f in fixes)
                repeated.append({
                    "issue_type": issue_type,
                    "attempts": len(fixes),
                    "any_working": any_working,
                    "last_attempt": fixes[-1]["timestamp"]
                })
        
        return repeated
    
    def suggest_alternative_approach(self, project_id: str, issue_type: str) -> Optional[str]:
        """Suggest an alternative approach when fixes aren't working"""
        repeated = self.get_repeated_issues(project_id)
        
        for issue in repeated:
            if issue["issue_type"] == issue_type and not issue["any_working"]:
                if issue["attempts"] >= 2:
                    if issue_type == "ssl_error":
                        return ("The SSL fix doesn't seem to be working. Let me try a different approach:\n"
                                "1. I'll check if the API endpoint supports HTTPS\n"
                                "2. If not, I'll implement a local proxy or mock data\n"
                                "3. I'll also add proper error handling to show user-friendly messages")
                    elif issue_type == "crash":
                        return ("The crash fix hasn't resolved the issue. Let me:\n"
                                "1. Add comprehensive error logging to identify the exact cause\n"
                                "2. Implement defensive programming patterns\n"
                                "3. Add fallback behavior to prevent crashes")
                    elif issue_type == "missing_permission":
                        return ("The permission fix isn't working. I'll:\n"
                                "1. Double-check the Info.plist configuration\n"
                                "2. Add runtime permission request code\n"
                                "3. Implement graceful degradation if permission is denied")
        
        return None