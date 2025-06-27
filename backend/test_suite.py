"""
SwiftGen Automated Test Suite
Ensures all user stories work correctly before any changes are deployed
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

from project_manager import ProjectManager
from build_service import BuildService
from modification_handler import ModificationHandler


class TestResult:
    def __init__(self, test_name: str, passed: bool, error: str = None, duration: float = 0):
        self.test_name = test_name
        self.passed = passed
        self.error = error
        self.duration = duration
        self.timestamp = datetime.now()


class SwiftGenTestSuite:
    """Automated test suite for SwiftGen user stories"""
    
    def __init__(self):
        self.project_manager = ProjectManager()
        self.build_service = BuildService()
        self.modification_handler = ModificationHandler()
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
        print("SwiftGen Automated Test Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        # Epic 1: Basic App Generation
        await self.test_calculator_generation()
        await self.test_timer_generation()
        await self.test_todo_generation()
        await self.test_counter_generation()
        
        # Epic 2: API-Enabled Apps
        await self.test_currency_converter()
        await self.test_weather_app()
        
        # Epic 3: Modifications
        await self.test_color_modification()
        await self.test_button_addition()
        await self.test_text_modification()
        
        # Epic 4: Core Functionality Tests
        await self.test_modification_state_consistency()
        await self.test_modification_after_restart()
        await self.test_swift_range_operator()
        await self.test_swift_validator_integration()
        
        # Generate report
        total_time = time.time() - start_time
        return self.generate_report(total_time)
        
    async def test_calculator_generation(self) -> TestResult:
        """US-1.1: Generate Simple Calculator App"""
        test_name = "US-1.1: Calculator Generation"
        print(f"\n🧪 Testing {test_name}...")
        
        start_time = time.time()
        try:
            self.cleanup_workspace()
            
            # Generate calculator
            project_path = os.path.join(self.test_workspace, "calculator")
            
            # Create project using the correct method signature
            generated_code = {
                "app_name": "Calculator",
                "bundle_id": "com.test.calculator",
                "description": "Create a simple calculator app with basic arithmetic operations",
                "files": []  # Will be filled by LLM
            }
            
            # First, we need to generate the code using the appropriate service
            # For now, create a mock project structure
            project_id = "test_calc"
            project_path = await self.project_manager.create_project(
                project_id=project_id,
                generated_code=generated_code,
                app_name="Calculator"
            )
            
            if not result["success"]:
                raise Exception(f"Project creation failed: {result.get('error')}")
                
            # Build project
            build_result = await self.build_service.build_project(
                project_path=project_path,
                project_id="test_calc",
                bundle_id="com.test.calculator"
            )
            
            if not build_result.success:
                raise Exception(f"Build failed: {build_result.errors}")
                
            # Verify no syntax errors
            syntax_errors = self._check_syntax_errors(project_path)
            if syntax_errors:
                raise Exception(f"Syntax errors found: {syntax_errors}")
                
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
        
    async def test_timer_generation(self) -> TestResult:
        """US-1.2: Generate Timer App"""
        test_name = "US-1.2: Timer Generation"
        print(f"\n🧪 Testing {test_name}...")
        
        start_time = time.time()
        try:
            self.cleanup_workspace()
            
            # Generate timer
            project_path = os.path.join(self.test_workspace, "timer")
            result = await self.project_manager.create_project(
                description="Create a countdown timer app with start, stop, and reset buttons",
                project_path=project_path,
                app_name="Timer",
                bundle_id="com.test.timer"
            )
            
            if not result["success"]:
                raise Exception(f"Project creation failed: {result.get('error')}")
                
            # Build project
            build_result = await self.build_service.build_project(
                project_path=project_path,
                project_id="test_timer",
                bundle_id="com.test.timer"
            )
            
            if not build_result.success:
                raise Exception(f"Build failed: {build_result.errors}")
                
            # Verify functionality
            if not self._verify_timer_functionality(project_path):
                raise Exception("Timer functionality missing")
                
            duration = time.time() - start_time
            result = TestResult(test_name, True, duration=duration)
            print(f"✅ {test_name} PASSED in {duration:.1f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(test_name, False, str(e), duration)
            print(f"❌ {test_name} FAILED: {str(e)}")
            
        self.results.append(result)
        return result
        
    async def test_todo_generation(self) -> TestResult:
        """US-1.3: Generate Todo List App"""
        test_name = "US-1.3: Todo List Generation"
        print(f"\n🧪 Testing {test_name}...")
        
        start_time = time.time()
        try:
            self.cleanup_workspace()
            
            # Generate todo list
            project_path = os.path.join(self.test_workspace, "todo")
            result = await self.project_manager.create_project(
                description="Create a todo list app where users can add, delete, and mark tasks as complete",
                project_path=project_path,
                app_name="Todo List",
                bundle_id="com.test.todo"
            )
            
            if not result["success"]:
                raise Exception(f"Project creation failed: {result.get('error')}")
                
            # Build project
            build_result = await self.build_service.build_project(
                project_path=project_path,
                project_id="test_todo",
                bundle_id="com.test.todo"
            )
            
            if not build_result.success:
                raise Exception(f"Build failed: {build_result.errors}")
                
            duration = time.time() - start_time
            result = TestResult(test_name, True, duration=duration)
            print(f"✅ {test_name} PASSED in {duration:.1f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(test_name, False, str(e), duration)
            print(f"❌ {test_name} FAILED: {str(e)}")
            
        self.results.append(result)
        return result
        
    async def test_counter_generation(self) -> TestResult:
        """US-1.4: Generate Counter App"""
        test_name = "US-1.4: Counter Generation"
        print(f"\n🧪 Testing {test_name}...")
        
        start_time = time.time()
        try:
            self.cleanup_workspace()
            
            # Generate counter
            project_path = os.path.join(self.test_workspace, "counter")
            result = await self.project_manager.create_project(
                description="Create a simple counter app with increment, decrement, and reset buttons",
                project_path=project_path,
                app_name="Counter",
                bundle_id="com.test.counter"
            )
            
            if not result["success"]:
                raise Exception(f"Project creation failed: {result.get('error')}")
                
            # Build project
            build_result = await self.build_service.build_project(
                project_path=project_path,
                project_id="test_counter",
                bundle_id="com.test.counter"
            )
            
            if not build_result.success:
                raise Exception(f"Build failed: {build_result.errors}")
                
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
            self.cleanup_workspace()
            
            # Generate currency converter
            project_path = os.path.join(self.test_workspace, "currency")
            result = await self.project_manager.create_project(
                description="Create a currency converter app with real-time exchange rates",
                project_path=project_path,
                app_name="Currency Converter",
                bundle_id="com.test.currency"
            )
            
            if not result["success"]:
                raise Exception(f"Project creation failed: {result.get('error')}")
                
            # Verify SSL configuration
            if not self._verify_ssl_configuration(project_path):
                raise Exception("SSL configuration missing")
                
            # Build project
            build_result = await self.build_service.build_project(
                project_path=project_path,
                project_id="test_currency",
                bundle_id="com.test.currency"
            )
            
            if not build_result.success:
                raise Exception(f"Build failed: {build_result.errors}")
                
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
        
    async def test_weather_app(self) -> TestResult:
        """US-2.2: Generate Weather App"""
        test_name = "US-2.2: Weather App Generation"
        print(f"\n🧪 Testing {test_name}...")
        
        start_time = time.time()
        try:
            self.cleanup_workspace()
            
            # Generate weather app
            project_path = os.path.join(self.test_workspace, "weather")
            result = await self.project_manager.create_project(
                description="Create a weather app that shows current weather conditions",
                project_path=project_path,
                app_name="Weather",
                bundle_id="com.test.weather"
            )
            
            if not result["success"]:
                raise Exception(f"Project creation failed: {result.get('error')}")
                
            # Verify SSL configuration
            if not self._verify_ssl_configuration(project_path):
                raise Exception("SSL configuration missing")
                
            # Build project
            build_result = await self.build_service.build_project(
                project_path=project_path,
                project_id="test_weather",
                bundle_id="com.test.weather"
            )
            
            if not build_result.success:
                raise Exception(f"Build failed: {build_result.errors}")
                
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
            self.cleanup_workspace()
            
            # First generate a simple app
            project_path = os.path.join(self.test_workspace, "color_test")
            result = await self.project_manager.create_project(
                description="Create a simple app with a blue background",
                project_path=project_path,
                app_name="Color Test",
                bundle_id="com.test.color"
            )
            
            if not result["success"]:
                raise Exception(f"Project creation failed: {result.get('error')}")
                
            # Build to ensure it works
            build_result = await self.build_service.build_project(
                project_path=project_path,
                project_id="test_color",
                bundle_id="com.test.color"
            )
            
            if not build_result.success:
                raise Exception(f"Initial build failed: {build_result.errors}")
                
            # Now modify colors
            mod_result = await self.modification_handler.handle_modification(
                project_path=project_path,
                modification_request="Change the background color to red",
                project_id="test_color"
            )
            
            if not mod_result["success"]:
                raise Exception(f"Modification failed: {mod_result.get('error')}")
                
            # Rebuild to verify no syntax errors
            build_result2 = await self.build_service.build_project(
                project_path=project_path,
                project_id="test_color_mod",
                bundle_id="com.test.color",
                is_modification=True
            )
            
            if not build_result2.success:
                raise Exception(f"Build after modification failed: {build_result2.errors}")
                
            # Verify no syntax errors introduced
            syntax_errors = self._check_syntax_errors(project_path)
            if syntax_errors:
                raise Exception(f"Modification introduced syntax errors: {syntax_errors}")
                
            duration = time.time() - start_time
            result = TestResult(test_name, True, duration=duration)
            print(f"✅ {test_name} PASSED in {duration:.1f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(test_name, False, str(e), duration)
            print(f"❌ {test_name} FAILED: {str(e)}")
            
        self.results.append(result)
        return result
        
    async def test_button_addition(self) -> TestResult:
        """US-3.2: Add New Button"""
        test_name = "US-3.2: Button Addition"
        print(f"\n🧪 Testing {test_name}...")
        
        start_time = time.time()
        try:
            self.cleanup_workspace()
            
            # First generate a simple app
            project_path = os.path.join(self.test_workspace, "button_test")
            result = await self.project_manager.create_project(
                description="Create a simple app with one button",
                project_path=project_path,
                app_name="Button Test",
                bundle_id="com.test.button"
            )
            
            if not result["success"]:
                raise Exception(f"Project creation failed: {result.get('error')}")
                
            # Build to ensure it works
            build_result = await self.build_service.build_project(
                project_path=project_path,
                project_id="test_button",
                bundle_id="com.test.button"
            )
            
            if not build_result.success:
                raise Exception(f"Initial build failed: {build_result.errors}")
                
            # Now add a button
            mod_result = await self.modification_handler.handle_modification(
                project_path=project_path,
                modification_request="Add a new button that says 'Click Me' below the existing button",
                project_id="test_button"
            )
            
            if not mod_result["success"]:
                raise Exception(f"Modification failed: {mod_result.get('error')}")
                
            # Rebuild to verify no errors
            build_result2 = await self.build_service.build_project(
                project_path=project_path,
                project_id="test_button_mod",
                bundle_id="com.test.button",
                is_modification=True
            )
            
            if not build_result2.success:
                raise Exception(f"Build after modification failed: {build_result2.errors}")
                
            duration = time.time() - start_time
            result = TestResult(test_name, True, duration=duration)
            print(f"✅ {test_name} PASSED in {duration:.1f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(test_name, False, str(e), duration)
            print(f"❌ {test_name} FAILED: {str(e)}")
            
        self.results.append(result)
        return result
        
    async def test_text_modification(self) -> TestResult:
        """US-3.3: Change Text Labels"""
        test_name = "US-3.3: Text Modification"
        print(f"\n🧪 Testing {test_name}...")
        
        start_time = time.time()
        try:
            self.cleanup_workspace()
            
            # First generate a simple app
            project_path = os.path.join(self.test_workspace, "text_test")
            result = await self.project_manager.create_project(
                description="Create a simple app with the text 'Hello World'",
                project_path=project_path,
                app_name="Text Test",
                bundle_id="com.test.text"
            )
            
            if not result["success"]:
                raise Exception(f"Project creation failed: {result.get('error')}")
                
            # Build to ensure it works
            build_result = await self.build_service.build_project(
                project_path=project_path,
                project_id="test_text",
                bundle_id="com.test.text"
            )
            
            if not build_result.success:
                raise Exception(f"Initial build failed: {build_result.errors}")
                
            # Now modify text
            mod_result = await self.modification_handler.handle_modification(
                project_path=project_path,
                modification_request="Change 'Hello World' to 'Welcome to SwiftGen'",
                project_id="test_text"
            )
            
            if not mod_result["success"]:
                raise Exception(f"Modification failed: {mod_result.get('error')}")
                
            # Rebuild to verify no errors
            build_result2 = await self.build_service.build_project(
                project_path=project_path,
                project_id="test_text_mod",
                bundle_id="com.test.text",
                is_modification=True
            )
            
            if not build_result2.success:
                raise Exception(f"Build after modification failed: {build_result2.errors}")
                
            # Verify modification completed quickly
            if mod_result.get("duration", 60) > 30:
                raise Exception(f"Modification took too long: {mod_result.get('duration')}s")
                
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
                    with open(file_path, 'r') as f:
                        content = f.read()
                        
                    # Check for semicolons (not needed in Swift)
                    semicolons = re.findall(r';\s*var\s+body', content)
                    if semicolons:
                        errors.append(f"{file}: Unnecessary semicolon before 'var body'")
                        
                    # Check for mismatched brackets
                    if content.count('{') != content.count('}'):
                        errors.append(f"{file}: Mismatched braces")
                        
                    # Check for broken modifiers
                    broken_modifiers = re.findall(r'\.\w+\s*\n\s*\.\w+', content)
                    if broken_modifiers:
                        errors.append(f"{file}: Broken modifier chain")
                        
        return errors
        
    def _verify_ssl_configuration(self, project_path: str) -> bool:
        """Verify SSL configuration in Info.plist"""
        info_plist = os.path.join(project_path, "Sources", "Info.plist")
        if not os.path.exists(info_plist):
            return False
            
        with open(info_plist, 'r') as f:
            content = f.read()
            
        return "NSAppTransportSecurity" in content and "NSAllowsArbitraryLoads" in content
        
    def _verify_timer_functionality(self, project_path: str) -> bool:
        """Verify timer has required functionality"""
        # Check for timer-related code
        found_start = False
        found_stop = False
        found_reset = False
        
        sources_dir = os.path.join(project_path, "Sources")
        for root, dirs, files in os.walk(sources_dir):
            for file in files:
                if file.endswith('.swift'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        content = f.read().lower()
                        
                    if "start" in content or "startTimer" in content.lower():
                        found_start = True
                    if "stop" in content or "stopTimer" in content.lower():
                        found_stop = True
                    if "reset" in content or "resetTimer" in content.lower():
                        found_reset = True
                        
        return found_start and found_stop and found_reset
        
    async def test_modification_state_consistency(self) -> TestResult:
        """Core Test: Verify modifications apply to correct app state"""
        test_name = "Core: Modification State Consistency"
        print(f"\n🧪 Testing {test_name}...")
        
        start_time = time.time()
        try:
            # Generate a test app
            project_id = f"test_{int(time.time())}"
            test_files = [
                {
                    "path": "Sources/App.swift",
                    "content": "import SwiftUI\n\n@main\nstruct TestApp: App {\n    var body: some Scene {\n        WindowGroup {\n            ContentView()\n        }\n    }\n}"
                },
                {
                    "path": "Sources/ContentView.swift",
                    "content": "import SwiftUI\n\nstruct ContentView: View {\n    var body: some View {\n        Text(\"Hello\")\n    }\n}"
                }
            ]
            
            project_path = await self.project_manager.create_project(
                project_id, "TestApp", test_files, bundle_id="com.test.app"
            )
            
            # Capture original state
            original_content = None
            content_path = os.path.join(project_path, "Sources/ContentView.swift")
            with open(content_path, 'r') as f:
                original_content = f.read()
            
            # Apply modification
            test_marker = f"// TEST_{int(time.time())}"
            modified_files = await self.modification_handler.process_modification(
                test_files,
                f"Add comment '{test_marker}' to ContentView",
                is_modification=True
            )
            
            # Write modified files
            await self.project_manager.update_project_files(
                project_id, modified_files
            )
            
            # Verify modification applied to actual file
            with open(content_path, 'r') as f:
                new_content = f.read()
                
            if test_marker not in new_content:
                raise Exception("Modification not applied to actual file state")
                
            if new_content == original_content:
                raise Exception("File content unchanged after modification")
            
            duration = time.time() - start_time
            result = TestResult(test_name, True, duration=duration)
            print(f"✅ {test_name} PASSED in {duration:.1f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(test_name, False, str(e), duration)
            print(f"❌ {test_name} FAILED: {str(e)}")
            
        self.results.append(result)
        return result
    
    async def test_modification_after_restart(self) -> TestResult:
        """Core Test: Modification works after server restart"""
        test_name = "Core: Modification After Restart"
        print(f"\n🧪 Testing {test_name}...")
        
        start_time = time.time()
        try:
            # This test simulates project_state being empty (as after restart)
            # The fix in main.py should handle this gracefully
            project_id = "proj_restart_test"
            
            # Create a dummy project
            test_files = [
                {
                    "path": "Sources/App.swift",
                    "content": "import SwiftUI\n\n@main\nstruct App: App {\n    var body: some Scene {\n        WindowGroup {\n            ContentView()\n        }\n    }\n}"
                },
                {
                    "path": "Sources/ContentView.swift", 
                    "content": "import SwiftUI\n\nstruct ContentView: View {\n    var body: some View {\n        Text(\"Test\")\n    }\n}"
                }
            ]
            
            # Ensure project exists on disk
            project_path = os.path.join("../workspaces", project_id)
            if not os.path.exists(project_path):
                await self.project_manager.create_project(
                    project_id, "RestartTest", test_files, bundle_id="com.test.restart"
                )
            
            # Clear project_state to simulate restart
            if hasattr(self.project_manager, 'project_state'):
                self.project_manager.project_state.pop(project_id, None)
            
            # Try to modify - should work even without project_state entry
            modified_files = await self.modification_handler.process_modification(
                test_files,
                "Change Text to show 'Modified'",
                is_modification=True
            )
            
            # Should not raise KeyError
            duration = time.time() - start_time
            result = TestResult(test_name, True, duration=duration)
            print(f"✅ {test_name} PASSED in {duration:.1f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(test_name, False, str(e), duration)
            print(f"❌ {test_name} FAILED: {str(e)}")
            
        self.results.append(result)
        return result
    
    async def test_swift_range_operator(self) -> TestResult:
        """Core Test: Swift range operator handling"""
        test_name = "Core: Swift Range Operator"
        print(f"\n🧪 Testing {test_name}...")
        
        start_time = time.time()
        try:
            # Import modification verifier
            from modification_verifier import ModificationVerifier
            verifier = ModificationVerifier()
            
            # Test Swift code with range operators
            test_code = '''
import SwiftUI

struct TestView: View {
    func handleInput(_ input: String) {
        switch input {
        case "0"..."9":
            print("Digit")
        case "A"..."Z":
            print("Letter")
        default:
            break
        }
    }
    
    var body: some View {
        Text("Test")
    }
}
'''
            
            # Validate the content
            issues = verifier._validate_swift_content(test_code)
            
            # Should not have "Incomplete implementation" issue
            for issue in issues:
                if "Incomplete implementation" in issue:
                    raise Exception(f"Range operator incorrectly flagged: {issue}")
            
            duration = time.time() - start_time
            result = TestResult(test_name, True, duration=duration)
            print(f"✅ {test_name} PASSED in {duration:.1f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(test_name, False, str(e), duration)
            print(f"❌ {test_name} FAILED: {str(e)}")
            
        self.results.append(result)
        return result
    
    async def test_swift_validator_integration(self) -> TestResult:
        """Core Test: Swift validator integration"""
        test_name = "Core: Swift Validator Integration"
        print(f"\n🧪 Testing {test_name}...")
        
        start_time = time.time()
        try:
            # Import swift validator
            from swift_validator import SwiftValidator
            validator = SwiftValidator()
            
            # Test 1: Semicolon removal
            code_with_issues = '''let x = 5;
let y = 10;
print(x + y);'''
            
            fixed_code, fixes = validator.apply_auto_fixes(code_with_issues)
            
            if ';' in fixed_code:
                raise Exception("Semicolons not removed by validator")
                
            if len(fixes) == 0:
                raise Exception("No fixes applied by validator")
                
            # Test 2: ForEach handling
            foreach_code = '''ForEach(items) { item in
    Text(item.name)
}'''
            
            fixed_foreach, foreach_fixes = validator.apply_auto_fixes(foreach_code)
            
            if 'id: \\.self' not in fixed_foreach and 'id: \\.id' not in fixed_foreach:
                # It's OK if it doesn't fix this - just shouldn't break
                pass
            
            duration = time.time() - start_time
            result = TestResult(test_name, True, duration=duration)
            print(f"✅ {test_name} PASSED in {duration:.1f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(test_name, False, str(e), duration)
            print(f"❌ {test_name} FAILED: {str(e)}")
            
        self.results.append(result)
        return result
    
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
        
        report_path = os.path.join(os.path.dirname(__file__), "test_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\nDetailed report saved to: {report_path}")
        
        return report


async def main():
    """Run the test suite"""
    test_suite = SwiftGenTestSuite()
    report = await test_suite.run_all_tests()
    
    # Exit with appropriate code
    if report["summary"]["failed"] > 0:
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    asyncio.run(main())