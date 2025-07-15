#!/usr/bin/env python3
"""
Clean up old and irrelevant files from SwiftGen project
Keeps only essential files and archives old session/daily files
"""

import os
import shutil
from datetime import datetime
import glob

# Define what to keep
ESSENTIAL_DOCS = [
    "CLAUDE.md",  # Master reference
    "README.md",
    "MASTER_ISSUES_AND_FIXES.md",
    "SWIFTGEN_ENHANCEMENT_PLAN_2025.md",
    "TESTING_GUIDE.md",
    "docs/swiftgen-project-guide.md",
    "docs/implementation-tasks.md",
    "docs/quick-reference.md",
    "docs/CAPABILITIES.md",
    "docs/REGRESSION_TESTING_PLAN.md"
]

# Files to definitely remove
TO_REMOVE = [
    "**/DAILY_*.md",
    "**/SESSION_*.md", 
    "**/WORK_SUMMARY_*.md",
    "**/FIXES_APPLIED_*.md",
    "**/debug_*.md",
    "**/*_TEMPLATE.md",
    "**/TOMORROW_*.md",
    "**/STOP_AND_THINK.md",
    "**/TEST_*.md",
    "**/QUICK_FIX*.md",
    "**/UI_FIX_CRITICAL.md",
    "**/UI_STATUS_UPDATES_*.md",
    "**/UX_ENHANCEMENTS_*.md"
]

# Archive directory
ARCHIVE_DIR = "docs/archive/cleanup_2025_11"


def should_keep_file(filepath):
    """Check if file should be kept"""
    # Keep essential docs
    for essential in ESSENTIAL_DOCS:
        if filepath.endswith(essential):
            return True
            
    # Keep all Python files
    if filepath.endswith('.py'):
        return True
        
    # Keep configuration files
    if any(filepath.endswith(ext) for ext in ['.json', '.yaml', '.yml', '.toml', '.ini']):
        return True
        
    # Keep test files
    if 'test' in filepath and filepath.endswith('.py'):
        return True
        
    # Keep HTML/JS/CSS files
    if any(filepath.endswith(ext) for ext in ['.html', '.js', '.css']):
        return True
        
    return False


def get_files_to_remove():
    """Get list of files to remove or archive"""
    files_to_remove = []
    
    # Find files matching removal patterns
    for pattern in TO_REMOVE:
        matches = glob.glob(f"**/{pattern}", recursive=True)
        files_to_remove.extend(matches)
        
    # Also find old fix summaries and issues
    old_patterns = [
        "docs/archive/**/*.md",
        "backend/archive/**/*.md",
        "**/FIXES_*.md",
        "**/FIX_*.md",
        "**/ISSUES_*.md"
    ]
    
    for pattern in old_patterns:
        matches = glob.glob(pattern, recursive=True)
        for match in matches:
            if not should_keep_file(match):
                files_to_remove.append(match)
                
    # Remove duplicates
    return list(set(files_to_remove))


def cleanup_project():
    """Main cleanup function"""
    print("🧹 SwiftGen Project Cleanup")
    print("=" * 60)
    
    # Create archive directory
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    
    files_to_remove = get_files_to_remove()
    
    print(f"Found {len(files_to_remove)} files to clean up")
    
    # Group by action
    removed = []
    archived = []
    
    for filepath in files_to_remove:
        if os.path.exists(filepath):
            # Skip if it's an essential file
            if should_keep_file(filepath):
                continue
                
            # Archive session summaries and work summaries
            if any(x in filepath for x in ['SESSION_SUMMARY', 'WORK_SUMMARY', 'MASTER_ISSUES']):
                archive_path = os.path.join(ARCHIVE_DIR, os.path.basename(filepath))
                try:
                    shutil.move(filepath, archive_path)
                    archived.append(filepath)
                    print(f"📦 Archived: {filepath}")
                except Exception as e:
                    print(f"❌ Failed to archive {filepath}: {e}")
            else:
                # Remove old/temporary files
                try:
                    os.remove(filepath)
                    removed.append(filepath)
                    print(f"🗑️  Removed: {filepath}")
                except Exception as e:
                    print(f"❌ Failed to remove {filepath}: {e}")
                    
    # Clean up empty directories
    for root, dirs, files in os.walk('.', topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                if not os.listdir(dir_path):  # Empty directory
                    os.rmdir(dir_path)
                    print(f"📁 Removed empty directory: {dir_path}")
            except:
                pass
                
    print("\n" + "=" * 60)
    print(f"✅ Cleanup Complete!")
    print(f"   - Removed: {len(removed)} files")
    print(f"   - Archived: {len(archived)} files")
    print(f"   - Archive location: {ARCHIVE_DIR}")
    
    # Create cleanup report
    report = f"""# Cleanup Report - {datetime.now().isoformat()}

## Summary
- Total files processed: {len(files_to_remove)}
- Files removed: {len(removed)}
- Files archived: {len(archived)}

## Removed Files
{chr(10).join(f'- {f}' for f in sorted(removed))}

## Archived Files
{chr(10).join(f'- {f}' for f in sorted(archived))}

## Kept Essential Files
- CLAUDE.md (Master reference)
- MASTER_ISSUES_AND_FIXES.md
- README.md
- All Python source files
- All test files
- Configuration files
"""
    
    with open(os.path.join(ARCHIVE_DIR, "cleanup_report.md"), "w") as f:
        f.write(report)
        
    print(f"\n📄 Cleanup report saved to {ARCHIVE_DIR}/cleanup_report.md")


if __name__ == "__main__":
    # Run cleanup directly in automated mode
    cleanup_project()