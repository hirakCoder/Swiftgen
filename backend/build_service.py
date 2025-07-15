import os
import asyncio
import re
from typing import Dict, List, Optional, Tuple
import subprocess
import json
from datetime import datetime
import shutil

from models import BuildStatus, BuildResult

# Import error recovery system
try:
    from robust_error_recovery_system import RobustErrorRecoverySystem
    from claude_service import ClaudeService
    from enhanced_claude_service import EnhancedClaudeService
    from user_friendly_errors import UserFriendlyErrorHandler
except ImportError as e:
    print(f"Warning: Could not import recovery systems: {e}")
    RobustErrorRecoverySystem = None
    ClaudeService = None
    EnhancedClaudeService = None
    UserFriendlyErrorHandler = None

# Import simulator service
try:
    from simulator_service import SimulatorService, SimulatorState
except ImportError:
    print("Warning: SimulatorService not available")
    SimulatorService = None
    SimulatorState = None

# Import modern pattern validator
try:
    from modern_pattern_validator import ModernPatternValidator
except ImportError:
    print("Warning: ModernPatternValidator not available")
    ModernPatternValidator = None


def fix_naming_consistency_in_project_yml(project_path: str):
    """Fix naming consistency issues in project.yml before building"""
    try:
        import yaml

        project_yml_path = os.path.join(project_path, "project.yml")
        project_json_path = os.path.join(project_path, "project.json")

        if not os.path.exists(project_yml_path) or not os.path.exists(project_json_path):
            return

        # Get the app name from project.json
        with open(project_json_path, 'r') as f:
            metadata = json.load(f)
            app_name = metadata.get('app_name', 'App')

        # Read project.yml
        with open(project_yml_path, 'r') as f:
            content = f.read()

        # Create consistent names
        display_name = app_name.strip()  # "Cool Timer"
        product_name = ''.join(display_name.split())  # "CoolTimer"

        # Fix all occurrences
        # 1. Fix PRODUCT_NAME to have no spaces
        content = re.sub(
            r'(PRODUCT_NAME:\s*["\']?)([^"\'\n]+)(["\']?)',
            f'\\1{product_name}\\3',
            content
        )

        # 2. Ensure display name is consistent
        content = re.sub(
            r'(INFOPLIST_KEY_CFBundleDisplayName:\s*["\']?)([^"\'\n]+)(["\']?)',
            f'\\1{display_name}\\3',
            content
        )

        # Write back
        with open(project_yml_path, 'w') as f:
            f.write(content)

        # Logging handled by caller

    except Exception as e:
        # Warning logged silently
        pass


