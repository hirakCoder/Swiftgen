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

        self.status_callback = None

    def set_status_callback(self, callback):
        """Set callback for status updates"""
        self.status_callback = callback

    async def _update_status(self, message: str):
        """Send status update if callback is set"""
        if self.status_callback:
            await self.status_callback(message)

    async def build_project(self, project_path: str, project_id: str, bundle_id: Optional[str] = None) -> BuildResult:
        """Build iOS project using xcodebuild and optionally launch in simulator"""

        # Convert to absolute path if it's relative
        if not os.path.isabs(project_path):
            project_path = os.path.abspath(os.path.join(self.backend_dir, project_path))

        build_log_path = os.path.join(self.build_logs_dir, f"{project_id}_build.log")

        try:
            # First, generate Xcode project using xcodegen
            await self._update_status("Generating Xcode project...")
            print(f"Generating Xcode project for {project_id}...")

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
            print(f"Cleaning build folder for {project_id}...")
            await self._clean_build(project_path)

            # Run xcodebuild
            await self._update_status("Building app...")
            print(f"Building project {project_id}...")
            start_time = datetime.now()

            success, output, errors = await self._run_xcodebuild(project_path)

            build_time = (datetime.now() - start_time).total_seconds()

            # Save build log
            with open(build_log_path, 'w') as f:
                f.write(output)
                if errors:
                    f.write("\n\nERRORS:\n")
                    f.write("\n".join(errors))

            # Parse warnings from output
            warnings = self._parse_warnings(output)

            if success:
                app_path = self._get_app_path(project_path)
                if app_path and self.simulator_service:
                    await self._update_status("Build successful! Preparing simulator...")

                    # Get bundle ID if not provided
                    if not bundle_id:
                        bundle_id = self._get_bundle_id_from_project(project_path)

                    if bundle_id:
                        # Launch in simulator
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

                # Return success even if simulator launch failed
                return BuildResult(
                    success=True,
                    errors=[],
                    warnings=warnings,
                    build_time=build_time,
                    log_path=build_log_path,
                    app_path=app_path if app_path else None,
                    simulator_launched=False
                )
            else:
                return BuildResult(
                    success=False,
                    errors=errors,
                    warnings=warnings,
                    build_time=build_time,
                    log_path=build_log_path
                )

        except Exception as e:
            return BuildResult(
                success=False,
                errors=[f"Build system error: {str(e)}"],
                warnings=[],
                build_time=0,
                log_path=build_log_path
            )

    def _get_bundle_id_from_project(self, project_path: str) -> Optional[str]:
        """Extract bundle ID from project files"""
        # Try to get from project.json
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

        # Try to get from project.yml
        project_yml_path = os.path.join(project_path, "project.yml")
        if os.path.exists(project_yml_path):
            try:
                import yaml
                with open(project_yml_path, 'r') as f:
                    data = yaml.safe_load(f)
                    # Look in targets
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
            # Check if xcodegen is installed
            check_process = await asyncio.create_subprocess_exec(
                'which', 'xcodegen',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await check_process.communicate()

            if check_process.returncode != 0:
                return False, "xcodegen not found. Please install it: brew install xcodegen"

            # Run xcodegen
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

                # Parse the JSON structure
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

        # Find the .xcodeproj file
        xcodeproj = None
        print(f"Looking for .xcodeproj in: {project_path}")

        for item in os.listdir(project_path):
            if item.endswith('.xcodeproj'):
                xcodeproj = item
                print(f"Found xcodeproj: {xcodeproj}")
                break

        if not xcodeproj:
            return False, "", ["No .xcodeproj file found. xcodegen may have failed."]

        # Get the scheme name (usually same as project name without extension)
        scheme_name = xcodeproj.replace('.xcodeproj', '')

        # Use absolute paths
        xcodeproj_path = os.path.join(project_path, xcodeproj)
        derived_data_path = os.path.join(project_path, 'DerivedData')

        # Get available simulators
        available_simulators = await self._get_available_simulators()
        print(f"Available simulators: {available_simulators[:5]}...")

        # Define preferred simulators based on what's available
        preferred_simulators = []

        # Add iPhone 16 series first (since that's what you have)
        for sim in ["iPhone 16 Pro", "iPhone 16 Pro Max", "iPhone 16", "iPhone 16 Plus"]:
            if sim in available_simulators:
                preferred_simulators.append(f'platform=iOS Simulator,name={sim}')

        # Add other iPhone models as fallback
        for sim in ["iPhone 15 Pro", "iPhone 15", "iPhone 14 Pro", "iPhone 14", "iPhone 13"]:
            if sim in available_simulators:
                preferred_simulators.append(f'platform=iOS Simulator,name={sim}')

        # Add generic destinations as last resort
        preferred_simulators.extend([
            'generic/platform=iOS Simulator',
            'platform=iOS Simulator,OS=latest'
        ])

        # Try each destination
        for destination in preferred_simulators:
            cmd = [
                'xcodebuild',
                '-project', xcodeproj_path,
                '-scheme', scheme_name,
                '-configuration', 'Debug',
                '-derivedDataPath', derived_data_path,
                '-destination', destination,
                # Disable code signing for simulator builds
                'CODE_SIGN_IDENTITY=',
                'CODE_SIGNING_REQUIRED=NO',
                'CODE_SIGNING_ALLOWED=NO',
                'build'
            ]

            print(f"Trying xcodebuild with destination: {destination}")

            try:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                stdout, stderr = await process.communicate()

                output = stdout.decode()
                stderr_output = stderr.decode()

                if process.returncode == 0:
                    print(f"Build succeeded with destination: {destination}")
                    return True, output, []

                # Check if it's a destination error
                if "Unable to find a device" not in stderr_output and "Cannot find a simulator" not in stderr_output:
                    # It's a different error, not a simulator issue
                    errors = self._parse_errors(stderr_output + output)
                    return False, output, errors

                print(f"Destination {destination} not available, trying next...")

            except Exception as e:
                print(f"Error with destination {destination}: {str(e)}")
                continue

        # If all destinations failed
        return False, "", [
            "No suitable iOS Simulator found.",
            f"Available simulators: {', '.join(available_simulators[:5])}...",
            "Please ensure Xcode is properly installed with iOS simulators."
        ]

    def _parse_errors(self, text: str) -> List[str]:
        """Parse error messages from build output"""
        errors = []
        lines = text.split('\n')

        for i, line in enumerate(lines):
            line = line.strip()

            # Look for error patterns
            if ('error:' in line.lower() or
                'fatal:' in line.lower() or
                'Error:' in line or
                '** BUILD FAILED **' in line or
                'CodeSign' in line):

                # Don't duplicate the BUILD FAILED message
                if '** BUILD FAILED **' in line and errors:
                    continue

                errors.append(line)

        return errors[:10]  # Limit to first 10 errors

    def _parse_warnings(self, output: str) -> List[str]:
        """Parse warning messages from build output"""
        warnings = []
        for line in output.split('\n'):
            if 'warning:' in line.lower():
                warnings.append(line.strip())
        return warnings[:10]  # Limit to first 10 warnings

    def _get_app_path(self, project_path: str) -> Optional[str]:
        """Get path to built .app bundle"""
        derived_data = os.path.join(project_path, "DerivedData")
        build_products = os.path.join(derived_data, "Build", "Products", "Debug-iphonesimulator")

        if os.path.exists(build_products):
            for item in os.listdir(build_products):
                if item.endswith('.app'):
                    return os.path.join(build_products, item)

        return None