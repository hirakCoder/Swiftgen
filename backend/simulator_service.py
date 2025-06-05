import os
import asyncio
import json
from typing import Tuple, Optional, List, Dict

class SimulatorService:
    """Service for managing iOS Simulator operations"""

    def __init__(self):
        self.default_device_type = "iPhone 16 Pro"
        self.fallback_devices = ["iPhone 16", "iPhone 15", "iPhone 14"]

    async def ensure_simulator_booted(self) -> Tuple[bool, Optional[str], str]:
        """Ensure iOS simulator is booted and ready"""

        print("Checking simulator status...")

        # First check if any simulator is already booted
        booted_device = await self._get_booted_device_id()

        if booted_device:
            device_info = await self._get_device_info(booted_device)
            print(f"Using already booted simulator: {device_info}")
            return True, booted_device, f"Simulator ready: {device_info}"

        # No booted device, try to boot one
        print("No booted simulator found. Attempting to boot simulator...")

        # Get available devices
        available_devices = await self._get_available_devices()

        # Try to boot preferred device
        device_to_boot = None
        device_name = None

        for device_type in [self.default_device_type] + self.fallback_devices:
            if device_type in available_devices:
                device_to_boot = available_devices[device_type]
                device_name = device_type
                break

        if not device_to_boot:
            # Use first available iOS device
            for name, device_id in available_devices.items():
                device_to_boot = device_id
                device_name = name
                break

        if not device_to_boot:
            return False, None, "No iOS simulators available"

        # Boot the device
        print(f"Booting {device_name} simulator...")

        boot_cmd = ['xcrun', 'simctl', 'boot', device_to_boot]
        process = await asyncio.create_subprocess_exec(
            *boot_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        # Check if boot was successful or device was already booted
        if process.returncode == 0 or "already booted" in stderr.decode().lower():
            # Open Simulator app
            await self._open_simulator_app()

            # Wait for simulator to be ready
            await asyncio.sleep(3)

            return True, device_to_boot, f"Simulator booted: {device_name}"
        else:
            error_msg = stderr.decode() if stderr else "Unknown error"
            return False, None, f"Failed to boot simulator: {error_msg}"

    async def install_and_launch_app(self, app_path: str, bundle_id: str,
                                     status_callback=None) -> Tuple[bool, str]:
        """Install and launch app in simulator with enhanced debugging"""

        print(f"[SIMULATOR] Installing app:")
        print(f"  App Path: {app_path}")
        print(f"  Bundle ID: {bundle_id}")

        # Verify app bundle structure
        if not os.path.exists(app_path):
            return False, f"App bundle not found at: {app_path}"

        # Check for the executable inside the app bundle
        app_name = os.path.basename(app_path).replace('.app', '')
        executable_path = os.path.join(app_path, app_name)

        print(f"[SIMULATOR] Checking for executable at: {executable_path}")

        if not os.path.exists(executable_path):
            # List contents of app bundle for debugging
            print(f"[SIMULATOR] App bundle contents:")
            try:
                contents = os.listdir(app_path)
                for item in contents:
                    item_path = os.path.join(app_path, item)
                    if os.path.isfile(item_path):
                        # Check if it's executable
                        is_exec = os.access(item_path, os.X_OK)
                        print(f"  - {item} {'(executable)' if is_exec else ''}")
                    else:
                        print(f"  - {item}/ (directory)")

                # Check if there's a different executable name
                executables = [f for f in contents if os.path.isfile(os.path.join(app_path, f))
                               and os.access(os.path.join(app_path, f), os.X_OK)]

                if executables:
                    print(f"[SIMULATOR] Found executables: {executables}")

                    # Check Info.plist for the actual executable name
                    info_plist_path = os.path.join(app_path, "Info.plist")
                    if os.path.exists(info_plist_path):
                        try:
                            # Try to read Info.plist to find CFBundleExecutable
                            import plistlib
                            with open(info_plist_path, 'rb') as f:
                                plist = plistlib.load(f)
                                actual_exec = plist.get('CFBundleExecutable', '')
                                print(f"[SIMULATOR] Info.plist CFBundleExecutable: {actual_exec}")
                        except Exception as e:
                            print(f"[SIMULATOR] Error reading Info.plist: {e}")

                    return False, f"Expected executable '{app_name}' not found, but found: {', '.join(executables)}. This indicates a mismatch between app name and PRODUCT_NAME in build settings."
                else:
                    return False, f"No executable found in app bundle. Build may have failed to produce an executable."

            except Exception as e:
                return False, f"Error inspecting app bundle: {str(e)}"

        try:
            # Get booted device
            device_id = await self._get_booted_device_id()
            if not device_id:
                return False, "No booted simulator found"

            # Install app
            if status_callback:
                await status_callback("Installing app to simulator...")

            print(f"[SIMULATOR] Running: xcrun simctl install {device_id} {app_path}")

            install_cmd = ['xcrun', 'simctl', 'install', device_id, app_path]
            process = await asyncio.create_subprocess_exec(
                *install_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                print(f"[SIMULATOR] Install failed: {error_msg}")

                # Parse specific error messages
                if "is missing its bundle executable" in error_msg:
                    # Extract the expected executable name from error
                    import re
                    match = re.search(r'"([^"]+\.app)/([^"]+)"', error_msg)
                    if match:
                        expected_exec = match.group(2)
                        return False, f"App installation failed: Expected executable '{expected_exec}' not found in app bundle. Check PRODUCT_NAME in build settings."

                return False, f"Failed to install app: {error_msg}"

            print(f"[SIMULATOR] App installed successfully")

            # Launch app
            if status_callback:
                await status_callback("Launching app...")

            print(f"[SIMULATOR] Running: xcrun simctl launch {device_id} {bundle_id}")

            launch_cmd = ['xcrun', 'simctl', 'launch', device_id, bundle_id]
            process = await asyncio.create_subprocess_exec(
                *launch_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                print(f"[SIMULATOR] Launch failed: {error_msg}")

                # Try to get more info about why launch failed
                if "FBSOpenApplicationServiceErrorDomain" in error_msg:
                    return False, f"App launch failed - bundle ID mismatch or app not properly installed. Verify bundle ID: {bundle_id}"
                else:
                    return False, f"Failed to launch app: {error_msg}"

            print(f"[SIMULATOR] App launched successfully")
            return True, "App installed and launched successfully"

        except Exception as e:
            print(f"[SIMULATOR] Exception during install/launch: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, f"Error during install/launch: {str(e)}"

    async def _get_booted_device_id(self) -> Optional[str]:
        """Get the device ID of the currently booted simulator"""

        cmd = ['xcrun', 'simctl', 'list', 'devices', 'booted', '-j']
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            try:
                data = json.loads(stdout.decode())
                devices = data.get('devices', {})

                # Find booted device
                for runtime, device_list in devices.items():
                    for device in device_list:
                        if device.get('state') == 'Booted':
                            return device['udid']
            except json.JSONDecodeError:
                pass

        return None

    async def _get_device_info(self, device_id: str) -> str:
        """Get information about a specific device"""

        cmd = ['xcrun', 'simctl', 'list', 'devices', '-j']
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            try:
                data = json.loads(stdout.decode())
                devices = data.get('devices', {})

                for runtime, device_list in devices.items():
                    for device in device_list:
                        if device.get('udid') == device_id:
                            return f"{device['name']} ({device_id})"
            except json.JSONDecodeError:
                pass

        return device_id

    async def _get_available_devices(self) -> Dict[str, str]:
        """Get available iOS simulator devices"""

        cmd = ['xcrun', 'simctl', 'list', 'devices', 'available', '-j']
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        available = {}

        if process.returncode == 0:
            try:
                data = json.loads(stdout.decode())
                devices = data.get('devices', {})

                # Find iOS devices
                for runtime, device_list in devices.items():
                    if 'iOS' in runtime:
                        for device in device_list:
                            if device.get('isAvailable', False):
                                available[device['name']] = device['udid']
            except json.JSONDecodeError:
                pass

        return available

    async def _open_simulator_app(self):
        """Open the Simulator app"""

        cmd = ['open', '-a', 'Simulator']
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        await process.communicate()

    async def capture_screenshot(self, output_path: str) -> bool:
        """Capture a screenshot from the booted simulator"""

        device_id = await self._get_booted_device_id()
        if not device_id:
            return False

        cmd = ['xcrun', 'simctl', 'io', device_id, 'screenshot', output_path]
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        return process.returncode == 0