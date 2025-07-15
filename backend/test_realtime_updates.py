#!/usr/bin/env python3
"""
Test script to verify real-time UI updates are working
"""

import asyncio
import websockets
import json
import requests
import time

async def test_realtime_updates():
    """Test that real-time updates are being sent properly"""
    
    project_id = f"test_proj_{int(time.time())}"
    
    print(f"Testing with project_id: {project_id}")
    
    # Connect to WebSocket
    uri = f"ws://localhost:8000/ws/{project_id}"
    
    received_messages = []
    
    async with websockets.connect(uri) as websocket:
        print("WebSocket connected!")
        
        # Wait for connection confirmation
        msg = await websocket.recv()
        data = json.loads(msg)
        print(f"Connection confirmed: {data}")
        
        # Start generation in background
        async def start_generation():
            await asyncio.sleep(0.5)  # Let WebSocket settle
            
            # Send generation request
            response = requests.post(
                "http://localhost:8000/api/generate",
                json={
                    "description": "Create a simple food delivery app",
                    "project_id": project_id
                }
            )
            print(f"Generation API response: {response.status_code}")
        
        # Start generation task
        gen_task = asyncio.create_task(start_generation())
        
        # Listen for messages
        try:
            while True:
                msg = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                data = json.loads(msg)
                
                print(f"\n[RECEIVED] Type: {data.get('type')}, Status: {data.get('status')}")
                print(f"           Message: {data.get('message', '')[:80]}...")
                
                received_messages.append(data)
                
                # If complete, break
                if data.get('type') == 'complete':
                    print("\nGeneration completed!")
                    break
                    
        except asyncio.TimeoutError:
            print("\nTimeout waiting for messages")
    
    # Analyze results
    print(f"\n\nSUMMARY:")
    print(f"Total messages received: {len(received_messages)}")
    
    status_messages = [m for m in received_messages if m.get('type') == 'status']
    print(f"Status updates: {len(status_messages)}")
    
    if status_messages:
        print("\nStatus progression:")
        for msg in status_messages:
            print(f"  - {msg.get('status')}: {msg.get('message', '')[:60]}...")
    
    # Check for key statuses
    statuses_found = {msg.get('status') for msg in status_messages}
    expected_statuses = {'initializing', 'analyzing', 'building'}
    missing_statuses = expected_statuses - statuses_found
    
    if missing_statuses:
        print(f"\n⚠️  Missing expected statuses: {missing_statuses}")
    else:
        print(f"\n✅ All expected statuses were sent!")
    
    return len(status_messages) > 0

if __name__ == "__main__":
    print("Testing SwiftGen Real-time Updates")
    print("==================================")
    print("Make sure the backend is running on http://localhost:8000")
    print()
    
    try:
        success = asyncio.run(test_realtime_updates())
        if success:
            print("\n✅ Test PASSED - Real-time updates are working!")
        else:
            print("\n❌ Test FAILED - No status updates received")
    except Exception as e:
        print(f"\n❌ Test FAILED with error: {e}")