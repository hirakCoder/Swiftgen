#!/usr/bin/env python3
"""Test a single modification with detailed monitoring"""

import asyncio
import aiohttp
import json
import websockets
from datetime import datetime

async def monitor_websocket(project_id, stop_event):
    """Monitor WebSocket for real-time updates"""
    uri = f"ws://localhost:8000/ws/{project_id}"
    messages = []
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"📡 Connected to WebSocket for {project_id}")
            
            while not stop_event.is_set():
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    msg_type = data.get('type', 'unknown')
                    
                    # Format based on message type
                    if msg_type == 'status':
                        print(f"[{timestamp}] 📍 {data.get('message', '')}")
                    elif msg_type == 'complete':
                        print(f"[{timestamp}] ✅ COMPLETE: {data.get('message', '')}")
                        # Print modification details
                        if 'modification_summary' in data:
                            print(f"   📝 Summary: {data['modification_summary']}")
                        if 'files_modified' in data:
                            print(f"   📁 Files Modified: {data['files_modified']}")
                        if 'changes_made' in data:
                            print(f"   🔧 Changes:")
                            for change in data['changes_made']:
                                print(f"      - {change}")
                    elif msg_type == 'error':
                        print(f"[{timestamp}] ❌ ERROR: {data.get('message', '')}")
                    else:
                        print(f"[{timestamp}] {data}")
                    
                    messages.append(data)
                    
                except asyncio.TimeoutError:
                    continue
                    
    except Exception as e:
        print(f"WebSocket error: {e}")
    
    return messages

async def test_single_modification():
    """Test a single modification with monitoring"""
    
    print("🧪 Single Modification Test")
    print("=" * 60)
    
    # Step 1: Create a simple app
    app_name = "ModTest"
    description = "Create a simple timer app with start and stop buttons"
    
    print(f"\n1️⃣ Creating {app_name}...")
    
    async with aiohttp.ClientSession() as session:
        # Create app
        async with session.post("http://localhost:8000/api/generate", 
                              json={"app_name": app_name, "description": description}) as resp:
            result = await resp.json()
            project_id = result.get('project_id')
            print(f"   Project ID: {project_id}")
    
    # Wait for build
    print("\n   ⏳ Waiting for initial build...")
    await asyncio.sleep(30)  # Give it time to build
    
    # Check status
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://localhost:8000/api/projects/{project_id}/status") as resp:
            status = await resp.json()
            print(f"   Build Status: {status.get('build_status')}")
            print(f"   Files: {status.get('file_count')}")
    
    if status.get('build_status') != 'success':
        print("   ❌ Initial build failed, aborting test")
        return
    
    # Step 2: Make modification with monitoring
    modification = "Add a dark mode toggle button in the top right corner"
    
    print(f"\n2️⃣ Making modification: {modification}")
    
    # Start WebSocket monitoring
    stop_event = asyncio.Event()
    monitor_task = asyncio.create_task(monitor_websocket(project_id, stop_event))
    
    # Make modification request
    async with aiohttp.ClientSession() as session:
        async with session.post("http://localhost:8000/api/modify", 
                              json={"project_id": project_id, "modification": modification}) as resp:
            mod_result = await resp.json()
            print(f"   Modification started: {mod_result}")
    
    # Monitor for 60 seconds
    await asyncio.sleep(60)
    stop_event.set()
    
    # Wait for monitor to finish
    messages = await monitor_task
    
    # Final status check
    print(f"\n3️⃣ Final Status Check")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://localhost:8000/api/projects/{project_id}/status") as resp:
            final_status = await resp.json()
            print(f"   Build Status: {final_status.get('build_status')}")
    
    # Analyze results
    print(f"\n📊 Analysis:")
    
    # Check if we got clear modification feedback
    complete_messages = [m for m in messages if m.get('type') == 'complete']
    if complete_messages:
        last_complete = complete_messages[-1]
        if 'modification_summary' in last_complete or 'files_modified' in last_complete:
            print("   ✅ Clear modification feedback provided")
        else:
            print("   ❌ No clear modification details in completion message")
    else:
        print("   ❌ No completion message received")
    
    # Check for errors
    error_messages = [m for m in messages if m.get('type') == 'error']
    if error_messages:
        print(f"   ⚠️  {len(error_messages)} errors during modification")
        for err in error_messages:
            print(f"      - {err.get('message', 'Unknown error')}")
    
    # Check for duplicate file issues
    all_text = ' '.join(str(m) for m in messages)
    if 'duplicate' in all_text.lower() or 'used twice' in all_text:
        print("   ❌ Duplicate file issue detected!")
    else:
        print("   ✅ No duplicate file issues")

async def main():
    await test_single_modification()

if __name__ == "__main__":
    asyncio.run(main())