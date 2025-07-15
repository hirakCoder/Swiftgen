#!/usr/bin/env python3
"""Test that LLM routing fix works correctly"""

import sys
sys.path.append('backend')

from intelligent_llm_router import IntelligentLLMRouter

def test_routing():
    router = IntelligentLLMRouter()
    
    # Test calculator app
    calc_desc = "Create an advanced scientific calculator with complex mathematical functions including derivatives, integrals, matrix operations, and equation solving. Include a graphing capability for plotting functions."
    calc_type = router.analyze_request(calc_desc)
    calc_provider = router.route_initial_request(calc_desc)
    
    print(f"Calculator App:")
    print(f"  Description: {calc_desc[:50]}...")
    print(f"  Request Type: {calc_type}")
    print(f"  Routed to: {calc_provider}")
    print(f"  Expected: openai (GPT-4) or anthropic (Claude)")
    print(f"  ✅ PASS" if calc_provider in ["openai", "anthropic"] else "❌ FAIL")
    print()
    
    # Test weather app
    weather_desc = "Build a weather app that fetches real-time weather data from OpenWeatherMap API. Show current conditions, 7-day forecast, weather maps, and severe weather alerts."
    weather_type = router.analyze_request(weather_desc)
    weather_provider = router.route_initial_request(weather_desc)
    
    print(f"Weather App:")
    print(f"  Description: {weather_desc[:50]}...")
    print(f"  Request Type: {weather_type}")
    print(f"  Routed to: {weather_provider}")
    print(f"  Expected: anthropic (Claude) for API integration")
    print(f"  ✅ PASS" if weather_provider == "anthropic" else "❌ FAIL")
    print()
    
    # Test simple UI app
    ui_desc = "Create a beautiful timer app with animations and modern design"
    ui_type = router.analyze_request(ui_desc)
    ui_provider = router.route_initial_request(ui_desc)
    
    print(f"Timer App (UI-focused):")
    print(f"  Description: {ui_desc[:50]}...")
    print(f"  Request Type: {ui_type}")
    print(f"  Routed to: {ui_provider}")
    print(f"  Expected: xai (xAI Grok)")
    print(f"  ✅ PASS" if ui_provider == "xai" else "❌ FAIL")

if __name__ == "__main__":
    print("🧪 Testing LLM Routing Fix")
    print("="*60)
    test_routing()