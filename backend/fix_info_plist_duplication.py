"""
Fix for Multiple Info.plist error in Xcode projects
"""
import os
import re
import subprocess
import logging

logger = logging.getLogger(__name__)

def fix_info_plist_duplication(project_path: str) -> bool:
    """
    Fix "Multiple commands produce Info.plist" error
    This happens when there are duplicate Info.plist references in the project
    """
    try:
        # Find the .xcodeproj directory
        xcodeproj_path = None
        for item in os.listdir(project_path):
            if item.endswith('.xcodeproj'):
                xcodeproj_path = os.path.join(project_path, item)
                break
        
        if not xcodeproj_path:
            logger.error("No .xcodeproj found")
            return False
        
        # Clean build folder
        build_path = os.path.join(project_path, "build")
        if os.path.exists(build_path):
            logger.info("Cleaning build folder")
            subprocess.run(["rm", "-rf", build_path], capture_output=True)
        
        # Clean derived data
        derived_data_path = os.path.expanduser("~/Library/Developer/Xcode/DerivedData")
        if os.path.exists(derived_data_path):
            # Find and remove project-specific derived data
            for item in os.listdir(derived_data_path):
                if project_path.split('/')[-1].lower() in item.lower():
                    item_path = os.path.join(derived_data_path, item)
                    logger.info(f"Removing derived data: {item_path}")
                    subprocess.run(["rm", "-rf", item_path], capture_output=True)
        
        # Clean the project
        logger.info("Running xcodebuild clean")
        clean_result = subprocess.run(
            ["xcodebuild", "clean", "-project", xcodeproj_path],
            capture_output=True,
            text=True,
            cwd=project_path
        )
        
        if clean_result.returncode != 0:
            logger.warning(f"Clean failed: {clean_result.stderr}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to fix Info.plist duplication: {e}")
        return False


def check_for_duplicate_files(project_path: str) -> list:
    """Check for duplicate files in the project structure"""
    duplicates = []
    seen_files = {}
    
    sources_path = os.path.join(project_path, "Sources")
    if os.path.exists(sources_path):
        for root, dirs, files in os.walk(sources_path):
            for file in files:
                if file.endswith('.swift'):
                    if file in seen_files:
                        duplicates.append({
                            'filename': file,
                            'path1': seen_files[file],
                            'path2': os.path.join(root, file)
                        })
                    else:
                        seen_files[file] = os.path.join(root, file)
    
    return duplicates


def remove_duplicate_files(project_path: str) -> int:
    """Remove duplicate files, keeping the one in the most appropriate directory"""
    duplicates = check_for_duplicate_files(project_path)
    removed_count = 0
    
    for dup in duplicates:
        path1 = dup['path1']
        path2 = dup['path2']
        
        # Determine which file to keep based on directory structure
        # Prefer Utils over Networking for SSL files
        if "APIClient+SSL" in dup['filename'] or "CombineNetworking+SSL" in dup['filename']:
            if "Utils" in path1 and "Networking" in path2:
                # Keep Utils version, remove Networking
                os.remove(path2)
                logger.info(f"Removed duplicate: {path2}")
                removed_count += 1
            elif "Networking" in path1 and "Utils" in path2:
                # Keep Utils version, remove Networking
                os.remove(path1)
                logger.info(f"Removed duplicate: {path1}")
                removed_count += 1
        else:
            # For other files, keep the one in the more specific directory
            if path1.count('/') > path2.count('/'):
                os.remove(path2)
                logger.info(f"Removed duplicate: {path2}")
                removed_count += 1
            else:
                os.remove(path1)
                logger.info(f"Removed duplicate: {path1}")
                removed_count += 1
    
    return removed_count