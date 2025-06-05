import os
import shutil
import json
import yaml
import re
from typing import Dict, List, Optional
from datetime import datetime

class ProjectManager:
    def __init__(self):
        self.workspaces_dir = "../workspaces"
        self.templates_dir = "../templates/ios_app_template"
        os.makedirs(self.workspaces_dir, exist_ok=True)

    def _create_safe_bundle_id(self, app_name: str) -> str:
        """Create a safe bundle ID from app name - NO SPACES ALLOWED"""
        # Remove all non-alphanumeric characters and convert to lowercase
        safe_name = re.sub(r'[^a-zA-Z0-9]', '', app_name).lower()

        # Ensure it starts with a letter
        if safe_name and not safe_name[0].isalpha():
            safe_name = 'app' + safe_name

        # Fallback if empty
        if not safe_name:
            safe_name = 'myapp'

        # Ensure reasonable length
        safe_name = safe_name[:20]

        return f"com.swiftgen.{safe_name}"

    def _create_safe_target_name(self, app_name: str) -> str:
        """Create a safe target name for Xcode - no spaces or special characters"""
        # Remove all non-alphanumeric characters
        safe_name = re.sub(r'[^a-zA-Z0-9]', '', app_name)

        # Ensure it starts with a letter
        if safe_name and not safe_name[0].isalpha():
            safe_name = 'App' + safe_name

        # Fallback if empty
        if not safe_name:
            safe_name = 'MyApp'

        # Ensure reasonable length
        safe_name = safe_name[:30]

        return safe_name

    def _create_safe_product_name(self, app_name: str) -> str:
        """Create a safe product name (executable name) - MUST MATCH EVERYWHERE"""
        # This MUST match what's used in project.yml PRODUCT_NAME
        safe_name = re.sub(r'[^a-zA-Z0-9]', '', app_name)

        if not safe_name:
            safe_name = "MyApp"

        # Ensure it starts with a letter
        if safe_name and not safe_name[0].isalpha():
            safe_name = 'App' + safe_name

        return safe_name

    def _fix_file_path(self, path: str) -> str:
        """Fix file paths that aren't actually Swift source files"""
        # Remove any non-Swift files from Sources
        if path.startswith("Sources/") and not path.endswith(".swift"):
            # If it's an asset or config file, skip it
            if "Assets.xcassets" in path or ".json" in path or ".pdf" in path:
                return None

        # Ensure Swift files are in Sources directory
        if path.endswith(".swift") and not path.startswith("Sources/"):
            return f"Sources/{os.path.basename(path)}"

        return path

    async def create_project(self, project_id: str, generated_code: Dict, app_name: str) -> str:
        """Create a new iOS project from generated code"""

        # CRITICAL: Create all names ONCE and use consistently
        safe_target_name = self._create_safe_target_name(app_name)
        safe_product_name = self._create_safe_product_name(app_name)
        safe_bundle_id = self._create_safe_bundle_id(app_name)

        print(f"\n[PROJECT MANAGER] Creating project with CONSISTENT naming:")
        print(f"  Original App Name: {app_name}")
        print(f"  Safe Target Name: {safe_target_name}")
        print(f"  Safe Product Name: {safe_product_name}")
        print(f"  Safe Bundle ID: {safe_bundle_id}")

        project_path = os.path.join(self.workspaces_dir, project_id)
        os.makedirs(project_path, exist_ok=True)

        # Create Info.plist with correct executable name
        self._create_info_plist(project_path, app_name, safe_product_name)

        # Create Sources directory
        sources_dir = os.path.join(project_path, "Sources")
        os.makedirs(sources_dir, exist_ok=True)

        # CRITICAL FIX: Debug what we're receiving
        print(f"\n[PROJECT MANAGER] Received generated_code keys: {generated_code.keys()}")
        print(f"[PROJECT MANAGER] Type of generated_code: {type(generated_code)}")

        # Get files from generated_code
        files_to_write = generated_code.get("files", [])
        print(f"[PROJECT MANAGER] Number of files to write: {len(files_to_write)}")

        # Write generated files - CRITICAL: Fix paths and filter non-Swift files
        has_main_file = False
        files_written = 0
        valid_swift_files = []

        for i, file_info in enumerate(files_to_write):
            print(f"\n[PROJECT MANAGER] Processing file {i+1}:")
            print(f"  Type: {type(file_info)}")
            print(f"  Keys: {file_info.keys() if isinstance(file_info, dict) else 'Not a dict'}")

            if not isinstance(file_info, dict):
                print(f"[WARNING] File info is not a dict: {file_info}")
                continue

            original_path = file_info.get("path", "")
            content = file_info.get("content", "")

            print(f"  Original path: {original_path}")
            print(f"  Content length: {len(content)} chars")
            print(f"  Content preview: {content[:100]}..." if content else "  No content!")

            # CRITICAL: Ensure we have both path and content
            if not original_path or not content:
                print(f"[WARNING] Missing path or content for file {i+1}")
                print(f"  Path: '{original_path}'")
                print(f"  Has content: {bool(content)}")
                continue

            fixed_path = self._fix_file_path(original_path)

            # Skip non-Swift files in Sources
            if fixed_path is None:
                print(f"[PROJECT MANAGER] Skipping non-Swift file: {original_path}")
                continue

            # Only process actual Swift files
            if not fixed_path.endswith(".swift"):
                print(f"[PROJECT MANAGER] Skipping non-Swift file: {fixed_path}")
                continue

            file_path = os.path.join(project_path, fixed_path)

            # CRITICAL: Ensure content exists and is not empty
            if not content.strip():
                print(f"[WARNING] Empty file content for {fixed_path}")
                continue

            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    files_written += 1
                    print(f"[PROJECT MANAGER] Successfully wrote file: {file_path}")
                    print(f"  File size: {len(content)} bytes")
            except Exception as e:
                print(f"[ERROR] Failed to write file {file_path}: {str(e)}")
                continue

            valid_swift_files.append({
                "path": fixed_path,
                "content": content
            })

            # Check if we have a main app file
            if "@main" in content:
                has_main_file = True
                print(f"[PROJECT MANAGER] Found @main in {fixed_path}")

        print(f"\n[PROJECT MANAGER] Wrote {files_written} Swift files to disk")

        # CRITICAL: If no @main file exists, create one with consistent naming
        if not has_main_file:
            print(f"[PROJECT MANAGER] No @main app file found, creating default with name: {safe_target_name}App")
            app_content = f"""import SwiftUI

@main
struct {safe_target_name}App: App {{
    var body: some Scene {{
        WindowGroup {{
            ContentView()
        }}
    }}
}}
"""
            app_path = os.path.join(sources_dir, "App.swift")
            try:
                with open(app_path, 'w', encoding='utf-8') as f:
                    f.write(app_content)
                files_written += 1
                print(f"[PROJECT MANAGER] Created default App.swift at {app_path}")
            except Exception as e:
                print(f"[ERROR] Failed to create App.swift: {str(e)}")

            # Also create a ContentView if we don't have one
            has_content_view = any("ContentView" in f.get("content", "") for f in valid_swift_files)
            if not has_content_view:
                content_view_content = """import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack {
            Image(systemName: "globe")
                .imageScale(.large)
                .foregroundStyle(.tint)
            Text("Hello, world!")
        }
        .padding()
    }
}
"""
                content_view_path = os.path.join(sources_dir, "ContentView.swift")
                try:
                    with open(content_view_path, 'w', encoding='utf-8') as f:
                        f.write(content_view_content)
                    files_written += 1
                    print(f"[PROJECT MANAGER] Created default ContentView.swift at {content_view_path}")
                except Exception as e:
                    print(f"[ERROR] Failed to create ContentView.swift: {str(e)}")

        # CRITICAL: Verify we have actual Swift files
        print(f"\n[PROJECT MANAGER] Verifying Swift files in {sources_dir}...")
        try:
            actual_files = os.listdir(sources_dir)
            print(f"[PROJECT MANAGER] Files in Sources directory: {actual_files}")

            # Read and verify each file
            for filename in actual_files:
                if filename.endswith('.swift'):
                    file_path = os.path.join(sources_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            print(f"[PROJECT MANAGER] Verified {filename}: {len(content)} bytes")
                            if "@main" in content:
                                print(f"  - Contains @main entry point")
                    except Exception as e:
                        print(f"[ERROR] Could not read {filename}: {str(e)}")
        except Exception as e:
            print(f"[ERROR] Could not list Sources directory: {str(e)}")

        # Generate project.yml for xcodegen with CONSISTENT NAMING
        project_yml = self._generate_project_yml(
            app_name,
            safe_bundle_id,
            safe_target_name,
            safe_product_name,
            generated_code.get("dependencies", [])
        )

        with open(os.path.join(project_path, "project.yml"), 'w') as f:
            yaml.dump(project_yml, f, default_flow_style=False)

        # Save project metadata with all naming info
        metadata = {
            "project_id": project_id,
            "app_name": app_name,
            "created_at": datetime.now().isoformat(),
            "bundle_id": safe_bundle_id,
            "product_name": safe_product_name,
            "target_name": safe_target_name,
            "files": [f["path"] for f in valid_swift_files],
            "modifications": []
        }

        with open(os.path.join(project_path, "project.json"), 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"\n[PROJECT MANAGER] Project creation complete:")
        print(f"  - Project path: {project_path}")
        print(f"  - Files written: {files_written}")
        print(f"  - Bundle ID: {safe_bundle_id}")

        return project_path

    def _verify_swift_files(self, sources_dir: str) -> bool:
        """Verify Swift files exist and are valid"""
        swift_files = []
        for root, _, files in os.walk(sources_dir):
            for file in files:
                if file.endswith('.swift'):
                    swift_files.append(os.path.join(root, file))

        print(f"[PROJECT MANAGER] Verification: Found {len(swift_files)} Swift files")

        if not swift_files:
            raise Exception("CRITICAL: No Swift files found after project creation!")

        # Verify at least one has @main
        has_main = False
        for file_path in swift_files:
            with open(file_path, 'r') as f:
                if '@main' in f.read():
                    has_main = True
                    print(f"[PROJECT MANAGER] Verified @main in {os.path.basename(file_path)}")
                    break

        if not has_main:
            raise Exception("CRITICAL: No @main entry point found in any Swift file!")

        return True

    def _create_info_plist(self, project_path: str, app_name: str, executable_name: str):
        """Create Info.plist with EXPLICIT executable name"""
        info_plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>{executable_name}</string>
    <key>CFBundleIdentifier</key>
    <string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>{app_name}</string>
    <key>CFBundleDisplayName</key>
    <string>{app_name}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSRequiresIPhoneOS</key>
    <true/>
    <key>UILaunchStoryboardName</key>
    <string>LaunchScreen</string>
    <key>UIRequiredDeviceCapabilities</key>
    <array>
        <string>armv7</string>
    </array>
    <key>UISupportedInterfaceOrientations</key>
    <array>
        <string>UIInterfaceOrientationPortrait</string>
        <string>UIInterfaceOrientationLandscapeLeft</string>
        <string>UIInterfaceOrientationLandscapeRight</string>
    </array>
    <key>UISupportedInterfaceOrientations~ipad</key>
    <array>
        <string>UIInterfaceOrientationPortrait</string>
        <string>UIInterfaceOrientationPortraitUpsideDown</string>
        <string>UIInterfaceOrientationLandscapeLeft</string>
        <string>UIInterfaceOrientationLandscapeRight</string>
    </array>
</dict>
</plist>"""

        with open(os.path.join(project_path, "Info.plist"), 'w') as f:
            f.write(info_plist_content)

    def _generate_project_yml(self, app_name: str, bundle_id: str,
                              target_name: str, product_name: str,
                              dependencies: List[str]) -> Dict:
        """Generate xcodegen configuration with PROPER COMPILATION SETTINGS"""

        print(f"\n[PROJECT YML] Generating with consistent names:")
        print(f"  Project Name: {target_name}")
        print(f"  Target Name: {target_name}")
        print(f"  Product Name: {product_name}")
        print(f"  Bundle ID: {bundle_id}")

        config = {
            'name': target_name,
            'options': {
                'bundleIdPrefix': bundle_id.rsplit('.', 1)[0],
                'createIntermediateGroups': True,
                'deploymentTarget': {
                    'iOS': '16.0'
                }
            },
            'targets': {
                target_name: {
                    'type': 'application',
                    'platform': 'iOS',
                    # CRITICAL FIX: Use string path instead of complex object
                    'sources': 'Sources',
                    'settings': {
                        'base': {
                            'INFOPLIST_FILE': 'Info.plist',
                            'PRODUCT_BUNDLE_IDENTIFIER': bundle_id,
                            'MARKETING_VERSION': '1.0',
                            'CURRENT_PROJECT_VERSION': '1',
                            'PRODUCT_NAME': product_name,
                            'PRODUCT_MODULE_NAME': target_name,
                            'EXECUTABLE_NAME': product_name,
                            'CODE_SIGN_STYLE': 'Manual',
                            'DEVELOPMENT_TEAM': '',
                            'CODE_SIGN_IDENTITY': '',
                            'CODE_SIGNING_REQUIRED': 'NO',
                            'CODE_SIGNING_ALLOWED': 'NO',
                            'ASSETCATALOG_COMPILER_APPICON_NAME': 'AppIcon',
                            'ASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME': 'AccentColor',
                            'CLANG_ENABLE_MODULES': 'YES',
                            'SWIFT_OPTIMIZATION_LEVEL': '-Onone',
                            'ENABLE_TESTABILITY': 'YES',
                            'GCC_DYNAMIC_NO_PIC': 'NO',
                            'GCC_OPTIMIZATION_LEVEL': '0',
                            'GCC_PREPROCESSOR_DEFINITIONS': 'DEBUG=1 $(inherited)',
                            'MTL_ENABLE_DEBUG_INFO': 'INCLUDE_SOURCE',
                            'MTL_FAST_MATH': 'YES',
                            'OTHER_SWIFT_FLAGS': '-D DEBUG',
                            'SWIFT_ACTIVE_COMPILATION_CONDITIONS': 'DEBUG',
                            'ENABLE_PREVIEWS': 'YES',
                            'DEVELOPMENT_ASSET_PATHS': '',
                            'IPHONEOS_DEPLOYMENT_TARGET': '16.0',
                            'SDKROOT': 'iphoneos',
                            'SUPPORTED_PLATFORMS': 'iphonesimulator iphoneos',
                            'TARGETED_DEVICE_FAMILY': '1,2',
                            'SWIFT_VERSION': '5.9'
                        }
                    }
                }
            }
        }

        # Add dependencies if any
        if dependencies:
            config['targets'][target_name]['dependencies'] = []
            for dep in dependencies:
                config['targets'][target_name]['dependencies'].append({
                    'package': dep
                })

        return config

    async def update_project_files(self, project_id: str, updated_files: List[Dict]) -> bool:
        """Update existing project files"""
        project_path = os.path.join(self.workspaces_dir, project_id)
        if not os.path.exists(project_path):
            return False

        # Load project metadata to maintain naming consistency
        metadata_path = os.path.join(project_path, "project.json")
        metadata = {}
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)

        # Backup current files
        backup_dir = os.path.join(project_path, ".backups", datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(backup_dir, exist_ok=True)

        # Update each file
        for file_info in updated_files:
            # Fix file paths
            original_path = file_info["path"]
            fixed_path = self._fix_file_path(original_path)

            if fixed_path is None or not fixed_path.endswith(".swift"):
                print(f"[PROJECT MANAGER] Skipping non-Swift file update: {original_path}")
                continue

            file_path = os.path.join(project_path, fixed_path)

            # Backup existing file if it exists
            if os.path.exists(file_path):
                backup_path = os.path.join(backup_dir, fixed_path)
                os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                shutil.copy2(file_path, backup_path)

            # Write new content
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(file_info["content"])

        # Update metadata
        if metadata:
            metadata["last_modified"] = datetime.now().isoformat()
            metadata["modifications"].append({
                "timestamp": datetime.now().isoformat(),
                "files_updated": [f["path"] for f in updated_files if f["path"].endswith(".swift")]
            })

            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

        return True

    async def get_project_status(self, project_id: str) -> Optional[Dict]:
        """Get project status and metadata"""
        project_path = os.path.join(self.workspaces_dir, project_id)
        metadata_path = os.path.join(project_path, "project.json")

        if not os.path.exists(metadata_path):
            return None

        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        # Check if app was built
        derived_data = os.path.join(project_path, "DerivedData")
        app_built = False
        app_path = None

        if os.path.exists(derived_data):
            # Look for .app bundle
            for root, dirs, files in os.walk(derived_data):
                for dir_name in dirs:
                    if dir_name.endswith('.app'):
                        app_path = os.path.join(root, dir_name)
                        app_built = True

                        # Verify executable exists
                        expected_executable = metadata.get('product_name', '')
                        if expected_executable:
                            exec_path = os.path.join(app_path, expected_executable)
                            if not os.path.exists(exec_path):
                                print(f"[WARNING] Expected executable '{expected_executable}' not found in app bundle")
                                app_built = False
                        break
                if app_built:
                    break

        metadata['app_built'] = app_built
        metadata['project_path'] = project_path
        metadata['app_path'] = app_path

        return metadata

    async def get_project_files(self, project_id: str) -> List[Dict]:
        """Get all source files in project"""
        project_path = os.path.join(self.workspaces_dir, project_id)
        sources_dir = os.path.join(project_path, "Sources")

        files = []
        if os.path.exists(sources_dir):
            for root, _, filenames in os.walk(sources_dir):
                for filename in filenames:
                    if filename.endswith('.swift'):
                        file_path = os.path.join(root, filename)
                        relative_path = os.path.relpath(file_path, project_path)

                        with open(file_path, 'r') as f:
                            content = f.read()

                        files.append({
                            "path": relative_path,
                            "name": filename,
                            "content": content
                        })

        return files

    async def get_project_path(self, project_id: str) -> Optional[str]:
        """Get project directory path"""
        project_path = os.path.join(self.workspaces_dir, project_id)
        if os.path.exists(project_path):
            return project_path
        return None

    async def list_projects(self) -> List[Dict]:
        """List all projects in workspace"""
        projects = []

        if os.path.exists(self.workspaces_dir):
            for project_id in os.listdir(self.workspaces_dir):
                if project_id.startswith('proj_'):
                    project_path = os.path.join(self.workspaces_dir, project_id)
                    metadata_path = os.path.join(project_path, "project.json")

                    if os.path.exists(metadata_path):
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)

                        projects.append({
                            "project_id": project_id,
                            "app_name": metadata.get("app_name", "Unknown"),
                            "bundle_id": metadata.get("bundle_id", "Unknown"),
                            "product_name": metadata.get("product_name", "Unknown"),
                            "created_at": metadata.get("created_at", ""),
                            "last_modified": metadata.get("last_modified", metadata.get("created_at", ""))
                        })

        # Sort by last modified date
        projects.sort(key=lambda x: x.get("last_modified", ""), reverse=True)
        return projects