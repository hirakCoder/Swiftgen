# SwiftGen Regression Testing Plan
## Ensuring Stability with Every Change

### Overview
This document outlines the regression testing strategy to ensure that new features and fixes don't break existing functionality. Every critical change must pass these tests before merging to the develop or main branch.

---

## 🧪 Test Categories

### 1. Core Functionality Tests

#### 1.1 Basic App Generation
```python
# test_core_generation.py
class TestCoreGeneration:
    test_cases = [
        "Create a simple counter app",
        "Build a todo list with add and delete",
        "Make a timer with start and stop",
        "Create a calculator with basic operations"
    ]
    
    def test_basic_apps(self):
        for description in self.test_cases:
            # Generate app
            # Verify build success
            # Check simulator launch
            # Validate no crashes
```

#### 1.2 Modification System
```python
class TestModifications:
    scenarios = [
        ("counter app", "add dark theme"),
        ("todo app", "add search functionality"),
        ("timer app", "change UI colors to blue")
    ]
    
    def test_modifications(self):
        for base_app, modification in self.scenarios:
            # Generate base app
            # Apply modification
            # Verify build success
            # Check modification applied
```

### 2. Error Recovery Tests

#### 2.1 Common Swift Errors
```python
class TestErrorRecovery:
    error_scenarios = [
        "missing_imports",
        "undefined_types",
        "protocol_conformance",
        "string_literal_errors",
        "exhaustive_switch"
    ]
    
    def test_recovery(self):
        for scenario in self.error_scenarios:
            # Inject specific error
            # Run recovery system
            # Verify fix applied
            # Check build success
```

### 3. Integration Tests

#### 3.1 WebSocket Communication
```python
class TestWebSocket:
    def test_connection_timing(self):
        # Start generation
        # Verify WebSocket connects
        # Check status updates received
        # Validate completion message
```

#### 3.2 Multi-LLM Fallback
```python
class TestLLMFallback:
    def test_fallback_mechanism(self):
        # Simulate primary LLM failure
        # Verify fallback triggered
        # Check secondary LLM used
        # Validate output quality
```

### 4. UI/UX Tests

#### 4.1 Progress Display
```javascript
// test_ui_progress.js
describe('Progress Display', () => {
    it('shows all generation stages', async () => {
        // Trigger generation
        // Check each stage displays
        // Verify stage transitions
        // Validate completion state
    });
});
```

#### 4.2 Error Handling
```javascript
describe('Error Display', () => {
    it('shows build errors properly', async () => {
        // Trigger failing generation
        // Check error message display
        // Verify error details shown
        // Test retry functionality
    });
});
```

---

## 🔄 Continuous Integration Pipeline

### GitHub Actions Workflow
```yaml
name: Regression Tests
on:
  pull_request:
    branches: [develop, main]
  push:
    branches: [develop]

jobs:
  backend-tests:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run Core Tests
        run: |
          cd backend
          pytest tests/test_core_generation.py -v
          pytest tests/test_modifications.py -v
          pytest tests/test_error_recovery.py -v
      
      - name: Run Integration Tests
        run: |
          cd backend
          pytest tests/test_integration.py -v
      
      - name: Generate Coverage Report
        run: |
          cd backend
          pytest --cov=. --cov-report=xml

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      
      - name: Run UI Tests
        run: |
          cd frontend
          npm test
      
      - name: Run E2E Tests
        run: |
          cd frontend
          npm run test:e2e

  build-verification:
    runs-on: macos-latest
    needs: [backend-tests, frontend-tests]
    steps:
      - name: Generate Test Apps
        run: |
          # Script to generate and build test apps
          python scripts/verify_builds.py
```

---

## 📋 Test Implementation Plan

### Phase 1: Core Tests (Week 1)
- [ ] Set up pytest framework
- [ ] Implement basic generation tests
- [ ] Create modification test suite
- [ ] Add WebSocket tests

### Phase 2: Error Recovery Tests (Week 2)
- [ ] Create error injection framework
- [ ] Test each recovery strategy
- [ ] Validate pattern-based fixes
- [ ] Test LLM fallback recovery

### Phase 3: UI Tests (Week 3)
- [ ] Set up Jest for frontend tests
- [ ] Create Playwright E2E tests
- [ ] Test progress indicators
- [ ] Validate error displays

### Phase 4: CI/CD Integration (Week 4)
- [ ] Configure GitHub Actions
- [ ] Set up test reporting
- [ ] Create build verification
- [ ] Implement automatic rollback

---

## 🎯 Critical Test Scenarios

### Must-Pass Before Any Release
1. **Simple App Generation**
   - Counter app builds and runs
   - Todo app with basic CRUD works
   - Timer app functions correctly

2. **Modification System**
   - Can add dark theme to any app
   - Can modify UI colors
   - Can add simple features

3. **Error Recovery**
   - Fixes missing imports
   - Handles undefined types
   - Resolves string errors

4. **WebSocket Updates**
   - Progress shows in real-time
   - Errors display properly
   - Completion state correct

---

## 📊 Test Metrics

### Coverage Goals
- **Unit Tests**: 80% code coverage
- **Integration Tests**: All API endpoints
- **E2E Tests**: Critical user paths
- **Error Recovery**: 90% success rate

### Performance Benchmarks
- **Generation Time**: <30s for simple apps
- **Build Time**: <20s for standard apps
- **Recovery Time**: <10s per attempt
- **WebSocket Latency**: <100ms

---

## 🔍 Monitoring & Alerts

### Test Failure Alerts
```python
# Slack notification on test failure
def notify_test_failure(test_name, error):
    slack_webhook.post({
        "text": f"❌ Regression Test Failed: {test_name}",
        "error": str(error),
        "branch": os.environ.get('GITHUB_REF'),
        "commit": os.environ.get('GITHUB_SHA')
    })
```

### Daily Test Report
```python
# Generate daily test summary
def generate_daily_report():
    return {
        "total_tests": count_all_tests(),
        "passed": count_passed_tests(),
        "failed": count_failed_tests(),
        "coverage": calculate_coverage(),
        "performance": measure_performance()
    }
```

---

## 🚀 Getting Started

### Local Test Execution
```bash
# Backend tests
cd backend
python -m pytest tests/ -v --cov=.

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e

# Full regression suite
./scripts/run_regression_tests.sh
```

### Adding New Tests
1. Create test file in appropriate directory
2. Follow naming convention: `test_<feature>.py`
3. Include in CI pipeline
4. Document in this plan
5. Set coverage requirements

---

## 📝 Test Case Template

```python
"""
Test: <Feature Name>
Purpose: <What this test validates>
Priority: <HIGH/MEDIUM/LOW>
Category: <CORE/INTEGRATION/UI/PERFORMANCE>
"""

import pytest
from datetime import datetime

class Test<FeatureName>:
    """Regression tests for <feature>"""
    
    @pytest.fixture
    def setup(self):
        """Test setup"""
        # Initialize test environment
        pass
    
    def test_basic_functionality(self, setup):
        """Test basic feature operation"""
        # Arrange
        # Act
        # Assert
        pass
    
    def test_error_cases(self, setup):
        """Test error handling"""
        # Test various failure scenarios
        pass
    
    def test_performance(self, setup):
        """Test performance requirements"""
        # Measure and validate performance
        pass
```

---

*Document Version: 1.0*  
*Last Updated: June 13, 2025*  
*Test Suite Version: 0.1.0*