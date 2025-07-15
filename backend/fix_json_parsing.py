#!/usr/bin/env python3
"""Find and fix the JSON parsing issue"""

import asyncio
import sys
import os
import json
import re

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def debug_generation():
    from enhanced_claude_service import EnhancedClaudeService
    import logging
    
    # Enable debug logging
    logging.basicConfig(level=logging.DEBUG)
    
    print("🔍 Debugging JSON Parsing Issue")
    print("="*60)
    
    service = EnhancedClaudeService()
    
    # Monkey patch to intercept the response
    original_generate = service.generate_ios_app
    
    async def debug_generate(description, app_name=None, retry_count=0):
        print(f"\n📤 Calling generate_ios_app:")
        print(f"   Description: {description}")
        print(f"   App name: {app_name}")
        print(f"   Retry count: {retry_count}")
        
        try:
            # Call original method
            result = await original_generate(description, app_name, retry_count)
            
            print(f"\n📥 Result received:")
            print(f"   Type: {type(result)}")
            print(f"   Keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
            
            if isinstance(result, dict):
                print(f"   Success: {result.get('success', 'NOT SET')}")
                print(f"   Error: {result.get('error', 'None')}")
                print(f"   Has files: {'files' in result}")
                print(f"   Has response: {'response' in result}")
                
                if 'response' in result and isinstance(result['response'], str):
                    resp = result['response']
                    print(f"\n📝 Response analysis:")
                    print(f"   Length: {len(resp)}")
                    print(f"   Starts with: {resp[:50]}...")
                    print(f"   Ends with: ...{resp[-50:]}")
                    
                    # Try to parse it
                    try:
                        parsed = json.loads(resp)
                        print(f"   ✅ Valid JSON!")
                        print(f"   JSON keys: {list(parsed.keys())}")
                    except json.JSONDecodeError as e:
                        print(f"   ❌ JSON error: {e}")
                
                # Check where success=False is coming from
                if result.get('success') == False and 'files' in result:
                    print("\n⚠️  Success is False but files exist!")
                    print(f"   Number of files: {len(result.get('files', []))}")
            
            return result
            
        except Exception as e:
            print(f"\n❌ Exception in generate_ios_app: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    # Replace method
    service.generate_ios_app = debug_generate
    
    # Also check the _generate_with_current_model
    original_generate_model = service._generate_with_current_model
    
    async def debug_generate_model(system_prompt, user_prompt):
        print(f"\n🤖 _generate_with_current_model called")
        print(f"   System prompt length: {len(system_prompt)}")
        print(f"   User prompt length: {len(user_prompt)}")
        
        result = await original_generate_model(system_prompt, user_prompt)
        
        print(f"\n🤖 Model response:")
        print(f"   Type: {type(result)}")
        print(f"   Length: {len(str(result))}")
        
        if isinstance(result, str):
            # Check if it's valid JSON
            try:
                parsed = json.loads(result)
                print(f"   ✅ Valid JSON with keys: {list(parsed.keys())}")
                print(f"   ios_version in response: {parsed.get('ios_version', 'NOT FOUND')}")
            except:
                print(f"   ❌ Not valid JSON")
                print(f"   First 200 chars: {result[:200]}")
        
        return result
    
    service._generate_with_current_model = debug_generate_model
    
    # Test with a simple app
    try:
        result = await service.generate_ios_app(
            description="Create a simple counter app",
            app_name="DebugApp"
        )
        
        print("\n" + "="*60)
        print("FINAL RESULT:")
        print(f"Success: {result.get('success', False)}")
        print(f"Has files: {'files' in result and len(result['files']) > 0}")
        
    except Exception as e:
        print(f"\n💥 Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(debug_generation())