# SwiftGen Regression Test Guide

## Overview
This guide provides comprehensive regression testing procedures for SwiftGen MVP to ensure all functionality works correctly after changes.

## Test Environment Setup

### Prerequisites
1. Python 3.8+ installed
2. Xcode 15+ installed
3. iOS Simulator available
4. All dependencies installed (`pip install -r requirements.txt`)

### Starting the Server
```bash
cd backend
python main.py
```

Wait for: "Application startup complete" message

## Test Suites

### 1. Unit Tests
Run individual component tests without external dependencies.

```bash
# Test agents
python test_agents_unit.py

# Test complexity detection
python -m pytest tests/test_complexity_detector.py -v

# Test error recovery
python -m pytest tests/test_error_recovery.py -v
```

**Expected Results:**
- All tests should pass
- No import errors
- Test report generated

### 2. Integration Tests
Test complete workflows with the server running.

```bash
# Run comprehensive test suite
python test_swiftgen_comprehensive.py

# Run curl-based tests
./test_curl_commands.sh
```

**Expected Results:**
- Server responds to health checks
- App generation completes within 2 minutes
- Modifications apply successfully
- Simulator launches (if available)

### 3. App Generation Tests

#### Simple App Test
```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Create a simple counter app with increment and decrement buttons"}'
```

**Verify:**
- Response contains project_id
- Status changes from "queued" → "generating" → "building" → "completed"
- App launches in simulator
- Counter functionality works

#### Medium Complexity App Test
```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Build a todo list app with categories, local storage, and search functionality"}'
```

**Verify:**
- Uses 4 recovery attempts (check logs)
- Generates multiple Swift files
- Categories and search work
- Data persists between launches

#### Complex App Test
```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Create a weather app that fetches data from openweathermap API with 5-day forecast and location services"}'
```

**Verify:**
- Uses 5 recovery attempts
- SSL configuration added for API
- Network code generated
- Location permissions configured

### 4. Modification Tests

First, generate a base app:
```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Create a simple notes app"}'
```

Note the project_id from response, then test modifications:

#### Test 1: Add Dark Mode
```bash
curl -X POST http://localhost:8000/api/modify \
  -H "Content-Type: application/json" \
  -d '{"project_id": "PROJECT_ID", "modification": "Add a dark mode toggle in settings"}'
```

**Verify:**
- Dark mode toggle appears
- Theme persists between launches
- All screens update correctly

#### Test 2: Change UI
```bash
curl -X POST http://localhost:8000/api/modify \
  -H "Content-Type: application/json" \
  -d '{"project_id": "PROJECT_ID", "modification": "Change the color scheme to blue and add larger buttons"}'
```

**Verify:**
- Colors change to blue theme
- Buttons are visibly larger
- No syntax errors

#### Test 3: Add Feature
```bash
curl -X POST http://localhost:8000/api/modify \
  -H "Content-Type: application/json" \
  -d '{"project_id": "PROJECT_ID", "modification": "Add ability to export notes as PDF"}'
```

**Verify:**
- Export button added
- PDF generation works
- File sharing works

### 5. Error Recovery Tests

#### Test SSL Error Recovery
```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Create an app that fetches quotes from api.quotable.io"}'
```

**Verify:**
- SSL errors detected and fixed
- Info.plist updated with ATS settings
- API calls succeed

#### Test Syntax Error Recovery
Monitor logs while generating complex apps. Verify:
- Syntax errors are automatically fixed
- Recovery attempts increase with complexity
- Build eventually succeeds

### 6. Agent System Tests

Run agent-specific tests:
```bash
python -c "
import asyncio
from agent_coordinator import agent_coordinator
from agents.ui_agent import UIAgent
from agents.api_agent import APIAgent
from agents.build_agent import BuildAgent

async def test():
    # Register agents
    coordinator = agent_coordinator
    ui = UIAgent(coordinator)
    api = APIAgent(coordinator)
    build = BuildAgent(coordinator)
    
    coordinator.register_agent(ui)
    coordinator.register_agent(api)
    coordinator.register_agent(build)
    
    # Test coordination
    result = await coordinator.coordinate_task('generate_app', {
        'description': 'Test app'
    })
    print(f'Coordination result: {result}')
    
    # Check metrics
    metrics = coordinator.get_agent_metrics()
    print(f'Agent metrics: {metrics}')

asyncio.run(test())
"
```

### 7. Performance Tests

#### Response Time Test
```bash
time curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Create a calculator app"}'
```

**Expected:**
- Initial response < 1 second
- Simple app completion < 60 seconds
- Complex app completion < 180 seconds

#### Concurrent Request Test
```bash
# Generate multiple apps simultaneously
for i in {1..3}; do
  curl -X POST http://localhost:8000/api/generate \
    -H "Content-Type: application/json" \
    -d "{\"description\": \"Create test app $i\"}" &
done
wait
```

**Verify:**
- All requests processed
- No crashes or timeouts
- Each app generates successfully

## Regression Checklist

Before any release, verify:

- [ ] All unit tests pass
- [ ] Simple app generation works
- [ ] Complex app generation works
- [ ] Modifications apply correctly
- [ ] Dark mode can be added
- [ ] SSL errors are handled
- [ ] Simulator launches apps
- [ ] Error recovery works
- [ ] Agent coordination works
- [ ] No memory leaks (monitor during long tests)
- [ ] API response times acceptable
- [ ] Concurrent requests handled
- [ ] Old files cleaned up
- [ ] Documentation updated

## Common Issues and Solutions

### Issue: "Cannot connect to server"
**Solution:** Ensure server is running on port 8000

### Issue: "Simulator not available"
**Solution:** Open Xcode and download simulators

### Issue: "Build failed after 5 attempts"
**Check:**
- Error logs in backend/
- Xcode command line tools installed
- Bundle ID is valid

### Issue: "Modifications not applying"
**Check:**
- Project files exist on disk
- File permissions correct
- LLM API keys valid

## Automated Test Execution

Run all tests with single command:
```bash
./run_all_tests.sh
```

This script will:
1. Start the server
2. Run unit tests
3. Run integration tests
4. Generate test report
5. Clean up test artifacts

## Test Report

After running tests, check:
- `test_report.md` - Comprehensive results
- `test_results.txt` - Summary of curl tests
- `backend/logs/` - Detailed server logs

## Continuous Testing

For CI/CD integration:
```yaml
# .github/workflows/test.yml
name: SwiftGen Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: |
          python main.py &
          sleep 10
          python test_swiftgen_comprehensive.py
```

## Summary

Regular regression testing ensures SwiftGen remains stable and reliable. Run these tests:
- After any code changes
- Before deployments
- When updating dependencies
- After fixing bugs

Keep this guide updated with new test cases as features are added.