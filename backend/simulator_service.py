import os
import subprocess
import asyncio
import json
import time
from typing import Dict, Optional, Tuple, List

class SimulatorService:
    def __init__(self):
        self.active_simulator = None
        self.simulator_booted = False

    async def ensure_simulator_booted(self) -> Tuple[bool, str, str]:
        """Ensure a simulator is booted and ready"""
        print("Checking simulator status...")

        # Get list of available devices
        devices = await self._get_available_devices()
        if not devices:
            return False, "", "No iOS simulators found"

        # Check if any simulator is already booted
        booted_device = await self._get_booted_device()
        if booted_device:
            self.active_simulator = booted_device['udid']
            self.simulator_booted = True
            print(f"Using already booted simulator: {booted_device['name']} ({booted_device['udid']})")
            return True, self.active_simulator, f"Using {booted_device['name']}"

        # Boot the first available iPhone 16 series or fallback to others
        preferred_devices = ['iPhone 16 Pro', 'iPhone 16 Pro Max', 'iPhone 16', 'iPhone 16 Plus',
                           'iPhone 15 Pro', 'iPhone 15', 'iPhone 14 Pro', 'iPhone 14']

        device_to_boot = None
        for pref in preferred_devices:
            for device in devices:
                if device['name'] == pref and device['state'] == 'Shutdown':
                    device_to_boot = device
                    break
            if device_to_boot:
                break

        if not device_to_boot and devices:
            # Just use the first available device
            device_to_boot = devices[0]

        if not device_to_boot:
            return False, "", "No suitable iOS simulator found"

        # Boot the simulator
        print(f"Booting simulator: {device_to_boot['name']} ({device_to_boot['udid']})")
        success = await self._boot_simulator(device_to_boot['udid'])

        if success:
            self.active_simulator = device_to_boot['udid']
            self.simulator_booted = True

            # Open Simulator app
            await self._open_simulator_app()

            # Wait for simulator to be ready
            await self._wait_for_simulator_ready(device_to_boot['udid'])

            return True, device_to_boot['udid'], f"Booted {device_to_boot['name']}"
        else:
            return False, "", f"Failed to boot {device_to_boot['name']}"

    async def install_and_launch_app(self, app_path: str, bundle_id: str, update_callback=None) -> Tuple[bool, str]:
        """Install and launch the app in the simulator"""
        if not self.active_simulator:
            success, udid, message = await self.ensure_simulator_booted()
            if not success:
                return False, f"Failed to boot simulator: {message}"

        # Install the app
        if update_callback:
            await update_callback("Installing app to simulator...")

        print(f"Installing app: {app_path}")
        install_success = await self._install_app(self.active_simulator, app_path)
        if not install_success:
            return False, "Failed to install app to simulator"

        if update_callback:
            await update_callback("Launching app...")

        # Launch the app
        print(f"Launching app with bundle ID: {bundle_id}")
        launch_success = await self._launch_app(self.active_simulator, bundle_id)
        if not launch_success:
            return False, "Failed to launch app"

        # Bring Simulator to front
        await self._bring_simulator_to_front()

        return True, "App launched successfully"

    async def _get_available_devices(self) -> List[Dict]:
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
                devices = []

                for runtime, runtime_devices in devices_data.get('devices', {}).items():
                    if 'iOS' in runtime:
                        for device in runtime_devices:
                            if device.get('isAvailable', False):
                                devices.append({
                                    'udid': device['udid'],
                                    'name': device['name'],
                                    'state': device['state'],
                                    'runtime': runtime
                                })

                return devices
        except Exception as e:
            print(f"Error getting devices: {e}")

        return []

    async def _get_booted_device(self) -> Optional[Dict]:
        """Get the currently booted device if any"""
        devices = await self._get_available_devices()
        for device in devices:
            if device['state'] == 'Booted':
                return device
        return None

    async def _boot_simulator(self, udid: str) -> bool:
        """Boot a specific simulator"""
        try:
            cmd = ['xcrun', 'simctl', 'boot', udid]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            # Check if already booted (not an error)
            if process.returncode != 0:
                stderr_text = stderr.decode()
                if "Unable to boot device in current state: Booted" in stderr_text:
                    return True
                print(f"Boot error: {stderr_text}")
                return False

            return True
        except Exception as e:
            print(f"Error booting simulator: {e}")
            return False

    async def _open_simulator_app(self):
        """Open the Simulator app"""
        try:
            cmd = ['open', '-a', 'Simulator']
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
        except Exception as e:
            print(f"Error opening Simulator app: {e}")

    async def _wait_for_simulator_ready(self, udid: str, timeout: int = 30):
        """Wait for simulator to be ready"""
        print("Waiting for simulator to be ready...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check if simulator is booted and ready
            devices = await self._get_available_devices()
            for device in devices:
                if device['udid'] == udid and device['state'] == 'Booted':
                    # Give it a bit more time to fully initialize
                    await asyncio.sleep(2)
                    return True

            await asyncio.sleep(1)

        return False

    async def _install_app(self, udid: str, app_path: str) -> bool:
        """Install app to simulator"""
        try:
            cmd = ['xcrun', 'simctl', 'install', udid, app_path]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                print(f"Install error: {stderr.decode()}")
                return False

            return True
        except Exception as e:
            print(f"Error installing app: {e}")
            return False

    async def _launch_app(self, udid: str, bundle_id: str) -> bool:
        """Launch app in simulator"""
        try:
            # First, terminate any existing instance
            terminate_cmd = ['xcrun', 'simctl', 'terminate', udid, bundle_id]
            await asyncio.create_subprocess_exec(
                *terminate_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Wait a moment
            await asyncio.sleep(0.5)

            # Launch the app
            cmd = ['xcrun', 'simctl', 'launch', udid, bundle_id]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                print(f"Launch error: {stderr.decode()}")
                return False

            print(f"App launched: {stdout.decode().strip()}")
            return True
        except Exception as e:
            print(f"Error launching app: {e}")
            return False

    async def _bring_simulator_to_front(self):
        """Bring Simulator app to front"""
        try:
            # Use AppleScript to bring Simulator to front
            script = '''
            tell application "Simulator"
                activate
            end tell
            '''
            cmd = ['osascript', '-e', script]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
        except Exception as e:
            print(f"Error bringing Simulator to front: {e}")

    async def take_screenshot(self, output_path: str) -> bool:
        """Take a screenshot of the simulator"""
        if not self.active_simulator:
            return False

        try:
            cmd = ['xcrun', 'simctl', 'io', self.active_simulator, 'screenshot', output_path]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            return process.returncode == 0
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return False