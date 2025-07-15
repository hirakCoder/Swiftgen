#!/usr/bin/env python3
"""Test the API directly to see full response"""

import asyncio
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_direct():
    import anthropic
    from enhanced_prompts import get_generation_prompts
    
    # Get API key
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        print("❌ No CLAUDE_API_KEY found")
        return
        
    print("🧪 Testing direct API call with enhanced prompts")
    print("="*60)
    
    # Get our enhanced prompts
    system_prompt, user_prompt = get_generation_prompts("TestCounter", "A simple counter app with increment button")
    
    # Truncate system prompt to see key parts
    print(f"\n📋 System prompt length: {len(system_prompt)}")
    print("\n🔍 Checking for key improvements:")
    improvements = [
        "UI ANTI-PATTERNS",
        "UI QUALITY PRINCIPLES", 
        "Target iOS: 17.0",
        "Multiple Gradients",
        "Simple, Clean Design"
    ]
    for imp in improvements:
        if imp in system_prompt:
            print(f"  ✅ {imp}")
        else:
            print(f"  ❌ {imp}")
    
    # Make direct API call
    print("\n📤 Making API call...")
    client = anthropic.AsyncAnthropic(api_key=api_key)
    
    try:
        message = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8192,
            temperature=0.7,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        response = message.content[0].text
        print(f"\n📥 Response length: {len(response)}")
        
        # Try to parse
        try:
            parsed = json.loads(response)
            print("\n✅ Valid JSON response!")
            print(f"   App name: {parsed.get('app_name')}")
            print(f"   iOS version: {parsed.get('ios_version')}")
            print(f"   Files: {len(parsed.get('files', []))}")
            
            # Check first file for quality
            if parsed.get('files'):
                for file in parsed['files']:
                    if 'ContentView' in file.get('path', ''):
                        content = file['content']
                        print("\n🔍 ContentView quality check:")
                        print(f"   LinearGradient count: {content.count('LinearGradient')}")
                        print(f"   Custom colors: {content.count('Color(red:')}")
                        print(f"   System colors: {content.count('Color.primary') + content.count('Color.accentColor')}")
                        print(f"   foregroundColor used: {content.count('foregroundColor')}")
                        
                        # Show button code
                        lines = content.split('\n')
                        button_start = -1
                        for i, line in enumerate(lines):
                            if 'Button' in line and button_start == -1:
                                button_start = i
                            if button_start >= 0 and i < button_start + 10:
                                print(f"   {i}: {line}")
                                
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON parse error: {e}")
            print("\nResponse preview:")
            print(response[:500])
            
    except Exception as e:
        print(f"\n❌ API error: {e}")

if __name__ == "__main__":
    asyncio.run(test_direct())