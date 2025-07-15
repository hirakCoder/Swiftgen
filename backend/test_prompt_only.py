#!/usr/bin/env python3
"""Test just the prompt to see what's generated"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from enhanced_prompts import get_generation_prompts

# Get prompts
system_prompt, user_prompt = get_generation_prompts("TestCounter", "A simple counter app")

print("SYSTEM PROMPT LENGTH:", len(system_prompt))
print("\nSYSTEM PROMPT PREVIEW (first 500 chars):")
print(system_prompt[:500])
print("\n...")
print("\nKEY SECTIONS FOUND:")
sections = [
    "UI QUALITY PRINCIPLES",
    "UI ANTI-PATTERNS", 
    "UI BEST PRACTICES",
    "APP-SPECIFIC UI GUIDELINES",
    "HIG-COMPLIANT UI COMPONENTS"
]
for section in sections:
    if section in system_prompt:
        print(f"✅ {section}")
        # Find and show a bit of that section
        idx = system_prompt.find(section)
        preview = system_prompt[idx:idx+200].split('\n')[0:3]
        for line in preview:
            print(f"   {line[:60]}...")
    else:
        print(f"❌ {section}")

print("\n\nUSER PROMPT LENGTH:", len(user_prompt))
print("\nUSER PROMPT PREVIEW:")
print(user_prompt[:300])