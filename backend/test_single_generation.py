#!/usr/bin/env python3
"""Test a single app generation"""

import asyncio
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_single_generation():
    from enhanced_claude_service import EnhancedClaudeService
    from ui_quality_validator import UIQualityValidator
    
    print("🧪 Testing Single App Generation")
    print("=" * 60)
    
    service = EnhancedClaudeService()
    validator = UIQualityValidator()
    
    app_description = "Create a simple counter app with increment and decrement buttons"
    app_name = "SimpleCounter"
    
    print(f"\n📱 Generating {app_name}...")
    print(f"   Description: {app_description}")
    
    try:
        # Generate the app
        result = await service.generate_ios_app(
            description=app_description,
            app_name=app_name
        )
        
        # Check generation result
        print(f"\n✅ Generation Result:")
        print(f"   Success: {result.get('success', 'NOT SET')}")
        print(f"   iOS Version: {result.get('ios_version', 'NOT SET')}")
        print(f"   Files: {len(result.get('files', []))}")
        print(f"   Features: {result.get('features', [])}")
        
        # Check if files have content
        if 'files' in result:
            for file in result['files']:
                print(f"\n📄 {file['path']}:")
                print(f"   Content length: {len(file.get('content', ''))}")
                if file['path'].endswith('ContentView.swift'):
                    # Check for anti-patterns
                    content = file.get('content', '')
                    issues = []
                    
                    # Check for gradients
                    if 'LinearGradient' in content or 'RadialGradient' in content:
                        issues.append("Uses gradient (anti-pattern)")
                    
                    # Check for custom colors
                    if 'Color(red:' in content or 'Color(#' in content:
                        issues.append("Uses custom colors (anti-pattern)")
                    
                    # Check for proper foreground color
                    if '.foregroundColor(' not in content and '.foregroundStyle(' not in content:
                        issues.append("Missing explicit text colors")
                    
                    if issues:
                        print(f"   ⚠️  Issues: {issues}")
                    else:
                        print(f"   ✅ No anti-patterns detected")
        
        # Validate UI quality
        if result.get('success') and 'files' in result:
            is_valid, issues, score = validator.validate_ui_quality(result['files'])
            
            print(f"\n🎨 UI Quality Check:")
            print(f"   Score: {score}/100")
            print(f"   Valid: {is_valid}")
            if issues:
                print(f"   Issues:")
                for issue in issues:
                    print(f"     - {issue}")
                    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_single_generation())