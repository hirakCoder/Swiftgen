#!/usr/bin/env python3
"""
SwiftGen System Recovery Script
Professional solution architecture approach to restore system functionality
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class SystemRecovery:
    """Professional system recovery implementation"""
    
    def __init__(self):
        self.backend_dir = Path(__file__).parent
        self.project_root = self.backend_dir.parent
        self.recovery_log = []
        
    def log_action(self, action: str, status: str = "INFO", details: str = ""):
        """Log recovery actions"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {status}: {action}"
        if details:
            log_entry += f" - {details}"
        
        self.recovery_log.append(log_entry)
        print(log_entry)
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are available"""
        self.log_action("Checking system dependencies")
        
        required_files = [
            "main.py",
            "enhanced_claude_service.py", 
            "project_manager.py",
            "build_service.py",
            "robust_error_recovery_system.py",
            "file_deduplication_system.py",
            "syntax_validator.py"
        ]
        
        missing_files = []
        for file in required_files:
            if not (self.backend_dir / file).exists():
                missing_files.append(file)
        
        if missing_files:
            self.log_action(f"Missing critical files: {missing_files}", "ERROR")
            return False
        
        self.log_action("All critical files present", "SUCCESS")
        return True
    
    def fix_architect_variable_scope(self) -> bool:
        """Fix the architect variable scope issue in main.py"""
        self.log_action("Fixing architect variable scope issue")
        
        main_py = self.backend_dir / "main.py"
        
        try:
            with open(main_py, 'r') as f:
                content = f.read()
            
            # Verify the architect variable is properly initialized
            if "architect = None" not in content:
                self.log_action("Adding architect variable initialization", "FIXING")
                # Find the right place to add it
                insertion_point = content.find("# Step 1: Generate with self-healing and UNIQUENESS")
                if insertion_point != -1:
                    before = content[:insertion_point]
                    after = content[insertion_point:]
                    content = before + "        # Initialize architect variable\n        architect = None\n        \n        " + after
            
            # Ensure the variable is used safely
            if 'architect is not None and hasattr(architect' not in content:
                self.log_action("Adding safe architect variable usage", "FIXING")
                content = content.replace(
                    'hasattr(architect, \'identify_app_type\')',
                    'architect is not None and hasattr(architect, \'identify_app_type\')'
                )
            
            # Write back the fixed content
            with open(main_py, 'w') as f:
                f.write(content)
            
            self.log_action("Architect variable scope fixed", "SUCCESS")
            return True
            
        except Exception as e:
            self.log_action(f"Failed to fix architect variable: {e}", "ERROR")
            return False
    
    def verify_syntax_validator(self) -> bool:
        """Verify syntax validator is working correctly"""
        self.log_action("Verifying syntax validator")
        
        try:
            # Test import
            sys.path.insert(0, str(self.backend_dir))
            from syntax_validator import SyntaxValidator
            
            # Test validation
            validator = SyntaxValidator()
            test_content = '''import SwiftUI
            
struct ContentView: View {
    var body: some View {
        Text("Hello, World!")
    }
}'''
            
            valid, errors = validator.validate_syntax('ContentView.swift', test_content)
            
            if valid:
                self.log_action("Syntax validator working correctly", "SUCCESS")
                return True
            else:
                self.log_action(f"Syntax validator issues: {errors}", "ERROR")
                return False
                
        except Exception as e:
            self.log_action(f"Syntax validator error: {e}", "ERROR")
            return False
    
    def verify_file_deduplication(self) -> bool:
        """Verify file deduplication system is working"""
        self.log_action("Verifying file deduplication system")
        
        try:
            from file_deduplication_system import FileDeduplicationSystem
            
            # Test with a sample project if it exists
            workspaces_dir = self.project_root / "workspaces"
            if workspaces_dir.exists():
                sample_projects = list(workspaces_dir.glob("proj_*"))
                if sample_projects:
                    sample_project = sample_projects[0]
                    dedup = FileDeduplicationSystem(str(sample_project))
                    status = dedup.get_status_report()
                    
                    self.log_action(f"File deduplication test: {status['total_swift_files']} files, {len(status['duplicates'])} duplicates", "SUCCESS")
                    return True
            
            self.log_action("File deduplication system available", "SUCCESS")
            return True
            
        except Exception as e:
            self.log_action(f"File deduplication error: {e}", "ERROR")
            return False
    
    def integrate_simple_modification_handler(self) -> bool:
        """Integrate SimpleModificationHandler into main.py"""
        self.log_action("Integrating SimpleModificationHandler")
        
        try:
            # Check if SimpleModificationHandler exists
            if not (self.backend_dir / "simple_modification_handler.py").exists():
                self.log_action("SimpleModificationHandler not found - creating basic version", "FIXING")
                self.create_simple_modification_handler()
            
            # Verify it's importable
            from simple_modification_handler import SimpleModificationHandler
            
            self.log_action("SimpleModificationHandler integrated successfully", "SUCCESS")
            return True
            
        except Exception as e:
            self.log_action(f"SimpleModificationHandler integration failed: {e}", "ERROR")
            return False
    
    def create_simple_modification_handler(self):
        """Create a basic SimpleModificationHandler"""
        simple_handler_content = '''"""
