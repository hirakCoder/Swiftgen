#!/usr/bin/env python3
"""
Test Runner for SwiftGen
Ensures all changes are tested before deployment
"""

import asyncio
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_suite import SwiftGenTestSuite


async def run_tests(test_filter=None):
    """Run tests with optional filter"""
    print("\n🚀 SwiftGen Test Runner")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    test_suite = SwiftGenTestSuite()
    
    if test_filter:
        print(f"Running filtered tests: {test_filter}")
        if test_filter == "basic":
            # Run only basic app generation tests
            await test_suite.test_calculator_generation()
            await test_suite.test_timer_generation()
            await test_suite.test_todo_generation()
            await test_suite.test_counter_generation()
        elif test_filter == "api":
            # Run only API app tests
            await test_suite.test_currency_converter()
            await test_suite.test_weather_app()
        elif test_filter == "modifications":
            # Run only modification tests
            await test_suite.test_color_modification()
            await test_suite.test_button_addition()
            await test_suite.test_text_modification()
        elif test_filter == "calculator":
            # Run only calculator test
            await test_suite.test_calculator_generation()
        elif test_filter == "currency":
            # Run only currency converter test
            await test_suite.test_currency_converter()
        else:
            print(f"Unknown filter: {test_filter}")
            print("Available filters: basic, api, modifications, calculator, currency")
            return
    else:
        # Run all tests
        report = await test_suite.run_all_tests()
        
        # Show critical failures
        if report["summary"]["failed"] > 0:
            print("\n⚠️  CRITICAL: Tests failed!")
            print("DO NOT deploy changes until all tests pass!")
            return 1
        else:
            print("\n✅ All tests passed! Safe to deploy.")
            return 0


def main():
    """Main entry point"""
    # Parse command line arguments
    test_filter = None
    if len(sys.argv) > 1:
        test_filter = sys.argv[1]
    
    # Run tests
    result = asyncio.run(run_tests(test_filter))
    
    # Exit with proper code
    sys.exit(result if isinstance(result, int) else 0)


if __name__ == "__main__":
    main()