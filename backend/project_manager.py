import os
import shutil
import json
import yaml
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import hashlib

class ProjectManager:
    """Project Manager with permanent fixes for app naming issues"""

    def __init__(self):
        self.workspaces_dir = "../workspaces"
        self.templates_dir = "../templates/ios_app_template"
        os.makedirs(self.workspaces_dir, exist_ok=True)

        # Reserved Swift keywords and types to avoid
        self.reserved_types = {
            'Task', 'State', 'Action', 'Result', 'Error', 'Never', 'Any',
            'AnyObject', 'Void', 'Bool', 'Int', 'Double', 'Float', 'String',
            'Array', 'Dictionary', 'Set', 'Optional', 'Collection'
        }

        # Simplified validation rules
        self.max_files = 10  # Prevent overly complex apps
        self.min_content_size = 100  # Ensure files have real content

    def _sanitize_display_name(self, name: str) -> str:
        """Sanitize display name to remove problematic characters while keeping it readable"""
        # Remove special characters that cause build issues
        sanitized = name.replace('?', '')
        sanitized = sanitized.replace('!', '')
        sanitized = sanitized.replace('@', ' at ')
        sanitized = sanitized.replace('#', '')
        sanitized = sanitized.replace('$', '')
        sanitized = sanitized.replace('%', ' percent ')
        sanitized = sanitized.replace('^', '')
        sanitized = sanitized.replace('&', ' and ')
        sanitized = sanitized.replace('*', '')
        sanitized = sanitized.replace('(', '')
        sanitized = sanitized.replace(')', '')
        sanitized = sanitized.replace('[', '')
        sanitized = sanitized.replace(']', '')
        sanitized = sanitized.replace('{', '')
        sanitized = sanitized.replace('}', '')
        sanitized = sanitized.replace('|', '')
        sanitized = sanitized.replace('\\', '')
        sanitized = sanitized.replace('/', ' ')
        sanitized = sanitized.replace('<', '')
        sanitized = sanitized.replace('>', '')
        sanitized = sanitized.replace(',', '')
        sanitized = sanitized.replace(';', '')
        sanitized = sanitized.replace(':', '')
        sanitized = sanitized.replace('"', '')
        sanitized = sanitized.replace("'", '')
        # Clean up multiple spaces and trim
        sanitized = ' '.join(sanitized.split())
        return sanitized.strip()

    def _create_safe_bundle_id(self, app_name: str) -> str:
        """Create a safe bundle ID from app name"""
        # CRITICAL: Remove spaces first
        safe_name = app_name.replace(" ", "").lower()
        safe_name = re.sub(r'[^a-z0-9]', '', safe_name)

        if safe_name and not safe_name[0].isalpha():
            safe_name = 'app' + safe_name

        if not safe_name:
            safe_name = 'myapp'

        safe_name = safe_name[:20]

        return f"com.swiftgen.{safe_name}"

    def _create_safe_target_name(self, app_name: str) -> str:
        """Create a safe target name for Xcode - no spaces or special characters"""
        # CRITICAL FIX: Remove spaces FIRST to prevent casing issues
        safe_name = app_name.replace(" ", "")

        # Remove all non-alphanumeric characters
        safe_name = re.sub(r'[^a-zA-Z0-9]', '', safe_name)

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
        # CRITICAL FIX: This MUST match exactly what's used in project.yml
        # Remove ALL spaces first to prevent "Cool Timer" vs "Cool TImer" issues
        safe_name = app_name.replace(" ", "")

        # Then remove any other non-alphanumeric characters
        safe_name = re.sub(r'[^a-zA-Z0-9]', '', safe_name)

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
            return None

        # Ensure proper Swift file paths
        if path.endswith(".swift") and not path.startswith("Sources/"):
            return f"Sources/{path}"

        return path

    def _validate_swift_content(self, content: str, filename: str) -> Tuple[bool, List[str]]:
        """Validate Swift content for common issues"""
        issues = []

        # Check for empty content
        if not content or len(content.strip()) < 10:
            issues.append(f"{filename}: File content is too short or empty")
            return False, issues

        # Check for reserved type usage
        for reserved in self.reserved_types:
            pattern = rf'\b(struct|class|enum)\s+{reserved}\b'
            if re.search(pattern, content):
                issues.append(f"{filename}: Uses reserved type name '{reserved}'")

        # Check for basic Swift structure
        if not any(keyword in content for keyword in ['import', 'struct', 'class', 'func', '@main']):
            issues.append(f"{filename}: Doesn't appear to be valid Swift code")

        return len(issues) == 0, issues

    def _validate_project_consistency(self, project_path: str, app_name: str,
                                      safe_target_name: str, safe_product_name: str) -> bool:
        """Validate and fix project consistency issues"""

        # Check project.yml
        project_yml_path = os.path.join(project_path, "project.yml")
        if os.path.exists(project_yml_path):
            with open(project_yml_path, 'r') as f:
                content = f.read()

            # Fix any inconsistencies
            original_content = content

            # Ensure PRODUCT_NAME has no spaces
            content = re.sub(
                r'(PRODUCT_NAME:\s*")([^"]+)(")',
                f'\\1{safe_product_name}\\3',
                content
            )

            # Ensure target name is consistent
            content = re.sub(
                r'^name:\s*.+$',
                f'name: {safe_target_name}',
                content,
                flags=re.MULTILINE
            )

            if content != original_content:
                print(f"[PROJECT MANAGER] Fixed naming inconsistencies in project.yml")
                with open(project_yml_path, 'w') as f:
                    f.write(content)

        return True

    async def create_project(self, project_id: str, generated_code: Dict,
                             app_name: str = None) -> str:
        """Create a new iOS project with CONSISTENT naming"""

        # CRITICAL: Sanitize app name immediately
        if app_name:
            # Sanitize display name to remove problematic characters
            display_name = self._sanitize_display_name(app_name)
            safe_app_name = re.sub(r'[^a-zA-Z0-9]', '', app_name)
        else:
            raw_name = generated_code.get("app_name", "MyApp")
            # Sanitize display name to remove problematic characters
            display_name = self._sanitize_display_name(raw_name)
            safe_app_name = re.sub(r'[^a-zA-Z0-9]', '', display_name)

        # Create all safe names upfront
        safe_target_name = self._create_safe_target_name(safe_app_name)
        safe_product_name = self._create_safe_product_name(safe_app_name)
        bundle_id = generated_code.get("bundle_id") or self._create_safe_bundle_id(safe_app_name)

        print(f"\n[PROJECT MANAGER] Creating project:")
        print(f"  Display Name: {display_name}")
        print(f"  Safe Target Name: {safe_target_name}")
        print(f"  Safe Product Name: {safe_product_name}")
        print(f"  Bundle ID: {bundle_id}")

        # Create project directory
        project_path = os.path.join(self.workspaces_dir, project_id)
        os.makedirs(project_path, exist_ok=True)

        # Create Sources directory
        sources_dir = os.path.join(project_path, "Sources")
        os.makedirs(sources_dir, exist_ok=True)

        # Process and write files
        files = generated_code.get("files", [])
        valid_files = []
        validation_issues = []
        filename_to_paths = {}  # Track filenames for duplicate detection

        # First pass: collect all paths and check for duplicates
        for file_info in files:
            original_path = file_info.get("path", "")
            content = file_info.get("content", "")

            # Fix file path
            fixed_path = self._fix_file_path(original_path)
            if not fixed_path:
                print(f"[PROJECT MANAGER] Skipping non-Swift file: {original_path}")
                continue

            # Ensure the file is in Sources directory
            if not fixed_path.startswith("Sources/"):
                fixed_path = f"Sources/{os.path.basename(fixed_path)}"

            # Check for duplicate filenames
            filename = os.path.basename(fixed_path)
            if filename in filename_to_paths:
                print(f"[PROJECT MANAGER] WARNING: Duplicate filename '{filename}' detected during creation!")
                print(f"  Existing: {filename_to_paths[filename]}")
                print(f"  Skipping: {fixed_path}")
                validation_issues.append(f"Duplicate filename '{filename}': {fixed_path} (kept {filename_to_paths[filename]})")
                continue
            
            filename_to_paths[filename] = fixed_path

        # Second pass: validate and write files
        for file_info in files:
            original_path = file_info.get("path", "")
            content = file_info.get("content", "")

            # Fix file path
            fixed_path = self._fix_file_path(original_path)
            if not fixed_path:
                continue

            # Ensure the file is in Sources directory
            if not fixed_path.startswith("Sources/"):
                fixed_path = f"Sources/{os.path.basename(fixed_path)}"

            # Only process if this is the chosen path for this filename
            filename = os.path.basename(fixed_path)
            if filename_to_paths.get(filename) != fixed_path:
                continue

            # Validate content
            is_valid, issues = self._validate_swift_content(content, fixed_path)
            if issues:
                validation_issues.extend(issues)

            if is_valid or len(issues) == 0:  # Allow files with warnings
                file_path = os.path.join(project_path, fixed_path)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                with open(file_path, 'w') as f:
                    f.write(content)

                valid_files.append(fixed_path)

        print(f"[PROJECT MANAGER] Wrote {len(valid_files)} files")

        if validation_issues:
            print(f"[PROJECT MANAGER] Validation warnings: {len(validation_issues)}")
            for issue in validation_issues[:5]:  # Show first 5 issues
                print(f"  - {issue}")

        # Create project.yml with CONSISTENT naming
        project_yml = {
            'name': safe_target_name,  # NO SPACES
            'options': {
                'bundleIdPrefix': 'com.swiftgen',
                'deploymentTarget': '16.0'
            },
            'settings': {
                'PRODUCT_NAME': safe_product_name,  # CONSISTENT, NO SPACES
                'PRODUCT_BUNDLE_IDENTIFIER': bundle_id,
                'MARKETING_VERSION': '1.0',
                'CURRENT_PROJECT_VERSION': '1',
                'DISPLAY_NAME': display_name  # Original name for UI display
            },
            'targets': {
                safe_target_name: {  # Target name matches project name
                    'type': 'application',
                    'platform': 'iOS',
                    'sources': ['Sources'],
                    'settings': {
                        'INFOPLIST_FILE': 'Info.plist',
                        'PRODUCT_NAME': safe_product_name,  # MUST BE CONSISTENT
                        'PRODUCT_BUNDLE_IDENTIFIER': bundle_id,
                        'SWIFT_VERSION': '5.9',
                        'TARGETED_DEVICE_FAMILY': '1,2',
                        'IPHONEOS_DEPLOYMENT_TARGET': '16.0'
                    }
                }
            }
        }

        # Write project.yml
        project_yml_path = os.path.join(project_path, 'project.yml')
        with open(project_yml_path, 'w') as f:
            yaml.dump(project_yml, f, default_flow_style=False, sort_keys=False)

        # Create Info.plist with display name
        info_plist = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>$(DEVELOPMENT_LANGUAGE)</string>
    <key>CFBundleDisplayName</key>
    <string>{display_name}</string>
    <key>CFBundleExecutable</key>
    <string>{safe_product_name}</string>
    <key>CFBundleIdentifier</key>
    <string>{bundle_id}</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>{safe_product_name}</string>
    <key>CFBundlePackageType</key>
    <string>$(PRODUCT_BUNDLE_PACKAGE_TYPE)</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSRequiresIPhoneOS</key>
    <true/>
    <key>UIApplicationSupportsIndirectInputEvents</key>
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
</plist>'''

        info_plist_path = os.path.join(project_path, 'Info.plist')
        with open(info_plist_path, 'w') as f:
            f.write(info_plist)

        # Store project metadata
        project_metadata = {
            'project_id': project_id,
            'app_name': display_name,  # Original display name
            'safe_app_name': safe_app_name,
            'target_name': safe_target_name,
            'product_name': safe_product_name,
            'bundle_id': bundle_id,
            'created_at': datetime.now().isoformat(),
            'files': valid_files,
            'validation_issues': validation_issues,
            'app_complexity': 'low'  # Default, will be updated by main.py
        }

        metadata_path = os.path.join(project_path, 'project.json')
        with open(metadata_path, 'w') as f:
            json.dump(project_metadata, f, indent=2)

        # Final validation
        self._validate_project_consistency(project_path, display_name, safe_target_name, safe_product_name)

        print(f"\n[PROJECT MANAGER] Project created successfully:")
        print(f"  Path: {project_path}")
        print(f"  Files: {len(valid_files)}")
        print(f"  Bundle ID: {bundle_id}")

        return project_path

    async def update_project_files(self, project_id: str, modified_files: List[Dict]) -> bool:
        """Update project files after modification - fixed to write ALL files"""

        project_path = await self.get_project_path(project_id)
        if not project_path:
            raise ValueError(f"Project {project_id} not found")

        # Load project metadata
        metadata_path = os.path.join(project_path, 'project.json')
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        # Get safe names from metadata
        safe_product_name = metadata.get('product_name')
        safe_target_name = metadata.get('target_name')

        updated_files = []
        failed_files = []
        
        print(f"[PROJECT MANAGER] Updating {len(modified_files)} files for project {project_id}")

        # Write ALL files provided by the LLM
        for file_info in modified_files:
            try:
                original_path = file_info.get("path", "")
                content = file_info.get("content", "")
                
                if not original_path or not content:
                    print(f"[PROJECT MANAGER] Skipping empty file entry")
                    continue

                # Fix file path
                fixed_path = self._fix_file_path(original_path)
                if not fixed_path:
                    print(f"[PROJECT MANAGER] Skipping non-Swift file: {original_path}")
                    continue

                # Ensure the file is in Sources directory
                if not fixed_path.startswith("Sources/"):
                    fixed_path = f"Sources/{os.path.basename(fixed_path)}"

                file_path = os.path.join(project_path, fixed_path)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Log what we're writing
                print(f"[PROJECT MANAGER] Writing file: {fixed_path} ({len(content)} bytes)")

                with open(file_path, 'w') as f:
                    f.write(content)

                updated_files.append(fixed_path)
                
            except Exception as e:
                error_msg = f"Failed to write {original_path}: {str(e)}"
                print(f"[PROJECT MANAGER] ERROR: {error_msg}")
                failed_files.append(error_msg)

        # Report results
        print(f"[PROJECT MANAGER] Successfully wrote {len(updated_files)} files")
        if failed_files:
            print(f"[PROJECT MANAGER] Failed to write {len(failed_files)} files: {failed_files}")
            # Don't raise exception - partial success is better than total failure
            # raise Exception(f"Failed to write {len(failed_files)} files: {failed_files}")

        # Update metadata
        metadata['files'] = updated_files
        metadata['modified_at'] = datetime.now().isoformat()

        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Validate consistency
        self._validate_project_consistency(project_path, metadata.get('app_name'),
                                           safe_target_name, safe_product_name)

        return True

    def _cleanup_duplicate_files(self, project_path: str, filename_to_paths: Dict[str, str]):
        """Remove duplicate files that aren't in the approved list"""
        sources_dir = os.path.join(project_path, "Sources")
        
        # Walk through all Swift files in the project
        for root, dirs, files in os.walk(sources_dir):
            for file in files:
                if file.endswith('.swift'):
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, project_path)
                    
                    # If this filename exists in our approved list but this isn't the approved path
                    if file in filename_to_paths and filename_to_paths[file] != relative_path:
                        print(f"[PROJECT MANAGER] Removing duplicate file: {relative_path}")
                        try:
                            os.remove(full_path)
                        except Exception as e:
                            print(f"[PROJECT MANAGER] Error removing duplicate: {e}")

    async def get_project_path(self, project_id: str) -> Optional[str]:
        """Get the path to a project"""
        project_path = os.path.join(self.workspaces_dir, project_id)
        if os.path.exists(project_path):
            return project_path
        return None

    async def list_projects(self) -> List[Dict]:
        """List all projects with metadata"""
        projects = []

        if not os.path.exists(self.workspaces_dir):
            return projects

        for project_id in os.listdir(self.workspaces_dir):
            project_path = os.path.join(self.workspaces_dir, project_id)
            metadata_path = os.path.join(project_path, 'project.json')

            if os.path.isdir(project_path) and os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)

                    projects.append({
                        'project_id': project_id,
                        'app_name': metadata.get('app_name', 'Unknown'),
                        'bundle_id': metadata.get('bundle_id', 'Unknown'),
                        'created_at': metadata.get('created_at', 'Unknown'),
                        'modified_at': metadata.get('modified_at', metadata.get('created_at', 'Unknown'))
                    })
                except Exception as e:
                    print(f"[PROJECT MANAGER] Error reading project {project_id}: {e}")

        # Sort by creation date (newest first)
        projects.sort(key=lambda x: x['created_at'], reverse=True)

        return projects

    async def delete_project(self, project_id: str) -> bool:
        """Delete a project"""
        project_path = await self.get_project_path(project_id)
        if project_path:
            try:
                shutil.rmtree(project_path)
                print(f"[PROJECT MANAGER] Deleted project: {project_id}")
                return True
            except Exception as e:
                print(f"[PROJECT MANAGER] Error deleting project {project_id}: {e}")
        return False