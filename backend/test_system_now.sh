#!/bin/bash

echo "===================================================="
echo "🚀 SwiftGen Production Test - July 14, 2025"
echo "===================================================="

BASE_URL="http://localhost:8000"

# Test 1: Health Check
echo -e "\n1. Testing Health Check..."
HEALTH=$(curl -s $BASE_URL/health)
if [[ $HEALTH == *"healthy"* ]]; then
    echo "✅ Health check PASSED"
else
    echo "❌ Health check FAILED"
    exit 1
fi

# Test 2: Simple Counter App
echo -e "\n2. Testing Simple Counter App Generation..."
RESPONSE=$(curl -s -X POST $BASE_URL/api/generate \
    -H "Content-Type: application/json" \
    -d '{
        "description": "Create a simple counter app with increment and decrement buttons. Show the count in large text.",
        "app_name": "SimpleCounter"
    }')

PROJECT_ID=$(echo $RESPONSE | grep -o '"project_id":"[^"]*' | cut -d'"' -f4)

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Failed to get project ID"
    echo "Response: $RESPONSE"
    exit 1
fi

echo "✅ Project created: $PROJECT_ID"

# Wait for build
echo "⏳ Waiting 30 seconds for build to complete..."
sleep 30

# Check status
echo -e "\n3. Checking Build Status..."
STATUS=$(curl -s $BASE_URL/api/status/$PROJECT_ID)

if [[ $STATUS == *'"build_success":true'* ]]; then
    echo "✅ BUILD SUCCESSFUL!"
    echo "Status: $STATUS" | jq '.' 2>/dev/null || echo "Status: $STATUS"
else
    echo "❌ Build failed or still in progress"
    echo "Status: $STATUS" | jq '.' 2>/dev/null || echo "Status: $STATUS"
fi

# Test 3: Complex App (Todo List)
echo -e "\n4. Testing Complex Todo App Generation..."
RESPONSE=$(curl -s -X POST $BASE_URL/api/generate \
    -H "Content-Type: application/json" \
    -d '{
        "description": "Create a todo list app with the ability to add, remove, and mark tasks as complete. Include categories and due dates.",
        "app_name": "TodoManager"
    }')

PROJECT_ID=$(echo $RESPONSE | grep -o '"project_id":"[^"]*' | cut -d'"' -f4)

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Failed to get project ID for complex app"
else
    echo "✅ Complex app project created: $PROJECT_ID"
    
    # Wait for build
    echo "⏳ Waiting 40 seconds for complex app build..."
    sleep 40
    
    # Check status
    STATUS=$(curl -s $BASE_URL/api/status/$PROJECT_ID)
    
    if [[ $STATUS == *'"build_success":true'* ]]; then
        echo "✅ COMPLEX APP BUILD SUCCESSFUL!"
    else
        echo "❌ Complex app build failed"
    fi
fi

echo -e "\n===================================================="
echo "📊 Test Summary Complete"
echo "===================================================="