#!/usr/bin/env python3
"""Minimal test to check prompt and generation"""

import asyncio
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_minimal():
    from enhanced_claude_service import EnhancedClaudeService
    from enhanced_prompts import get_generation_prompts
    
    # Check prompts first
    print("1. Checking prompts...")
    system_prompt, user_prompt = get_generation_prompts("TestApp", "A counter app")
    
    # Verify anti-patterns are there
    if "UI ANTI-PATTERNS" in system_prompt:
        print("✅ Anti-patterns in prompt")
    else:
        print("❌ Missing anti-patterns")
    
    # Try a very simple generation
    print("\n2. Testing generation...")
    service = EnhancedClaudeService()
    
    # Override to test directly
    simple_description = "Create a counter app with increment and decrement buttons"
    
    try:
        # Test the raw generation first
        system_prompt, user_prompt = get_generation_prompts("Counter", simple_description)
        
        # Try calling the model directly
        result = await service._generate_with_current_model(system_prompt, user_prompt)
        
        if result.get("success"):
            print("✅ Raw generation successful")
            
            # Check the content
            files = result.get("response", {}).get("files", [])
            if files:
                # Look at first file
                first_file = files[0]
                content = first_file.get("content", "")
                
                # Quick checks
                print(f"\n3. Content checks:")
                print(f"  - Has LinearGradient: {'LinearGradient' in content}")
                print(f"  - Has Color.primary: {'Color.primary' in content}")
                print(f"  - Has foregroundColor: {'foregroundColor' in content}")
                print(f"  - Has Text with color: {'.foregroundColor' in content}")
                
                # Print first few lines of ContentView
                for file in files:
                    if "ContentView" in file.get("path", ""):
                        lines = file["content"].split('\n')
                        print(f"\n4. ContentView preview (first 30 lines):")
                        for i, line in enumerate(lines[:30]):
                            if i < 30:
                                print(f"  {i+1}: {line}")
        else:
            print(f"❌ Generation failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_minimal())