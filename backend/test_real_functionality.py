#!/usr/bin/env python3
"""
Test Real SwiftGen Functionality
Tests actual app generation, modification, and error recovery
"""

import os
import json
import time
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"

class RealFunctionalityTest:
    def __init__(self):
        self.results = {
            'server_status': 'unknown',
            'app_generation': {},
            'modifications': {},
            'error_fixes': {},
            'timestamp': datetime.now().isoformat()
        }
        
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def check_server(self):
        """Check if server is running"""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                self.log("✅ Server is running")
                self.results['server_status'] = 'running'
                return True
        except:
            pass
        
        self.log("❌ Server not running", "ERROR")
        self.log("Please start server: python3 main.py", "ERROR")
        self.results['server_status'] = 'not_running'
        return False
    
    def test_app_generation(self, description: str, app_name: str):
        """Test generating a specific app"""
        self.log(f"\n{'='*60}")
        self.log(f"Testing: {app_name}")
        self.log(f"Description: {description}")
        
        result = {
            'description': description,
            'project_id': None,
            'generated': False,
            'errors': [],
            'validator_fixes': [],
            'build_status': 'unknown'
        }
        
        try:
            # Generate app
            self.log("Sending generation request...")
            response = requests.post(
                f"{BASE_URL}/api/generate",
                json={"description": description},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                project_id = data.get('project_id')
                result['project_id'] = project_id
                self.log(f"✅ Generation started: {project_id}")
                
                # Wait for generation
                self.log("Waiting for generation to complete...")
                time.sleep(20)
                
                # Check project
                project_path = f"../workspaces/{project_id}"
                if os.path.exists(project_path):
                    result['generated'] = True
                    
                    # Check for Swift files
                    swift_files = []
                    for root, dirs, files in os.walk(os.path.join(project_path, 'Sources')):
                        swift_files.extend([f for f in files if f.endswith('.swift')])
                    
                    self.log(f"✅ Generated {len(swift_files)} Swift files")
                    
                    # Check logs for validator activity
                    log_path = f"backend/debug_logs/debug_{project_id}.log"
                    if os.path.exists(log_path):
                        with open(log_path, 'r') as f:
                            log_content = f.read()
                            
                        # Look for validator fixes
                        if 'Swift validator' in log_content:
                            self.log("✅ Swift validator was active")
                            
                        if 'Added Hashable conformance' in log_content:
                            result['validator_fixes'].append('Hashable conformance')
                            
                        if 'Removed semicolons' in log_content:
                            result['validator_fixes'].append('Semicolon removal')
                            
                        if 'BUILD SUCCESSFUL' in log_content:
                            result['build_status'] = 'success'
                            self.log("✅ Build successful")
                        elif 'BUILD FAILED' in log_content:
                            result['build_status'] = 'failed'
                            self.log("❌ Build failed")
                    
                    # Check for SSL config if API app
                    if 'api' in description.lower() or 'weather' in description.lower() or 'currency' in description.lower():
                        info_plist = os.path.join(project_path, 'Info.plist')
                        if os.path.exists(info_plist):
                            with open(info_plist, 'r') as f:
                                if 'NSAppTransportSecurity' in f.read():
                                    self.log("✅ SSL configuration applied")
                                    result['validator_fixes'].append('SSL config')
                
            else:
                result['errors'].append(f"API error: {response.status_code}")
                self.log(f"❌ Generation failed: {response.status_code}", "ERROR")
                
        except Exception as e:
            result['errors'].append(str(e))
            self.log(f"❌ Exception: {e}", "ERROR")
        
        self.results['app_generation'][app_name] = result
        return result
    
    def test_modification(self, project_id: str, modification: str, mod_type: str):
        """Test modifying an app"""
        self.log(f"\n{'='*40}")
        self.log(f"Testing modification: {mod_type}")
        self.log(f"Request: {modification}")
        
        result = {
            'request': modification,
            'type': mod_type,
            'processed': False,
            'errors': [],
            'validator_fixes': []
        }
        
        try:
            # Send modification request
            response = requests.post(
                f"{BASE_URL}/api/modify",
                json={
                    "project_id": project_id,
                    "modification_request": modification
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result['processed'] = True
                self.log("✅ Modification processed")
                
                # Wait for processing
                time.sleep(10)
                
                # Check logs
                log_path = f"backend/debug_logs/debug_{project_id}.log"
                if os.path.exists(log_path):
                    with open(log_path, 'r') as f:
                        recent_content = f.read()[-5000:]  # Last 5KB
                    
                    if 'Swift validator' in recent_content:
                        self.log("✅ Validator processed modification")
                        
                    if 'syntax errors' in recent_content.lower():
                        result['validator_fixes'].append('Syntax fixes')
                        
            else:
                result['errors'].append(f"API error: {response.status_code}")
                self.log(f"❌ Modification failed: {response.status_code}", "ERROR")
                
        except Exception as e:
            result['errors'].append(str(e))
            self.log(f"❌ Exception: {e}", "ERROR")
        
        self.results['modifications'][mod_type] = result
        return result
    
    def test_error_recovery(self):
        """Test error recovery scenarios"""
        self.log(f"\n{'='*60}")
        self.log("TESTING ERROR RECOVERY")
        self.log(f"{'='*60}")
        
        # Check if error recovery files exist
        recovery_files = [
            'robust_error_recovery_system.py',
            'intelligent_error_recovery.py',
            'swift_validator.py',
            'automatic_ssl_fixer.py'
        ]
        
        for file in recovery_files:
            if os.path.exists(file):
                self.log(f"✅ {file} present")
                self.results['error_fixes'][file] = 'present'
            else:
                self.log(f"❌ {file} missing")
                self.results['error_fixes'][file] = 'missing'
        
        # Check integration
        with open('main.py', 'r') as f:
            main_content = f.read()
            
        integrations = {
            'swift_validator': 'swift_validator_integration' in main_content,
            'ssl_fixer': 'automatic_ssl_fixer' in main_content,
            'error_recovery': 'robust_error_recovery_system' in main_content
        }
        
        for feature, integrated in integrations.items():
            if integrated:
                self.log(f"✅ {feature} integrated")
                self.results['error_fixes'][f'{feature}_integrated'] = True
            else:
                self.log(f"⚠️  {feature} not integrated")
                self.results['error_fixes'][f'{feature}_integrated'] = False
    
    def generate_report(self):
        """Generate test report"""
        self.log(f"\n{'='*60}")
        self.log("TEST REPORT")
        self.log(f"{'='*60}")
        
        # Server status
        self.log(f"\n🖥️  Server Status: {self.results['server_status']}")
        
        # App Generation
        self.log("\n📱 App Generation Results:")
        for app_name, result in self.results['app_generation'].items():
            self.log(f"\n{app_name}:")
            self.log(f"  Generated: {'✅' if result['generated'] else '❌'}")
            self.log(f"  Build: {result['build_status']}")
            if result['validator_fixes']:
                self.log(f"  Validator fixes: {', '.join(result['validator_fixes'])}")
            if result['errors']:
                self.log(f"  Errors: {result['errors'][0]}")
        
        # Modifications
        if self.results['modifications']:
            self.log("\n🔧 Modification Results:")
            for mod_type, result in self.results['modifications'].items():
                self.log(f"\n{mod_type}:")
                self.log(f"  Processed: {'✅' if result['processed'] else '❌'}")
                if result['validator_fixes']:
                    self.log(f"  Validator fixes: {', '.join(result['validator_fixes'])}")
        
        # Error Recovery
        self.log("\n🔄 Error Recovery Status:")
        recovery_present = sum(1 for k, v in self.results['error_fixes'].items() if v == 'present' or v is True)
        self.log(f"Components active: {recovery_present}/{len(self.results['error_fixes'])}")
        
        # Save report
        with open('real_functionality_test_report.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.log("\n📄 Report saved to real_functionality_test_report.json")
    
    def run_tests(self):
        """Run all tests"""
        self.log("SwiftGen Real Functionality Test")
        self.log(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check server
        if not self.check_server():
            self.log("\nCannot proceed without server", "ERROR")
            self.generate_report()
            return
        
        # Test app generation
        test_apps = [
            ("Create a simple calculator app", "calculator"),
            ("Create a todo list app", "todo"),
            ("Create a currency converter with real-time exchange rates", "currency_converter"),
            ("Create a weather app", "weather")
        ]
        
        # Test at least one app
        for description, app_name in test_apps[:2]:  # Test first 2
            result = self.test_app_generation(description, app_name)
            
            # If generation successful, test modification
            if result['generated'] and result['project_id']:
                time.sleep(5)
                self.test_modification(
                    result['project_id'],
                    "Change the background color to blue",
                    "color_change"
                )
                
                self.test_modification(
                    result['project_id'],
                    "Add a settings button",
                    "add_button"
                )
        
        # Test error recovery
        self.test_error_recovery()
        
        # Generate report
        self.generate_report()
        
        self.log(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Run real functionality tests"""
    tester = RealFunctionalityTest()
    tester.run_tests()

if __name__ == "__main__":
    main()