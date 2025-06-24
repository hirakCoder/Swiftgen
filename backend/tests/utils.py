"""
Test utilities and helpers for SwiftGen tests
"""
import json
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, AsyncMock
import asyncio


class TestFileManager:
    """Helper for managing test files and directories"""
    
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or tempfile.mkdtemp(prefix="swiftgen_test_")
        self.created_dirs = []
    
    def create_project_structure(self, project_id: str) -> str:
        """Create a test project structure"""
        project_dir = os.path.join(self.base_dir, project_id)
        os.makedirs(project_dir, exist_ok=True)
        
        # Create standard iOS project structure
        sources_dir = os.path.join(project_dir, "Sources")
        os.makedirs(sources_dir, exist_ok=True)
        
        # Create basic files
        self.write_file(project_dir, "Info.plist", self.get_test_info_plist())
        self.write_file(sources_dir, "App.swift", self.get_test_app_swift())
        self.write_file(sources_dir, "ContentView.swift", self.get_test_content_view())
        
        self.created_dirs.append(project_dir)
        return project_dir
    
    def write_file(self, directory: str, filename: str, content: str):
        """Write a file to the test directory"""
        filepath = os.path.join(directory, filename)
        with open(filepath, 'w') as f:
            f.write(content)
    
    def cleanup(self):
        """Clean up all created directories"""
        for dir_path in self.created_dirs:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path, ignore_errors=True)
    
    @staticmethod
    def get_test_info_plist() -> str:
        return """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>TestApp</string>
    <key>CFBundleIdentifier</key>
    <string>com.test.app</string>
</dict>
</plist>"""
    
    @staticmethod
    def get_test_app_swift() -> str:
        return """import SwiftUI

@main
struct TestApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}"""
    
    @staticmethod
    def get_test_content_view() -> str:
        return """import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack {
            Text("Hello, World!")
                .padding()
        }
    }
}"""


class MockBuildService:
    """Mock build service for testing"""
    
    def __init__(self, should_succeed=True):
        self.should_succeed = should_succeed
        self.build_count = 0
        self.last_project_id = None
    
    async def build_project(self, project_id: str, files: List[Dict]) -> Dict:
        """Mock build project method"""
        self.build_count += 1
        self.last_project_id = project_id
        
        if self.should_succeed:
            return {
                "success": True,
                "logs": ["Build succeeded"],
                "app_path": f"/build/{project_id}/app"
            }
        else:
            return {
                "success": False,
                "logs": ["Build failed"],
                "errors": [{
                    "file": "ContentView.swift",
                    "line": 10,
                    "message": "Test error"
                }]
            }


class MockWebSocket:
    """Mock WebSocket for testing"""
    
    def __init__(self):
        self.messages_sent = []
        self.closed = False
    
    async def send_json(self, data: Dict):
        """Mock send_json method"""
        self.messages_sent.append(data)
    
    async def receive_json(self) -> Dict:
        """Mock receive_json method"""
        await asyncio.sleep(0.1)  # Simulate network delay
        return {"type": "test", "data": "test"}
    
    async def close(self):
        """Mock close method"""
        self.closed = True


def create_mock_llm_response(files: Optional[List[Dict]] = None) -> str:
    """Create a mock LLM response"""
    if files is None:
        files = [
            {
                "path": "Sources/App.swift",
                "content": "import SwiftUI\n\n@main\nstruct App: App { }"
            }
        ]
    
    return json.dumps({
        "files": files,
        "app_name": "TestApp",
        "bundle_id": "com.test.app",
        "explanation": "Test app created"
    })


def create_mock_modification_response(modified_files: Optional[List[Dict]] = None) -> str:
    """Create a mock modification response"""
    if modified_files is None:
        modified_files = [
            {
                "path": "Sources/ContentView.swift",
                "content": "import SwiftUI\n\nstruct ContentView: View {\n    var body: some View {\n        Button(\"Test\") { }\n    }\n}"
            }
        ]
    
    return json.dumps({
        "modified_files": modified_files,
        "explanation": "Added button as requested"
    })


def assert_websocket_message(messages: List[Dict], message_type: str) -> Optional[Dict]:
    """Assert that a specific message type was sent via WebSocket"""
    for msg in messages:
        if msg.get("type") == message_type:
            return msg
    
    raise AssertionError(f"No message of type '{message_type}' found in {len(messages)} messages")


def create_test_error(error_type: str = "syntax") -> Dict:
    """Create a test error object"""
    error_types = {
        "syntax": {
            "file": "ContentView.swift",
            "line": 10,
            "column": 5,
            "message": "Expected '}' in struct",
            "type": "syntax_error"
        },
        "type": {
            "file": "ContentView.swift",
            "line": 15,
            "column": 10,
            "message": "Cannot find 'CustomView' in scope",
            "type": "type_not_found"
        },
        "ssl": {
            "file": "NetworkManager.swift",
            "line": 25,
            "column": 0,
            "message": "App Transport Security has blocked a cleartext HTTP",
            "type": "ssl_error"
        }
    }
    
    return error_types.get(error_type, error_types["syntax"])


class AsyncContextManager:
    """Helper for testing async context managers"""
    
    def __init__(self, return_value=None):
        self.return_value = return_value
        self.entered = False
        self.exited = False
    
    async def __aenter__(self):
        self.entered = True
        return self.return_value
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.exited = True
        return False


def wait_for_condition(condition_func, timeout=5, interval=0.1):
    """Wait for a condition to become true"""
    import time
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(interval)
    
    return False