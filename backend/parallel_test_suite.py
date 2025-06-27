"""
Parallel Test Suite for SwiftGen
Runs tests concurrently for faster execution
"""

import asyncio
import time
from typing import Dict, List, Tuple
from datetime import datetime
import os
import json

from test_suite import SwiftGenTestSuite, TestResult


class ParallelTestSuite(SwiftGenTestSuite):
    """Enhanced test suite with parallel execution capabilities"""
    
    def __init__(self, max_parallel: int = 4):
        super().__init__()
        self.max_parallel = max_parallel
        self.semaphore = asyncio.Semaphore(max_parallel)
        
    async def run_with_semaphore(self, test_func):
        """Run test with semaphore to limit concurrent execution"""
        async with self.semaphore:
            return await test_func()
            
    async def run_all_tests_parallel(self) -> Dict:
        """Run complete test suite with parallel execution"""
        print("=" * 60)
        print("SwiftGen Parallel Test Suite")
        print(f"Max concurrent tests: {self.max_parallel}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Group tests by independence
        basic_app_tests = [
            self.test_calculator_generation,
            self.test_timer_generation,
            self.test_todo_generation,
            self.test_counter_generation
        ]
        
        api_app_tests = [
            self.test_currency_converter,
            self.test_weather_app
        ]
        
        modification_tests = [
            self.test_color_modification,
            self.test_button_addition,
            self.test_text_modification
        ]
        
        # Run basic app tests in parallel
        print("\n🚀 Running Basic App Tests in Parallel...")
        basic_start = time.time()
        basic_tasks = [self.run_with_semaphore(test) for test in basic_app_tests]
        basic_results = await asyncio.gather(*basic_tasks, return_exceptions=True)
        basic_time = time.time() - basic_start
        print(f"✅ Basic App Tests completed in {basic_time:.1f}s")
        
        # Run API app tests in parallel
        print("\n🚀 Running API App Tests in Parallel...")
        api_start = time.time()
        api_tasks = [self.run_with_semaphore(test) for test in api_app_tests]
        api_results = await asyncio.gather(*api_tasks, return_exceptions=True)
        api_time = time.time() - api_start
        print(f"✅ API App Tests completed in {api_time:.1f}s")
        
        # Run modification tests (these need sequential due to shared resources)
        print("\n🚀 Running Modification Tests...")
        mod_start = time.time()
        mod_results = []
        for test in modification_tests:
            result = await test()
            mod_results.append(result)
        mod_time = time.time() - mod_start
        print(f"✅ Modification Tests completed in {mod_time:.1f}s")
        
        # Process results
        all_results = []
        for result in basic_results + api_results + mod_results:
            if isinstance(result, Exception):
                # Handle exceptions from gather
                test_name = f"Unknown test (exception: {str(result)})"
                all_results.append(TestResult(test_name, False, str(result)))
            elif isinstance(result, TestResult):
                all_results.append(result)
                
        self.results = all_results
        
        # Generate report
        total_time = time.time() - start_time
        report = self.generate_parallel_report(total_time, basic_time, api_time, mod_time)
        
        return report
        
    async def run_category_parallel(self, category: str) -> Dict:
        """Run specific category of tests in parallel"""
        if category == "basic":
            tests = [
                self.test_calculator_generation,
                self.test_timer_generation,
                self.test_todo_generation,
                self.test_counter_generation
            ]
        elif category == "api":
            tests = [
                self.test_currency_converter,
                self.test_weather_app
            ]
        elif category == "modifications":
            # Modifications run sequentially due to dependencies
            return await self.run_modifications_sequential()
        else:
            raise ValueError(f"Unknown category: {category}")
            
        print(f"\n🚀 Running {category} tests in parallel...")
        start_time = time.time()
        
        tasks = [self.run_with_semaphore(test) for test in tests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for result in results:
            if isinstance(result, Exception):
                test_name = f"Unknown test in {category}"
                self.results.append(TestResult(test_name, False, str(result)))
            elif isinstance(result, TestResult):
                self.results.append(result)
                
        total_time = time.time() - start_time
        return self.generate_report(total_time)
        
    async def run_modifications_sequential(self) -> Dict:
        """Run modification tests sequentially (they share resources)"""
        tests = [
            self.test_color_modification,
            self.test_button_addition,
            self.test_text_modification
        ]
        
        for test in tests:
            result = await test()
            
        return {"status": "completed"}
        
    def generate_parallel_report(self, total_time: float, basic_time: float, 
                                api_time: float, mod_time: float) -> Dict:
        """Generate enhanced report with parallel execution metrics"""
        report = self.generate_report(total_time)
        
        # Add parallel execution metrics
        report["parallel_metrics"] = {
            "basic_apps_time": basic_time,
            "api_apps_time": api_time,
            "modifications_time": mod_time,
            "parallelization_efficiency": self.calculate_efficiency(total_time)
        }
        
        # Print parallel execution summary
        print("\n" + "=" * 60)
        print("Parallel Execution Summary")
        print("=" * 60)
        print(f"Basic Apps: {basic_time:.1f}s (4 tests in parallel)")
        print(f"API Apps: {api_time:.1f}s (2 tests in parallel)")
        print(f"Modifications: {mod_time:.1f}s (3 tests sequential)")
        print(f"Total Time: {total_time:.1f}s")
        print(f"Efficiency Gain: {self.calculate_efficiency(total_time):.1f}%")
        
        return report
        
    def calculate_efficiency(self, parallel_time: float) -> float:
        """Calculate efficiency gain from parallel execution"""
        # Estimate sequential time (sum of all test durations)
        sequential_estimate = sum(r.duration for r in self.results if r.duration > 0)
        if sequential_estimate == 0:
            return 0.0
            
        efficiency = ((sequential_estimate - parallel_time) / sequential_estimate) * 100
        return max(0.0, efficiency)  # Ensure non-negative


class ParallelStoryUpdater:
    """Parallel story status updater"""
    
    def __init__(self):
        self.tracker_path = "USER_STORY_TRACKER.md"
        self.stories_path = "PRODUCT_USER_STORIES.md"
        
    async def update_all_stories_parallel(self):
        """Update all story statuses in parallel"""
        print("\n📊 Parallel Story Status Update")
        print("=" * 40)
        
        # Stage 1: Gather all current information in parallel
        gather_tasks = [
            self.read_tracker_file(),
            self.read_stories_file(),
            self.get_latest_test_results(),
            self.check_recent_commits()
        ]
        
        results = await asyncio.gather(*gather_tasks)
        tracker_content, stories_content, test_results, recent_commits = results
        
        # Stage 2: Analyze what needs updating
        updates_needed = self.analyze_updates_needed(
            tracker_content, test_results, recent_commits
        )
        
        # Stage 3: Apply updates
        if updates_needed:
            await self.apply_updates(updates_needed)
            print(f"✅ Updated {len(updates_needed)} stories")
        else:
            print("✅ All stories up to date")
            
    async def read_tracker_file(self) -> str:
        """Read USER_STORY_TRACKER.md"""
        with open(self.tracker_path, 'r') as f:
            return f.read()
            
    async def read_stories_file(self) -> str:
        """Read PRODUCT_USER_STORIES.md"""
        with open(self.stories_path, 'r') as f:
            return f.read()
            
    async def get_latest_test_results(self) -> Dict:
        """Get latest test results"""
        try:
            with open("test_report.json", 'r') as f:
                return json.load(f)
        except:
            return {}
            
    async def check_recent_commits(self) -> List[str]:
        """Check recent git commits"""
        # Simulated - would actually run git log
        return []
        
    def analyze_updates_needed(self, tracker: str, tests: Dict, commits: List) -> List[Dict]:
        """Analyze what story updates are needed"""
        updates = []
        
        # Check test results against story status
        if tests:
            for test in tests.get("tests", []):
                if test["passed"] and "BLOCKED" in tracker:
                    story_id = self.extract_story_id(test["name"])
                    if story_id:
                        updates.append({
                            "story_id": story_id,
                            "new_status": "NEEDS_RETEST",
                            "reason": "Test now passing"
                        })
                        
        return updates
        
    def extract_story_id(self, test_name: str) -> str:
        """Extract story ID from test name"""
        # Example: "US-1.1: Calculator Generation" -> "US-1.1"
        if "US-" in test_name:
            parts = test_name.split(":")
            if parts:
                return parts[0].strip()
        return ""
        
    async def apply_updates(self, updates: List[Dict]):
        """Apply updates to tracker file"""
        # In real implementation, would update the markdown file
        for update in updates:
            print(f"  - {update['story_id']}: {update['new_status']} ({update['reason']})")


async def main():
    """Run parallel test suite"""
    import sys
    
    # Parse arguments
    parallel = "--parallel" in sys.argv
    category = None
    
    for arg in sys.argv[1:]:
        if arg not in ["--parallel"]:
            category = arg
            
    if parallel:
        print("🚀 Running tests in PARALLEL mode")
        suite = ParallelTestSuite(max_parallel=4)
        
        if category:
            report = await suite.run_category_parallel(category)
        else:
            report = await suite.run_all_tests_parallel()
    else:
        print("Running tests in sequential mode")
        suite = SwiftGenTestSuite()
        
        if category:
            # Run specific category
            if category == "basic":
                await suite.test_calculator_generation()
                await suite.test_timer_generation()
                await suite.test_todo_generation()
                await suite.test_counter_generation()
            elif category == "api":
                await suite.test_currency_converter()
                await suite.test_weather_app()
            elif category == "modifications":
                await suite.test_color_modification()
                await suite.test_button_addition()
                await suite.test_text_modification()
        else:
            report = await suite.run_all_tests()
            
    # Run story updater in parallel
    if "--update-stories" in sys.argv:
        updater = ParallelStoryUpdater()
        await updater.update_all_stories_parallel()


if __name__ == "__main__":
    asyncio.run(main())