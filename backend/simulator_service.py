import subprocess
import time
import os
import re
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import tempfile
import shutil

class SimulatorState(Enum):
    """Simulator state enumeration"""
    SHUTDOWN = "Shutdown"
    BOOTING = "Booting"
    BOOTED = "Booted"
    UNKNOWN = "Unknown"

@dataclass
class SimulatorDevice:
    """Represents a simulator device"""
    udid: str
    name: str
    state: SimulatorState
    runtime: str
    device_type: str
    is_available: bool = True

class SimulatorError(Exception):
    """Custom exception for simulator-related errors"""
    pass

class SimulatorService:
    """Production-ready service for managing iOS simulators"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self._active_device: Optional[SimulatorDevice] = None
        self._retry_attempts = 3
        self._retry_delay = 2.0
        self._boot_timeout = 60
        self._install_timeout = 120  # Increased from 30 to 120 seconds
        self._launch_timeout = 60   # Increased from 30 to 60 seconds

    async def list_available_devices(self) -> List[SimulatorDevice]:
        """List all available iOS simulator devices"""
        try:
            result = await self._run_command(["xcrun", "simctl", "list", "devices", "--json"])
            devices_data = json.loads(result.stdout)

            devices = []
            for runtime, runtime_devices in devices_data.get("devices", {}).items():
                if "iOS" in runtime:
                    for device in runtime_devices:
                        if device.get("isAvailable", True):
                            devices.append(SimulatorDevice(
                                udid=device["udid"],
                                name=device["name"],
                                state=SimulatorState(device.get("state", "Unknown")),
                                runtime=runtime,
                                device_type=device.get("deviceTypeIdentifier", ""),
                                is_available=device.get("isAvailable", True)
                            ))

            # Sort by iOS version (newest first) and then by device name
            devices.sort(key=lambda d: (self._extract_ios_version(d.runtime), d.name), reverse=True)
            return devices

        except Exception as e:
            self.logger.error(f"Failed to list devices: {e}")
            raise SimulatorError(f"Failed to list simulator devices: {e}")

    async def find_or_create_device(self, preferred_name: str = "iPhone 16 Pro") -> SimulatorDevice:
        """Find an existing device or create a new one"""
        devices = await self.list_available_devices()

        # First try to find preferred device
        for device in devices:
            if device.name == preferred_name and device.is_available:
                self.logger.info(f"Found preferred device: {device.name} ({device.udid})")
                return device

        # Find any available iPhone
        for device in devices:
            if "iPhone" in device.name and device.is_available:
                self.logger.info(f"Using available device: {device.name} ({device.udid})")
                return device

        # Create new device if none available
        return await self._create_device(preferred_name)

    async def boot_device(self, device: SimulatorDevice) -> bool:
        """Boot a simulator device with retry logic"""
        if device.state == SimulatorState.BOOTED:
            self.logger.info(f"Device {device.name} is already booted")
            self._active_device = device
            return True

        for attempt in range(self._retry_attempts):
            try:
                self.logger.info(f"Booting {device.name} (attempt {attempt + 1}/{self._retry_attempts})")

                # Shutdown if in weird state
                if device.state not in [SimulatorState.SHUTDOWN, SimulatorState.BOOTED]:
                    await self._run_command(["xcrun", "simctl", "shutdown", device.udid])
                    await asyncio.sleep(2)

                # Boot the device
                await self._run_command(
                    ["xcrun", "simctl", "boot", device.udid],
                    timeout=self._boot_timeout
                )

                # Wait for boot to complete
                await self._wait_for_boot(device)

                # Open Simulator app
                await self._open_simulator_app()

                self._active_device = device
                self.logger.info(f"Successfully booted {device.name}")
                return True

            except Exception as e:
                self.logger.warning(f"Boot attempt {attempt + 1} failed: {e}")
                if attempt < self._retry_attempts - 1:
                    await asyncio.sleep(self._retry_delay)
                else:
                    raise SimulatorError(f"Failed to boot device after {self._retry_attempts} attempts: {e}")

        return False

    async def install_app(self, device_udid: str, app_path: str) -> bool:
        """Install app with advanced retry and cleanup logic"""
        if not os.path.exists(app_path):
            raise SimulatorError(f"App not found at: {app_path}")

        # Clean up any existing installation
        app_info = await self._get_app_info(app_path)
        bundle_id = app_info.get("CFBundleIdentifier")

        if bundle_id:
            await self._uninstall_app_if_exists(device_udid, bundle_id)

        # Try installation with different strategies
        strategies = [
            self._install_with_xcrun,
            self._install_with_copy_method,
            self._install_with_temp_copy
        ]

        for strategy in strategies:
            try:
                if await strategy(device_udid, app_path):
                    self.logger.info(f"Successfully installed app using {strategy.__name__}")
                    return True
            except Exception as e:
                self.logger.warning(f"Installation strategy {strategy.__name__} failed: {e}")
                continue

        raise SimulatorError("All installation strategies failed")

    async def launch_app(self, device_udid: str, bundle_id: str) -> bool:
        """Launch app - simple and reliable"""
        for attempt in range(self._retry_attempts):
            try:
                self.logger.info(f"Launching {bundle_id} (attempt {attempt + 1})")

                # Only terminate if this is a retry attempt (app failed to launch)
                if attempt > 0:
                    await self._run_command(
                        ["xcrun", "simctl", "terminate", device_udid, bundle_id],
                        check=False
                    )
                    await asyncio.sleep(1)

                # Launch the app (without --console to avoid hanging)
                result = await self._run_command(
                    ["xcrun", "simctl", "launch", device_udid, bundle_id],
                    timeout=10  # Much shorter timeout since we just need to trigger launch
                )

                if result.returncode == 0:
                    self.logger.info(f"Launch command succeeded for {bundle_id}")
                    # Bring Simulator to foreground
                    await self._bring_simulator_to_foreground()
                    # Success - app launched
                    return True
                else:
                    self.logger.warning(f"Launch command failed with code {result.returncode}: {result.stderr}")

            except Exception as e:
                self.logger.warning(f"Launch attempt {attempt + 1} failed: {e}")
                if attempt < self._retry_attempts - 1:
                    await asyncio.sleep(self._retry_delay)

        return False

    async def install_and_launch_app(self, app_path: str, bundle_id: str, status_callback=None) -> Tuple[bool, str]:
        """Install and launch app in simulator - matches GitHub implementation"""
        try:
            # Verify app bundle exists
            if not os.path.exists(app_path) or not app_path.endswith('.app'):
                return False, f"Invalid app bundle path: {app_path}"
            
            # Ensure simulator is booted
            if status_callback:
                await status_callback("🔄 Ensuring simulator is ready...")
            
            # Find or boot a device (Simulator app will be opened during boot if needed)
            device = None
            devices = await self.list_available_devices()
            
            # Look for booted iPhone device
            booted_iphones = [d for d in devices if "iPhone" in d.name and d.state == SimulatorState.BOOTED]
            if booted_iphones:
                device = booted_iphones[0]
            else:
                # Try to boot iPhone 16
                iphone_devices = [d for d in devices if "iPhone 16" in d.name]
                if iphone_devices:
                    device = iphone_devices[0]
                    if status_callback:
                        await status_callback(f"📱 Booting {device.name}...")
                    await self.boot_device(device)
                else:
                    # Use any available device
                    device = devices[0] if devices else None
                    if device and device.state != SimulatorState.BOOTED:
                        await self.boot_device(device)
            
            if not device:
                return False, "No simulator device available"
            
            # Install the app
            if status_callback:
                await status_callback("📦 Installing app (this may take up to 2 minutes)...")
            
            self.logger.info(f"Installing app from {app_path} to device {device.udid}")
            install_success = await self.install_app(device.udid, app_path)
            if not install_success:
                self.logger.error(f"Failed to install app on device {device.udid}")
                return False, "Failed to install app"
            
            if status_callback:
                await status_callback("✅ App installed successfully!")
            
            # Always try to launch the app after installation
            # The is_app_running check is unreliable due to JSON parsing issues
            await asyncio.sleep(1)  # Brief pause after install
            
            # Launch the app (removed unreliable is_running check)
            if status_callback:
                await status_callback("🚀 Launching app...")
            
            self.logger.info(f"Attempting to launch {bundle_id} on device {device.udid}")
            launch_success = await self.launch_app(device.udid, bundle_id)
            
            if not launch_success:
                # Try one more time with a longer delay
                self.logger.warning("First launch attempt failed, retrying...")
                await asyncio.sleep(3)
                launch_success = await self.launch_app(device.udid, bundle_id)
            
            if not launch_success:
                self.logger.error(f"Failed to launch {bundle_id} after retries")
                return False, "Failed to launch app after multiple attempts"
            
            self.logger.info(f"Successfully launched {bundle_id}")
            
            # Bring Simulator to foreground after successful launch
            await self._bring_simulator_to_foreground()
            
            return True, f"App launched successfully on {device.name}"
            
        except Exception as e:
            self.logger.error(f"Error in install_and_launch_app: {e}")
            return False, f"Error: {str(e)}"

    async def capture_screenshot(self, output_path: str) -> bool:
        """Capture screenshot from active device"""
        if not self._active_device:
            raise SimulatorError("No active device")

        try:
            await self._run_command([
                "xcrun", "simctl", "io", self._active_device.udid,
                "screenshot", output_path
            ])
            return os.path.exists(output_path)
        except Exception as e:
            self.logger.error(f"Failed to capture screenshot: {e}")
            return False

    async def get_app_logs(self, bundle_id: str, lines: int = 100) -> str:
        """Get recent app logs"""
        if not self._active_device:
            return ""

        try:
            # Get device logs
            result = await self._run_command([
                "xcrun", "simctl", "spawn", self._active_device.udid,
                "log", "show", "--predicate", f'processIdentifier == "{bundle_id}"',
                "--last", f"{lines}m"
            ], check=False)

            return result.stdout
        except Exception:
            return ""

    async def is_app_running(self, device_udid: str, bundle_id: str) -> bool:
        """Check if app is currently running on device"""
        try:
            result = await self._run_command(
                ["xcrun", "simctl", "listapps", device_udid, "--json"],
                check=False
            )
            if result.returncode == 0 and result.stdout:
                import json
                try:
                    # Try to parse the JSON output
                    apps_data = json.loads(result.stdout)
                    for app_id, app_info in apps_data.items():
                        if app_id == bundle_id:
                            # Check if app has a process ID (meaning it's running)
                            process_id = app_info.get("ProcessID", 0)
                            if process_id > 0:
                                self.logger.debug(f"App {bundle_id} is running with PID {process_id}")
                                return True
                            else:
                                self.logger.debug(f"App {bundle_id} found but not running (no PID)")
                                return False
                    self.logger.debug(f"App {bundle_id} not found in installed apps")
                except json.JSONDecodeError as e:
                    # If JSON parsing fails, we can't reliably check if app is running
                    self.logger.warning(f"JSON parse error: {e}")
                    # Return False to trigger actual launch
                    return False
            return False
        except Exception as e:
            self.logger.warning(f"Failed to check if app is running: {e}")
            # Don't assume app is not running if check fails
            return False

    # Private helper methods
    
    async def _bring_simulator_to_foreground(self):
        """Bring the iOS Simulator app to the foreground"""
        try:
            # Use AppleScript to activate the Simulator app
            script = 'tell application "Simulator" to activate'
            await self._run_command(
                ["osascript", "-e", script],
                check=False,
                timeout=5
            )
            self.logger.debug("Brought Simulator app to foreground")
        except Exception as e:
            self.logger.debug(f"Could not bring Simulator to foreground: {e}")

    async def _run_command(self, cmd: List[str], timeout: int = 30, check: bool = True) -> subprocess.CompletedProcess:
        """Run command with timeout and logging"""
        self.logger.debug(f"Running command: {' '.join(cmd)}")

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )

            result = subprocess.CompletedProcess(
                args=cmd,
                returncode=process.returncode,
                stdout=stdout.decode('utf-8') if stdout else '',
                stderr=stderr.decode('utf-8') if stderr else ''
            )

            if check and result.returncode != 0:
                raise subprocess.CalledProcessError(
                    result.returncode, cmd, result.stdout, result.stderr
                )

            return result

        except asyncio.TimeoutError:
            if process:
                process.terminate()
                await process.wait()
            raise SimulatorError(f"Command timed out after {timeout}s: {' '.join(cmd)}")

    async def _wait_for_boot(self, device: SimulatorDevice, timeout: int = 60):
        """Wait for device to fully boot"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            result = await self._run_command([
                "xcrun", "simctl", "list", "devices", "--json"
            ])

            devices_data = json.loads(result.stdout)
            for runtime_devices in devices_data.get("devices", {}).values():
                for d in runtime_devices:
                    if d["udid"] == device.udid and d["state"] == "Booted":
                        # Additional check - wait for SpringBoard
                        await self._wait_for_springboard(device.udid)
                        return

            await asyncio.sleep(1)

        raise SimulatorError(f"Device failed to boot within {timeout}s")

    async def _wait_for_springboard(self, device_udid: str):
        """Wait for SpringBoard to be ready"""
        for i in range(10):
            # Only log on first attempt to reduce noise
            if i == 0:
                result = await self._run_command([
                    "xcrun", "simctl", "spawn", device_udid,
                    "launchctl", "print", "system"
                ], check=False)
            else:
                # Suppress logging for subsequent attempts
                cmd = ["xcrun", "simctl", "spawn", device_udid, "launchctl", "print", "system"]
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                result = subprocess.CompletedProcess(
                    args=cmd,
                    returncode=process.returncode,
                    stdout=stdout.decode('utf-8', errors='ignore'),
                    stderr=stderr.decode('utf-8', errors='ignore')
                )

            if "com.apple.SpringBoard" in result.stdout:
                return

            await asyncio.sleep(1)

    async def _open_simulator_app(self):
        """Open Simulator.app and bring to foreground"""
        try:
            await self._run_command(["open", "-a", "Simulator"])
            await asyncio.sleep(1)

            # Bring to foreground more aggressively
            await self._run_command([
                "osascript", "-e",
                'tell application "Simulator" to activate'
            ], check=False)
            
            # Also try to bring the window to front
            await self._run_command([
                "osascript", "-e",
                'tell application "System Events" to set frontmost of process "Simulator" to true'
            ], check=False)
        except Exception as e:
            self.logger.warning(f"Failed to open Simulator app: {e}")

    async def _get_app_info(self, app_path: str) -> Dict[str, str]:
        """Extract app info from Info.plist"""
        plist_path = os.path.join(app_path, "Info.plist")
        if not os.path.exists(plist_path):
            return {}

        try:
            result = await self._run_command([
                "plutil", "-convert", "json", "-o", "-", plist_path
            ])
            return json.loads(result.stdout)
        except Exception:
            return {}

    async def _uninstall_app_if_exists(self, device_udid: str, bundle_id: str):
        """Uninstall app if it exists"""
        try:
            await self._run_command([
                "xcrun", "simctl", "uninstall", device_udid, bundle_id
            ], check=False)
            await asyncio.sleep(1)
        except Exception:
            pass

    async def _install_with_xcrun(self, device_udid: str, app_path: str) -> bool:
        """Standard installation method"""
        self.logger.info(f"Attempting standard xcrun install (timeout: {self._install_timeout}s)")
        result = await self._run_command([
            "xcrun", "simctl", "install", device_udid, app_path
        ], timeout=self._install_timeout, check=False)

        if result.returncode != 0:
            self.logger.error(f"xcrun install failed: {result.stderr}")
        else:
            self.logger.info("xcrun install succeeded")
            
        return result.returncode == 0

    async def _install_with_copy_method(self, device_udid: str, app_path: str) -> bool:
        """Alternative installation using direct copy"""
        # Get device data directory
        device_dir = os.path.expanduser(
            f"~/Library/Developer/CoreSimulator/Devices/{device_udid}"
        )

        if not os.path.exists(device_dir):
            return False

        # Create app container
        container_path = os.path.join(
            device_dir, "data/Containers/Bundle/Application"
        )
        os.makedirs(container_path, exist_ok=True)

        # Generate unique container ID
        import uuid
        container_id = str(uuid.uuid4()).upper()
        app_container = os.path.join(container_path, container_id)

        try:
            # Copy app to container
            shutil.copytree(app_path, os.path.join(app_container, os.path.basename(app_path)))

            # Trigger installation
            await self._run_command([
                "xcrun", "simctl", "install", device_udid, app_path
            ], check=False)

            return True
        except Exception:
            # Clean up on failure
            if os.path.exists(app_container):
                shutil.rmtree(app_container)
            return False

    async def _install_with_temp_copy(self, device_udid: str, app_path: str) -> bool:
        """Installation using temporary copy to avoid permission issues"""
        temp_dir = tempfile.mkdtemp()
        temp_app_path = os.path.join(temp_dir, os.path.basename(app_path))

        try:
            # Copy to temp location
            shutil.copytree(app_path, temp_app_path)

            # Fix permissions
            await self._run_command([
                "chmod", "-R", "755", temp_app_path
            ])

            # Install from temp location
            result = await self._run_command([
                "xcrun", "simctl", "install", device_udid, temp_app_path
            ], timeout=self._install_timeout, check=False)

            return result.returncode == 0

        finally:
            # Clean up temp directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    async def _create_device(self, name: str) -> SimulatorDevice:
        """Create a new simulator device"""
        # Get available device types and runtimes
        result = await self._run_command([
            "xcrun", "simctl", "list", "devicetypes", "--json"
        ])
        devicetypes = json.loads(result.stdout)

        result = await self._run_command([
            "xcrun", "simctl", "list", "runtimes", "--json"
        ])
        runtimes = json.loads(result.stdout)

        # Find iPhone device type
        iphone_type = None
        for dt in devicetypes.get("devicetypes", []):
            if name in dt.get("name", ""):
                iphone_type = dt["identifier"]
                break

        if not iphone_type:
            # Fallback to any iPhone
            for dt in devicetypes.get("devicetypes", []):
                if "iPhone" in dt.get("name", ""):
                    iphone_type = dt["identifier"]
                    break

        # Find latest iOS runtime
        ios_runtime = None
        for rt in runtimes.get("runtimes", []):
            if "iOS" in rt.get("name", "") and rt.get("isAvailable", False):
                ios_runtime = rt["identifier"]

        if not iphone_type or not ios_runtime:
            raise SimulatorError("No suitable device type or runtime found")

        # Create device
        result = await self._run_command([
            "xcrun", "simctl", "create", name, iphone_type, ios_runtime
        ])

        device_udid = result.stdout.strip()

        return SimulatorDevice(
            udid=device_udid,
            name=name,
            state=SimulatorState.SHUTDOWN,
            runtime=ios_runtime,
            device_type=iphone_type
        )

    def _extract_ios_version(self, runtime: str) -> tuple:
        """Extract iOS version for sorting"""
        match = re.search(r'iOS[- ](\d+)\.(\d+)', runtime)
        if match:
            return (int(match.group(1)), int(match.group(2)))
        return (0, 0)

    async def cleanup(self):
        """Clean up resources"""
        if self._active_device:
            try:
                await self._run_command([
                    "xcrun", "simctl", "shutdown", self._active_device.udid
                ], check=False)
            except Exception:
                pass
            self._active_device = None