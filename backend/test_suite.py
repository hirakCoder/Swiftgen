#!/usr/bin/env python3
"""
Comprehensive Test Suite for SwiftGen
Tests all critical paths and ensures 95%+ success rate
"""

import asyncio
import json
import time
import os
from typing import Dict, List, Tuple
from datetime import datetime
import httpx
from colorama import Fore, Style, init

# Initialize colorama for colored output
init()

class SwiftGenTestSuite:
    """Comprehensive test suite for SwiftGen"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=120.0)
        self.results = {
            'passed': 0,
            'failed': 0,
            'total': 0,
            'test_details': [],
            'start_time': None,
            'end_time': None
        }
        
        # Test cases organized by complexity
        self.test_cases = {
            'simple': [
                {
                    'name': 'Basic Timer App',
                    'description': 'Create a simple timer app with start, stop, and reset functionality',
                    'expected_features': ['Timer', 'Start/Stop', 'Reset'],
                    'complexity': 'low'
                },
                {
                    'name': 'Todo List App',
                    'description': 'Build a todo list app where I can add, complete, and delete tasks',
                    'expected_features': ['Add tasks', 'Complete tasks', 'Delete tasks'],
                    'complexity': 'low'
                },
                {
                    'name': 'Calculator App',
                    'description': 'Create a basic calculator with addition, subtraction, multiplication, and division',
                    'expected_features': ['Basic operations', 'Clear function'],
                    'complexity': 'low'
                },
                {
                    'name': 'Counter App',
                    'description': 'Make a simple counter app with increment and decrement buttons',
                    'expected_features': ['Increment', 'Decrement', 'Display count'],
                    'complexity': 'low'
                },
                {
                    'name': 'Hello World App',
                    'description': 'Create a hello world app that displays a greeting message',
                    'expected_features': ['Display text', 'Basic UI'],
                    'complexity': 'low'
                }
            ],
            'medium': [
                {
                    'name': 'Weather App',
                    'description': 'Build a weather app that shows current weather and 5-day forecast using OpenWeatherMap API',
                    'expected_features': ['API integration', 'Current weather', 'Forecast'],
                    'complexity': 'medium'
                },
                {
                    'name': 'Notes App',
                    'description': 'Create a notes app with categories, search functionality, and data persistence',
                    'expected_features': ['Create notes', 'Categories', 'Search', 'Persistence'],
                    'complexity': 'medium'
                },
                {
                    'name': 'Recipe Book',
                    'description': 'Build a recipe book app with ingredients list, instructions, and favorite recipes',
                    'expected_features': ['Recipe list', 'Ingredients', 'Favorites'],
                    'complexity': 'medium'
                },
                {
                    'name': 'Expense Tracker',
                    'description': 'Create an expense tracker with categories, monthly budgets, and spending analytics',
                    'expected_features': ['Track expenses', 'Categories', 'Analytics'],
                    'complexity': 'medium'
                }
            ],
            'complex': [
                {
                    'name': 'E-commerce App',
                    'description': 'Build a complete e-commerce app with product catalog, shopping cart, user authentication, and checkout flow',
                    'expected_features': ['Product catalog', 'Shopping cart', 'Authentication', 'Checkout'],
                    'complexity': 'high'
                },
                {
                    'name': 'Social Media App',
                    'description': 'Create a social media app with user profiles, posts, comments, likes, and real-time feed updates',
                    'expected_features': ['User profiles', 'Posts', 'Comments', 'Real-time updates'],
                    'complexity': 'high'
                },
                {
                    'name': 'Food Delivery App',
                    'description': 'Build a food delivery app like DoorDash with restaurant listings, menu browsing, order tracking, and payment integration',
                    'expected_features': ['Restaurant listings', 'Menu browsing', 'Order tracking', 'Payment'],
                    'complexity': 'high'
                }
            ]
        }
        
        # Modification test cases
        self.modification_tests = [
            {
                'base_app': 'Timer App',
                'modifications': [
                    'Add a lap timer feature',
                    'Change the color scheme to dark mode',
                    'Add sound notifications when timer completes'
                ]
            },
            {
                'base_app': 'Todo List App',
                'modifications': [
                    'Add priority levels to tasks',
                    'Implement task categories',
                    'Add due dates to tasks'
                ]
            },
            {
                'base_app': 'Calculator App',
                'modifications': [
                    'Add scientific calculator functions',
                    'Implement calculation history',
                    'Add a tip calculator mode'
                ]
            }
        ]
    
    async def run_all_tests(self) -> Dict:
        """Run all tests and generate report"""
        self.results['start_time'] = datetime.now()
        print(f"\n{Fore.CYAN}═══════════════════════════════════════════════════════{Style.RESET_ALL}")
        print(f"{Fore.CYAN}        SwiftGen Comprehensive Test Suite{Style.RESET_ALL}")
        print(f"{Fore.CYAN}═══════════════════════════════════════════════════════{Style.RESET_ALL}\n")
        
        # Test server health
        if not await self.test_server_health():
            print(f"{Fore.RED}✗ Server is not responding. Please start the server first.{Style.RESET_ALL}")
            return self.results
        
        # Run generation tests
        print(f"\n{Fore.YELLOW}▶ Running Generation Tests{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'─' * 50}{Style.RESET_ALL}")
        
        for complexity, test_list in self.test_cases.items():
            print(f"\n{Fore.BLUE}Testing {complexity.upper()} complexity apps:{Style.RESET_ALL}")
            for test_case in test_list:
                await self.run_generation_test(test_case)
        
        # Run modification tests
        print(f"\n{Fore.YELLOW}▶ Running Modification Tests{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'─' * 50}{Style.RESET_ALL}")
        
        for mod_test in self.modification_tests:
            await self.run_modification_test(mod_test)
        
        # Run stress tests
        print(f"\n{Fore.YELLOW}▶ Running Stress Tests{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'─' * 50}{Style.RESET_ALL}")
        
        await self.run_stress_tests()
        
        # Generate report
        self.results['end_time'] = datetime.now()
        return self.generate_report()
    
    async def test_server_health(self) -> bool:
        """Test if server is healthy"""
        try:
            response = await self.client.get(f"{self.base_url}/api/health")
            return response.status_code == 200
        except:
            return False
    
    async def run_generation_test(self, test_case: Dict) -> bool:
        """Run a single generation test"""
        self.results['total'] += 1
        start_time = time.time()
        
        try:
            print(f"\n  Testing: {test_case['name']}...", end='', flush=True)
            
            # Generate app
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={"description": test_case['description']}
            )
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            result = response.json()
            project_id = result.get('project_id')
            
            # Wait for completion (with timeout)
            success = await self.wait_for_completion(project_id, timeout=90)
            
            elapsed_time = time.time() - start_time
            
            if success:
                print(f" {Fore.GREEN}✓{Style.RESET_ALL} ({elapsed_time:.1f}s)")
                self.results['passed'] += 1
                test_result = 'passed'
            else:
                print(f" {Fore.RED}✗{Style.RESET_ALL} ({elapsed_time:.1f}s)")
                self.results['failed'] += 1
                test_result = 'failed'
            
            self.results['test_details'].append({
                'name': test_case['name'],
                'type': 'generation',
                'complexity': test_case['complexity'],
                'result': test_result,
                'time': elapsed_time,
                'project_id': project_id
            })
            
            return success
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f" {Fore.RED}✗ Error: {str(e)}{Style.RESET_ALL} ({elapsed_time:.1f}s)")
            self.results['failed'] += 1
            self.results['test_details'].append({
                'name': test_case['name'],
                'type': 'generation',
                'complexity': test_case['complexity'],
                'result': 'failed',
                'error': str(e),
                'time': elapsed_time
            })
            return False
    
    async def run_modification_test(self, mod_test: Dict) -> bool:
        """Run modification tests"""
        base_app = mod_test['base_app']
        print(f"\n  Base app: {base_app}")
        
        # First generate the base app
        base_description = next(
            (tc['description'] for complexity in self.test_cases.values() 
             for tc in complexity if base_app in tc['name']),
            f"Create a {base_app.lower()}"
        )
        
        response = await self.client.post(
            f"{self.base_url}/api/generate",
            json={"description": base_description}
        )
        
        if response.status_code != 200:
            print(f"    {Fore.RED}✗ Failed to generate base app{Style.RESET_ALL}")
            return False
        
        project_id = response.json().get('project_id')
        
        # Wait for base app to complete
        if not await self.wait_for_completion(project_id, timeout=60):
            print(f"    {Fore.RED}✗ Base app generation timed out{Style.RESET_ALL}")
            return False
        
        # Run modifications
        all_passed = True
        for modification in mod_test['modifications']:
            self.results['total'] += 1
            start_time = time.time()
            
            print(f"    Modification: {modification}...", end='', flush=True)
            
            try:
                response = await self.client.post(
                    f"{self.base_url}/api/modify",
                    json={
                        "project_id": project_id,
                        "modification": modification
                    }
                )
                
                if response.status_code == 200:
                    # Wait for modification to complete
                    success = await self.wait_for_completion(project_id, timeout=60)
                    elapsed_time = time.time() - start_time
                    
                    if success:
                        print(f" {Fore.GREEN}✓{Style.RESET_ALL} ({elapsed_time:.1f}s)")
                        self.results['passed'] += 1
                    else:
                        print(f" {Fore.RED}✗{Style.RESET_ALL} ({elapsed_time:.1f}s)")
                        self.results['failed'] += 1
                        all_passed = False
                else:
                    raise Exception(f"HTTP {response.status_code}")
                    
            except Exception as e:
                elapsed_time = time.time() - start_time
                print(f" {Fore.RED}✗ Error: {str(e)}{Style.RESET_ALL} ({elapsed_time:.1f}s)")
                self.results['failed'] += 1
                all_passed = False
        
        return all_passed
    
    async def run_stress_tests(self):
        """Run stress tests"""
        print("\n  Concurrent generation test...", end='', flush=True)
        
        # Test concurrent generations
        concurrent_tasks = []
        for i in range(3):
            task = self.client.post(
                f"{self.base_url}/api/generate",
                json={"description": f"Create a simple app number {i+1}"}
            )
            concurrent_tasks.append(task)
        
        try:
            responses = await asyncio.gather(*concurrent_tasks)
            all_success = all(r.status_code == 200 for r in responses)
            
            if all_success:
                print(f" {Fore.GREEN}✓{Style.RESET_ALL}")
                self.results['passed'] += 1
            else:
                print(f" {Fore.RED}✗{Style.RESET_ALL}")
                self.results['failed'] += 1
                
            self.results['total'] += 1
            
        except Exception as e:
            print(f" {Fore.RED}✗ Error: {str(e)}{Style.RESET_ALL}")
            self.results['failed'] += 1
            self.results['total'] += 1
    
    async def wait_for_completion(self, project_id: str, timeout: int = 60) -> bool:
        """Wait for project to complete with WebSocket monitoring"""
        # For simplicity, we'll poll the project status
        # In production, this would use WebSocket
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = await self.client.get(f"{self.base_url}/api/projects")
                projects = response.json()
                
                project = next((p for p in projects if p['project_id'] == project_id), None)
                if project and 'status' in project:
                    if project['status'] == 'completed':
                        return True
                    elif project['status'] == 'failed':
                        return False
                
                await asyncio.sleep(2)
                
            except:
                await asyncio.sleep(2)
        
        return False
    
    def generate_report(self) -> Dict:
        """Generate test report"""
        duration = (self.results['end_time'] - self.results['start_time']).total_seconds()
        success_rate = (self.results['passed'] / self.results['total'] * 100) if self.results['total'] > 0 else 0
        
        print(f"\n{Fore.CYAN}═══════════════════════════════════════════════════════{Style.RESET_ALL}")
        print(f"{Fore.CYAN}                   Test Results{Style.RESET_ALL}")
        print(f"{Fore.CYAN}═══════════════════════════════════════════════════════{Style.RESET_ALL}")
        
        print(f"\n  Total Tests: {self.results['total']}")
        print(f"  {Fore.GREEN}Passed: {self.results['passed']}{Style.RESET_ALL}")
        print(f"  {Fore.RED}Failed: {self.results['failed']}{Style.RESET_ALL}")
        print(f"  Success Rate: {Fore.YELLOW}{success_rate:.1f}%{Style.RESET_ALL}")
        print(f"  Total Duration: {duration:.1f}s")
        
        # Show breakdown by complexity
        complexity_stats = {}
        for detail in self.results['test_details']:
            if detail.get('complexity'):
                complexity = detail['complexity']
                if complexity not in complexity_stats:
                    complexity_stats[complexity] = {'passed': 0, 'failed': 0}
                
                if detail['result'] == 'passed':
                    complexity_stats[complexity]['passed'] += 1
                else:
                    complexity_stats[complexity]['failed'] += 1
        
        print(f"\n  Breakdown by Complexity:")
        for complexity, stats in complexity_stats.items():
            total = stats['passed'] + stats['failed']
            rate = (stats['passed'] / total * 100) if total > 0 else 0
            print(f"    {complexity.capitalize()}: {stats['passed']}/{total} ({rate:.1f}%)")
        
        # Performance analysis
        print(f"\n  Performance Analysis:")
        generation_times = [d['time'] for d in self.results['test_details'] if d['type'] == 'generation' and 'time' in d]
        if generation_times:
            print(f"    Average generation time: {sum(generation_times)/len(generation_times):.1f}s")
            print(f"    Fastest generation: {min(generation_times):.1f}s")
            print(f"    Slowest generation: {max(generation_times):.1f}s")
        
        # Failed tests details
        failed_tests = [d for d in self.results['test_details'] if d['result'] == 'failed']
        if failed_tests:
            print(f"\n  {Fore.RED}Failed Tests:{Style.RESET_ALL}")
            for test in failed_tests[:5]:  # Show first 5 failures
                print(f"    - {test['name']}: {test.get('error', 'Unknown error')}")
        
        print(f"\n{Fore.CYAN}═══════════════════════════════════════════════════════{Style.RESET_ALL}\n")
        
        # Save detailed report
        report_path = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"Detailed report saved to: {report_path}")
        
        return {
            'success_rate': success_rate,
            'total_tests': self.results['total'],
            'passed': self.results['passed'],
            'failed': self.results['failed'],
            'duration': duration,
            'report_file': report_path
        }


async def main():
    """Run the test suite"""
    test_suite = SwiftGenTestSuite()
    
    # Check if specific test type is requested
    import sys
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        if test_type == 'simple':
            test_suite.test_cases = {'simple': test_suite.test_cases['simple']}
        elif test_type == 'medium':
            test_suite.test_cases = {'medium': test_suite.test_cases['medium']}
        elif test_type == 'complex':
            test_suite.test_cases = {'complex': test_suite.test_cases['complex']}
        elif test_type == 'quick':
            # Quick test with just a few cases
            test_suite.test_cases = {
                'simple': test_suite.test_cases['simple'][:2],
                'medium': test_suite.test_cases['medium'][:1]
            }
            test_suite.modification_tests = test_suite.modification_tests[:1]
    
    results = await test_suite.run_all_tests()
    
    # Exit with appropriate code
    if results['success_rate'] >= 95:
        print(f"\n{Fore.GREEN}✅ SUCCESS: Achieved {results['success_rate']:.1f}% success rate!{Style.RESET_ALL}")
        sys.exit(0)
    else:
        print(f"\n{Fore.RED}❌ FAILED: Only {results['success_rate']:.1f}% success rate (target: 95%+){Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())