class BuildService:
    """Build service with intelligent error recovery and simulator support"""

    def __init__(self):
        self.max_attempts = 3  # Default attempts for simple apps
        self.status_callback = None
        self.backend_dir = os.path.dirname(os.path.abspath(__file__))
        self.build_logs_dir = os.path.join(self.backend_dir, "build_logs")
        os.makedirs(self.build_logs_dir, exist_ok=True)
        self.app_complexity = None  # Will be set during build

        # Initialize simulator service if available
        self.simulator_service = SimulatorService() if SimulatorService else None

        # Initialize modern pattern validator
        self.pattern_validator = ModernPatternValidator(target_ios_version="16.0") if ModernPatternValidator else None

        # Initialize error recovery system
        self.error_recovery_system = None
        self.claude_service = None
        self.user_friendly_handler = UserFriendlyErrorHandler() if UserFriendlyErrorHandler else None
        
        # Initialize RAG knowledge base
        self.rag_kb = None
        try:
            from rag_knowledge_base import RAGKnowledgeBase
            self.rag_kb = RAGKnowledgeBase()
            print("✓ RAG Knowledge Base initialized for build service")
        except Exception as e:
            print(f"⚠️ RAG Knowledge Base not available: {e}")
        
        # Initialize file structure manager
        self.file_structure_manager = None
        try:
            from file_structure_manager import FileStructureManager
            self.file_structure_manager = FileStructureManager()
            print("✓ File Structure Manager initialized for build service")
        except Exception as e:
            print(f"⚠️ File Structure Manager not available: {e}")
        
        # Initialize debug logger
        self.debug_logger = None
        try:
            from debug_logger import DebugLogger
            # Will be initialized per project
            print("✓ Debug Logger available for build service")
        except Exception as e:
            print(f"⚠️ Debug Logger not available: {e}")

        try:
            if RobustErrorRecoverySystem:
                # Try to use enhanced service if available
                if EnhancedClaudeService:
                    self.claude_service = EnhancedClaudeService()
                elif ClaudeService:
                    self.claude_service = ClaudeService()

                if self.claude_service:
                    self.error_recovery_system = RobustErrorRecoverySystem(
                        claude_service=self.claude_service,
                        openai_key=os.getenv("OPENAI_API_KEY"),
                        xai_key=os.getenv("XAI_API_KEY"),
                        rag_kb=self.rag_kb  # Pass RAG to error recovery
                    )
                    print("✓ Robust error recovery system initialized with RAG support")
                else:
                    print("⚠️ Claude service not available - error recovery limited")
            else:
                print("⚠️ Robust error recovery system not available")
        except Exception as e:
            print(f"⚠️ Could not initialize error recovery: {e}")
            self.error_recovery_system = None

    def set_status_callback(self, callback):
        """Set callback for status updates"""
        self.status_callback = callback

    async def _update_status(self, message: str):
        """Send status update if callback is set"""
        if self.status_callback:
            try:
                await self.status_callback(message)
            except Exception as e:
                print(f"Error in status callback: {e}")

    async def build_project(self, project_path: str, project_id: str, bundle_id: str, app_complexity: str = None) -> BuildResult:
        """Build iOS project with multiple recovery strategies"""

        start_time = datetime.now()
        errors = []
        warnings = []
        build_log = []
        
        # CRITICAL: Reset attempted fixes for each new build to prevent getting stuck
        if self.error_recovery_system:
            self.error_recovery_system.reset_attempted_fixes()
            print(f"[BUILD] Reset error recovery attempts for fresh start")
        
        # Set max attempts based on complexity
        if app_complexity:
            self.app_complexity = app_complexity
            print(f"[BUILD] Setting complexity: {app_complexity}")
            if app_complexity == "high":
                self.max_attempts = 5  # More attempts for complex apps
                print(f"[BUILD] High complexity app - setting max_attempts to 5")
                await self._update_status("🏗️ Building complex app (may take longer)...")
            elif app_complexity == "medium":
                self.max_attempts = 4
                print(f"[BUILD] Medium complexity app - setting max_attempts to 4")
                await self._update_status("🏗️ Building medium complexity app...")
            else:
                self.max_attempts = 3
                print(f"[BUILD] Low complexity app - setting max_attempts to 3")
                await self._update_status("🏗️ Building app...")
        else:
            print(f"[BUILD] No complexity specified - using default max_attempts: {self.max_attempts}")
        
        # Initialize debug logger for this project
        if self.debug_logger is None:
            try:
                from debug_logger import DebugLogger
                self.debug_logger = DebugLogger(project_id)
            except:
                pass
        
        # Create log file path for this build
        log_filename = f"proj_{project_id}_build.log"
        log_path = os.path.join(self.build_logs_dir, log_filename)
        
        # Initialize log file
        with open(log_path, 'w') as f:
            f.write(f"Build Log for Project: {project_id}\n")
            f.write(f"Bundle ID: {bundle_id}\n")
            f.write(f"Started: {start_time}\n")
            f.write("-" * 50 + "\n")

        # Verify project structure
        sources_dir = os.path.join(project_path, "Sources")
        if not os.path.exists(sources_dir):
            return BuildResult(
                success=False,
                errors=[f"Sources directory not found at {sources_dir}"],
                warnings=[],
                build_time=(datetime.now() - start_time).total_seconds(),
                app_path=None,
                log_path=log_path
            )

        # Get Swift files recursively from all subdirectories
        swift_files = []
        for root, dirs, files in os.walk(sources_dir):
            for filename in files:
                if filename.endswith('.swift'):
                    file_path = os.path.join(root, filename)
                    # Calculate relative path from project root
                    relative_path = os.path.relpath(file_path, project_path)
                    with open(file_path, 'r') as f:
                        swift_files.append({
                            "path": relative_path,
                            "content": f.read()
                        })

        await self._update_status(f"Found {len(swift_files)} Swift files in project")
        
        # Log file structure if debug logger available
        if self.debug_logger:
            self.debug_logger.log_file_structure(swift_files, phase="initial")
            self.debug_logger.log_directory_structure(project_path)

        if not swift_files:
            return BuildResult(
                success=False,
                errors=["No Swift files found in Sources directory"],
                warnings=[],
                build_time=(datetime.now() - start_time).total_seconds(),
                app_path=None,
                log_path=log_path if 'log_path' in locals() else None
            )

        # Ensure we have project.yml
        project_yml_path = os.path.join(project_path, "project.yml")
        if not os.path.exists(project_yml_path):
            await self._update_status("❌ project.yml not found")
            return BuildResult(
                success=False,
                errors=["project.yml not found"],
                warnings=[],
                build_time=(datetime.now() - start_time).total_seconds(),
                app_path=None,
                log_path=log_path if 'log_path' in locals() else None
            )

        # Validate Swift syntax first
        await self._update_status("🔍 Validating Swift syntax...")
        syntax_errors = self._validate_swift_syntax(swift_files)
        if syntax_errors:
            errors.extend(syntax_errors)
            warnings.append(f"Found {len(syntax_errors)} syntax errors")

        # Validate modern Swift patterns
        if self.pattern_validator:
            await self._update_status("🔍 Validating modern Swift patterns...")
            pattern_issues = self.pattern_validator.validate_files(swift_files)
            
            if pattern_issues:
                # Get critical issues that would prevent build
                critical_issues = self.pattern_validator.get_critical_issues(pattern_issues)
                warning_issues = self.pattern_validator.get_warnings(pattern_issues)
                
                # Log issues for debugging
                print(f"[VALIDATOR] Found {len(critical_issues)} critical issues, {len(warning_issues)} warnings")
                
                # Format for display
                validation_summary = self.pattern_validator.format_issues_for_display(pattern_issues)
                await self._update_status(validation_summary)
                
                # Try auto-fix if we have critical issues
                if critical_issues:
                    await self._update_status("🔧 Attempting to auto-fix critical issues...")
                    fixed, fixed_files, fixes = self.pattern_validator.auto_fix_issues(swift_files, pattern_issues)
                    
                    if fixed and fixed_files:
                        # Write fixed files back
                        for file in fixed_files:
                            file_path = os.path.join(project_path, file["path"])
                            file_dir = os.path.dirname(file_path)
                            os.makedirs(file_dir, exist_ok=True)
                            
                            with open(file_path, 'w') as f:
                                f.write(file["content"])
                        
                        # Update swift_files for build
                        swift_files = fixed_files
                        await self._update_status(f"✅ Applied {len(fixes)} pattern fixes")
                        warnings.append(f"Auto-fixed {len(fixes)} pattern issues")
                    else:
                        # Add critical issues as errors
                        for issue in critical_issues[:5]:  # Limit to first 5
                            errors.append(f"{issue.file_path}:{issue.line_number} - {issue.message}")
                
                # Add warnings for non-critical issues
                for issue in warning_issues[:3]:  # Limit to first 3
                    warnings.append(f"{issue.file_path}:{issue.line_number} - {issue.message}")

        # Fix naming consistency
        fix_naming_consistency_in_project_yml(project_path)

        # Generate Xcode project
        await self._update_status("🔧 Generating Xcode project...")
        try:
            result = subprocess.run(
                ["xcodegen", "generate"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                error_msg = f"XcodeGen failed: {result.stderr}"
                await self._update_status(error_msg)
                errors.append(error_msg)
                return BuildResult(
                    success=False,
                    errors=errors,
                    warnings=warnings,
                    build_time=(datetime.now() - start_time).total_seconds(),
                    app_path=None,
                    log_path=log_path if 'log_path' in locals() else None
                )

        except subprocess.TimeoutExpired:
            errors.append("XcodeGen timed out")
            return BuildResult(
                success=False,
                errors=errors,
                warnings=warnings,
                build_time=(datetime.now() - start_time).total_seconds(),
                app_path=None,
                log_path=log_path if 'log_path' in locals() else None
            )
        except Exception as e:
            errors.append(f"XcodeGen error: {str(e)}")
            return BuildResult(
                success=False,
                errors=errors,
                warnings=warnings,
                build_time=(datetime.now() - start_time).total_seconds(),
                app_path=None,
                log_path=log_path if 'log_path' in locals() else None
            )

        # Attempt to build with recovery
        attempt = 0
        last_build_errors = []

        while attempt < self.max_attempts:
            attempt += 1
            print(f"[BUILD] Starting build attempt {attempt}/{self.max_attempts}")

            # Clean build folder for fresh start or after recovery
            if attempt == 1 or (attempt > 1 and 'recovery_applied' in locals() and recovery_applied):
                await self._update_status("🧹 Cleaning build folder...")
                build_dir = os.path.join(project_path, "build")
                if os.path.exists(build_dir):
                    shutil.rmtree(build_dir)
                if 'recovery_applied' in locals():
                    del recovery_applied

            await self._update_status(f"🏗️ Building app (attempt {attempt}/{self.max_attempts})...")

            # Run xcodebuild
            build_result = await self._run_xcodebuild(project_path, bundle_id, log_path)

            if build_result["success"]:
                # Build succeeded!
                await self._update_status("✅ Build completed successfully!")

                # Try to launch in simulator if available
                if self.simulator_service:
                    try:
                        app_path = build_result.get("app_path")
                        if app_path:
                            await self._update_status("📱 Preparing to launch in iOS Simulator...")
                            await self._update_status(f"Build completed successfully for {os.path.basename(app_path)}")
                            
                            # Use the combined install_and_launch_app method like in the GitHub version
                            launch_success, launch_message = await self.simulator_service.install_and_launch_app(
                                app_path,
                                bundle_id,
                                self._update_status
                            )
                            
                            if launch_success:
                                await self._update_status("🎉 App launched successfully!")
                                build_result["simulator_launched"] = True
                            else:
                                warnings.append(f"Simulator: {launch_message}")
                                await self._update_status(f"Simulator launch issue: {launch_message}")
                    except Exception as e:
                        await self._update_status(f"Simulator error: {str(e)}")
                        warnings.append(f"Simulator error: {str(e)}")

                return BuildResult(
                    success=True,
                    errors=[],
                    warnings=warnings,
                    build_time=(datetime.now() - start_time).total_seconds(),
                    app_path=build_result.get("app_path"),  # Fixed: was output_path
                    simulator_launched=build_result.get("simulator_launched", False),
                    log_path=log_path
                )

            # Build failed - try to recover
            current_errors = build_result.get("errors", [])
            last_build_errors = current_errors
            
            print(f"[BUILD] Build attempt {attempt} failed with {len(current_errors)} errors")
            
            # Log build errors if debug logger available
            if self.debug_logger:
                self.debug_logger.log_build_attempt(attempt, self.max_attempts)
                for error in current_errors[:10]:  # Log first 10 errors
                    self.debug_logger.log_build_error(error)

            if attempt < self.max_attempts:
                await self._update_status("❌ Build failed. Analyzing errors and applying fixes...")

                # Try error recovery if available
                if self.error_recovery_system and current_errors:
                    try:
                        # Parse unique errors
                        unique_errors = self._extract_unique_errors(current_errors)
                        print(f"[BUILD] Found {len(unique_errors)} unique errors for recovery")
                        
                        # Use user-friendly error messages
                        if self.user_friendly_handler:
                            friendly_message = self.user_friendly_handler.format_for_websocket(unique_errors)
                            await self._update_status(friendly_message)
                        else:
                            await self._update_status(f"🔧 Found {len(unique_errors)} errors. Attempting automatic recovery...")

                        # FIXED: Use correct parameter name 'swift_files'
                        success, fixed_files, fixes = await self.error_recovery_system.recover_from_errors(
                            errors=unique_errors,
                            swift_files=swift_files,  # CORRECT PARAMETER NAME
                            bundle_id=bundle_id
                        )

                        if success and fixed_files:
                            print(f"[BUILD] Recovery succeeded with {len(fixed_files)} fixed files")
                            await self._update_status(f"📝 Writing {len(fixed_files)} fixed files...")
                            
                            # Use file structure manager for organized writing and verification
                            if self.file_structure_manager:
                                # First organize files into proper structure
                                organized_files, file_mapping = self.file_structure_manager.organize_files(
                                    fixed_files, project_path
                                )
                                
                                # Write files with verification
                                write_success, written_files, failed_files = self.file_structure_manager.verify_and_write_files(
                                    organized_files, project_path
                                )
                                
                                if failed_files:
                                    warnings.append(f"Failed to write {len(failed_files)} files: {', '.join(failed_files[:3])}")
                                
                                # Log file structure
                                print(f"[BUILD] File structure after recovery:")
                                print(self.file_structure_manager.get_file_tree(project_path))
                                
                                # Debug logging for file operations
                                if self.debug_logger:
                                    self.debug_logger.log_error_recovery("File Structure Manager", {
                                        "organized_files": len(organized_files),
                                        "written_files": len(written_files),
                                        "failed_files": len(failed_files),
                                        "file_mapping": len(file_mapping)
                                    })
                                    self.debug_logger.log_file_structure(organized_files, phase="recovery")
                                    self.debug_logger.log_directory_structure(project_path)
                                
                                await self._update_status(f"✅ Verified {len(written_files)} files written successfully")
                            else:
                                # Fallback to original method
                                for file in fixed_files:
                                    if not isinstance(file, dict) or "path" not in file or "content" not in file:
                                        print(f"[BUILD] Skipping invalid file: {type(file)}")
                                        continue  # Skip invalid files silently
                                    
                                    # Use the full relative path to preserve directory structure
                                    file_path = os.path.join(project_path, file["path"])
                                    
                                    # Create directory if it doesn't exist
                                    file_dir = os.path.dirname(file_path)
                                    os.makedirs(file_dir, exist_ok=True)
                                    
                                    print(f"[BUILD] Writing fixed file: {file_path}")
                                    with open(file_path, 'w') as f:
                                        f.write(file["content"])
                                        
                                await self._update_status(f"✅ Fixed files written successfully")

                            # Update swift_files for next iteration
                            swift_files = fixed_files

                            await self._update_status(f"✅ Applied {len(fixes)} fixes. Rebuilding...")
                            await self._update_status(f"Applied {len(fixes)} automated fixes: {', '.join(fixes[:3])}")
                            # Mark that recovery was applied
                            recovery_applied = True
                            print(f"[BUILD] Recovery applied, continuing to next build attempt")
                            # Don't reset attempt to 0, just continue to next build
                            continue
                        else:
                            print(f"[BUILD] Recovery failed or no files returned")

                    except Exception as e:
                        # Log error recovery failure silently
                        warnings.append(f"Recovery system error: {str(e)}")

                # If no fixes were applied, try clean rebuild
                await self._update_status("No automatic fixes available. Trying clean rebuild...")
                build_dir = os.path.join(project_path, "build")
                if os.path.exists(build_dir):
                    shutil.rmtree(build_dir)

        # All attempts failed
        print(f"[BUILD] All {attempt} attempts exhausted. Build failed.")
        print(f"[BUILD] Last errors: {last_build_errors[:3]}")
        await self._update_status("❌ Build failed after all attempts")
        
        final_result = BuildResult(
            success=False,
            errors=last_build_errors,
            warnings=warnings,
            build_time=(datetime.now() - start_time).total_seconds(),
            app_path=None,
            log_path=log_path
        )
        print(f"[BUILD] Returning failed result to main.py")
        return final_result

    def _validate_swift_syntax(self, swift_files: List[Dict]) -> List[str]:
        """Basic Swift syntax validation"""
        errors = []

        for file in swift_files:
            content = file["content"]
            path = file["path"]

            # Check for common syntax errors
            if content.count('"') % 2 != 0:
                errors.append(f"{path}: Unmatched quotes detected")

            if content.count('{') != content.count('}'):
                errors.append(f"{path}: Mismatched braces")

            if content.count('(') != content.count(')'):
                errors.append(f"{path}: Mismatched parentheses")

            if content.count('[') != content.count(']'):
                errors.append(f"{path}: Mismatched square brackets")
            
            # CRITICAL: Check for invalid module imports
            invalid_imports = re.findall(r'import\s+(Components|Views|Models|ViewModels|Services|Utilities|Helpers|Extensions)\b', content)
            if invalid_imports:
                errors.append(f"{path}: Invalid local module imports detected: {', '.join(invalid_imports)}. SwiftUI doesn't use module imports for local files.")
            
            # Check for module prefixes (e.g., Components.MyView)
            module_prefixes = re.findall(r'(Components|Views|Models|ViewModels|Services|Utilities|Helpers|Extensions)\.(\w+)', content)
            if module_prefixes:
                errors.append(f"{path}: Invalid module prefixes detected. Use direct type references instead (e.g., MyView not Components.MyView)")

        return errors

    async def _run_xcodebuild(self, project_path: str, bundle_id: str, log_path: str = None) -> Dict:
        """Run xcodebuild command"""

        # Look for .xcodeproj file
        xcodeproj = None
        for item in os.listdir(project_path):
            if item.endswith('.xcodeproj'):
                xcodeproj = item
                break

        if not xcodeproj:
            return {
                "success": False,
                "errors": ["No .xcodeproj file found"]
            }

        # Build command
        build_command = [
            "xcodebuild",
            "-project", xcodeproj,
            "-scheme", xcodeproj.replace('.xcodeproj', ''),
            "-destination", "platform=iOS Simulator,name=iPhone 16",
            "-configuration", "Debug",
            "-derivedDataPath", "build",
            "CODE_SIGN_IDENTITY=",
            "CODE_SIGNING_REQUIRED=NO",
            "CODE_SIGNING_ALLOWED=NO",
            "build"
        ]

        try:
            # Clean any macOS metadata before building
            subprocess.run(
                ["xattr", "-cr", project_path],
                capture_output=True
            )
            
            # Run build
            result = subprocess.run(
                build_command,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Write build output to log file if provided
            if log_path:
                with open(log_path, 'a') as f:
                    f.write("\n--- xcodebuild output ---\n")
                    f.write(result.stdout)
                    if result.stderr:
                        f.write("\n--- xcodebuild errors ---\n")
                        f.write(result.stderr)
                    f.write("\n--- end xcodebuild output ---\n")

            if result.returncode == 0:
                # Find the .app bundle
                app_path = self._find_app_bundle(project_path)
                return {
                    "success": True,
                    "app_path": app_path,
                    "output": result.stdout
                }
            else:
                # Parse errors from output
                errors = self._parse_xcodebuild_errors(result.stdout + result.stderr)
                return {
                    "success": False,
                    "errors": errors,
                    "output": result.stdout + result.stderr
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "errors": ["Build timed out after 120 seconds"]
            }
        except Exception as e:
            return {
                "success": False,
                "errors": [f"Build error: {str(e)}"]
            }

    def _find_app_bundle(self, project_path: str) -> Optional[str]:
        """Find the built .app bundle"""
        build_dir = os.path.join(project_path, "build", "Build", "Products")
        # Looking for app bundle

        if os.path.exists(build_dir):
            for root, dirs, files in os.walk(build_dir):
                for dir_name in dirs:
                    if dir_name.endswith('.app'):
                        app_path = os.path.join(root, dir_name)
                        # Found app bundle
                        return app_path
        else:
            print(f"[BUILD] Build directory does not exist: {build_dir}")

        return None

    def _parse_xcodebuild_errors(self, output: str) -> List[str]:
        """Parse errors from xcodebuild output"""
        errors = []

        # Common error patterns
        error_patterns = [
            r"error: (.+)",
            r"fatal error: (.+)",
            r"\*\* BUILD FAILED \*\*",
            r"The following build commands failed:",
            r"CompileSwift normal .+ (.+\.swift)",
            r"(.+\.swift):(\d+):(\d+): error: (.+)"
        ]

        lines = output.split('\n')
        for i, line in enumerate(lines):
            for pattern in error_patterns:
                match = re.search(pattern, line)
                if match:
                    if "BUILD FAILED" in line:
                        # Look for the actual error in nearby lines
                        for j in range(max(0, i-10), min(len(lines), i+10)):
                            if "error:" in lines[j]:
                                errors.append(lines[j].strip())
                    else:
                        errors.append(line.strip())
                    break

        # Remove duplicates while preserving order
        seen = set()
        unique_errors = []
        for error in errors:
            if error not in seen:
                seen.add(error)
                unique_errors.append(error)

        return unique_errors[:10]  # Limit to first 10 errors

    def _extract_unique_errors(self, errors: List[str]) -> List[str]:
        """Extract unique, meaningful errors"""
        unique = []
        seen = set()

        for error in errors:
            # Clean up the error
            cleaned = re.sub(r'/.+/Sources/', 'Sources/', error)
            cleaned = re.sub(r'^\s*\d+\s+', '', cleaned)

            if cleaned not in seen and len(cleaned) > 10:
                seen.add(cleaned)
                unique.append(cleaned)

        return unique