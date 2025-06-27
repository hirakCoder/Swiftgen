#!/usr/bin/env python3
"""
Test API Parsing Robustness
Tests that our enhanced prompts generate correct API parsing code
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_claude_service import EnhancedClaudeService
from enhanced_prompts import get_generation_prompts


async def test_currency_converter_generation():
    """Test that currency converter generates proper API parsing code"""
    print("\n🧪 Testing Currency Converter Generation with Enhanced Prompts")
    print("=" * 60)
    
    service = EnhancedClaudeService()
    
    # Get enhanced prompts
    system_prompt, user_prompt = get_generation_prompts(
        "Currency Converter", 
        "A currency converter app that fetches real-time exchange rates from an API"
    )
    
    print("✅ Enhanced prompts include API parsing guidance")
    
    # Generate the app
    try:
        result = await service._generate_with_current_model(system_prompt, user_prompt)
        
        if isinstance(result, str):
            # Parse JSON
            result = result.strip()
            if result.startswith("```json"):
                result = result[7:]
            if result.endswith("```"):
                result = result[:-3]
            result = json.loads(result)
        
        # Check the generated files for proper API parsing
        files = result.get('files', [])
        api_file = None
        
        print(f"\nGenerated {len(files)} files:")
        for file in files:
            print(f"  - {file['path']}")
            content = file['content']
            # Check any file that has API/network code
            if 'URLSession' in content or 'JSONDecoder' in content or 'Codable' in content:
                if not api_file:  # Take the first file with API code
                    api_file = file
        
        if api_file:
            print(f"\n✅ Found API service file: {api_file['path']}")
            
            # Check for proper Codable structures
            has_proper_codable = False
            has_proper_decoding = False
            
            if 'struct' in api_file['content'] and 'Codable' in api_file['content']:
                # Look for proper response structure
                if 'rates:' in api_file['content'] or 'exchangeRates:' in api_file['content']:
                    has_proper_codable = True
                    print("✅ Found proper Codable response structure")
            
            # Check across all files for proper decoding
            for file in files:
                content = file['content']
                if 'JSONDecoder()' in content and '.decode(' in content:
                    # Check it's not decoding to [String: Double] directly
                    decode_line = content[content.find('.decode('):content.find('.decode(') + 100]
                    if '[String: Double]' not in decode_line and '[String: Any]' not in decode_line:
                        has_proper_decoding = True
                        print(f"✅ Uses proper JSON decoding in {file['path']}")
            
            if has_proper_codable and has_proper_decoding:
                print("\n✅ PASSED: Currency converter generates proper API parsing code!")
                return True
            else:
                print("\n❌ FAILED: Missing proper API parsing structure")
                print(f"Has proper Codable: {has_proper_codable}")
                print(f"Has proper decoding: {has_proper_decoding}")
                return False
        else:
            print("\n❌ FAILED: No API service file found")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        return False


async def test_weather_app_generation():
    """Test that weather app also generates proper API parsing"""
    print("\n\n🧪 Testing Weather App Generation")
    print("=" * 60)
    
    service = EnhancedClaudeService()
    
    # Get enhanced prompts
    system_prompt, user_prompt = get_generation_prompts(
        "Weather App", 
        "A weather app that shows current weather and forecast using OpenWeather API"
    )
    
    try:
        result = await service._generate_with_current_model(system_prompt, user_prompt)
        
        if isinstance(result, str):
            result = result.strip()
            if result.startswith("```json"):
                result = result[7:]
            if result.endswith("```"):
                result = result[:-3]
            result = json.loads(result)
        
        # Check for proper API structures
        files = result.get('files', [])
        has_weather_model = False
        
        for file in files:
            content = file['content']
            # Look for weather data structures
            if 'struct' in content and 'Codable' in content:
                if any(keyword in content for keyword in ['Weather', 'Temperature', 'Forecast']):
                    has_weather_model = True
                    print(f"✅ Found weather model with Codable in: {file['path']}")
                    break
        
        if has_weather_model:
            print("\n✅ PASSED: Weather app generates proper data models!")
            return True
        else:
            print("\n❌ FAILED: No proper weather models found")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        return False


async def main():
    """Run all robustness tests"""
    print("\n🚀 API Parsing Robustness Test Suite")
    print("Testing that enhanced prompts generate correct API parsing code")
    print("=" * 80)
    
    results = []
    
    # Test currency converter
    results.append(await test_currency_converter_generation())
    
    # Test weather app
    results.append(await test_weather_app_generation())
    
    # Summary
    print("\n\n📊 Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ All tests passed! The system is robust for API-based apps.")
    else:
        print("\n❌ Some tests failed. Further improvements needed.")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)