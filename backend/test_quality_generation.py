#!/usr/bin/env python3
"""Test the improved generation quality"""

import asyncio
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_generation():
    from enhanced_claude_service import EnhancedClaudeService
    from ui_quality_validator import UIQualityValidator
    
    print("🧪 Testing Improved Generation Quality")
    print("=" * 60)
    
    service = EnhancedClaudeService()
    validator = UIQualityValidator()
    
    # Test cases
    test_apps = [
        {
            "name": "TimerPro",
            "description": "Create a professional timer app with multiple timers, lap times, and sound alerts"
        },
        {
            "name": "CurrencyConverter",
            "description": "Build a currency converter app with real-time exchange rates, calculator, and favorite currencies"
        },
        {
            "name": "TodoMaster", 
            "description": "Create a todo list app with categories, due dates, priorities, and reminders"
        }
    ]
    
    for app in test_apps:
        print(f"\n📱 Generating {app['name']}...")
        print(f"   Description: {app['description']}")
        
        try:
            # Generate the app
            result = await service.generate_ios_app(
                description=app['description'],
                app_name=app['name']
            )
            
            # Check generation result
            print(f"\n✅ Generation Result:")
            print(f"   Success: {result.get('success', False)}")
            print(f"   iOS Version: {result.get('ios_version', 'Not set')}")
            print(f"   Files: {len(result.get('files', []))}")
            print(f"   Features: {result.get('features', [])[:3]}")
            
            # Validate UI quality
            if result.get('success') and 'files' in result:
                is_valid, issues, score = validator.validate_ui_quality(result['files'])
                
                print(f"\n🎨 UI Quality Check:")
                print(f"   Score: {score}/100")
                print(f"   Valid: {is_valid}")
                if issues:
                    print(f"   Issues:")
                    for issue in issues[:3]:
                        print(f"     - {issue}")
                
                # Show a snippet of the main view
                for file in result['files']:
                    if 'ContentView' in file['path']:
                        content = file['content']
                        # Find the body implementation
                        body_start = content.find('var body:')
                        if body_start != -1:
                            snippet = content[body_start:body_start+300]
                            print(f"\n📄 ContentView snippet:")
                            print("   ```swift")
                            for line in snippet.split('\n')[:8]:
                                print(f"   {line}")
                            print("   ```")
                        break
                        
        except Exception as e:
            print(f"\n❌ Error generating {app['name']}: {e}")
        
        print("\n" + "-" * 60)

if __name__ == "__main__":
    asyncio.run(test_generation())