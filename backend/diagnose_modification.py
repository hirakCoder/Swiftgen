#!/usr/bin/env python3
"""
Diagnostic script to test why modifications are failing
"""

import os
import sys
import json

# Add backend to path
sys.path.append('backend')

# Check which components are available
print("=== SwiftGen Modification Diagnostic ===")
print()

# Check environment
print("1. Environment Settings:")
print(f"   USE_SMART_HANDLER: {os.environ.get('USE_SMART_HANDLER', 'true')}")
print(f"   USE_OPTIMIZED_HANDLER: {os.environ.get('USE_OPTIMIZED_HANDLER', 'false')}")
print()

# Check imports
print("2. Component Availability:")
components = {
    "SmartModificationHandler": False,
    "SimpleModificationHandler": False,
    "OptimizedModificationHandler": False,
    "ModificationVerifier": False,
    "EnhancedClaudeService": False,
    "json_fixer": False
}

for component in components:
    try:
        if component == "SmartModificationHandler":
            from smart_modification_handler import SmartModificationHandler
        elif component == "SimpleModificationHandler":
            from simple_modification_handler import SimpleModificationHandler
        elif component == "OptimizedModificationHandler":
            from optimized_modification_handler import OptimizedModificationHandler
        elif component == "ModificationVerifier":
            from modification_verifier import ModificationVerifier
        elif component == "EnhancedClaudeService":
            from enhanced_claude_service import EnhancedClaudeService
        elif component == "json_fixer":
            from json_fixer import extract_and_fix_json
        components[component] = True
        print(f"   ✓ {component}")
    except ImportError as e:
        print(f"   ✗ {component}: {str(e)}")

print()
print("3. Testing Validation Logic:")

# Test the validation that was causing issues
test_content = '''import SwiftUI

struct ContentView: View {
    @State private var count = 0
    
    var body: some View {
        VStack {
            Text("Count: \\(count)")
            Button("Increment") {
                count += 1
            }
        }
    }
}'''

print("   Testing Swift content validation...")

# Test modification verifier
try:
    from modification_verifier import ModificationVerifier
    verifier = ModificationVerifier()
    issues = verifier._validate_swift_content(test_content)
    if issues:
        print(f"   ✗ ModificationVerifier rejected valid Swift: {issues}")
    else:
        print(f"   ✓ ModificationVerifier accepted valid Swift")
except Exception as e:
    print(f"   ✗ ModificationVerifier test failed: {e}")

# Test smart handler validation
try:
    # Simulate the validation logic
    content_lower = test_content.lower()
    swift_indicators = [
        "import ", "struct ", "class ", "func ", "var ", "let ",
        "protocol ", "enum ", "extension ", "@main", "@observable",
        "view {", "body:", ".swift", "swiftui", "foundation"
    ]
    
    is_swift = any(indicator in content_lower for indicator in swift_indicators)
    if is_swift:
        print(f"   ✓ SmartHandler validation would accept this content")
    else:
        print(f"   ✗ SmartHandler validation would reject this content")
except Exception as e:
    print(f"   ✗ SmartHandler validation test failed: {e}")

print()
print("4. Handler Configuration:")

# Check which handler is being used
try:
    from enhanced_claude_service import EnhancedClaudeService
    service = EnhancedClaudeService()
    
    use_smart = os.environ.get("USE_SMART_HANDLER", "true").lower() == "true"
    use_optimized = os.environ.get("use_optimized_handler", "false").lower() == "true"
    
    if use_smart:
        print("   → SmartModificationHandler is ACTIVE (default)")
        try:
            from smart_modification_handler import SmartModificationHandler
            handler = SmartModificationHandler(service)
            print(f"   ✓ Handler initialized successfully")
            print(f"   - Max retries: {handler.max_retries}")
            print(f"   - Allow partial success: {handler.allow_partial_success}")
            print(f"   - Use progressive enhancement: {handler.use_progressive_enhancement}")
        except Exception as e:
            print(f"   ✗ Handler initialization failed: {e}")
    elif use_optimized:
        print("   → OptimizedModificationHandler is ACTIVE")
    else:
        print("   → SimpleModificationHandler is ACTIVE")
        
except Exception as e:
    print(f"   ✗ Could not determine handler configuration: {e}")

print()
print("5. Recent Issues Found:")
print("   - Overly strict Swift validation rejecting valid files")
print("   - SmartModificationHandler validation only accepting files starting with specific keywords")
print("   - ModificationVerifier using limited keyword list")
print()
print("Fixes Applied:")
print("   ✓ Made SmartModificationHandler validation more lenient")
print("   ✓ Made ModificationVerifier validation more lenient")
print("   ✓ Added fallback mechanism for xAI failures")
print("   ✓ Enhanced JSON fixer for unterminated strings")