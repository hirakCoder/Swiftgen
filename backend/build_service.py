import os
import subprocess
import asyncio
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from models import BuildStatus, BuildResult

class BuildService:
    def __init__(self):
        # Use absolute path for build logs
        self.backend_dir = os.path.dirname(os.path.abspath(__file__))
        self.workspaces_dir = os.path.abspath(os.path.join(self.backend_dir, "..", "workspaces"))
        self.build_logs_dir = os.path.join(self.workspaces_dir, "build_logs")
        os.makedirs(self.build_logs_dir, exist_ok=True)

        # Try to import SimulatorService
        try:
            from simulator_service import SimulatorService
            self.simulator_service = SimulatorService()
        except ImportError:
            print("Warning: simulator_service not available. Simulator launch disabled.")
            self.simulator_service = None

        # Import ClaudeService for intelligent error recovery
        try:
            from claude_service import ClaudeService
            self.claude_service = ClaudeService()
            self.has_ai_recovery = True
        except ImportError:
            print("Warning: claude_service not available. Auto-fix disabled.")
            self.claude_service = None
            self.has_ai_recovery = False

        self.status_callback = None
        self.max_retry_attempts = 3

    def set_status_callback(self, callback):
        """Set callback for status updates"""
        self.status_callback = callback

    async def _update_status(self, message: str):
        """Send status update if callback is set"""
        if self.status_callback:
            await self.status_callback(message)
        print(f"[BUILD STATUS] {message}")

    async def build_project(self, project_path: str, project_id: str, bundle_id: Optional[str] = None) -> BuildResult:
        """Build iOS project with intelligent error recovery"""

        if not os.path.isabs(project_path):
            project_path = os.path.abspath(os.path.join(self.backend_dir, project_path))

        build_log_path = os.path.join(self.build_logs_dir, f"{project_id}_build.log")

        # Generate Xcode project first
        await self._update_status("Generating Xcode project...")
        gen_result = await self._run_xcodegen(project_path)
        if not gen_result[0]:
            return BuildResult(
                success=False,
                errors=[f"Failed to generate Xcode project: {gen_result[1]}"],
                warnings=[],
                build_time=0,
                log_path=build_log_path
            )

        # Clean build folder
        await self._update_status("Cleaning build folder...")
        await self._clean_build(project_path)

        # Build with intelligent retry
        start_time = datetime.now()

        for attempt in range(self.max_retry_attempts):
            await self._update_status(f"Building app (attempt {attempt + 1}/{self.max_retry_attempts})...")

            success, output, errors = await self._run_xcodebuild(project_path)

            # Save build log
            with open(build_log_path, 'a') as f:
                f.write(f"\n\n=== BUILD ATTEMPT {attempt + 1} ===\n")
                f.write(output)
                if errors:
                    f.write("\n\nERRORS:\n")
                    f.write("\n".join(errors))

            if success:
                # Build succeeded!
                build_time = (datetime.now() - start_time).total_seconds()
                return await self._handle_successful_build(
                    project_path, project_id, bundle_id, build_log_path,
                    build_time, output
                )
            else:
                # Build failed - attempt intelligent recovery
                if attempt < self.max_retry_attempts - 1 and self.has_ai_recovery:
                    await self._update_status("Build failed. Analyzing errors and applying AI fixes...")

                    fixed = await self._intelligent_error_recovery(
                        project_path, project_id, errors, output
                    )

                    if fixed:
                        await self._update_status("Applied AI-generated fixes. Rebuilding...")
                        continue
                    else:
                        await self._update_status("AI fix didn't resolve all issues. Trying alternative approach...")
                else:
                    # Final attempt failed
                    build_time = (datetime.now() - start_time).total_seconds()
                    return BuildResult(
                        success=False,
                        errors=errors[:5],  # Limit errors shown
                        warnings=self._parse_warnings(output),
                        build_time=build_time,
                        log_path=build_log_path
                    )

        # Should never reach here
        return BuildResult(
            success=False,
            errors=["Max retry attempts reached"],
            warnings=[],
            build_time=(datetime.now() - start_time).total_seconds(),
            log_path=build_log_path
        )

    async def _intelligent_error_recovery(self, project_path: str, project_id: str,
                                        errors: List[str], build_output: str) -> bool:
        """Use AI to intelligently fix build errors with multi-stage recovery"""

        if not self.claude_service:
            return False

        try:
            # Import the intelligent recovery system
            from intelligent_error_recovery import IntelligentErrorRecovery

            # Initialize recovery system if not already done
            if not hasattr(self, 'error_recovery_system'):
                self.error_recovery_system = IntelligentErrorRecovery(self.claude_service)

            # Get all Swift files
            swift_files = []
            sources_dir = os.path.join(project_path, "Sources")

            if os.path.exists(sources_dir):
                for file in os.listdir(sources_dir):
                    if file.endswith('.swift'):
                        file_path = os.path.join(sources_dir, file)
                        with open(file_path, 'r') as f:
                            content = f.read()
                        swift_files.append({
                            "path": f"Sources/{file}",
                            "content": content
                        })

            # Use multi-stage recovery
            await self._update_status("Analyzing build errors...")
            fixed, modified_files = await self.error_recovery_system.recover_from_errors(
                errors, swift_files, project_path
            )

            if fixed:
                # Apply the fixes
                await self._update_status("Applying automated fixes...")
                for file_info in modified_files:
                    file_path = os.path.join(project_path, file_info["path"])
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)

                    with open(file_path, 'w') as f:
                        f.write(file_info["content"])

                return True
            else:
                # Fallback to original Claude-based recovery
                await self._update_status("Attempting advanced AI recovery...")
                return await self._original_claude_recovery(project_path, project_id, errors, build_output)

        except ImportError:
            # If intelligent recovery not available, use original method
            print("Intelligent recovery system not available, using standard recovery")
            return await self._original_claude_recovery(project_path, project_id, errors, build_output)
        except Exception as e:
            print(f"Error in intelligent recovery: {str(e)}")
            return False

    async def _original_claude_recovery(self, project_path: str, project_id: str,
                                      errors: List[str], build_output: str) -> bool:
        """Original Claude-based recovery as fallback"""

        try:
            # Get all Swift files
            swift_files = []
            sources_dir = os.path.join(project_path, "Sources")

            if os.path.exists(sources_dir):
                for file in os.listdir(sources_dir):
                    if file.endswith('.swift'):
                        file_path = os.path.join(sources_dir, file)
                        with open(file_path, 'r') as f:
                            content = f.read()
                        swift_files.append({
                            "path": f"Sources/{file}",
                            "content": content
                        })

            # Create intelligent error recovery prompt
            prompt = self._create_error_recovery_prompt(errors, swift_files, build_output)

            # Get AI fix
            await self._update_status("Requesting AI analysis of build errors...")

            # Call Claude API directly for error fixing
            response = await self._call_claude_for_fixes(prompt)

            if response and "files" in response:
                # Apply the fixes
                await self._update_status("Applying AI-generated code fixes...")

                for file_info in response["files"]:
                    file_path = os.path.join(project_path, file_info["path"])
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)

                    with open(file_path, 'w') as f:
                        f.write(file_info["content"])

                fixes_applied = response.get('fixes_applied', ['Applied AI fixes'])
                print(f"AI Fixes applied: {fixes_applied}")

                return True
            else:
                print("AI couldn't generate fixes")
                return False

        except Exception as e:
            print(f"Error in Claude recovery: {str(e)}")
            return False

    def _create_error_recovery_prompt(self, errors: List[str], swift_files: List[Dict],
                                     build_output: str) -> str:
        """Create a sophisticated prompt for error recovery"""

        # Extract the most relevant part of build output
        relevant_output = self._extract_relevant_build_output(build_output, errors)

        errors_text = '\n'.join(errors)
        code_sections = []
        for f in swift_files:
            code_sections.append(f"File: {f['path']}\n```swift\n{f['content']}\n```")
        code_context = '\n\n'.join(code_sections)

        # Analyze common error patterns
        error_hints = []
        if "cannot find type" in errors_text or "cannot find" in errors_text:
            error_hints.append("Missing imports - ensure all necessary frameworks are imported (SwiftUI, Foundation, etc.)")
        if "@main" in errors_text:
            error_hints.append("Main app struct issues - ensure proper App protocol conformance")
        if "error:" in errors_text and ".swift:" in errors_text:
            error_hints.append("Syntax errors - check for proper Swift syntax")

        prompt = f"""You are an expert iOS developer. Fix these Swift compilation errors:

BUILD ERRORS:
{errors_text}

ERROR ANALYSIS HINTS:
{chr(10).join(error_hints) if error_hints else "No specific patterns detected"}

RELEVANT BUILD OUTPUT:
{relevant_output}

CURRENT CODE FILES:
{code_context}

REQUIREMENTS:
1. Analyze each error carefully - understand the ROOT CAUSE
2. Common issues to check:
   - Missing imports (ALWAYS import SwiftUI for SwiftUI apps)
   - Typos in type names or method calls
   - Missing protocol conformance
   - Incorrect syntax
   - Missing closing braces
3. Provide COMPLETE fixed code (not snippets)
4. Ensure all Swift syntax is correct
5. Follow iOS 16+ and SwiftUI best practices
6. Make minimal changes to fix the errors
7. Preserve all existing functionality

CRITICAL: Many errors are caused by missing imports. ENSURE:
- Every SwiftUI file starts with: import SwiftUI
- App main files have proper structure
- All necessary frameworks are imported

Return ONLY a JSON object:
{{
    "files": [
        {{
            "path": "Sources/filename.swift",
            "content": "// Complete FIXED Swift code with all imports"
        }}
        // Include ALL files that need fixes
    ],
    "fixes_applied": [
        "Added missing SwiftUI import",
        "Fixed App protocol conformance",
        // List each specific fix
    ],
    "explanation": "Brief explanation of what was wrong"
}}"""

        return prompt

    def _extract_relevant_build_output(self, build_output: str, errors: List[str]) -> str:
        """Extract relevant parts of build output around errors"""

        lines = build_output.split('\n')
        relevant_lines = []

        for error in errors[:3]:  # Focus on first 3 errors
            # Find error in output and get context
            for i, line in enumerate(lines):
                if error in line:
                    # Get 5 lines before and after
                    start = max(0, i - 5)
                    end = min(len(lines), i + 6)
                    relevant_lines.extend(lines[start:end])
                    relevant_lines.append("---")
                    break

        return '\n'.join(relevant_lines[:100])  # Limit size

    async def _call_claude_for_fixes(self, prompt: str) -> Optional[Dict]:
        """Call Claude API for error fixes"""

        if not self.claude_service:
            return None

        try:
            # Use the claude service's internal method
            response = await self.claude_service._call_claude_api(prompt)
            return response
        except Exception as e:
            print(f"Error calling Claude for fixes: {str(e)}")
            return None

    async def _handle_successful_build(self, project_path: str, project_id: str,
                                      bundle_id: Optional[str], build_log_path: str,
                                      build_time: float, output: str) -> BuildResult:
        """Handle successful build and launch simulator"""

        warnings = self._parse_warnings(output)
        app_path = self._get_app_path(project_path)

        if app_path and self.simulator_service:
            await self._update_status("Build successful! Preparing simulator...")

            if not bundle_id:
                bundle_id = self._get_bundle_id_from_project(project_path)

            if bundle_id:
                await self._update_status("Booting simulator...")
                simulator_ready, _, sim_message = await self.simulator_service.ensure_simulator_booted()

                if simulator_ready:
                    await self._update_status("Installing and launching app...")
                    launch_success, launch_message = await self.simulator_service.install_and_launch_app(
                        app_path,
                        bundle_id,
                        self._update_status
                    )

                    if launch_success:
                        await self._update_status("✅ App launched successfully in simulator!")
                        return BuildResult(
                            success=True,
                            errors=[],
                            warnings=warnings,
                            build_time=build_time,
                            log_path=build_log_path,
                            app_path=app_path,
                            simulator_launched=True,
                            simulator_message=launch_message
                        )
                    else:
                        warnings.append(f"Failed to launch app: {launch_message}")
                else:
                    warnings.append(f"Failed to boot simulator: {sim_message}")
            else:
                warnings.append("Could not determine bundle ID for app launch")

        return BuildResult(
            success=True,
            errors=[],
            warnings=warnings,
            build_time=build_time,
            log_path=build_log_path,
            app_path=app_path if app_path else None,
            simulator_launched=False
        )

    # Keep all the existing helper methods from your current build_service.py
    def _get_bundle_id_from_project(self, project_path: str) -> Optional[str]:
        """Extract bundle ID from project files"""
        project_json_path = os.path.join(project_path, "project.json")
        if os.path.exists(project_json_path):
            try:
                with open(project_json_path, 'r') as f:
                    data = json.load(f)
                    bundle_id = data.get('bundle_id')
                    if bundle_id:
                        return bundle_id
            except:
                pass

        project_yml_path = os.path.join(project_path, "project.yml")
        if os.path.exists(project_yml_path):
            try:
                import yaml
                with open(project_yml_path, 'r') as f:
                    data = yaml.safe_load(f)
                    for target_name, target_data in data.get('targets', {}).items():
                        settings = target_data.get('settings', {}).get('base', {})
                        bundle_id = settings.get('PRODUCT_BUNDLE_IDENTIFIER')
                        if bundle_id:
                            return bundle_id
            except:
                pass

        return None

    async def _run_xcodegen(self, project_path: str) -> Tuple[bool, str]:
        """Run xcodegen to create Xcode project"""
        try:
            check_process = await asyncio.create_subprocess_exec(
                'which', 'xcodegen',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await check_process.communicate()

            if check_process.returncode != 0:
                return False, "xcodegen not found. Please install it: brew install xcodegen"

            process = await asyncio.create_subprocess_exec(
                'xcodegen', 'generate',
                cwd=project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                print(f"xcodegen error: {error_msg}")
                return False, error_msg

            print(f"xcodegen output: {stdout.decode()}")
            return True, stdout.decode()

        except FileNotFoundError:
            return False, "xcodegen not found. Please install it: brew install xcodegen"
        except Exception as e:
            return False, f"xcodegen error: {str(e)}"

    async def _clean_build(self, project_path: str):
        """Clean build artifacts"""
        derived_data_path = os.path.join(project_path, "DerivedData")
        if os.path.exists(derived_data_path):
            subprocess.run(['rm', '-rf', derived_data_path])

    async def _get_available_simulators(self) -> List[str]:
        """Get list of available iOS simulators"""
        try:
            cmd = ['xcrun', 'simctl', 'list', 'devices', 'available', '-j']
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                devices_data = json.loads(stdout.decode())
                simulators = []

                for runtime, devices in devices_data.get('devices', {}).items():
                    if 'iOS' in runtime:
                        for device in devices:
                            if device.get('isAvailable', False):
                                simulators.append(device['name'])

                return simulators
        except:
            pass

        return []

    async def _run_xcodebuild(self, project_path: str) -> Tuple[bool, str, List[str]]:
        """Execute xcodebuild command"""

        xcodeproj = None
        print(f"Looking for .xcodeproj in: {project_path}")

        for item in os.listdir(project_path):
            if item.endswith('.xcodeproj'):
                xcodeproj = item
                print(f"Found xcodeproj: {xcodeproj}")
                break

        if not xcodeproj:
            return False, "", ["No .xcodeproj file found. xcodegen may have failed."]

        scheme_name = xcodeproj.replace('.xcodeproj', '')
        xcodeproj_path = os.path.join(project_path, xcodeproj)
        derived_data_path = os.path.join(project_path, 'DerivedData')

        # Get available simulators
        available_simulators = await self._get_available_simulators()
        print(f"Available simulators: {available_simulators}")

        # Build command
        destinations_to_try = []

        for sim_name in ["iPhone 16 Pro", "iPhone 16", "iPhone 15", "iPhone 14"]:
            if sim_name in available_simulators:
                destinations_to_try.append(f"platform=iOS Simulator,name={sim_name}")
                break

        destinations_to_try.append("generic/platform=iOS Simulator")

        for destination in destinations_to_try:
            cmd = [
                'xcodebuild',
                '-project', xcodeproj_path,
                '-scheme', scheme_name,
                '-configuration', 'Debug',
                '-derivedDataPath', derived_data_path,
                '-destination', destination,
                '-sdk', 'iphonesimulator',
                'CODE_SIGN_IDENTITY=',
                'CODE_SIGNING_REQUIRED=NO',
                'CODE_SIGNING_ALLOWED=NO',
                'build'
            ]

            print(f"Trying build with destination: {destination}")

            try:
                env = os.environ.copy()
                env['PLATFORM_NAME'] = 'iphonesimulator'

                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=env
                )

                stdout, stderr = await process.communicate()

                output = stdout.decode()
                stderr_output = stderr.decode()

                if process.returncode == 0:
                    print(f"Build succeeded with destination: {destination}")
                    return True, output, []

                # Parse errors
                errors = self._parse_errors(stderr_output + output)

                # If it's actual compilation errors (not destination issues), return them
                if errors and not any("destination" in e.lower() for e in errors):
                    return False, output, errors

                print(f"Destination {destination} failed, trying next...")

            except Exception as e:
                print(f"Error with destination {destination}: {str(e)}")
                continue

        # Try minimal build as last resort
        print("Trying minimal build...")

        cmd = [
            'xcodebuild',
            '-project', xcodeproj_path,
            '-scheme', scheme_name,
            '-sdk', 'iphonesimulator',
            '-configuration', 'Debug',
            '-derivedDataPath', derived_data_path,
            'CODE_SIGN_IDENTITY=',
            'CODE_SIGNING_REQUIRED=NO',
            'build'
        ]

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                print("Minimal build succeeded!")
                return True, stdout.decode(), []
            else:
                errors = self._parse_errors(stderr.decode() + stdout.decode())
                return False, stdout.decode(), errors

        except Exception as e:
            return False, "", [f"Build failed: {str(e)}"]

    def _parse_errors(self, text: str) -> List[str]:
        """Parse error messages from build output"""
        errors = []
        lines = text.split('\n')

        for i, line in enumerate(lines):
            line = line.strip()

            # Look for Swift compilation errors specifically
            if ('error:' in line and '.swift' in line) or \
               ('** BUILD FAILED **' in line) or \
               ('fatal error:' in line):

                # Don't duplicate BUILD FAILED
                if '** BUILD FAILED **' in line and errors:
                    continue

                # For Swift errors, try to get the full error message
                if '.swift:' in line and 'error:' in line:
                    # This is a Swift compilation error
                    error_msg = line

                    # Sometimes error details are on next lines
                    if i + 1 < len(lines) and lines[i + 1].strip():
                        next_line = lines[i + 1].strip()
                        if not any(keyword in next_line for keyword in ['error:', 'warning:', '.swift:']):
                            error_msg += f" {next_line}"

                    errors.append(error_msg)
                else:
                    errors.append(line)

        return errors[:10]

    def _parse_warnings(self, output: str) -> List[str]:
        """Parse warning messages from build output"""
        warnings = []
        for line in output.split('\n'):
            if 'warning:' in line.lower() and '.swift' in line:
                warnings.append(line.strip())
        return warnings[:10]

    def _get_app_path(self, project_path: str) -> Optional[str]:
        """Get path to built .app bundle"""
        derived_data = os.path.join(project_path, "DerivedData")
        build_products = os.path.join(derived_data, "Build", "Products", "Debug-iphonesimulator")

        if os.path.exists(build_products):
            for item in os.listdir(build_products):
                if item.endswith('.app'):
                    return os.path.join(build_products, item)

        return None