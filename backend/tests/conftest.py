"""
Pytest configuration and fixtures for SwiftGen tests
"""
import os
import sys
import json
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock, patch
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import logging

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Test constants
TEST_PROJECT_ID = "test_proj_123"
TEST_APP_NAME = "TestApp"
TEST_DESCRIPTION = "A test app for unit tests"
TEST_FILES = [
    {
        "path": "Sources/App.swift",
        "content": 'import SwiftUI\n\n@main\nstruct TestApp: App {\n    var body: some Scene {\n        WindowGroup {\n            ContentView()\n        }\n    }\n}'
    },
    {
        "path": "Sources/ContentView.swift", 
        "content": 'import SwiftUI\n\nstruct ContentView: View {\n    var body: some View {\n        Text("Hello, World!")\n    }\n}'
    }
]


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_openai():
    """Mock OpenAI client"""
    with patch('openai.OpenAI') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        
        # Mock chat completions
        mock_completion = Mock()
        mock_completion.choices = [
            Mock(message=Mock(content=json.dumps({
                "files": TEST_FILES,
                "app_name": TEST_APP_NAME,
                "bundle_id": "com.test.app"
            })))
        ]
        mock_instance.chat.completions.create = Mock(return_value=mock_completion)
        
        yield mock_instance


@pytest.fixture
def mock_anthropic():
    """Mock Anthropic client"""
    with patch('anthropic.Anthropic') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        
        # Mock messages create
        mock_message = Mock()
        mock_message.content = [Mock(text=json.dumps({
            "files": TEST_FILES,
            "app_name": TEST_APP_NAME
        }))]
        mock_instance.messages.create = Mock(return_value=mock_message)
        
        yield mock_instance


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace directory"""
    temp_dir = tempfile.mkdtemp(prefix="swiftgen_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_project_state():
    """Mock project state"""
    return {
        "project_id": TEST_PROJECT_ID,
        "app_name": TEST_APP_NAME,
        "description": TEST_DESCRIPTION,
        "generated_files": TEST_FILES,
        "modification_history": [],
        "build_logs": [],
        "status": "ready"
    }


@pytest.fixture
async def test_client():
    """Create test client for FastAPI app"""
    from main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_websocket():
    """Mock WebSocket for testing"""
    ws = AsyncMock()
    ws.send_json = AsyncMock()
    ws.receive_json = AsyncMock()
    ws.close = AsyncMock()
    return ws


@pytest.fixture
def mock_llm_response():
    """Standard mock LLM response"""
    return {
        "files": TEST_FILES,
        "app_name": TEST_APP_NAME,
        "bundle_id": "com.test.app",
        "explanation": "Test app created successfully"
    }


@pytest.fixture
def mock_build_success():
    """Mock successful build result"""
    return {
        "success": True,
        "logs": ["Build succeeded"],
        "app_path": "/path/to/app",
        "errors": []
    }


@pytest.fixture
def mock_build_failure():
    """Mock failed build result"""
    return {
        "success": False,
        "logs": ["Build failed"],
        "errors": [{
            "file": "ContentView.swift",
            "line": 10,
            "column": 5,
            "message": "Cannot find 'InvalidType' in scope",
            "type": "type_not_found"
        }]
    }


@pytest.fixture
def mock_modification_request():
    """Mock modification request"""
    return {
        "modification": "Add a button to the main view",
        "files": TEST_FILES
    }


@pytest.fixture
def mock_ssl_error():
    """Mock SSL error for testing"""
    return {
        "error": "App Transport Security has blocked a cleartext HTTP",
        "domain": "api.example.com",
        "suggestion": "Use HTTPS instead of HTTP"
    }


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests"""
    # Reset any singleton patterns used in the codebase
    yield
    # Cleanup after test


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set test environment variables"""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("XAI_API_KEY", "test-key")
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")


class MockLLMService:
    """Mock LLM service for testing"""
    
    def __init__(self, response=None):
        self.response = response or {"files": TEST_FILES}
        self.call_count = 0
        self.last_prompt = None
    
    async def generate_ios_app(self, app_name, description, **kwargs):
        self.call_count += 1
        self.last_prompt = description
        return self.response
    
    async def apply_modification(self, modification, files, **kwargs):
        self.call_count += 1
        self.last_prompt = modification
        return self.response


@pytest.fixture
def mock_llm_service():
    """Create mock LLM service"""
    return MockLLMService()


# Markers for different test categories
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "llm: Tests requiring LLM")
    config.addinivalue_line("markers", "critical: Critical path tests")


# Skip tests that require API keys in CI
def pytest_collection_modifyitems(config, items):
    """Modify test collection based on environment"""
    if os.getenv("CI"):
        skip_ci = pytest.mark.skip(reason="Skipping in CI environment")
        for item in items:
            if "llm" in item.keywords:
                item.add_marker(skip_ci)


# Async test support
pytest_plugins = ['pytest_asyncio']