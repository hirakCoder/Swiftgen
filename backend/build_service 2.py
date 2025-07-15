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
except ImportError as e:
    print(f"Warning: Could not import recovery systems: {e}")
    RobustErrorRecoverySystem = None
    ClaudeService = None
    EnhancedClaudeService = None

# Import simulator service
try:
    from simulator_service import SimulatorService, SimulatorState
except ImportError:
    print("Warning: SimulatorService not available")
    SimulatorService = None
    SimulatorState = None


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
        self.max_attempts = 3  # Allow enough attempts for recovery
        self.status_callback = None
        self.backend_dir = os.path.dirname(os.path.abspath(__file__))
        self.build_logs_dir = os.path.join(self.backend_dir, "build_logs")
        os.makedirs(self.build_logs_dir, exist_ok=True)

        # Initialize simulator service if available
        self.simulator_service = SimulatorService() if SimulatorService else None

        # Initialize error recovery system
        self.error_recovery_system = None
        self.claude_service = None

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
                        xai_key=os.getenv("XAI_API_KEY")
                    )
                    print("✓ Robust error recovery system initialized")
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

    async def build_project(self, project_path: str, project_id: str, bundle_id: str) -> BuildResult:
        """Build iOS project with multiple recovery strategies"""

        start_time = datetime.now()
        errors = []
        warnings = []
        build_log = []
        
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

            if attempt < self.max_attempts:
                await self._update_status("❌ Build failed. Analyzing errors and applying fixes...")

                # Try error recovery if available
                if self.error_recovery_system and current_errors:
                    try:
                        # Parse unique errors
                        unique_errors = self._extract_unique_errors(current_errors)
                        print(f"[BUILD] Found {len(unique_errors)} unique errors for recovery")
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
                            # Write fixed files back preserving directory structure
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