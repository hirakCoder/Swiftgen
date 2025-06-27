"""
SwiftGen Automated Test Suite - Fixed Version
Tests the actual API workflow end-to-end
"""

import asyncio
import json
import os
import subprocess
import shutil
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import re
import time

# Import the actual services used by the API
from enhanced_claude_service import EnhancedClaudeService
from project_manager import ProjectManager
from build_service import BuildService
from modification_handler import ModificationHandler
from ui_enhancement_handler import UIEnhancementHandler
from automatic_ssl_fixer import AutomaticSSLFixer


class TestResult:
    def __init__(self, test_name: str, passed: bool, error: str = None, duration: float = 0):
        self.test_name = test_name
        self.passed = passed
        self.error = error
        self.duration = duration
        self.timestamp = datetime.now()


class SwiftGenIntegrationTests:
    """Integration tests that use the actual SwiftGen workflow"""
    
    def __init__(self):
        # Initialize actual services
        self.claude_service = EnhancedClaudeService()
        self.project_manager = ProjectManager()
        self.build_service = BuildService()
        self.modification_handler = ModificationHandler()
        self.ui_handler = UIEnhancementHandler()
        self.ssl_fixer = AutomaticSSLFixer()
        
        self.results = []
        self.test_workspace = "/tmp/swiftgen_tests"
        
    def cleanup_workspace(self):
        """Clean up test workspace"""
        if os.path.exists(self.test_workspace):
            shutil.rmtree(self.test_workspace)
        os.makedirs(self.test_workspace, exist_ok=True)
        
    async def run_all_tests(self) -> Dict:
        """Run complete test suite"""
        print("=" * 60)
        print("SwiftGen Integration Test Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run a subset of critical tests
        await self.test_calculator_generation()
        await self.test_currency_converter()
        await self.test_color_modification()
        
        # Generate report
        total_time = time.time() - start_time
        return self.generate_report(total_time)
        
    async def test_calculator_generation(self) -> TestResult:
        """US-1.1: Generate Simple Calculator App"""
        test_name = "US-1.1: Calculator Generation"
        print(f"\n🧪 Testing {test_name}...")
        
        start_time = time.time()
        try:
            # Step 1: Generate code using Claude
            description = "Create a simple calculator app with basic arithmetic operations"
            project_id = f"test_calc_{int(time.time())}"
            
            # Generate the app code
            generated_code = await self.claude_service.generate_ios_app(
                description=description,
                include_ui_enhancements=True
            )
            
            if not generated_code or not generated_code.get("files"):
                raise Exception("No code generated")
                
            # Step 2: Create project
            project_path = await self.project_manager.create_project(
                project_id=project_id,
                generated_code=generated_code,
                app_name="Calculator"
            )
            
            if not project_path:
                raise Exception("Project creation failed")
                
            # Step 3: Apply UI enhancements
            enhanced_files = await self.ui_handler.enhance_generated_ui(
                generated_code.get("files", []),
                "Calculator",
                ios_version="16.0"
            )
            
            # Write enhanced files
            for file_data in enhanced_files:
                file_path = os.path.join(project_path, file_data["path"])
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(file_data["content"])
                    
            # Step 4: Build project
            build_result = await self.build_service.build_project(
                project_path=project_path,
                project_id=project_id,
                bundle_id="com.test.calculator",
                app_complexity="simple"
            )
            
            if not build_result.success:
                raise Exception(f"Build failed: {build_result.errors[:3]}")
                
            # Verify no syntax errors
            syntax_errors = self._check_syntax_errors(project_path)
            if syntax_errors:
                raise Exception(f"Syntax errors found: {syntax_errors[:2]}")
                
            # Verify build time < 2 minutes
            if build_result.build_time > 120:
                raise Exception(f"Build took too long: {build_result.build_time}s")
                
            duration = time.time() - start_time
            result = TestResult(test_name, True, duration=duration)
            print(f"✅ {test_name} PASSED in {duration:.1f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(test_name, False, str(e), duration)
            print(f"❌ {test_name} FAILED: {str(e)}")
            
        self.results.append(result)
        return result
        
    async def test_currency_converter(self) -> TestResult:
        """US-2.1: Generate Currency Converter"""
        test_name = "US-2.1: Currency Converter Generation"
        print(f"\n🧪 Testing {test_name}...")
        
        start_time = time.time()
        try:
            # Step 1: Generate code
            description = "Create a currency converter app with real-time exchange rates"
            project_id = f"test_currency_{int(time.time())}"
            
            generated_code = await self.claude_service.generate_ios_app(
                description=description,
                include_ui_enhancements=True
            )
            
            if not generated_code or not generated_code.get("files"):
                raise Exception("No code generated")
                
            # Step 2: Create project
            project_path = await self.project_manager.create_project(
                project_id=project_id,
                generated_code=generated_code,
                app_name="Currency Converter"
            )
            
            if not project_path:
                raise Exception("Project creation failed")
                
            # Step 3: Apply SSL fix for API apps
            ssl_fixed = await self.ssl_fixer.fix_ssl_if_needed(project_path, description)
            if not ssl_fixed:
                raise Exception("SSL configuration failed")
                
            # Verify SSL configuration
            if not self._verify_ssl_configuration(project_path):
                raise Exception("SSL configuration missing in Info.plist")
                
            # Step 4: Build project
            build_result = await self.build_service.build_project(
                project_path=project_path,
                project_id=project_id,
                bundle_id="com.test.currency",
                app_complexity="simple"
            )
            
            if not build_result.success:
                raise Exception(f"Build failed: {build_result.errors[:3]}")
                
            # Verify build time < 2 minutes
            if build_result.build_time > 120:
                raise Exception(f"Build took too long: {build_result.build_time}s")
                
            duration = time.time() - start_time
            result = TestResult(test_name, True, duration=duration)
            print(f"✅ {test_name} PASSED in {duration:.1f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(test_name, False, str(e), duration)
            print(f"❌ {test_name} FAILED: {str(e)}")
            
        self.results.append(result)
        return result
        
    async def test_color_modification(self) -> TestResult:
        """US-3.1: Change App Colors"""
        test_name = "US-3.1: Color Modification"
        print(f"\n🧪 Testing {test_name}...")
        
        start_time = time.time()
        try:
            # First generate a simple app
            description = "Create a simple app with a blue background"
            project_id = f"test_color_{int(time.time())}"
            
            generated_code = await self.claude_service.generate_ios_app(
                description=description,
                include_ui_enhancements=True
            )
            
            if not generated_code or not generated_code.get("files"):
                raise Exception("No code generated")
                
            # Create project
            project_path = await self.project_manager.create_project(
                project_id=project_id,
                generated_code=generated_code,
                app_name="Color Test"
            )
            
            if not project_path:
                raise Exception("Project creation failed")
                
            # Build to ensure it works
            build_result = await self.build_service.build_project(
                project_path=project_path,
                project_id=project_id,
                bundle_id="com.test.color",
                app_complexity="simple"
            )
            
            if not build_result.success:
                raise Exception(f"Initial build failed: {build_result.errors[:2]}")
                
            # Now modify colors
            mod_result = await self.modification_handler.handle_modification(
                project_path=project_path,
                modification_request="Change the background color to red",
                project_id=project_id
            )
            
            if not mod_result["success"]:
                raise Exception(f"Modification failed: {mod_result.get('error')}")
                
            # Rebuild to verify no syntax errors
            build_result2 = await self.build_service.build_project(
                project_path=project_path,
                project_id=f"{project_id}_mod",
                bundle_id="com.test.color",
                app_complexity="simple",
                is_modification=True
            )
            
            if not build_result2.success:
                raise Exception(f"Build after modification failed: {build_result2.errors[:2]}")
                
            # Verify no syntax errors introduced
            syntax_errors = self._check_syntax_errors(project_path)
            if syntax_errors:
                raise Exception(f"Modification introduced syntax errors: {syntax_errors[:2]}")
                
            duration = time.time() - start_time
            result = TestResult(test_name, True, duration=duration)
            print(f"✅ {test_name} PASSED in {duration:.1f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(test_name, False, str(e), duration)
            print(f"❌ {test_name} FAILED: {str(e)}")
            
        self.results.append(result)
        return result
        
    def _check_syntax_errors(self, project_path: str) -> List[str]:
        """Check for common syntax errors in Swift files"""
        errors = []
        sources_dir = os.path.join(project_path, "Sources")
        
        if not os.path.exists(sources_dir):
            return ["Sources directory not found"]
            
        for root, dirs, files in os.walk(sources_dir):
            for file in files:
                if file.endswith('.swift'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                            
                        # Check for semicolons before var body
                        if re.search(r';\s*var\s+body', content):
                            errors.append(f"{file}: Unnecessary semicolon before 'var body'")
                            
                        # Check for mismatched brackets
                        if content.count('{') != content.count('}'):
                            errors.append(f"{file}: Mismatched braces")
                            
                        # Check for broken modifiers
                        if re.search(r'\.\w+\s*\n\s*\.\w+', content):
                            errors.append(f"{file}: Broken modifier chain")
                    except:
                        pass
                        
        return errors
        
    def _verify_ssl_configuration(self, project_path: str) -> bool:
        """Verify SSL configuration in Info.plist"""
        info_plist = os.path.join(project_path, "Sources", "Info.plist")
        if not os.path.exists(info_plist):
            return False
            
        try:
            with open(info_plist, 'r') as f:
                content = f.read()
                
            return "NSAppTransportSecurity" in content and "NSAllowsArbitraryLoads" in content
        except:
            return False
        
    def generate_report(self, total_time: float) -> Dict:
        """Generate test report"""
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total = len(self.results)
        
        print("\n" + "=" * 60)
        print("Test Results Summary")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"Failed: {failed} ({failed/total*100:.1f}%)")
        print(f"Total Time: {total_time:.1f}s")
        print("=" * 60)
        
        if failed > 0:
            print("\nFailed Tests:")
            for result in self.results:
                if not result.passed:
                    print(f"  ❌ {result.test_name}: {result.error}")
                    
        # Save detailed report
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": passed/total*100 if total > 0 else 0,
                "total_time": total_time
            },
            "tests": [
                {
                    "name": r.test_name,
                    "passed": r.passed,
                    "error": r.error,
                    "duration": r.duration,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in self.results
            ]
        }
        
        report_path = os.path.join(os.path.dirname(__file__), "test_report_integration.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\nDetailed report saved to: {report_path}")
        
        return report


async def main():
    """Run the integration test suite"""
    test_suite = SwiftGenIntegrationTests()
    report = await test_suite.run_all_tests()
    
    # Exit with appropriate code
    if report["summary"]["failed"] > 0:
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    asyncio.run(main())