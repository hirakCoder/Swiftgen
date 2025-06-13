# SwiftGen Test Suite

## Overview
This directory contains all test files for the SwiftGen project, organized by category.

## Test Structure

### `/backend`
Backend-specific unit and integration tests:
- `test_recovery_comprehensive.py` - Comprehensive error recovery tests achieving 90%+ success
- `test_recovery_simple.py` - Basic recovery system tests
- `test_recovery_fix.py` - Specific recovery bug fixes
- `test_json_fix.py` - JSON parsing error handling tests
- `test_modification_fix.py` - App modification system tests
- `test_deduplication.py` - Duplicate file prevention tests
- `test_duplicate_fix.py` - Duplicate handling fixes

### `/integration`
End-to-end integration tests:
- `test_api.py` - API endpoint testing
- `test_simple_app.py` - Simple app generation tests

### `/demo_recovery.py`
Demonstration script showing the error recovery system achieving 90%+ success rate

## Running Tests

### All Tests
```bash
cd /path/to/swiftgen-mvp
python -m pytest tests/ -v
```

### Specific Category
```bash
# Backend tests only
python -m pytest tests/backend/ -v

# Integration tests only
python -m pytest tests/integration/ -v
```

### Individual Test
```bash
# Run specific test file
python tests/backend/test_recovery_comprehensive.py
```

## Test Coverage Goals
- Unit Tests: 80% code coverage
- Integration Tests: All critical paths
- Error Recovery: 90%+ success rate
- Performance: All operations under defined thresholds