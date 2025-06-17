"""
Common test utilities for SwiftGen tests
"""

import os
import sys
import time
import json
from typing import Any, Dict, List, Optional


class TestRunner:
    """Base class for test runners"""
    
    def __init__(self, test_suite_name: str):
        self.test_suite_name = test_suite_name
        self.start_time = time.time()
    
    def run_all_tests(self):
        """Override in subclasses"""
        raise NotImplementedError


def print_test_header(test_name: str):
    """Print a formatted test header"""
    print(f"\n🔍 Testing: {test_name}")
    print("-" * 40)


def print_test_result(success: bool, message: str = ""):
    """Print test result with emoji"""
    if success:
        print(f"✅ PASS: {message}" if message else "✅ PASS")
    else:
        print(f"❌ FAIL: {message}" if message else "❌ FAIL")


def create_test_file(path: str, content: str) -> str:
    """Create a test file and return its path"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    return path


def cleanup_test_files(paths: List[str]):
    """Clean up test files"""
    for path in paths:
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                import shutil
                shutil.rmtree(path)
        except:
            pass


def mock_swift_file(name: str = "ContentView.swift") -> Dict[str, str]:
    """Create a mock Swift file"""
    return {
        "path": f"Sources/{name}",
        "content": """import SwiftUI

struct ContentView: View {
    var body: some View {
        Text("Hello, World!")
    }
}
"""
    }


def mock_swift_files_with_errors() -> List[Dict[str, str]]:
    """Create mock Swift files with common errors"""
    return [
        {
            "path": "Sources/ContentView.swift",
            "content": """import SwiftUI

struct ContentView: View {
    @State private var tasks: [Task] = []
    
    var body: some View {
        NavigationView {
            List(tasks) { task in
                Text(task.title)
            }
        }
    }
}

struct Task: Identifiable {
    let id = UUID()
    let title: String
}
"""
        },
        {
            "path": "Sources/TimerView.swift",
            "content": """// Missing import SwiftUI

struct TimerView: View {
    @State private var timer: Timer?
    
    var body: some View {
        Text('Timer: 00:00')  // Single quotes
    }
}
"""
        }
    ]


def assert_file_contains(file_path: str, expected_content: str, message: str = ""):
    """Assert that a file contains expected content"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    assert expected_content in content, message or f"Expected '{expected_content}' not found in file"


def assert_json_valid(json_string: str, message: str = ""):
    """Assert that a string is valid JSON"""
    try:
        json.loads(json_string)
    except json.JSONDecodeError as e:
        raise AssertionError(message or f"Invalid JSON: {e}")


def measure_time(func):
    """Decorator to measure function execution time"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"⏱️  {func.__name__} took {duration:.3f}s")
        return result
    return wrapper