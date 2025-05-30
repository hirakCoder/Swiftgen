import os
import shutil
import json
import yaml
from typing import Dict, List, Optional
from datetime import datetime

class ProjectManager:
    def __init__(self):
        self.workspaces_dir = "../workspaces"
        self.templates_dir = "../templates/ios_app_template"
        os.makedirs(self.workspaces_dir, exist_ok=True)
    
    async def create_project(self, project_id: str, generated_code: Dict, app_name: str) -> str:
        """Create a new iOS project from generated code"""
        
        project_path = os.path.join(self.workspaces_dir, project_id)
        os.makedirs(project_path, exist_ok=True)
        
        # Copy template files
        shutil.copy(
            os.path.join(self.templates_dir, "Info.plist"),
            os.path.join(project_path, "Info.plist")
        )
        
        # Create Sources directory
        sources_dir = os.path.join(project_path, "Sources")
        os.makedirs(sources_dir, exist_ok=True)
        
        # Write generated files
        for file_info in generated_code.get("files", []):
            file_path = os.path.join(project_path, file_info["path"])
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write(file_info["content"])
        
        # Generate project.yml for xcodegen
        project_yml = self._generate_project_yml(
            app_name,
            generated_code.get("bundle_id", f"com.swiftgen.{app_name.lower()}"),
            generated_code.get("dependencies", [])
        )
        
        with open(os.path.join(project_path, "project.yml"), 'w') as f:
            yaml.dump(project_yml, f, default_flow_style=False)
        
        # Save project metadata
        metadata = {
            "project_id": project_id,
            "app_name": app_name,
            "created_at": datetime.now().isoformat(),
            "bundle_id": generated_code.get("bundle_id"),
            "files": [f["path"] for f in generated_code.get("files", [])],
            "modifications": []
        }

        with open(os.path.join(project_path, "project.json"), 'w') as f:
            json.dump(metadata, f, indent=2)

        return project_path

    async def update_project_files(self, project_id: str, updated_files: List[Dict]) -> bool:
        """Update existing project files"""
        project_path = os.path.join(self.workspaces_dir, project_id)
        if not os.path.exists(project_path):
            return False

        # Backup current files
        backup_dir = os.path.join(project_path, ".backups", datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(backup_dir, exist_ok=True)

        # Update each file
        for file_info in updated_files:
            file_path = os.path.join(project_path, file_info["path"])

            # Backup existing file if it exists
            if os.path.exists(file_path):
                backup_path = os.path.join(backup_dir, file_info["path"])
                os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                shutil.copy2(file_path, backup_path)

            # Write new content
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(file_info["content"])

        # Update metadata
        metadata_path = os.path.join(project_path, "project.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)

            metadata["last_modified"] = datetime.now().isoformat()
            metadata["modifications"].append({
                "timestamp": datetime.now().isoformat(),
                "files_updated": [f["path"] for f in updated_files]
            })

            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

        return True

    def _generate_project_yml(self, app_name: str, bundle_id: str, dependencies: List[str]) -> Dict:
        """Generate xcodegen configuration"""

        # Clean app name for use as target name
        target_name = ''.join(c for c in app_name if c.isalnum())
        if not target_name:
            target_name = "MyApp"

        config = {
            'name': target_name,
            'options': {
                'bundleIdPrefix': bundle_id.rsplit('.', 1)[0],
                'createIntermediateGroups': True,
                'deploymentTarget': {
                    'iOS': '16.0'
                }
            },
            'settings': {
                'base': {
                    'SWIFT_VERSION': '5.9',
                    'DEVELOPMENT_TEAM': '',
                    'PRODUCT_NAME': app_name,
                    # Disable code signing for simulator builds
                    'CODE_SIGN_IDENTITY': '',
                    'CODE_SIGNING_REQUIRED': 'NO',
                    'CODE_SIGNING_ALLOWED': 'NO',
                    'CODE_SIGN_ENTITLEMENTS': '',
                    'EXPANDED_CODE_SIGN_IDENTITY': '',
                    'PROVISIONING_PROFILE_SPECIFIER': '',
                    'PROVISIONING_PROFILE': ''
                }
            },
            'targets': {
                target_name: {
                    'type': 'application',
                    'platform': 'iOS',
                    'sources': [
                        {
                            'path': 'Sources',
                            'excludes': ['**/*.md']
                        }
                    ],
                    'settings': {
                        'base': {
                            'INFOPLIST_FILE': 'Info.plist',
                            'PRODUCT_BUNDLE_IDENTIFIER': bundle_id,
                            'MARKETING_VERSION': '1.0',
                            'CURRENT_PROJECT_VERSION': '1',
                            # Additional settings to ensure no code signing
                            'CODE_SIGN_STYLE': 'Manual',
                            'DEVELOPMENT_TEAM': '',
                            'CODE_SIGN_IDENTITY': '',
                            'CODE_SIGNING_REQUIRED': 'NO',
                            'CODE_SIGNING_ALLOWED': 'NO'
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
        app_built = os.path.exists(derived_data) and any(
            f.endswith('.app')
            for root, dirs, files in os.walk(derived_data)
            for f in files
        )

        metadata['app_built'] = app_built
        metadata['project_path'] = project_path

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
                            "created_at": metadata.get("created_at", ""),
                            "last_modified": metadata.get("last_modified", metadata.get("created_at", ""))
                        })

        # Sort by last modified date
        projects.sort(key=lambda x: x.get("last_modified", ""), reverse=True)
        return projects