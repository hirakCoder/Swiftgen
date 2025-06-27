#!/usr/bin/env python3
"""
Robust Test Suite for SwiftGen
Tests app generation, build, and simulator launch
"""

import os
import sys
import json
import subprocess
import time
import shutil
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class TestResult:
    def __init__(self, name: str, passed: bool, details: Dict = None, error: str = None):
        self.name = name
        self.passed = passed
        self.details = details or {}
        self.error = error
        self.timestamp = datetime.now()

class RobustTestSuite:
    def __init__(self):
        self.results = []
        self.workspace_dir = "../workspaces"
        
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def run_command(self, cmd: List[str], cwd: str = None, timeout: int = 30) -> Tuple[bool, str, str]:
        """Run a command and return success, stdout, stderr"""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def check_swift_syntax(self, file_path: str) -> Tuple[bool, List[str]]:
        """Check Swift file syntax using swiftc"""
        self.log(f"Checking syntax: {os.path.basename(file_path)}")
        
        # Use swiftc to check syntax
        success, stdout, stderr = self.run_command(
            ["swiftc", "-parse", file_path],
            timeout=10
        )
        
        errors = []
        if not success:
            # Parse error messages
            for line in stderr.split('\n'):
                if 'error:' in line:
                    errors.append(line.strip())
        
        return success, errors
    
    def validate_project_structure(self, project_path: str) -> Dict:
        """Validate project has required files and structure"""
        self.log("Validating project structure")
        
        validation = {
            'has_sources': False,
            'has_project_yml': False,
            'has_info_plist': False,
            'has_xcodeproj': False,
            'swift_files': [],
            'syntax_errors': []
        }
        
        # Check for required files
        validation['has_project_yml'] = os.path.exists(os.path.join(project_path, 'project.yml'))
        validation['has_info_plist'] = os.path.exists(os.path.join(project_path, 'Info.plist'))
        
        # Check for .xcodeproj
        for item in os.listdir(project_path):
            if item.endswith('.xcodeproj'):
                validation['has_xcodeproj'] = True
                break
        
        # Check Sources directory
        sources_dir = os.path.join(project_path, 'Sources')
        if os.path.exists(sources_dir):
            validation['has_sources'] = True
            
            # Find all Swift files
            for root, dirs, files in os.walk(sources_dir):
                for file in files:
                    if file.endswith('.swift'):
                        file_path = os.path.join(root, file)
                        validation['swift_files'].append(file_path)
                        
                        # Check syntax
                        syntax_ok, errors = self.check_swift_syntax(file_path)
                        if not syntax_ok:
                            validation['syntax_errors'].extend(errors)
        
        return validation
    
    def test_app_generation(self, app_description: str, test_name: str) -> TestResult:
        """Test generating an app from description"""
        self.log(f"\n{'='*60}")
        self.log(f"Testing: {test_name}")
        self.log(f"Description: {app_description}")
        self.log(f"{'='*60}")
        
        start_time = time.time()
        project_name = f"test_{test_name}_{int(time.time())}"
        project_path = os.path.join(self.workspace_dir, project_name)
        
        # Clean up if exists
        if os.path.exists(project_path):
            shutil.rmtree(project_path)
        
        try:
            # Step 1: Generate app using API
            self.log("Step 1: Generating app...")
            import requests
            
            response = requests.post("http://localhost:8000/api/generate", json={
                "description": app_description
            }, timeout=60)
            
            if response.status_code != 200:
                return TestResult(test_name, False, error=f"API returned {response.status_code}")
            
            data = response.json()
            actual_project_id = data.get('project_id')
            actual_project_path = os.path.join(self.workspace_dir, actual_project_id)
            
            # Wait for generation
            self.log("Waiting for generation to complete...")
            time.sleep(15)
            
            # Step 2: Validate project structure
            if not os.path.exists(actual_project_path):
                return TestResult(test_name, False, error="Project directory not created")
            
            validation = self.validate_project_structure(actual_project_path)
            
            # Step 3: Check for syntax errors
            if validation['syntax_errors']:
                self.log(f"❌ Found {len(validation['syntax_errors'])} syntax errors", "ERROR")
                for error in validation['syntax_errors'][:3]:
                    self.log(f"   {error}", "ERROR")
                return TestResult(
                    test_name, 
                    False, 
                    details=validation,
                    error=f"{len(validation['syntax_errors'])} syntax errors"
                )
            
            # Step 4: Check if build succeeded
            self.log("Step 4: Checking build...")
            build_dir = os.path.join(actual_project_path, 'build/Build/Products/Debug-iphonesimulator')
            
            if os.path.exists(build_dir):
                apps = [f for f in os.listdir(build_dir) if f.endswith('.app')]
                if apps:
                    self.log(f"✅ Build successful: {apps[0]}", "SUCCESS")
                    validation['build_success'] = True
                    validation['app_bundle'] = apps[0]
                else:
                    validation['build_success'] = False
            else:
                validation['build_success'] = False
            
            # Step 5: Check for SSL config if needed
            if 'api' in app_description.lower() or 'weather' in app_description.lower() or 'currency' in app_description.lower():
                info_plist_path = os.path.join(actual_project_path, 'Info.plist')
                if os.path.exists(info_plist_path):
                    with open(info_plist_path, 'r') as f:
                        content = f.read()
                        validation['has_ssl_config'] = 'NSAppTransportSecurity' in content
                        if not validation['has_ssl_config']:
                            self.log("⚠️  Missing SSL configuration for API app", "WARNING")
            
            duration = time.time() - start_time
            validation['duration'] = duration
            validation['project_id'] = actual_project_id
            
            # Determine if test passed
            passed = (
                validation['has_sources'] and 
                validation['has_project_yml'] and
                validation['has_info_plist'] and
                len(validation['syntax_errors']) == 0 and
                len(validation['swift_files']) > 0
            )
            
            if passed:
                self.log(f"✅ Test passed in {duration:.2f}s", "SUCCESS")
            else:
                self.log(f"❌ Test failed in {duration:.2f}s", "ERROR")
            
            return TestResult(test_name, passed, details=validation)
            
        except Exception as e:
            self.log(f"❌ Exception: {str(e)}", "ERROR")
            return TestResult(test_name, False, error=str(e))
    
    def run_test_suite(self) -> Dict:
        """Run complete test suite"""
        self.log("\n" + "="*60)
        self.log("SwiftGen Robust Test Suite")
        self.log(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("="*60)
        
        # Check if server is running
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code != 200:
                self.log("❌ Server not responding properly", "ERROR")
                return {"error": "Server not running"}
        except:
            self.log("❌ Cannot connect to server", "ERROR")
            self.log("Please start the server with: python3 main.py", "ERROR")
            return {"error": "Cannot connect to server"}
        
        # Define test cases
        test_cases = [
            # Basic apps
            ("Create a simple calculator app", "calculator"),
            ("Create a timer app", "timer"),
            ("Create a todo list app", "todo"),
            ("Create a counter app", "counter"),
            
            # API apps
            ("Create a currency converter app with real-time exchange rates", "currency"),
            ("Create a weather app that shows current weather", "weather"),
            ("Create a quote of the day app", "quote"),
        ]
        
        # Run tests
        for description, name in test_cases:
            result = self.test_app_generation(description, name)
            self.results.append(result)
            
            # Small delay between tests
            time.sleep(3)
        
        # Generate summary
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        
        self.log("\n" + "="*60)
        self.log("TEST SUMMARY")
        self.log("="*60)
        self.log(f"Total Tests: {total}")
        self.log(f"Passed: {passed}")
        self.log(f"Failed: {total - passed}")
        self.log(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Detailed results
        self.log("\nDetailed Results:")
        for result in self.results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            self.log(f"\n{result.name}: {status}")
            
            if result.details:
                details = result.details
                self.log(f"  - Swift files: {len(details.get('swift_files', []))}")
                self.log(f"  - Syntax errors: {len(details.get('syntax_errors', []))}")
                self.log(f"  - Build success: {details.get('build_success', False)}")
                self.log(f"  - Duration: {details.get('duration', 0):.2f}s")
            
            if result.error:
                self.log(f"  - Error: {result.error}")
        
        # Save results
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': total,
            'passed': passed,
            'failed': total - passed,
            'success_rate': (passed/total)*100,
            'results': [
                {
                    'name': r.name,
                    'passed': r.passed,
                    'error': r.error,
                    'details': r.details,
                    'timestamp': r.timestamp.isoformat()
                }
                for r in self.results
            ]
        }
        
        with open('robust_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"\nReport saved to robust_test_report.json")
        
        # Return summary
        return report

def main():
    """Run the test suite"""
    suite = RobustTestSuite()
    report = suite.run_test_suite()
    
    # Exit with appropriate code
    if 'error' in report:
        sys.exit(1)
    elif report['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()