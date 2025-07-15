#!/usr/bin/env python3
"""Test with proper environment loading"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_simple():
    from enhanced_claude_service import EnhancedClaudeService
    from ui_quality_validator import UIQualityValidator
    
    print("🧪 Testing generation with UI quality improvements")
    print("="*60)
    
    service = EnhancedClaudeService()
    validator = UIQualityValidator()
    
    # Test a simple app
    print("\n📱 Generating simple counter app...")
    
    result = await service.generate_ios_app(
        description="Create a counter app with increment and decrement buttons",
        app_name="QualityCounter"
    )
    
    if result.get("success"):
        print("✅ Generation successful!")
        
        files = result.get("files", [])
        print(f"\nFiles generated: {len(files)}")
        
        # Run quality validation
        is_valid, issues, score = validator.validate_ui_quality(files)
        
        print(f"\n📊 UI Quality Score: {score}/100")
        print(f"Valid: {is_valid}")
        
        if issues:
            print("\nIssues found:")
            for issue in issues[:5]:
                print(f"  - {issue}")
        else:
            print("\n✨ No quality issues found!")
            
        # Check specific quality metrics
        for file in files:
            if "ContentView" in file.get("path", ""):
                content = file["content"]
                print("\n🔍 ContentView Analysis:")
                print(f"  Gradients: {content.count('Gradient')}")
                print(f"  System colors: {content.count('.primary') + content.count('.accentColor')}")
                print(f"  Custom colors: {content.count('Color(red:')}")
                print(f"  Explicit text colors: {content.count('.foregroundColor')}")
                print(f"  Button frame sizing: {content.count('.frame(minWidth:') + content.count('.frame(width:')}")
                break
    else:
        print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
        # Check for specific issues
        if "response" in result:
            print(f"\nDebug: Response type = {type(result['response'])}")

if __name__ == "__main__":
    asyncio.run(test_simple())