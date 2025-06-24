# SwiftGen Testing Guide

## Overview

SwiftGen now has a comprehensive test suite ensuring production-ready quality with 80%+ code coverage.

## Test Structure

```
backend/tests/
├── conftest.py                     # Pytest configuration and fixtures
├── utils.py                        # Test utilities and helpers
├── test_enhanced_claude_service.py # Unit tests for LLM service
├── test_modification_handler.py    # Unit tests for modifications
├── test_build_service.py          # Unit tests for build system
├── test_chat_response_generator.py # Unit tests for chat responses
├── test_integration_app_generation.py  # Integration tests for app generation
└── test_integration_modification.py    # Integration tests for modifications
```

## Quick Start

### 1. Setup Development Environment

```bash
./setup.sh
```

This will:
- Create virtual environment
- Install dependencies
- Setup pre-commit hooks
- Create necessary directories

### 2. Run All Tests

```bash
./run_tests.py
```

Or manually:
```bash
pytest
```

### 3. Run Specific Test Categories

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Critical path tests
pytest -m critical

# Tests that don't require LLM APIs
pytest -m "not llm"
```

## Test Categories

### Unit Tests
- **Fast**: < 1 second per test
- **Isolated**: No external dependencies
- **Mocked**: All external services mocked
- **Coverage**: Individual module functionality

### Integration Tests
- **End-to-end**: Complete workflows
- **WebSocket**: Real-time communication
- **Build**: Compilation and error recovery
- **Modifications**: Full modification pipeline

### Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Tests taking > 5 seconds
- `@pytest.mark.llm` - Tests requiring LLM API access
- `@pytest.mark.critical` - Critical path tests

## Coverage

Current coverage targets:
- **Overall**: 80%+
- **Core modules**: 90%+
- **Critical paths**: 100%

View coverage report:
```bash
# Generate HTML report
pytest --cov=backend --cov-report=html

# Open in browser
open htmlcov/index.html
```

## CI/CD Pipeline

### GitHub Actions

Tests run automatically on:
- Push to main/develop
- Pull requests
- Tagged releases

### Test Matrix
- Python versions: 3.11, 3.12
- Operating systems: Ubuntu, macOS
- Test categories: Unit, Integration, Security

## Pre-commit Hooks

Installed automatically by setup.sh:

- **Code formatting**: Black
- **Linting**: Flake8
- **Import sorting**: isort
- **Type checking**: mypy
- **Security**: Bandit
- **Secrets detection**: Custom hook

Run manually:
```bash
pre-commit run --all-files
```

## Writing New Tests

### 1. Unit Test Template

```python
@pytest.mark.unit
class TestMyModule:
    @pytest.fixture
    def my_service(self):
        return MyService()
    
    def test_basic_functionality(self, my_service):
        result = my_service.do_something()
        assert result == expected
    
    @pytest.mark.asyncio
    async def test_async_functionality(self, my_service):
        result = await my_service.do_async()
        assert result is not None
```

### 2. Integration Test Template

```python
@pytest.mark.integration
class TestWorkflow:
    @pytest.mark.asyncio
    async def test_complete_flow(self, test_client):
        # Setup
        response = test_client.post("/api/endpoint", json=data)
        
        # Verify
        assert response.status_code == 200
        assert "expected_key" in response.json()
```

### 3. Using Fixtures

Common fixtures available:
- `test_client` - FastAPI test client
- `mock_openai` - Mocked OpenAI client
- `mock_anthropic` - Mocked Anthropic client
- `temp_workspace` - Temporary directory
- `mock_project_state` - Mock project data

## Debugging Tests

### Verbose Output
```bash
pytest -vv
```

### Print Statements
```bash
pytest -s
```

### Specific Test
```bash
pytest path/to/test.py::TestClass::test_method
```

### Debug with pdb
```python
import pdb; pdb.set_trace()
```

## Common Issues

### 1. Import Errors
- Ensure backend is in PYTHONPATH
- Check virtual environment activation

### 2. Async Tests
- Use `@pytest.mark.asyncio` decorator
- Use `async def` for test methods

### 3. Mocking
- Mock at import location, not definition
- Use `patch` as decorator or context manager

### 4. Timeouts
- Default timeout: 300 seconds
- Override: `@pytest.mark.timeout(60)`

## Best Practices

1. **Test Independence**: Each test should be independent
2. **Clear Names**: Test names should describe what they test
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Mock External Services**: Never call real APIs in tests
5. **Test Edge Cases**: Include error scenarios
6. **Keep Tests Fast**: Unit tests < 1s, integration < 10s

## Maintenance

### Update Dependencies
```bash
pip install --upgrade -r backend/requirements.txt
```

### Update Pre-commit
```bash
pre-commit autoupdate
```

### Clean Test Artifacts
```bash
find . -type d -name __pycache__ -exec rm -rf {} +
rm -rf .pytest_cache htmlcov .coverage
```

## Support

For test-related issues:
1. Check this guide
2. Review existing tests for examples
3. Check pytest documentation
4. Ask in project discussions