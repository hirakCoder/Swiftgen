#!/usr/bin/env python3
"""
Test runner for SwiftGen
Runs all tests with coverage reporting
"""
import subprocess
import sys
import os
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_banner():
    """Print test runner banner"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}🧪 SwiftGen Test Runner{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")


def run_command(cmd, description):
    """Run a command and report results"""
    print(f"{YELLOW}➤ {description}{RESET}")
    print(f"  Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"{GREEN}✓ Success{RESET}")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"{RED}✗ Failed{RESET}")
        if result.stderr:
            print(f"{RED}Error:{RESET}")
            print(result.stderr)
        if result.stdout:
            print(result.stdout)
    
    print()
    return result.returncode == 0


def main():
    """Run all tests with different configurations"""
    print_banner()
    
    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    all_passed = True
    
    # 1. Run unit tests only
    if not run_command(
        ["pytest", "-m", "unit", "-v"],
        "Running unit tests"
    ):
        all_passed = False
    
    # 2. Run integration tests
    if not run_command(
        ["pytest", "-m", "integration", "-v"],
        "Running integration tests"
    ):
        all_passed = False
    
    # 3. Run critical tests
    if not run_command(
        ["pytest", "-m", "critical", "-v"],
        "Running critical path tests"
    ):
        all_passed = False
    
    # 4. Run all tests with coverage
    if not run_command(
        ["pytest", "--cov=backend", "--cov-report=html", "--cov-report=term", "-v"],
        "Running all tests with coverage"
    ):
        all_passed = False
    
    # 5. Check code quality (optional)
    print(f"{YELLOW}➤ Code Quality Checks{RESET}")
    
    # Black formatting check
    run_command(
        ["black", "--check", "backend/"],
        "Checking code formatting (black)"
    )
    
    # Flake8 linting
    run_command(
        ["flake8", "backend/", "--max-line-length=120", "--exclude=venv,__pycache__"],
        "Running flake8 linter"
    )
    
    # Summary
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}📊 Test Summary{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    
    if all_passed:
        print(f"{GREEN}✓ All tests passed!{RESET}")
        print(f"\n📈 Coverage report available at: {project_root}/htmlcov/index.html")
    else:
        print(f"{RED}✗ Some tests failed{RESET}")
        sys.exit(1)
    
    print(f"{BLUE}{'='*70}{RESET}\n")


if __name__ == "__main__":
    main()