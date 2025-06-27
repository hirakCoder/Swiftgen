"""
File Structure Manager for SwiftGen AI
Handles proper file organization, verification, and path resolution for complex iOS apps
"""

import os
import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Set, Any
from pathlib import Path

class FileStructureManager:
    """Manages file structure and verification for iOS projects"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Standard iOS project structure
        self.standard_structure = {
            "Views": ["ContentView", "MainView", "TabView", "NavigationView"],
            "Models": ["Model", "DataModel", "Entity", "Type"],
            "ViewModels": ["ViewModel", "Manager", "Controller", "Store"],
            "Services": ["Service", "API", "Network", "DataStore"],
            "Utils": ["Helper", "Extension", "Utility", "Constants"],
            "Views": ["Component", "Card", "Cell", "Row", "Item", "View"]  # All views in same directory
        }
        
        # File type patterns
        self.file_patterns = {
            "view": r".*View\.swift$|.*Screen\.swift$|.*Page\.swift$",
            "model": r".*Model\.swift$|.*Entity\.swift$|.*Type\.swift$",
            "viewmodel": r".*ViewModel\.swift$|.*VM\.swift$|.*Store\.swift$",
            "service": r".*Service\.swift$|.*API\.swift$|.*Manager\.swift$",
            "component": r".*Component\.swift$|.*Card\.swift$|.*Cell\.swift$",
            "extension": r".*\+.*\.swift$|Extension.*\.swift$",
            "app": r".*App\.swift$"
        }
    
    def organize_files(self, files: List[Dict], project_path: str) -> Tuple[List[Dict], Dict[str, str]]:
        """Organize files into proper directory structure"""
        organized_files = []
        file_mapping = {}  # old_path -> new_path
        seen_files = set()  # Track files we've already processed to prevent duplicates
        
        for file in files:
            original_path = file.get("path", "")
            content = file.get("content", "")
            filename = os.path.basename(original_path)
            
            # Skip SSL-related files to prevent reorganization issues
            if any(ssl_file in filename for ssl_file in ["APIClient+SSL", "CombineNetworking+SSL", "NetworkConfiguration"]):
                # Keep SSL files where they are
                proper_path = original_path
            else:
                # Determine proper path based on content and filename
                proper_path = self._determine_proper_path(original_path, content)
            
            # Prevent duplicate files
            file_key = (filename, proper_path)
            if file_key in seen_files:
                self.logger.warning(f"Skipping duplicate file: {proper_path}")
                continue
            seen_files.add(file_key)
            
            # Update file path if needed
            if proper_path != original_path:
                self.logger.info(f"Reorganizing {original_path} -> {proper_path}")
                file_mapping[original_path] = proper_path
            
            # Fix syntax errors and update imports
            fixed_content = self._fix_swift_syntax_errors(content)
            final_content = self._update_imports_for_new_structure(fixed_content, file_mapping)
            
            organized_files.append({
                "path": proper_path,
                "content": final_content
            })
        
        return organized_files, file_mapping
    
    def _determine_proper_path(self, file_path: str, content: str) -> str:
        """Determine the proper path for a file based on its content and name"""
        filename = os.path.basename(file_path)
        
        # Check if already in proper structure
        if any(subdir in file_path for subdir in ["Sources/Views/", "Sources/Models/", 
                                                   "Sources/ViewModels/", "Sources/Services/"]):
            return file_path
        
        # Determine subdirectory based on file type
        subdirectory = self._determine_subdirectory(filename, content)
        
        # Build proper path
        if subdirectory:
            return f"Sources/{subdirectory}/{filename}"
        else:
            # Default to Sources root for unclassified files
            return f"Sources/{filename}"
    
    def _determine_subdirectory(self, filename: str, content: str) -> Optional[str]:
        """Determine which subdirectory a file belongs to"""
        
        # Check filename patterns first
        for file_type, pattern in self.file_patterns.items():
            if re.match(pattern, filename):
                if file_type == "view":
                    return "Views"
                elif file_type == "model":
                    return "Models"
                elif file_type == "viewmodel":
                    return "ViewModels"
                elif file_type == "service":
                    return "Services"
                elif file_type == "component":
                    return "Views"  # Keep components in Views to avoid import issues
                elif file_type == "extension":
                    return "Utils"
        
        # Check content for clues
        if ": View" in content or "struct.*View.*{" in content:
            return "Views"
        elif "ObservableObject" in content or "class.*ViewModel" in content:
            return "ViewModels"
        elif "struct.*Model" in content or ": Codable" in content or ": Identifiable" in content:
            return "Models"
        elif "Service" in content or "API" in content or "Network" in content:
            return "Services"
        elif "extension" in content:
            return "Utils"
        
        # Check for specific keywords in filenames
        name_lower = filename.lower()
        for directory, keywords in self.standard_structure.items():
            for keyword in keywords:
                if keyword.lower() in name_lower:
                    return directory
        
        return None
    
    def _fix_swift_syntax_errors(self, content: str) -> str:
        """Fix common Swift syntax errors that may be introduced during modification"""
        import re
        
        # Fix semicolon errors in access modifiers
        content = re.sub(r'private\s*;\s*var', 'private var', content)
        content = re.sub(r'public\s*;\s*var', 'public var', content)
        content = re.sub(r'internal\s*;\s*var', 'internal var', content)
        content = re.sub(r'fileprivate\s*;\s*var', 'fileprivate var', content)
        
        # Also fix for func, let, etc.
        content = re.sub(r'private\s*;\s*func', 'private func', content)
        content = re.sub(r'public\s*;\s*func', 'public func', content)
        content = re.sub(r'private\s*;\s*let', 'private let', content)
        content = re.sub(r'public\s*;\s*let', 'public let', content)
        
        # Fix other common semicolon issues
        content = re.sub(r'}\s*;\s*else', '} else', content)
        content = re.sub(r'}\s*;\s*catch', '} catch', content)
        
        # Fix empty parameter lists with semicolons
        content = re.sub(r'\(\s*;\s*\)', '()', content)
        
        return content
    
    def _update_imports_for_new_structure(self, content: str, file_mapping: Dict[str, str]) -> str:
        """Update import statements and references for new file structure"""
        updated_content = content
        
        # Remove invalid local module imports
        invalid_imports = ["Views", "Models", "ViewModels", "Services", "Utils"]
        for module in invalid_imports:
            updated_content = re.sub(f"import {module}\\s*\n", "", updated_content)
        
        # Update type references if files were moved
        for old_path, new_path in file_mapping.items():
            old_name = os.path.basename(old_path).replace(".swift", "")
            new_name = os.path.basename(new_path).replace(".swift", "")
            
            # If the file name hasn't changed, no need to update references
            if old_name == new_name:
                continue
            
            # Update references to the type
            updated_content = re.sub(f"\\b{old_name}\\b", new_name, updated_content)
        
        return updated_content
    
    def verify_and_write_files(self, files: List[Dict], project_path: str) -> Tuple[bool, List[str], List[str]]:
        """Write files to disk with verification"""
        written_files = []
        failed_files = []
        
        for file in files:
            file_path = os.path.join(project_path, file["path"])
            
            try:
                # Create directory structure
                file_dir = os.path.dirname(file_path)
                os.makedirs(file_dir, exist_ok=True)
                
                # Fix common syntax errors before writing
                content = self._fix_swift_syntax_errors(file["content"])
                
                # Write file
                with open(file_path, 'w') as f:
                    f.write(content)
                
                # Verify file exists and has content
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    written_files.append(file["path"])
                    self.logger.info(f"✓ Verified: {file['path']} ({os.path.getsize(file_path)} bytes)")
                else:
                    failed_files.append(file["path"])
                    self.logger.error(f"✗ Failed verification: {file['path']}")
                    
            except Exception as e:
                failed_files.append(file["path"])
                self.logger.error(f"✗ Failed to write {file['path']}: {e}")
        
        success = len(failed_files) == 0
        return success, written_files, failed_files
    
    def find_missing_files(self, errors: List[str], existing_files: List[Dict]) -> List[Dict[str, str]]:
        """Identify missing files from build errors"""
        missing_files = []
        existing_paths = {f["path"] for f in existing_files}
        
        for error in errors:
            # Pattern: cannot find 'TypeName' in scope
            match = re.search(r"cannot find '(\w+)' in scope", error)
            if match:
                type_name = match.group(1)
                
                # Check if it's likely a View
                if type_name.endswith("View") or type_name.endswith("Screen"):
                    file_name = f"{type_name}.swift"
                    expected_path = f"Sources/Views/{file_name}"
                    
                    # Check if file exists in any form
                    file_exists = any(
                        type_name in path or file_name in path 
                        for path in existing_paths
                    )
                    
                    if not file_exists:
                        missing_files.append({
                            "type": type_name,
                            "suggested_path": expected_path,
                            "category": "view"
                        })
                
                # Check for models
                elif any(suffix in type_name for suffix in ["Model", "Entity", "Type", "Data"]):
                    file_name = f"{type_name}.swift"
                    expected_path = f"Sources/Models/{file_name}"
                    
                    if not any(type_name in path for path in existing_paths):
                        missing_files.append({
                            "type": type_name,
                            "suggested_path": expected_path,
                            "category": "model"
                        })
        
        return missing_files
    
    def create_missing_file_prompt(self, missing_files: List[Dict[str, str]]) -> str:
        """Create a prompt for generating missing files"""
        if not missing_files:
            return ""
        
        prompt = "Create the following missing Swift files:\n\n"
        
        for file_info in missing_files:
            type_name = file_info["type"]
            category = file_info["category"]
            path = file_info["suggested_path"]
            
            if category == "view":
                prompt += f"- {path}: Create a SwiftUI View named {type_name} with appropriate UI\n"
            elif category == "model":
                prompt += f"- {path}: Create a data model named {type_name} that conforms to Codable and Identifiable\n"
        
        prompt += "\nEnsure all files follow SwiftUI best practices and integrate with the existing code."
        return prompt
    
    def validate_project_structure(self, project_path: str) -> Dict[str, Any]:
        """Validate the project has proper structure"""
        sources_dir = os.path.join(project_path, "Sources")
        
        if not os.path.exists(sources_dir):
            return {
                "valid": False,
                "errors": ["Sources directory not found"],
                "warnings": []
            }
        
        errors = []
        warnings = []
        structure = {}
        
        # Check for expected subdirectories
        expected_dirs = ["Views", "Models", "ViewModels", "Services"]
        for dir_name in expected_dirs:
            dir_path = os.path.join(sources_dir, dir_name)
            if os.path.exists(dir_path):
                # Count files in directory
                swift_files = [f for f in os.listdir(dir_path) if f.endswith('.swift')]
                structure[dir_name] = len(swift_files)
            else:
                # Only warn, don't error - not all apps need all directories
                if dir_name in ["Views", "Models"]:
                    warnings.append(f"{dir_name} directory not found")
        
        # Check for orphaned files in Sources root
        root_files = [f for f in os.listdir(sources_dir) 
                     if f.endswith('.swift') and os.path.isfile(os.path.join(sources_dir, f))]
        
        # App.swift is expected in root
        non_app_files = [f for f in root_files if not f.endswith('App.swift')]
        if len(non_app_files) > 3:  # Allow a few files in root
            warnings.append(f"{len(non_app_files)} Swift files in Sources root - consider organizing into subdirectories")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "structure": structure,
            "root_files": root_files
        }
    
    def get_file_tree(self, project_path: str) -> str:
        """Get a visual representation of the file structure"""
        sources_dir = os.path.join(project_path, "Sources")
        if not os.path.exists(sources_dir):
            return "Sources directory not found"
        
        tree = ["Sources/"]
        
        for root, dirs, files in os.walk(sources_dir):
            level = root.replace(sources_dir, '').count(os.sep)
            indent = "  " * level
            subdir = os.path.basename(root)
            
            if level > 0:
                tree.append(f"{indent}{subdir}/")
            
            subindent = "  " * (level + 1)
            for file in sorted(files):
                if file.endswith('.swift'):
                    tree.append(f"{subindent}{file}")
        
        return "\n".join(tree)