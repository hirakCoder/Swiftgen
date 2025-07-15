#!/usr/bin/env python3
"""
Simple test for timer app generation
"""

import asyncio
import httpx
import json
import time
import websockets


async def test_timer_with_websocket():
    """Test timer app generation with WebSocket monitoring"""
    print("\n" + "="*60)
    print("Testing Timer App Generation with WebSocket")
    print("="*60)
    
    project_id = f"test_timer_{int(time.time())}"
    
    # Connect to WebSocket first
    ws_url = f"ws://localhost:8000/ws/{project_id}"
    
    async with websockets.connect(ws_url) as websocket:
        print(f"✓ Connected to WebSocket: {ws_url}")
        
        # Start monitoring WebSocket messages in background
        async def monitor_ws():
            try:
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    print(f"📨 WS: {data.get('type', 'unknown')} - {data.get('message', '')}")
                    
                    # Check for completion
                    if data.get('status') == 'completed':
                        return True
                    elif data.get('status') == 'failed':
                        print(f"❌ Generation failed: {data.get('error', 'Unknown error')}")
                        return False
            except Exception as e:
                print(f"WS Error: {e}")
                return False
        
        # Start WebSocket monitoring task
        ws_task = asyncio.create_task(monitor_ws())
        
        # Make the generation request
        async with httpx.AsyncClient(timeout=60.0) as client:
            print("\n📤 Sending generation request...")
            response = await client.post(
                "http://localhost:8000/api/generate",
                json={
                    "description": "Create a simple timer app with start, stop and reset buttons",
                    "project_id": project_id
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Generation started: {data.get('app_name')} (ID: {project_id})")
            else:
                print(f"❌ Failed to start generation: {response.status_code}")
                print(f"Response: {response.text}")
                return
        
        # Wait for WebSocket task to complete or timeout
        try:
            result = await asyncio.wait_for(ws_task, timeout=120)
            
            if result:
                print("\n✅ Timer app generated successfully!")
                
                # Get final status
                async with httpx.AsyncClient() as client:
                    status_response = await client.get(
                        f"http://localhost:8000/api/project/{project_id}/status"
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"\n📊 Final Status:")
                        print(f"  - App Name: {status_data.get('app_name')}")
                        print(f"  - Files: {status_data.get('swift_file_count')}")
                        print(f"  - Status: {status_data.get('status')}")
                        
                        # List files
                        files_response = await client.get(
                            f"http://localhost:8000/api/project/{project_id}/files"
                        )
                        
                        if files_response.status_code == 200:
                            files_data = files_response.json()
                            print(f"\n📁 Generated Files:")
                            for file in files_data.get('files', []):
                                print(f"  - {file['path']} ({file['size']} bytes)")
            else:
                print("\n❌ Timer app generation failed!")
                
        except asyncio.TimeoutError:
            print("\n❌ Timeout waiting for generation to complete")


async def test_simple_timer():
    """Test timer app without WebSocket"""
    print("\n" + "="*60)
    print("Testing Timer App Generation (Simple)")
    print("="*60)
    
    project_id = f"test_timer_simple_{int(time.time())}"
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Generate the app
        print("📤 Sending generation request...")
        response = await client.post(
            "http://localhost:8000/api/generate",
            json={
                "description": "Create a simple timer app",
                "project_id": project_id
            }
        )
        
        if response.status_code != 200:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        data = response.json()
        print(f"✓ Started: {data.get('app_name')} (ID: {project_id})")
        
        # Poll for completion
        for i in range(30):  # 2.5 minutes max
            await asyncio.sleep(5)
            
            status_response = await client.get(
                f"http://localhost:8000/api/project/{project_id}/status"
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get('status', 'unknown')
                print(f"  Status check {i+1}: {status}")
                
                if status == 'completed':
                    print(f"\n✅ Success! Files: {status_data.get('swift_file_count')}")
                    return
                elif status == 'failed':
                    print(f"\n❌ Failed: {status_data.get('error')}")
                    return
            else:
                print(f"  Status check failed: {status_response.status_code}")
        
        print("\n❌ Timeout!")


if __name__ == "__main__":
    print("🚀 SwiftGen Timer App Test")
    
    # Test without WebSocket first
    asyncio.run(test_simple_timer())
    
    # Then test with WebSocket
    asyncio.run(test_timer_with_websocket())