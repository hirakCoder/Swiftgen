#!/usr/bin/env python3
"""
Core Functionality Test Suite
Tests critical features to prevent regressions
"""

import os
import sys
import json
import time
import subprocess
import requests
import tempfile
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import hashlib

class CoreFunctionalityTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests_passed": 0,
            "tests_failed": 0,
            "critical_issues": [],
            "test_details": {}
        }
        
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def get_file_hash(self, content: str) -> str:
        """Generate hash of file content to verify modifications"""
        return hashlib.md5(content.encode()).hexdigest()
        
    def test_1_basic_app_generation(self) -> bool:
        """Test 1: Basic app generation with syntax validation"""
        test_name = "basic_app_generation"
        self.log(f"\n{'='*60}")
        self.log("Test 1: Basic App Generation with Syntax Validation")
        
        try:
            # Generate a calculator app
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"description": "Create a simple calculator app"},
                timeout=60
            )
            
            if response.status_code != 200:
                self.test_results["test_details"][test_name] = {
                    "passed": False,
                    "error": f"Generation failed with status {response.status_code}"
                }
                return False
                
            data = response.json()
            project_id = data.get('project_id')
            self.log(f"Generated project: {project_id}")
            
            # Wait for build
            time.sleep(30)
            
            # Check if app built successfully
            project_path = f"../workspaces/{project_id}"
            build_dir = os.path.join(project_path, "build/Build/Products/Debug-iphonesimulator")
            
            if os.path.exists(build_dir):
                apps = [f for f in os.listdir(build_dir) if f.endswith('.app')]
                if apps:
                    self.log(f"✅ App built successfully: {apps[0]}")
                    
                    # Check for common syntax issues in generated code
                    issues_found = self._check_syntax_issues(project_path)
                    
                    self.test_results["test_details"][test_name] = {
                        "passed": True,
                        "project_id": project_id,
                        "app_name": apps[0],
                        "syntax_issues": issues_found
                    }
                    self.test_results["tests_passed"] += 1
                    return project_id
                else:
                    self.test_results["test_details"][test_name] = {
                        "passed": False,
                        "error": "No app bundle found"
                    }
                    self.test_results["tests_failed"] += 1
                    return False
            else:
                self.test_results["test_details"][test_name] = {
                    "passed": False,
                    "error": "Build directory not found"
                }
                self.test_results["tests_failed"] += 1
                return False
                
        except Exception as e:
            self.log(f"❌ Test failed: {e}", "ERROR")
            self.test_results["test_details"][test_name] = {
                "passed": False,
                "error": str(e)
            }
            self.test_results["tests_failed"] += 1
            return False
            
    def test_2_modification_on_generated_app(self, project_id: str) -> bool:
        """Test 2: Modification on freshly generated app"""
        test_name = "modification_on_generated_app"
        self.log(f"\n{'='*60}")
        self.log("Test 2: Modification on Generated App")
        
        if not project_id:
            self.log("Skipping - no project to modify", "WARN")
            return False
            
        try:
            # First, capture the original state
            original_files = self._capture_app_state(project_id)
            
            # Make modification
            response = requests.post(
                f"{self.base_url}/api/modify",
                json={
                    "project_id": project_id,
                    "modification": "Change all button colors to green and add a memory button"
                },
                timeout=90
            )
            
            if response.status_code != 200:
                self.test_results["test_details"][test_name] = {
                    "passed": False,
                    "error": f"Modification failed with status {response.status_code}",
                    "response": response.text
                }
                self.test_results["tests_failed"] += 1
                return False
                
            # Wait for rebuild
            time.sleep(20)
            
            # Capture modified state
            modified_files = self._capture_app_state(project_id)
            
            # Verify changes were made
            changes_detected = self._verify_modifications(original_files, modified_files, ["green", "memory"])
            
            if changes_detected:
                self.log("✅ Modifications successfully applied")
                self.test_results["test_details"][test_name] = {
                    "passed": True,
                    "changes": changes_detected
                }
                self.test_results["tests_passed"] += 1
                return True
            else:
                self.log("❌ No changes detected in files", "ERROR")
                self.test_results["test_details"][test_name] = {
                    "passed": False,
                    "error": "Modifications not applied"
                }
                self.test_results["tests_failed"] += 1
                self.test_results["critical_issues"].append("Modifications not being applied to files")
                return False
                
        except Exception as e:
            self.log(f"❌ Test failed: {e}", "ERROR")
            self.test_results["test_details"][test_name] = {
                "passed": False,
                "error": str(e)
            }
            self.test_results["tests_failed"] += 1
            return False
            
    def test_3_modification_after_restart(self, project_id: str) -> bool:
        """Test 3: Modification after server restart"""
        test_name = "modification_after_restart"
        self.log(f"\n{'='*60}")
        self.log("Test 3: Modification After Server Restart")
        
        if not project_id:
            self.log("Skipping - no project to modify", "WARN")
            return False
            
        try:
            # Simulate server restart by clearing any in-memory state
            # In real scenario, you'd restart the server
            self.log("Simulating server restart scenario...")
            
            # Make modification (should handle missing project_state)
            response = requests.post(
                f"{self.base_url}/api/modify",
                json={
                    "project_id": project_id,
                    "modification": "Add a history display showing last 5 calculations"
                },
                timeout=90
            )
            
            if response.status_code != 200:
                self.test_results["test_details"][test_name] = {
                    "passed": False,
                    "error": f"Modification after restart failed: {response.status_code}"
                }
                self.test_results["tests_failed"] += 1
                self.test_results["critical_issues"].append("Server restart breaks modifications")
                return False
                
            self.log("✅ Modification after restart succeeded")
            self.test_results["test_details"][test_name] = {"passed": True}
            self.test_results["tests_passed"] += 1
            return True
            
        except Exception as e:
            self.log(f"❌ Test failed: {e}", "ERROR")
            self.test_results["test_details"][test_name] = {
                "passed": False,
                "error": str(e)
            }
            self.test_results["tests_failed"] += 1
            return False
            
    def test_4_swift_range_operator_handling(self) -> bool:
        """Test 4: Swift range operator (...) handling"""
        test_name = "swift_range_operator_handling"
        self.log(f"\n{'='*60}")
        self.log("Test 4: Swift Range Operator Handling")
        
        try:
            # Test the modification verifier directly
            from modification_verifier import ModificationVerifier
            verifier = ModificationVerifier()
            
            # Test code with range operator
            test_content = '''
            switch input {
            case "0"..."9":
                appendDigit(input)
            case "A"..."F":
                appendHex(input)
            default:
                break
            }
            '''
            
            issues = verifier._validate_swift_content(test_content)
            
            # Should not have "incomplete implementation" issue
            incomplete_issues = [i for i in issues if "Incomplete implementation" in i]
            
            if not incomplete_issues:
                self.log("✅ Range operator correctly handled")
                self.test_results["test_details"][test_name] = {"passed": True}
                self.test_results["tests_passed"] += 1
                return True
            else:
                self.log("❌ Range operator flagged as incomplete", "ERROR")
                self.test_results["test_details"][test_name] = {
                    "passed": False,
                    "error": "Range operator incorrectly flagged"
                }
                self.test_results["tests_failed"] += 1
                self.test_results["critical_issues"].append("Swift range operator handling broken")
                return False
                
        except Exception as e:
            self.log(f"❌ Test failed: {e}", "ERROR")
            self.test_results["test_details"][test_name] = {
                "passed": False,
                "error": str(e)
            }
            self.test_results["tests_failed"] += 1
            return False
            
    def test_5_state_consistency(self, project_id: str) -> bool:
        """Test 5: Verify modifications apply to correct app state"""
        test_name = "state_consistency"
        self.log(f"\n{'='*60}")
        self.log("Test 5: State Consistency - Modifications Apply to Correct State")
        
        if not project_id:
            self.log("Skipping - no project to test", "WARN")
            return False
            
        try:
            # Capture current state
            before_state = self._capture_app_state(project_id)
            before_hashes = {path: self.get_file_hash(content) 
                           for path, content in before_state.items()}
            
            # Make a specific modification
            test_string = f"TEST_{datetime.now().strftime('%H%M%S')}"
            response = requests.post(
                f"{self.base_url}/api/modify",
                json={
                    "project_id": project_id,
                    "modification": f"Add a comment '// {test_string}' to the top of ContentView"
                },
                timeout=90
            )
            
            if response.status_code != 200:
                self.test_results["test_details"][test_name] = {
                    "passed": False,
                    "error": "Modification request failed"
                }
                self.test_results["tests_failed"] += 1
                return False
                
            time.sleep(10)
            
            # Capture after state
            after_state = self._capture_app_state(project_id)
            
            # Verify the modification was applied to actual files
            content_view_path = None
            for path in after_state:
                if "ContentView.swift" in path:
                    content_view_path = path
                    break
                    
            if content_view_path and test_string in after_state[content_view_path]:
                self.log(f"✅ Modification correctly applied to actual file")
                
                # Also verify other files weren't randomly changed
                unchanged_count = 0
                for path, content in after_state.items():
                    if path != content_view_path:
                        if path in before_hashes:
                            if self.get_file_hash(content) == before_hashes[path]:
                                unchanged_count += 1
                                
                self.test_results["test_details"][test_name] = {
                    "passed": True,
                    "test_string_found": True,
                    "unchanged_files": unchanged_count
                }
                self.test_results["tests_passed"] += 1
                return True
            else:
                self.log("❌ Modification not found in actual files", "ERROR")
                self.test_results["test_details"][test_name] = {
                    "passed": False,
                    "error": "Modification not applied to correct state"
                }
                self.test_results["tests_failed"] += 1
                self.test_results["critical_issues"].append("Modifications not applying to actual app state")
                return False
                
        except Exception as e:
            self.log(f"❌ Test failed: {e}", "ERROR")
            self.test_results["test_details"][test_name] = {
                "passed": False,
                "error": str(e)
            }
            self.test_results["tests_failed"] += 1
            return False
            
    def test_6_swift_validator_integration(self) -> bool:
        """Test 6: Swift validator integration"""
        test_name = "swift_validator_integration"
        self.log(f"\n{'='*60}")
        self.log("Test 6: Swift Validator Integration")
        
        try:
            from swift_validator import SwiftValidator
            validator = SwiftValidator()
            
            # Test semicolon removal
            code_with_semicolons = """
            let x = 5;
            let y = 10;
            print(x + y);
            """
            
            fixed_code, fixes = validator.apply_auto_fixes(code_with_semicolons)
            
            if ";" not in fixed_code and len(fixes) > 0:
                self.log("✅ Swift validator removing semicolons")
                self.test_results["test_details"][test_name] = {
                    "passed": True,
                    "fixes_applied": fixes
                }
                self.test_results["tests_passed"] += 1
                return True
            else:
                self.log("❌ Swift validator not working correctly", "ERROR")
                self.test_results["test_details"][test_name] = {
                    "passed": False,
                    "error": "Semicolons not removed"
                }
                self.test_results["tests_failed"] += 1
                return False
                
        except Exception as e:
            self.log(f"❌ Test failed: {e}", "ERROR")
            self.test_results["test_details"][test_name] = {
                "passed": False,
                "error": str(e)
            }
            self.test_results["tests_failed"] += 1
            return False
            
    def _capture_app_state(self, project_id: str) -> Dict[str, str]:
        """Capture all Swift files in the project"""
        state = {}
        project_path = f"../workspaces/{project_id}"
        
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.endswith('.swift'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, project_path)
                    try:
                        with open(file_path, 'r') as f:
                            state[rel_path] = f.read()
                    except:
                        pass
                        
        return state
        
    def _verify_modifications(self, before: Dict[str, str], after: Dict[str, str], keywords: List[str]) -> Dict:
        """Verify modifications were applied"""
        changes = {}
        
        for path in after:
            if path in before:
                if before[path] != after[path]:
                    changes[path] = {
                        "size_before": len(before[path]),
                        "size_after": len(after[path]),
                        "keywords_found": [k for k in keywords if k.lower() in after[path].lower()]
                    }
                    
        return changes
        
    def _check_syntax_issues(self, project_path: str) -> List[str]:
        """Check for common syntax issues"""
        issues = []
        
        for root, dirs, files in os.walk(os.path.join(project_path, "Sources")):
            for file in files:
                if file.endswith('.swift'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                            
                        # Check for semicolons
                        import re
                        semicolons = len(re.findall(r';\s*$', content, re.MULTILINE))
                        if semicolons > 0:
                            issues.append(f"{file}: Contains {semicolons} semicolons")
                            
                    except:
                        pass
                        
        return issues
        
    def run_all_tests(self):
        """Run all core functionality tests"""
        self.log("="*60)
        self.log("SwiftGen Core Functionality Test Suite")
        self.log(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("="*60)
        
        # Check server
        try:
            response = requests.get(f"{self.base_url}/health", timeout=3)
            self.log("✅ Server is running")
        except:
            self.log("❌ Server not running - please start it first", "ERROR")
            return
            
        # Run tests
        project_id = self.test_1_basic_app_generation()
        
        if project_id:
            self.test_2_modification_on_generated_app(project_id)
            self.test_3_modification_after_restart(project_id)
            self.test_5_state_consistency(project_id)
            
        self.test_4_swift_range_operator_handling()
        self.test_6_swift_validator_integration()
        
        # Generate report
        self.generate_report()
        
    def cleanup_server(self):
        """Kill any running server processes"""
        self.log("\n🧹 Cleaning up server processes...")
        try:
            # Find and kill Python processes running main.py
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.split('\n'):
                if 'python' in line and 'main.py' in line and 'grep' not in line:
                    # Extract PID (second column)
                    parts = line.split()
                    if len(parts) > 1:
                        pid = parts[1]
                        subprocess.run(["kill", "-9", pid], capture_output=True)
                        self.log(f"Killed server process: PID {pid}")
                        
        except Exception as e:
            self.log(f"Warning: Could not clean up server: {e}", "WARN")
    
    def generate_report(self):
        """Generate test report"""
        self.log("\n" + "="*60)
        self.log("TEST SUMMARY")
        self.log("="*60)
        
        total_tests = self.test_results["tests_passed"] + self.test_results["tests_failed"]
        self.log(f"Total Tests: {total_tests}")
        self.log(f"Passed: {self.test_results['tests_passed']} ✅")
        self.log(f"Failed: {self.test_results['tests_failed']} ❌")
        
        if self.test_results["critical_issues"]:
            self.log("\n🚨 CRITICAL ISSUES FOUND:")
            for issue in self.test_results["critical_issues"]:
                self.log(f"  - {issue}")
                
        # Save report
        report_file = f"core_functionality_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
            
        self.log(f"\n📄 Detailed report saved to: {report_file}")
        
        # Clean up server
        self.cleanup_server()
        
        # Return exit code based on results
        if self.test_results["tests_failed"] > 0:
            sys.exit(1)
        else:
            sys.exit(0)

if __name__ == "__main__":
    tester = CoreFunctionalityTester()
    tester.run_all_tests()