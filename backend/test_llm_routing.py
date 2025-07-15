#!/usr/bin/env python3
"""Test LLM routing for different app types"""

import requests
import json
import time

def test_calculator_app():
    """Test calculator app - should route to Claude or GPT-4 for algorithms"""
    
    print("Testing Calculator App Generation (expecting Claude/GPT-4)...")
    
    url = "http://localhost:8000/api/generate"
    
    payload = {
        "description": "Create an advanced scientific calculator with complex mathematical functions including derivatives, integrals, matrix operations, and equation solving. Include a graphing capability for plotting functions.",
        "app_name": "MathGenius Pro"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=180)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: {result.get('message', 'App generation started')}")
            print(f"   Project ID: {result.get('project_id')}")
            return True, result.get('project_id')
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False, None

def test_weather_app():
    """Test weather app - should route to Claude for API integration"""
    
    print("\nTesting Weather App Generation (expecting Claude for API)...")
    
    url = "http://localhost:8000/api/generate"
    
    payload = {
        "description": "Build a weather app that fetches real-time weather data from OpenWeatherMap API. Show current conditions, 7-day forecast, weather maps, and severe weather alerts. Include location search and GPS-based weather.",
        "app_name": "WeatherPro"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=180)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: {result.get('message', 'App generation started')}")
            print(f"   Project ID: {result.get('project_id')}")
            return True, result.get('project_id')
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False, None

def test_game_app():
    """Test game app - complex logic should route to GPT-4"""
    
    print("\nTesting Game App Generation (expecting GPT-4 for complex logic)...")
    
    url = "http://localhost:8000/api/generate"
    
    payload = {
        "description": "Create a puzzle game with complex game mechanics including physics simulation, collision detection, level progression system, score tracking with leaderboards, and particle effects for visual feedback.",
        "app_name": "PuzzlePhysics"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=180)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: {result.get('message', 'App generation started')}")
            print(f"   Project ID: {result.get('project_id')}")
            return True, result.get('project_id')
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False, None

def check_routing_logs():
    """Check server logs to see which LLM was selected"""
    
    print("\n📊 Checking LLM Routing Results...")
    print("Please check server logs for '[ROUTER] Selected' messages")
    print("Expected routing:")
    print("  - MathGenius Pro: Claude or GPT-4 (algorithms)")
    print("  - WeatherPro: Claude (API integration)")
    print("  - PuzzlePhysics: GPT-4 (complex logic)")

if __name__ == "__main__":
    print("🧪 LLM ROUTING TEST SUITE")
    print("=" * 60)
    
    # Test different app types
    calc_success, calc_id = test_calculator_app()
    time.sleep(30)  # Wait for processing
    
    weather_success, weather_id = test_weather_app()
    time.sleep(30)
    
    game_success, game_id = test_game_app()
    
    # Summary
    print("\n" + "="*60)
    print("📊 LLM ROUTING TEST SUMMARY")
    print("="*60)
    print(f"Calculator App: {'✅ PASS' if calc_success else '❌ FAIL'}")
    print(f"Weather App: {'✅ PASS' if weather_success else '❌ FAIL'}")
    print(f"Game App: {'✅ PASS' if game_success else '❌ FAIL'}")
    
    check_routing_logs()
    
    print("\n💡 Note: Monitor server logs to verify correct LLM selection")