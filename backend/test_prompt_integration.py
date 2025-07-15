#!/usr/bin/env python3
"""Test that enhanced prompts are being used"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from enhanced_prompts import get_generation_prompts, get_modification_prompts

# Test generation prompts
print("Testing Enhanced Prompts Integration")
print("="*60)

print("\n1. Generation Prompt:")
print("-"*40)
system_prompt, user_prompt = get_generation_prompts("TestApp", "A simple test app")

# Check for our new anti-patterns section
if "UI ANTI-PATTERNS - NEVER DO THESE:" in system_prompt:
    print("✅ Anti-patterns section found!")
else:
    print("❌ Anti-patterns section missing!")

if "UI QUALITY PRINCIPLES" in system_prompt:
    print("✅ Quality principles found!")
else:
    print("❌ Quality principles missing!")

if "APP-SPECIFIC UI GUIDELINES" in system_prompt:
    print("✅ App-specific guidelines found!")
else:
    print("❌ App-specific guidelines missing!")

# Count key phrases
key_phrases = [
    "Multiple Gradients",
    "Gradient Text", 
    "Complex Backgrounds",
    "Simple, Clean Design",
    "System Colors Only",
    "CLARITY",
    "DEFERENCE",
    "DEPTH"
]

found = 0
for phrase in key_phrases:
    if phrase in system_prompt:
        found += 1

print(f"\n✅ Found {found}/{len(key_phrases)} key quality phrases")

print("\n2. Modification Prompt:")
print("-"*40)
mod_prompt = get_modification_prompts()

if "MODIFICATION QUALITY RULES" in mod_prompt:
    print("✅ Modification quality rules found!")
else:
    print("❌ Modification quality rules missing!")

if "NEVER ADD THESE (ANTI-PATTERNS)" in mod_prompt:
    print("✅ Modification anti-patterns found!")
else:
    print("❌ Modification anti-patterns missing!")

# Test iOS version consistency
print("\n3. iOS Version Consistency:")
print("-"*40)
if "Target iOS: 17.0" in system_prompt:
    print("✅ Generation targets iOS 17.0")
else:
    print("❌ Generation iOS version mismatch")

if "iOS 17.0 Target" in mod_prompt:
    print("✅ Modification targets iOS 17.0")
else:
    print("❌ Modification iOS version mismatch")

print("\n" + "="*60)
print("Enhanced prompts are properly integrated!" if found > 6 else "Some issues with prompt integration")