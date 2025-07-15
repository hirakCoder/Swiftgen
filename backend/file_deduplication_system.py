"""
File Deduplication System for SwiftGen
Prevents duplicate files from being created that cause Xcode build errors
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime
import logging

class FileDeduplicationSystem:
    """Robust system to prevent and resolve duplicate files in Swift projects"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.sources_path = self.project_path / "Sources"
        self.logger = logging.getLogger(__name__)
        
        # Common file patterns that should be unique
        self.unique_files = {
            "ContentView.swift": ["Sources/", "Sources/Views/"],
            "App.swift": ["Sources/"],
            "AppApp.swift": ["Sources/"],
            "main.swift": ["Sources/"],
        }
        
        # Preferred locations for common files
        self.preferred_locations = {
            "ContentView.swift": "Sources/",
            "App.swift": "Sources/",
            "AppApp.swift": "Sources/",
            "main.swift": "Sources/",
        }
    
    def scan_for_duplicates(self) -> Dict[str, List[str]]:
        """Scan project for duplicate files and return them grouped by filename"""
        duplicates = {}
        
        if not self.sources_path.exists():
            return duplicates
            
        # Walk through all Swift files
        for root, dirs, files in os.walk(self.sources_path):
            for file in files:
                if file.endswith('.swift'):
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(self.project_path)
                    
                    if file not in duplicates:
                        duplicates[file] = []
                    duplicates[file].append(str(rel_path))
        
        # Filter to only return actual duplicates
        return {k: v for k, v in duplicates.items() if len(v) > 1}
    
    def resolve_duplicate(self, filename: str, file_paths: List[str]) -> Optional[str]:
        """Resolve which file to keep when duplicates are found"""
        if filename not in self.preferred_locations:
            # For non-standard files, keep the first one found
            return file_paths[0]
        
        preferred_location = self.preferred_locations[filename]
        
        # Find the file in the preferred location
        for path in file_paths:
            if path.startswith(preferred_location):
                return path
        
        # If preferred location not found, keep the first one
        return file_paths[0]
    
    def remove_duplicate_files(self) -> Dict[str, List[str]]:
        """Remove duplicate files, keeping only the preferred version"""
        duplicates = self.scan_for_duplicates()
        removed_files = {}
        
        for filename, file_paths in duplicates.items():
            if len(file_paths) <= 1:
                continue
            
            # Determine which file to keep
            file_to_keep = self.resolve_duplicate(filename, file_paths)
            files_to_remove = [f for f in file_paths if f != file_to_keep]
            
            self.logger.info(f"Resolving duplicate {filename}: keeping {file_to_keep}, removing {files_to_remove}")
            
            # Remove the duplicate files
            for file_path in files_to_remove:
                full_path = self.project_path / file_path
                try:
                    if full_path.exists():
                        full_path.unlink()
                        self.logger.info(f"Removed duplicate file: {file_path}")
                except Exception as e:
                    self.logger.error(f"Failed to remove {file_path}: {e}")
            
            if files_to_remove:
                removed_files[filename] = files_to_remove
        
        return removed_files
    
    def prevent_duplicate_creation(self, new_files: Dict[str, str]) -> Dict[str, str]:
        """Prevent creation of duplicate files by checking against existing files"""
        cleaned_files = {}
        existing_files = self.get_existing_files()
        
        for file_path, content in new_files.items():
            filename = Path(file_path).name
            
            # Check if this file already exists somewhere
            existing_paths = [path for path in existing_files if Path(path).name == filename]
            
            if existing_paths:
                # File already exists, decide what to do
                if filename in self.preferred_locations:
                    preferred_location = self.preferred_locations[filename]
                    
                    # If we're trying to create in preferred location, allow it
                    if file_path.startswith(preferred_location):
                        cleaned_files[file_path] = content
                        # Remove existing files in non-preferred locations
                        for existing_path in existing_paths:
                            if not existing_path.startswith(preferred_location):
                                full_path = self.project_path / existing_path
                                try:
                                    if full_path.exists():
                                        full_path.unlink()
                                        self.logger.info(f"Removed existing file to prevent duplicate: {existing_path}")
                                except Exception as e:
                                    self.logger.error(f"Failed to remove existing file {existing_path}: {e}")
                    else:
                        # Trying to create in non-preferred location, skip
                        self.logger.info(f"Skipping creation of {file_path} - file already exists in preferred location")
                        continue
                else:
                    # For non-standard files, update the existing one
                    existing_path = existing_paths[0]
                    cleaned_files[existing_path] = content
                    self.logger.info(f"Updating existing file instead of creating duplicate: {existing_path}")
            else:
                # New file, allow creation
                cleaned_files[file_path] = content
        
        return cleaned_files
    
    def get_existing_files(self) -> List[str]:
        """Get list of all existing Swift files in the project"""
        files = []
        
        if not self.sources_path.exists():
            return files
            
        for root, dirs, file_list in os.walk(self.sources_path):
            for file in file_list:
                if file.endswith('.swift'):
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(self.project_path)
                    files.append(str(rel_path))
        
        return files
    
    def ensure_unique_files(self, files_to_write: Dict[str, str]) -> Dict[str, str]:
        """Ensure all files to be written are unique and don't create duplicates"""
        
        # First, clean up any existing duplicates
        self.remove_duplicate_files()
        
        # Then, prevent creation of new duplicates
        cleaned_files = self.prevent_duplicate_creation(files_to_write)
        
        # Final validation - check for duplicates within the files being written
        filename_to_path = {}
        final_files = {}
        
        for file_path, content in cleaned_files.items():
            filename = Path(file_path).name
            
            if filename in filename_to_path:
                # Duplicate within the new files
                existing_path = filename_to_path[filename]
                
                # Choose the preferred location
                if filename in self.preferred_locations:
                    preferred_location = self.preferred_locations[filename]
                    
                    if file_path.startswith(preferred_location):
                        # Current file is in preferred location, use it
                        final_files[file_path] = content
                        filename_to_path[filename] = file_path
                        # Remove the previous entry if it exists
                        if existing_path in final_files:
                            del final_files[existing_path]
                    elif not existing_path.startswith(preferred_location):
                        # Neither is in preferred location, keep the first one
                        continue
                else:
                    # Keep the first occurrence
                    continue
            else:
                # No duplicate, add to final files
                final_files[file_path] = content
                filename_to_path[filename] = file_path
        
        return final_files
    
    def validate_project_structure(self) -> List[str]:
        """Validate project structure and return any issues found"""
        issues = []
        
        # Check for duplicate files
        duplicates = self.scan_for_duplicates()
        for filename, paths in duplicates.items():
            if len(paths) > 1:
                issues.append(f"Duplicate file {filename} found in: {', '.join(paths)}")
        
        # Check for required files
        required_files = ["ContentView.swift", "App.swift"]
        existing_files = self.get_existing_files()
        existing_filenames = [Path(f).name for f in existing_files]
        
        for required_file in required_files:
            if required_file not in existing_filenames:
                issues.append(f"Missing required file: {required_file}")
        
        return issues
    
    def get_status_report(self) -> Dict:
        """Get a comprehensive status report of the file system"""
        return {
            "project_path": str(self.project_path),
            "total_swift_files": len(self.get_existing_files()),
            "existing_files": self.get_existing_files(),
            "duplicates": self.scan_for_duplicates(),
            "validation_issues": self.validate_project_structure(),
            "timestamp": datetime.now().isoformat()
        }