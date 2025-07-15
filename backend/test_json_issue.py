#!/usr/bin/env python3
"""Debug JSON parsing issue"""

import asyncio
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_generation_debug():
    from enhanced_claude_service import EnhancedClaudeService
    
    print("🔍 Debugging JSON parsing issue")
    print("="*60)
    
    service = EnhancedClaudeService()
    
    # Patch the _generate_with_current_model to see raw response
    original_method = service._generate_with_current_model
    
    async def debug_generate(system_prompt, user_prompt):
        print("\n📤 Sending request to LLM...")
        raw_response = await original_method(system_prompt, user_prompt)
        
        print(f"\n📥 Raw response type: {type(raw_response)}")
        print(f"📏 Response length: {len(str(raw_response))}")
        
        if isinstance(raw_response, str):
            print("\n📝 Response preview (first 500 chars):")
            print(raw_response[:500])
            print("\n...")
            print("\n📝 Response end (last 200 chars):")
            print(raw_response[-200:])
            
            # Check for common issues
            if raw_response.startswith("```json"):
                print("\n⚠️  Response starts with markdown code block")
            if not raw_response.strip().startswith("{"):
                print("\n⚠️  Response doesn't start with {")
            if not raw_response.strip().endswith("}"):
                print("\n⚠️  Response doesn't end with }")
                
            # Try to find JSON in response
            import re
            json_match = re.search(r'\{[\s\S]*\}', raw_response)
            if json_match:
                print(f"\n✅ Found JSON-like structure at position {json_match.start()}")
                json_str = json_match.group(0)
                try:
                    parsed = json.loads(json_str)
                    print("✅ JSON is valid!")
                    print(f"   Keys: {list(parsed.keys())}")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parse error: {e}")
                    # Show the problematic part
                    error_pos = e.pos
                    print(f"\n   Error around position {error_pos}:")
                    start = max(0, error_pos - 50)
                    end = min(len(json_str), error_pos + 50)
                    print(f"   ...{json_str[start:end]}...")
            else:
                print("\n❌ No JSON structure found in response")
                
        return raw_response
    
    # Replace method temporarily
    service._generate_with_current_model = debug_generate
    
    try:
        # Try a simple generation
        result = await service.generate_ios_app(
            description="Create a simple counter app with one button to increment",
            app_name="DebugCounter"
        )
        
        print(f"\n📊 Final result:")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Error: {result.get('error', 'None')}")
        
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_generation_debug())