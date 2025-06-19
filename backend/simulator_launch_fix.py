#!/usr/bin/env python3
"""Fix for simulator launch issues - adds better logging and error handling"""

import os
import sys

def create_patch():
    """Create a patch for build_service.py to improve simulator launch logging"""
    
    patch_content = """
# Patch for build_service.py - Add this after line 411 (in the simulator launch section)
# This adds better logging and error handling for simulator launches

                    try:
                        app_path = build_result.get("app_path")
                        if app_path:
                            print(f"[BUILD] Found app bundle at: {app_path}")
                            
                            if not os.path.exists(app_path):
                                print(f"[BUILD] WARNING: App bundle does not exist at {app_path}")
                                warnings.append(f"App bundle not found at {app_path}")
                            else:
                                print(f"[BUILD] App bundle exists, size: {os.path.getsize(app_path)} bytes")
                                
                                await self._update_status("📱 Preparing to launch in iOS Simulator...")
                                await self._update_status(f"Build completed successfully for {os.path.basename(app_path)}")
                                
                                print(f"[BUILD] Calling simulator_service.install_and_launch_app...")
                                print(f"[BUILD]   app_path: {app_path}")
                                print(f"[BUILD]   bundle_id: {bundle_id}")
                                
                                # Use the combined install_and_launch_app method like in the GitHub version
                                launch_success, launch_message = await self.simulator_service.install_and_launch_app(
                                    app_path,
                                    bundle_id,
                                    self._update_status
                                )
                                
                                print(f"[BUILD] Simulator launch result: success={launch_success}, message={launch_message}")
                                
                                if launch_success:
                                    await self._update_status("🎉 App launched successfully!")
                                    build_result["simulator_launched"] = True
                                    print(f"[BUILD] ✓ App successfully launched in simulator")
                                else:
                                    warnings.append(f"Simulator: {launch_message}")
                                    await self._update_status(f"Simulator launch issue: {launch_message}")
                                    print(f"[BUILD] ⚠️ Simulator launch failed: {launch_message}")
                        else:
                            print(f"[BUILD] No app_path in build result - skipping simulator launch")
                            warnings.append("No app bundle found after successful build")
                    except Exception as e:
                        print(f"[BUILD] ERROR during simulator launch: {type(e).__name__}: {str(e)}")
                        import traceback
                        traceback.print_exc()
                        await self._update_status(f"Simulator error: {str(e)}")
                        warnings.append(f"Simulator error: {str(e)}")
"""
    
    return patch_content

def apply_logging_improvements():
    """Apply logging improvements to build_service.py"""
    
    build_service_path = os.path.join(os.path.dirname(__file__), "build_service.py")
    
    print("=== Simulator Launch Fix ===\n")
    print("This patch adds better logging to help debug simulator launch issues.\n")
    
    print("Patch location: build_service.py, around line 411-432")
    print("Current code should be replaced with the patched version above.\n")
    
    print("Key improvements:")
    print("1. Adds logging for app bundle existence check")
    print("2. Logs simulator service calls with parameters")
    print("3. Logs launch results clearly")
    print("4. Better error handling with stack traces")
    print("5. More informative warning messages\n")
    
    print("To apply manually:")
    print("1. Open build_service.py")
    print("2. Find the simulator launch section (lines 410-432)")
    print("3. Replace with the patched version")
    print("4. Save and restart the backend\n")
    
    patch = create_patch()
    
    # Save patch to file
    patch_file = os.path.join(os.path.dirname(__file__), "simulator_launch_patch.txt")
    with open(patch_file, 'w') as f:
        f.write(patch)
    
    print(f"Patch saved to: {patch_file}")
    
    return patch

if __name__ == "__main__":
    apply_logging_improvements()