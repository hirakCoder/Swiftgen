#!/usr/bin/env python3
"""Test intelligent routing system"""

import sys
sys.path.append('backend')

from intelligent_llm_router import IntelligentLLMRouter

def test_intelligent_routing():
    router = IntelligentLLMRouter()
    
    test_cases = [
        # Simple UI app - should go to xAI
        {
            "desc": "Create a simple timer app with start and stop buttons",
            "expected": "xai",
            "reason": "Simple UI app"
        },
        # Calculator app - should go to GPT-4 for algorithms
        {
            "desc": "Create an advanced scientific calculator with complex mathematical functions including derivatives, integrals, matrix operations, and equation solving",
            "expected": ["openai", "anthropic"],
            "reason": "Complex computational requirements"
        },
        # Weather app - should go to GPT-4 for API integration
        {
            "desc": "Build a weather app that fetches real-time weather data from OpenWeatherMap API",
            "expected": ["openai", "anthropic"],
            "reason": "External API integration"
        },
        # Complex UI app - should NOT go to xAI
        {
            "desc": "Create a dashboard with multiple charts, graphs, and real-time data visualization with custom animations",
            "expected": "anthropic",
            "reason": "Complex UI requirements"
        },
        # Simple modification - should go to xAI
        {
            "desc": "Change the button color to blue",
            "expected": "xai",
            "reason": "Simple UI modification",
            "is_mod": True
        },
        # Complex modification - should NOT go to xAI
        {
            "desc": "Add a complete statistics dashboard with charts showing weekly and monthly trends, export functionality, and data persistence",
            "expected": "anthropic",
            "reason": "Complex feature addition",
            "is_mod": True
        },
        # Algorithm-heavy app
        {
            "desc": "Build a sudoku solver that uses backtracking algorithm to solve puzzles",
            "expected": "openai",
            "reason": "Algorithm implementation"
        },
        # Multi-feature app - should NOT go to xAI
        {
            "desc": "Create a todo app with categories, priorities, due dates, search functionality, and cloud sync",
            "expected": "anthropic",
            "reason": "Multiple complex features"
        }
    ]
    
    print("🧪 Testing Intelligent Routing System")
    print("="*70)
    
    passed = 0
    total = len(test_cases)
    
    for i, test in enumerate(test_cases, 1):
        desc = test["desc"]
        expected = test["expected"]
        reason = test["reason"]
        is_mod = test.get("is_mod", False)
        
        # Analyze request
        request_type = router.analyze_request(desc, modification_history=[{"dummy": True}] if is_mod else None)
        provider = router.route_initial_request(desc, is_modification=is_mod)
        
        # Check if result matches expected
        if isinstance(expected, list):
            success = provider in expected
        else:
            success = provider == expected
        
        status = "✅ PASS" if success else "❌ FAIL"
        passed += 1 if success else 0
        
        print(f"\nTest {i}: {reason}")
        print(f"  Description: {desc[:60]}...")
        print(f"  Request Type: {request_type}")
        print(f"  Routed to: {provider}")
        print(f"  Expected: {expected}")
        print(f"  {status}")
    
    print("\n" + "="*70)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Intelligent routing is working correctly.")
    else:
        print("⚠️  Some tests failed. Review the routing logic.")

if __name__ == "__main__":
    test_intelligent_routing()