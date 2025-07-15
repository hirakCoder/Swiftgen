#!/usr/bin/env python3
"""
SwiftGen System Diagnostic Tool
Checks all components and dependencies
"""

import os
import sys
import subprocess
import json
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class SystemDiagnostic:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.successes = []
        
    def run_diagnostics(self):
        """Run all diagnostic checks"""
        print("\n🔍 SwiftGen System Diagnostic Tool")
        print("=" * 60)
        print(f"Running diagnostics at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Check Python version
        self.check_python_version()
        
        # Check required packages
        self.check_packages()
        
        # Check API keys
        self.check_api_keys()
        
        # Check file structure
        self.check_file_structure()
        
        # Check Xcode tools
        self.check_xcode_tools()
        
        # Check module imports
        self.check_imports()
        
        # Print summary
        self.print_summary()
        
    def check_python_version(self):
        """Check Python version"""
        print("\n📌 Checking Python version...")
        
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            self.successes.append(f"Python {version.major}.{version.minor}.{version.micro} ✅")
            print(f"  ✅ Python {version.major}.{version.minor}.{version.micro}")
        else:
            self.issues.append(f"Python version {version.major}.{version.minor} is too old. Need 3.8+")
            print(f"  ❌ Python {version.major}.{version.minor} - Need Python 3.8 or higher")
    
    def check_packages(self):
        """Check required Python packages"""
        print("\n📦 Checking required packages...")
        
        # Package import name mappings
        package_imports = {
            "fastapi": "fastapi",
            "uvicorn": "uvicorn",
            "anthropic": "anthropic",
            "python-dotenv": "dotenv",  # Import name is different!
            "websockets": "websockets",
            "pyyaml": "yaml",  # Import name is different!
            "aiofiles": "aiofiles",
            "httpx": "httpx",
            "pydantic": "pydantic",
            "aiohttp": "aiohttp"
        }
        
        for package_name, import_name in package_imports.items():
            try:
                # Special handling for dotenv
                if import_name == "dotenv":
                    from dotenv import load_dotenv
                    version = "imported successfully"
                # Special handling for yaml
                elif import_name == "yaml":
                    import yaml
                    version = getattr(yaml, "__version__", "imported successfully")
                else:
                    module = __import__(import_name)
                    version = getattr(module, "__version__", "unknown")
                
                print(f"  ✅ {package_name} ({version})")
                self.successes.append(f"{package_name} installed")
            except ImportError:
                print(f"  ❌ {package_name} not installed (tried importing '{import_name}')")
                self.issues.append(f"Missing package: {package_name}")
    
    def check_api_keys(self):
        """Check API key configuration"""
        print("\n🔑 Checking API keys...")
        
        # Load .env if exists
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except:
            pass
        
        # Check Claude API key
        claude_key = os.getenv("CLAUDE_API_KEY", "")
        if claude_key and claude_key != "YOUR_CLAUDE_API_KEY_HERE":
            print(f"  ✅ CLAUDE_API_KEY configured ({claude_key[:10]}...)")
            self.successes.append("Claude API key configured")
        else:
            print("  ❌ CLAUDE_API_KEY not configured")
            self.issues.append("Claude API key missing - Core functionality won't work!")
        
        # Check optional API keys
        openai_key = os.getenv("OPENAI_API_KEY", "")
        if openai_key:
            print(f"  ✅ OPENAI_API_KEY configured ({openai_key[:10]}...)")
            self.successes.append("OpenAI API key configured")
        else:
            print("  ⚠️  OPENAI_API_KEY not configured (optional - for enhanced error recovery)")
            self.warnings.append("OpenAI API key not configured - multi-model recovery limited")
        
        xai_key = os.getenv("XAI_API_KEY", "")
        if xai_key:
            print(f"  ✅ XAI_API_KEY configured")
        else:
            print("  ℹ️  XAI_API_KEY not configured (optional)")
    
    def check_file_structure(self):
        """Check required files exist"""
        print("\n📁 Checking file structure...")
        
        required_files = [
            "main.py",
            "claude_service.py",
            "build_service.py",
            "project_manager.py",
            "models.py",
            "simulator_service.py",
            "robust_error_recovery_system_backup.py",
            "intelligent_error_recovery.py"
        ]
        
        for file in required_files:
            if os.path.exists(file):
                print(f"  ✅ {file}")
                self.successes.append(f"{file} exists")
            else:
                print(f"  ❌ {file} missing")
                self.issues.append(f"Missing file: {file}")
        
        # Check directories
        required_dirs = [
            "../frontend",
            "../templates/ios_app_template",
            "../workspaces"
        ]
        
        for dir_path in required_dirs:
            if os.path.exists(dir_path):
                print(f"  ✅ {dir_path}/")
            else:
                print(f"  ⚠️  {dir_path}/ missing (will be created automatically)")
                self.warnings.append(f"Directory {dir_path} will be created on first use")
    
    def check_xcode_tools(self):
        """Check Xcode and related tools"""
        print("\n🛠️  Checking Xcode tools...")
        
        # Check xcodebuild
        try:
            result = subprocess.run(['xcodebuild', '-version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                print(f"  ✅ {version}")
                self.successes.append("Xcode installed")
            else:
                raise Exception("xcodebuild failed")
        except:
            print("  ❌ xcodebuild not found")
            self.issues.append("Xcode not installed - Cannot build iOS apps!")
        
        # Check xcodegen
        try:
            result = subprocess.run(['which', 'xcodegen'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("  ✅ xcodegen installed")
                self.successes.append("xcodegen installed")
            else:
                raise Exception("xcodegen not found")
        except:
            print("  ❌ xcodegen not found")
            self.issues.append("xcodegen not installed - run: brew install xcodegen")
        
        # Check xcrun
        try:
            result = subprocess.run(['xcrun', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("  ✅ xcrun available")
                self.successes.append("xcrun available")
        except:
            print("  ⚠️  xcrun issues detected")
            self.warnings.append("xcrun might have issues")
    
    def check_imports(self):
        """Test importing all modules"""
        print("\n🔌 Testing module imports...")
        
        modules_to_test = [
            "claude_service",
            "build_service",
            "project_manager",
            "models",
            "simulator_service",
            "robust_error_recovery_system",
            "intelligent_error_recovery"
        ]
        
        for module_name in modules_to_test:
            try:
                module = __import__(module_name)
                print(f"  ✅ {module_name} imports successfully")
                self.successes.append(f"{module_name} imports")
            except ImportError as e:
                print(f"  ❌ {module_name} import failed: {str(e)}")
                self.issues.append(f"Cannot import {module_name}: {str(e)}")
            except Exception as e:
                print(f"  ❌ {module_name} has errors: {str(e)}")
                self.issues.append(f"{module_name} has errors: {str(e)}")
    
    def print_summary(self):
        """Print diagnostic summary"""
        print("\n" + "=" * 60)
        print("📋 DIAGNOSTIC SUMMARY")
        print("=" * 60)
        
        print(f"\n✅ Successes: {len(self.successes)}")
        for success in self.successes[:5]:  # Show first 5
            print(f"  • {success}")
        if len(self.successes) > 5:
            print(f"  • ... and {len(self.successes) - 5} more")
        
        if self.warnings:
            print(f"\n⚠️  Warnings: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if self.issues:
            print(f"\n❌ Issues: {len(self.issues)}")
            for issue in self.issues:
                print(f"  • {issue}")
        
        # Overall status
        print("\n" + "=" * 60)
        if not self.issues:
            print("✅ SYSTEM READY - All critical components are working!")
        elif len(self.issues) <= 2:
            print("⚠️  SYSTEM MOSTLY READY - Minor issues to fix")
        else:
            print("❌ SYSTEM NOT READY - Critical issues need attention")
        
        # Recommendations
        if self.issues:
            print("\n📝 Recommendations:")
            
            if any("Missing package" in i for i in self.issues):
                print("  1. Install missing packages: pip install -r requirements.txt")
            
            if any("Claude API key" in i for i in self.issues):
                print("  2. Set Claude API key in .env file: CLAUDE_API_KEY=your_key_here")
            
            if any("xcodegen" in i for i in self.issues):
                print("  3. Install xcodegen: brew install xcodegen")
            
            if any("Missing file" in i for i in self.issues):
                print("  4. Ensure all Python files are in the backend directory")
        
        print("=" * 60)


def main():
    """Run diagnostics"""
    diagnostic = SystemDiagnostic()
    diagnostic.run_diagnostics()


if __name__ == "__main__":
    main()
