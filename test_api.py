#!/usr/bin/env python3
import requests
import json

# Test the /api/generate endpoint
base_url = "http://localhost:8000"

# Test 1: Valid new app generation request
print("Test 1: Valid new app generation")
payload1 = {
    "description": "Create a simple calculator app",
    "ios_version": "17.0",
    "project_id": "proj_test123"
}
response1 = requests.post(f"{base_url}/api/generate", json=payload1)
print(f"Status: {response1.status_code}")
print(f"Response: {response1.text}\n")

# Test 2: Missing description field
print("Test 2: Missing description field")
payload2 = {
    "ios_version": "17.0",
    "project_id": "proj_test456"
}
response2 = requests.post(f"{base_url}/api/generate", json=payload2)
print(f"Status: {response2.status_code}")
print(f"Response: {response2.text}\n")

# Test 3: Modification request to /api/generate (wrong endpoint)
print("Test 3: Modification request to /api/generate (should fail)")
payload3 = {
    "project_id": "proj_existing",
    "modification": "Add a dark mode"
}
response3 = requests.post(f"{base_url}/api/generate", json=payload3)
print(f"Status: {response3.status_code}")
print(f"Response: {response3.text}\n")

# Test 4: Correct modification request to /api/modify
print("Test 4: Correct modification request to /api/modify")
payload4 = {
    "project_id": "proj_existing",
    "modification": "Add a dark mode"
}
response4 = requests.post(f"{base_url}/api/modify", json=payload4)
print(f"Status: {response4.status_code}")
print(f"Response: {response4.text[:200] if response4.status_code == 200 else response4.text}\n")