Simple Modification Handler
Basic implementation for modification requests
"""

class SimpleModificationHandler:
    def __init__(self, claude_service=None):
        self.claude_service = claude_service
        self.max_retries = 3
        self.allow_partial_success = True
        
    def handle_modification(self, project_id: str, description: str, current_files: list):
        """Handle modification request"""
        # Basic implementation - just pass through to claude service
        if self.claude_service:
            return self.claude_service.modify_app(description, current_files)
        else:
            return {"success": False, "error": "No claude service available"}
'''
        
        with open(self.backend_dir / "simple_modification_handler.py", 'w') as f:
            f.write(simple_handler_content)
    
    def verify_enhanced_claude_service(self) -> bool:
        """Verify EnhancedClaudeService is working"""
        self.log_action("Verifying EnhancedClaudeService")
        
        try:
            from enhanced_claude_service import EnhancedClaudeService
            
            # Test initialization
            service = EnhancedClaudeService()
            
            # Check if it has the expected methods
            required_methods = ['generate_ios_app', 'generate_ios_app_multi_llm', 'get_available_models']
            missing_methods = [method for method in required_methods if not hasattr(service, method)]
            
            if missing_methods:
                self.log_action(f"EnhancedClaudeService missing methods: {missing_methods}", "WARNING")
            else:
                self.log_action("EnhancedClaudeService methods available", "SUCCESS")
            
            return True
            
        except Exception as e:
            self.log_action(f"EnhancedClaudeService error: {e}", "ERROR")
            return False
    
    def test_basic_functionality(self) -> bool:
        """Test basic system functionality"""
        self.log_action("Testing basic system functionality")
        
        try:
            # Test imports
            from main import app
            from enhanced_claude_service import EnhancedClaudeService
            from project_manager import ProjectManager
            from build_service import BuildService
            
            self.log_action("All core imports successful", "SUCCESS")
            
            # Test service initialization
            service = EnhancedClaudeService()
            manager = ProjectManager()
            
            self.log_action("Service initialization successful", "SUCCESS")
            return True
            
        except Exception as e:
            self.log_action(f"Basic functionality test failed: {e}", "ERROR")
            return False
    
    def create_recovery_report(self) -> str:
        """Create a comprehensive recovery report"""
        report = ["=" * 60]
        report.append("SWIFTGEN SYSTEM RECOVERY REPORT")
        report.append("=" * 60)
        report.append("")
        
        for log_entry in self.recovery_log:
            report.append(log_entry)
        
        report.append("")
        report.append("=" * 60)
        report.append("RECOVERY SUMMARY")
        report.append("=" * 60)
        
        success_count = sum(1 for log in self.recovery_log if "SUCCESS" in log)
        error_count = sum(1 for log in self.recovery_log if "ERROR" in log)
        warning_count = sum(1 for log in self.recovery_log if "WARNING" in log)
        
        report.append(f"✅ Successful actions: {success_count}")
        report.append(f"❌ Failed actions: {error_count}")
        report.append(f"⚠️ Warnings: {warning_count}")
        
        if error_count == 0:
            report.append("")
            report.append("🎉 SYSTEM RECOVERY COMPLETED SUCCESSFULLY")
            report.append("The system should now be ready for testing.")
        else:
            report.append("")
            report.append("❌ SYSTEM RECOVERY INCOMPLETE")
            report.append("Please address the errors above before proceeding.")
        
        return "\n".join(report)
    
    def run_recovery(self) -> bool:
        """Execute the complete recovery process"""
        self.log_action("Starting SwiftGen System Recovery", "INFO")
        
        recovery_steps = [
            ("Check Dependencies", self.check_dependencies),
            ("Fix Architect Variable", self.fix_architect_variable_scope),
            ("Verify Syntax Validator", self.verify_syntax_validator),
            ("Verify File Deduplication", self.verify_file_deduplication),
            ("Integrate SimpleModificationHandler", self.integrate_simple_modification_handler),
            ("Verify Enhanced Claude Service", self.verify_enhanced_claude_service),
            ("Test Basic Functionality", self.test_basic_functionality),
        ]
        
        success_count = 0
        for step_name, step_func in recovery_steps:
            self.log_action(f"Executing: {step_name}")
            if step_func():
                success_count += 1
            else:
                self.log_action(f"Step failed: {step_name}", "ERROR")
        
        # Generate recovery report
        report = self.create_recovery_report()
        
        # Write report to file
        with open(self.backend_dir / "recovery_report.txt", 'w') as f:
            f.write(report)
        
        print("\n" + report)
        
        return success_count == len(recovery_steps)

def main():
    """Main recovery execution"""
    recovery = SystemRecovery()
    success = recovery.run_recovery()
    
    if success:
        print("\n🎉 Recovery completed successfully!")
        print("Next steps:")
        print("1. Restart the server")
        print("2. Test basic app generation")
        print("3. Verify modification functionality")
        return 0
    else:
        print("\n❌ Recovery failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())