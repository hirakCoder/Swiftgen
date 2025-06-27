#!/usr/bin/env python3
"""
Test All SwiftGen Functionality
Comprehensive test of app generation, modification, and auto-fix with validator and SwiftLint
"""

import os
import sys
import json
import time
import requests
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple

# Test configurations
BASE_URL = "http://localhost:8000"
WORKSPACE_DIR = "../workspaces"

class FunctionalityTester:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'server_running': False,
            'tools_available': {},
            'app_tests': {},
            'modification_tests': {},
            'auto_fix_tests': {}
        }
        
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def check_prerequisites(self):
        """Check if all tools and services are available"""
        self.log("Checking prerequisites...")
        
        # Check server
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=3)
            self.results['server_running'] = response.status_code == 200
            self.log(f"Server: {'✅ Running' if self.results['server_running'] else '❌ Not running'}")
        except:
            self.log("Server: ❌ Not running", "ERROR")
            
        # Check tools
        tools = {
            'swiftc': ['swiftc', '--version'],
            'swiftlint': ['swiftlint', 'version'],
            'xcodegen': ['xcodegen', '--version'],
            'xcrun': ['xcrun', '--version']
        }
        
        for tool, cmd in tools.items():
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                self.results['tools_available'][tool] = result.returncode == 0
                self.log(f"{tool}: {'✅' if result.returncode == 0 else '❌'}")
            except:
                self.results['tools_available'][tool] = False
                self.log(f"{tool}: ❌")
    
    def test_app_generation(self, app_type: str, description: str) -> Dict:
        """Test generating a specific app type"""
        self.log(f"\n{'='*60}")
        self.log(f"Testing {app_type} generation")
        self.log(f"Description: {description}")
        
        if not self.results['server_running']:
            self.log("Cannot test - server not running", "ERROR")
            return {'error': 'Server not running'}
        
        try:
            # Send generation request
            response = requests.post(
                f"{BASE_URL}/api/generate",
                json={"description": description},
                timeout=60
            )
            
            if response.status_code != 200:
                self.log(f"Generation failed: {response.status_code}", "ERROR")
                return {'error': f'API returned {response.status_code}'}
            
            data = response.json()
            project_id = data.get('project_id')
            self.log(f"Project ID: {project_id}")
            
            # Wait for generation
            self.log("Waiting for generation to complete...")
            time.sleep(20)
            
            # Check results
            project_path = os.path.join(WORKSPACE_DIR, project_id)
            result = {
                'project_id': project_id,
                'generated': os.path.exists(project_path),
                'files': {},
                'validation': {},
                'build': {}
            }
            
            if result['generated']:
                # Count files
                for root, dirs, files in os.walk(project_path):
                    for file in files:
                        if file.endswith('.swift'):
                            rel_path = os.path.relpath(os.path.join(root, file), project_path)
                            result['files'][rel_path] = True
                
                self.log(f"✅ Generated {len(result['files'])} Swift files")
                
                # Check for common issues
                self._check_common_issues(project_path, result)
                
                # Run validation
                self._run_validation(project_path, result)
                
            return result
            
        except Exception as e:
            self.log(f"Exception: {e}", "ERROR")
            return {'error': str(e)}
    
    def _check_common_issues(self, project_path: str, result: Dict):
        """Check for common issues in generated code"""
        issues = {
            'semicolons': 0,
            'missing_imports': 0,
            'hashable_issues': 0,
            'ssl_configured': False
        }
        
        # Check Swift files
        for root, dirs, files in os.walk(os.path.join(project_path, 'Sources')):
            for file in files:
                if file.endswith('.swift'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Count semicolons
                    import re
                    semicolons = len(re.findall(r';\s*$', content, re.MULTILINE))
                    if semicolons > 0:
                        issues['semicolons'] += semicolons
                    
                    # Check for missing imports
                    if 'URLSession' in content and 'import Foundation' not in content:
                        issues['missing_imports'] += 1
                    
                    # Check for Hashable issues
                    if 'ForEach' in content and 'id:' not in content:
                        issues['hashable_issues'] += 1
        
        # Check Info.plist for SSL
        info_plist = os.path.join(project_path, 'Info.plist')
        if os.path.exists(info_plist):
            with open(info_plist, 'r') as f:
                if 'NSAppTransportSecurity' in f.read():
                    issues['ssl_configured'] = True
        
        result['common_issues'] = issues
        
        # Log issues
        if issues['semicolons'] > 0:
            self.log(f"⚠️  Found {issues['semicolons']} semicolons")
        if issues['missing_imports'] > 0:
            self.log(f"⚠️  Found {issues['missing_imports']} missing imports")
        if issues['hashable_issues'] > 0:
            self.log(f"⚠️  Found {issues['hashable_issues']} potential Hashable issues")
    
    def _run_validation(self, project_path: str, result: Dict):
        """Run validation tools on the project"""
        validation = {}
        
        # Run SwiftLint if available
        if self.results['tools_available'].get('swiftlint'):
            self.log("Running SwiftLint...")
            try:
                cmd = ['swiftlint', 'lint', '--path', project_path, '--reporter', 'json']
                swiftlint_result = subprocess.run(cmd, capture_output=True, text=True)
                
                if swiftlint_result.stdout:
                    issues = json.loads(swiftlint_result.stdout)
                    warnings = sum(1 for i in issues if i.get('severity') == 'warning')
                    errors = sum(1 for i in issues if i.get('severity') == 'error')
                    
                    validation['swiftlint'] = {
                        'warnings': warnings,
                        'errors': errors
                    }
                    
                    self.log(f"SwiftLint: {warnings} warnings, {errors} errors")
            except Exception as e:
                self.log(f"SwiftLint error: {e}", "ERROR")
        
        result['validation'] = validation
    
    def test_modification(self, project_id: str, modification: str, mod_type: str) -> Dict:
        """Test a modification request"""
        self.log(f"\n{'='*40}")
        self.log(f"Testing modification: {mod_type}")
        
        if not self.results['server_running']:
            return {'error': 'Server not running'}
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/modify",
                json={
                    "project_id": project_id,
                    "modification_request": modification
                },
                timeout=60
            )
            
            if response.status_code == 200:
                self.log("✅ Modification request accepted")
                
                # Wait for processing
                time.sleep(10)
                
                # Check for changes
                project_path = os.path.join(WORKSPACE_DIR, project_id)
                
                # Re-validate
                validation_result = {}
                self._run_validation(project_path, validation_result)
                
                return {
                    'success': True,
                    'validation': validation_result.get('validation', {})
                }
            else:
                return {'error': f'API returned {response.status_code}'}
                
        except Exception as e:
            self.log(f"Exception: {e}", "ERROR")
            return {'error': str(e)}
    
    def test_auto_fixes(self):
        """Test auto-fix capabilities"""
        self.log(f"\n{'='*60}")
        self.log("Testing Auto-Fix Capabilities")
        
        test_cases = [
            {
                'name': 'semicolon_removal',
                'code': 'let x = 5;\nlet y = 10;\nprint(x + y);',
                'expected_fix': 'let x = 5\nlet y = 10\nprint(x + y)'
            },
            {
                'name': 'hashable_conformance',
                'code': '''struct Item {
    let id: UUID
    let name: String
}

ForEach(items) { item in
    Text(item.name)
}''',
                'expected_fix': 'Add Hashable or use id parameter'
            }
        ]
        
        for test in test_cases:
            self.log(f"\nTesting: {test['name']}")
            
            # Test with swift_validator
            try:
                from swift_validator import SwiftValidator
                validator = SwiftValidator()
                
                fixed_content, fixes = validator.apply_auto_fixes(test['code'])
                
                if fixes:
                    self.log(f"✅ Validator applied {len(fixes)} fixes")
                    for fix in fixes:
                        self.log(f"   - {fix}")
                else:
                    self.log("❌ No fixes applied")
                    
                self.results['auto_fix_tests'][test['name']] = {
                    'fixes_applied': len(fixes),
                    'fixed': fixed_content != test['code']
                }
                
            except Exception as e:
                self.log(f"❌ Error: {e}", "ERROR")
                self.results['auto_fix_tests'][test['name']] = {
                    'error': str(e)
                }
    
    def generate_report(self):
        """Generate comprehensive report"""
        self.log(f"\n{'='*60}")
        self.log("COMPREHENSIVE FUNCTIONALITY REPORT")
        self.log(f"{'='*60}")
        
        # Prerequisites
        self.log("\n🔧 Prerequisites:")
        self.log(f"   Server: {'✅' if self.results['server_running'] else '❌'}")
        for tool, available in self.results['tools_available'].items():
            self.log(f"   {tool}: {'✅' if available else '❌'}")
        
        # App Generation
        self.log("\n📱 App Generation Tests:")
        for app_type, result in self.results['app_tests'].items():
            if 'error' in result:
                self.log(f"   {app_type}: ❌ {result['error']}")
            else:
                self.log(f"   {app_type}: {'✅' if result.get('generated') else '❌'}")
                if result.get('generated'):
                    self.log(f"      Files: {len(result.get('files', {}))}")
                    issues = result.get('common_issues', {})
                    if issues.get('semicolons', 0) > 0:
                        self.log(f"      Issues: {issues['semicolons']} semicolons")
        
        # Modifications
        self.log("\n🔧 Modification Tests:")
        for mod_type, result in self.results['modification_tests'].items():
            if 'error' in result:
                self.log(f"   {mod_type}: ❌ {result['error']}")
            else:
                self.log(f"   {mod_type}: {'✅' if result.get('success') else '❌'}")
        
        # Auto-fixes
        self.log("\n🔄 Auto-Fix Tests:")
        for test_name, result in self.results['auto_fix_tests'].items():
            if 'error' in result:
                self.log(f"   {test_name}: ❌ {result['error']}")
            else:
                self.log(f"   {test_name}: {'✅' if result.get('fixed') else '❌'}")
                if result.get('fixes_applied', 0) > 0:
                    self.log(f"      Fixes: {result['fixes_applied']}")
        
        # Save report
        with open('functionality_test_report.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.log("\n📄 Report saved to functionality_test_report.json")
    
    def run_all_tests(self):
        """Run all functionality tests"""
        self.log("SwiftGen Functionality Test Suite")
        self.log(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check prerequisites
        self.check_prerequisites()
        
        if self.results['server_running']:
            # Test different app types
            app_tests = [
                ('calculator', 'Create a calculator app with basic arithmetic operations'),
                ('todo', 'Create a todo list app with add, edit, and delete functionality'),
                ('weather', 'Create a weather app that shows current weather for any city'),
                ('notes', 'Create a note-taking app with categories')
            ]
            
            for app_type, description in app_tests[:2]:  # Test first 2
                result = self.test_app_generation(app_type, description)
                self.results['app_tests'][app_type] = result
                
                # If successful, test modification
                if result.get('generated') and result.get('project_id'):
                    mod_result = self.test_modification(
                        result['project_id'],
                        "Change the main color theme to blue",
                        "color_change"
                    )
                    self.results['modification_tests'][f"{app_type}_color"] = mod_result
        
        # Test auto-fixes regardless of server
        self.test_auto_fixes()
        
        # Generate report
        self.generate_report()
        
        self.log(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    tester = FunctionalityTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()