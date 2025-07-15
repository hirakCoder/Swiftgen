#!/usr/bin/env python3
"""Test full generation with quality checks"""

import asyncio
import sys
import os
import re

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def main():
    from enhanced_claude_service import EnhancedClaudeService
    from ui_quality_validator import UIQualityValidator
    
    print("🧪 Testing Full Generation with Quality Improvements")
    print("="*60)
    
    service = EnhancedClaudeService()
    validator = UIQualityValidator()
    
    # Test simple counter app
    print("\n📱 Generating Counter App...")
    
    result = await service.generate_ios_app(
        description="Create a simple counter app with increment and decrement buttons. Display the count prominently.",
        app_name="SimpleCounter"  
    )
    
    print(f"Success: {result.get('success', False)}")
    
    if result.get("success") and result.get("files"):
        print("✅ Generation successful!")
        
        # Analyze generated code
        files = result["files"]
        print(f"\nFiles generated: {len(files)}")
        
        # Find ContentView
        content_view = None
        for file in files:
            print(f"  - {file['path']}")
            if "ContentView" in file["path"]:
                content_view = file["content"]
        
        if content_view:
            print("\n🔍 Quality Analysis:")
            
            # Count UI elements
            gradients = len(re.findall(r'(Linear|Radial|Angular)Gradient', content_view))
            custom_colors = len(re.findall(r'Color\(red:|Color\(#|Color\(hex:', content_view))
            system_colors = len(re.findall(r'Color\.(primary|secondary|accentColor)|Color\(\.system', content_view))
            animations = len(re.findall(r'\.animation\(|withAnimation', content_view))
            
            print(f"  Gradients: {gradients} {'✅' if gradients <= 1 else '❌ (should be ≤1)'}")
            print(f"  Custom colors: {custom_colors} {'✅' if custom_colors == 0 else '❌ (should be 0)'}") 
            print(f"  System colors: {system_colors} {'✅' if system_colors > 0 else '❌ (should use system colors)'}")
            print(f"  Animations: {animations} {'✅' if animations <= 3 else '⚠️  (should be ≤3)'}")
            
            # Check for explicit text colors
            texts = content_view.count('Text(')
            text_with_color = len(re.findall(r'Text\([^}]+\.foreground(?:Color|Style)', content_view, re.DOTALL))
            print(f"  Text elements: {texts}")
            print(f"  Texts with color: {text_with_color} {'✅' if text_with_color >= texts/2 else '⚠️'}")
            
            # Run validator
            is_valid, issues, score = validator.validate_ui_quality(files)
            print(f"\n📊 UI Quality Score: {score}/100")
            
            if score >= 85:
                print("🎉 Excellent quality!")
            elif score >= 70:
                print("👍 Good quality")
            else:
                print("⚠️  Needs improvement")
            
            if issues:
                print("\nIssues detected:")
                for issue in issues[:5]:
                    print(f"  - {issue}")
            
            # Show a code snippet
            print("\n📝 Code Snippet (Button section):")
            lines = content_view.split('\n')
            in_button = False
            button_lines = []
            for line in lines:
                if 'Button' in line:
                    in_button = True
                if in_button:
                    button_lines.append(line)
                    if '}' in line and button_lines.count('{') == button_lines.count('}'):
                        break
            
            for i, line in enumerate(button_lines[:10]):
                print(f"    {line}")
                
    else:
        print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
        
        # If we have a response, show it
        if 'response' in result:
            print(f"\nResponse type: {type(result['response'])}")
            if isinstance(result['response'], str):
                print(f"Response preview: {result['response'][:200]}...")

if __name__ == "__main__":
    asyncio.run(main())