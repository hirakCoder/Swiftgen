#!/usr/bin/env python3
"""
Direct test of UI quality improvements
"""

import asyncio
import sys
import os
import re

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def main():
    # Import after path is set
    from enhanced_claude_service import EnhancedClaudeService
    from ui_quality_validator import UIQualityValidator
    
    print("🧪 Testing UI Quality Improvements - Sample Generation")
    print("="*60)
    
    # Initialize service
    service = EnhancedClaudeService()
    validator = UIQualityValidator()
    
    # Test 1: Simple Timer App
    print("\n📱 Generating Timer App...")
    try:
        result = await service.generate_ios_app(
            description="Create a simple timer app with start, pause, and reset buttons. Display time in MM:SS format.",
            app_name="SimpleTimer"
        )
        
        if result.get("success") and result.get("files"):
            print("✅ Generation successful!")
            
            # Get main content file
            content_file = None
            for file in result["files"]:
                if "ContentView" in file["path"]:
                    content_file = file
                    break
            
            if content_file:
                content = content_file["content"]
                
                # Quick quality checks
                print("\n🔍 Quality Checks:")
                
                # Check for gradients
                gradient_count = len(re.findall(r'(Linear|Radial|Angular)Gradient', content))
                print(f"  Gradients: {gradient_count} {'✅' if gradient_count <= 1 else '❌'}")
                
                # Check for system colors
                system_colors = len(re.findall(r'Color\.(primary|secondary|accentColor)|Color\(\.system', content))
                custom_colors = len(re.findall(r'Color\(red:|Color\(#|Color\(hex:', content))
                print(f"  System colors: {system_colors} ✅")
                print(f"  Custom colors: {custom_colors} {'✅' if custom_colors == 0 else '❌'}")
                
                # Check for explicit foreground colors
                texts = len(re.findall(r'Text\(', content))
                foreground_colors = len(re.findall(r'\.foregroundColor|\.foregroundStyle', content))
                print(f"  Texts: {texts}, Foreground colors: {foreground_colors}")
                
                # Run full validation
                is_valid, issues, score = validator.validate_ui_quality(result["files"])
                print(f"\n📊 UI Quality Score: {score}/100 {'✅' if score >= 85 else '⚠️'}")
                
                if issues:
                    print("\nIssues found:")
                    for issue in issues[:3]:
                        print(f"  - {issue}")
                
                # Show a snippet of the generated code
                print("\n📝 Code Snippet (ContentView):")
                lines = content.split('\n')
                for i, line in enumerate(lines[20:40]):  # Show lines 20-40
                    if any(keyword in line for keyword in ['Text', 'Button', 'Color', 'Gradient']):
                        print(f"  {i+20}: {line.strip()}")
                        
        else:
            print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Test Modification
    print("\n\n🔧 Testing Modification...")
    if 'result' in locals() and result.get("success"):
        try:
            mod_result = await service.modify_ios_app(
                app_name="SimpleTimer",
                description="Timer app", 
                modification="Add a dark mode toggle",
                files=result["files"]
            )
            
            if mod_result.get("files"):
                print("✅ Modification successful!")
                
                # Check quality maintained
                is_valid, issues, score = validator.validate_ui_quality(mod_result["files"])
                print(f"📊 Quality after modification: {score}/100")
                
                changes = mod_result.get("changes_made", [])
                print(f"\n Changes made: {len(changes)}")
                for change in changes[:3]:
                    print(f"  - {change}")
            else:
                print("❌ Modification failed")
                
        except Exception as e:
            print(f"❌ Modification error: {e}")

if __name__ == "__main__":
    # Run with proper event loop
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nTest failed: {e}")
        import traceback
        traceback.print_exc()