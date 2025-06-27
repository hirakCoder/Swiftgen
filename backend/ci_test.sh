#!/bin/bash
# CI/CD Test Script for SwiftGen
# Run this before deploying any changes

set -e  # Exit on any error

echo "============================================"
echo "SwiftGen CI/CD Test Suite"
echo "============================================"

# Check Python version
echo "Checking Python version..."
python3 --version

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install/update dependencies
echo "Checking dependencies..."
pip install -q requests

# Start server in background
echo "Starting server..."
python main.py > ci_server.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
echo "Waiting for server to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Server started successfully"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Server failed to start"
        cat ci_server.log
        kill $SERVER_PID 2>/dev/null
        exit 1
    fi
    sleep 1
done

# Run core functionality tests
echo -e "\n🧪 Running Core Functionality Tests..."
python test_core_functionality.py
CORE_TEST_RESULT=$?

# Run modification verifier tests
echo -e "\n🧪 Testing Modification Verifier..."
python -c "
from modification_verifier import ModificationVerifier
verifier = ModificationVerifier()

# Test Swift range operator
code = '''
switch value {
case \"0\"...\"9\":
    print(\"digit\")
default:
    break
}
'''
issues = verifier._validate_swift_content(code)
incomplete = [i for i in issues if 'Incomplete' in i]
if incomplete:
    print('❌ Range operator test FAILED')
    exit(1)
else:
    print('✅ Range operator test PASSED')
"
VERIFIER_TEST_RESULT=$?

# Run Swift validator tests
echo -e "\n🧪 Testing Swift Validator..."
python -c "
from swift_validator import SwiftValidator
validator = SwiftValidator()

# Test semicolon removal
code = 'let x = 5;\\nlet y = 10;'
fixed, fixes = validator.apply_auto_fixes(code)
if ';' not in fixed:
    print('✅ Swift validator test PASSED')
else:
    print('❌ Swift validator test FAILED')
    exit(1)
"
VALIDATOR_TEST_RESULT=$?

# Function to clean up on exit
cleanup() {
    echo -e "\nCleaning up..."
    if [ ! -z "$SERVER_PID" ]; then
        kill -9 $SERVER_PID 2>/dev/null
        echo "Killed server process: PID $SERVER_PID"
    fi
    
    # Kill any other Python main.py processes
    for pid in $(ps aux | grep "python.*main.py" | grep -v grep | awk '{print $2}'); do
        kill -9 $pid 2>/dev/null
        echo "Killed orphaned server process: PID $pid"
    done
    
    rm -f ci_server.log
}

# Set trap to clean up on exit (even on error)
trap cleanup EXIT

# Clean up
cleanup

# Report results
echo -e "\n============================================"
echo "Test Results:"
echo "============================================"

TOTAL_FAILED=0

if [ $CORE_TEST_RESULT -eq 0 ]; then
    echo "✅ Core Functionality Tests: PASSED"
else
    echo "❌ Core Functionality Tests: FAILED"
    TOTAL_FAILED=$((TOTAL_FAILED + 1))
fi

if [ $VERIFIER_TEST_RESULT -eq 0 ]; then
    echo "✅ Modification Verifier: PASSED"
else
    echo "❌ Modification Verifier: FAILED"
    TOTAL_FAILED=$((TOTAL_FAILED + 1))
fi

if [ $VALIDATOR_TEST_RESULT -eq 0 ]; then
    echo "✅ Swift Validator: PASSED"
else
    echo "❌ Swift Validator: FAILED"
    TOTAL_FAILED=$((TOTAL_FAILED + 1))
fi

echo "============================================"

if [ $TOTAL_FAILED -eq 0 ]; then
    echo "✅ All tests PASSED! Safe to deploy."
    exit 0
else
    echo "❌ $TOTAL_FAILED test suite(s) FAILED! Do not deploy."
    exit 1
fi