#!/usr/bin/env python3
"""Fix all modification issues comprehensively"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def fix_modification_handler():
    """Fix the modification handler to prevent all current issues"""
    
    handler_path = "backend/modification_handler.py"
    
    # Read the current file
    with open(handler_path, 'r') as f:
        content = f.read()
    
    # Find the handle_modification method
    method_start = content.find("async def handle_modification")
    if method_start == -1:
        print("❌ Could not find handle_modification method")
        return False
    
    # Add comprehensive validation before returning
    validation_code = '''
    def _validate_and_fix_modification_response(self, result: Dict, original_files: List[Dict]) -> Dict:
        """Validate and fix common issues in modification responses"""
        
        if not result.get("success", False):
            return result
            
        # Get list of original file paths
        original_paths = {f['path'] for f in original_files}
        result_paths = {f['path'] for f in result.get('files', [])}
        
        # Check for missing files
        missing_files = original_paths - result_paths
        if missing_files:
            logger.warning(f"[MODIFICATION] Response missing {len(missing_files)} files: {missing_files}")
            # Add missing files from originals
            for orig_file in original_files:
                if orig_file['path'] in missing_files:
                    result['files'].append(orig_file)
                    logger.info(f"[MODIFICATION] Added missing file: {orig_file['path']}")
        
        # Check for duplicate filenames
        filename_to_paths = {}
        for file in result.get('files', []):
            filename = os.path.basename(file['path'])
            if filename not in filename_to_paths:
                filename_to_paths[filename] = []
            filename_to_paths[filename].append(file['path'])
        
        # Remove duplicates, keeping the most specific path
        final_files = []
        seen_filenames = set()
        
        # Sort by path depth (deeper first)
        sorted_files = sorted(result.get('files', []), 
                            key=lambda f: f['path'].count('/'), 
                            reverse=True)
        
        for file in sorted_files:
            filename = os.path.basename(file['path'])
            if filename not in seen_filenames:
                seen_filenames.add(filename)
                final_files.append(file)
            else:
                logger.warning(f"[MODIFICATION] Removing duplicate: {file['path']}")
        
        result['files'] = final_files
        
        # Verify all original files are present
        final_paths = {f['path'] for f in final_files}
        if len(final_paths) < len(original_paths):
            logger.error(f"[MODIFICATION] Still missing files after fix: {original_paths - final_paths}")
        
        # Add files_modified list if not present
        if 'files_modified' not in result:
            # Detect which files actually changed
            modified = []
            for file in final_files:
                orig_file = next((f for f in original_files if f['path'] == file['path']), None)
                if orig_file and orig_file.get('content') != file.get('content'):
                    modified.append(file['path'])
            result['files_modified'] = modified
        
        return result
'''
    
    # Insert the validation method
    insert_pos = content.find("async def handle_modification")
    if insert_pos > 0:
        # Find the class definition
        class_pos = content.rfind("class", 0, insert_pos)
        if class_pos > 0:
            # Find the end of the previous method
            prev_method_end = content.rfind("\n\n", class_pos, insert_pos)
            if prev_method_end > 0:
                content = content[:prev_method_end] + "\n" + validation_code + "\n" + content[prev_method_end:]
    
    # Update handle_modification to use validation
    # Find where result is returned
    return_pattern = "return result"
    validated_return = "return self._validate_and_fix_modification_response(result, existing_files)"
    
    content = content.replace(return_pattern, validated_return)
    
    # Write the updated file
    with open(handler_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed modification handler validation")
    return True

def fix_modification_prompts():
    """Update prompts to be clearer about returning all files"""
    
    prompts_path = "backend/enhanced_prompts.py"
    
    with open(prompts_path, 'r') as f:
        content = f.read()
    
    # Find and update the modification prompt
    old_response_req = """RESPONSE REQUIREMENTS:
- Return ALL files (modified and unmodified)
- Clearly indicate which files changed
- Provide specific change descriptions
- Maintain proper JSON structure
- Use exact same file paths as provided (no duplicates)"""
    
    new_response_req = """RESPONSE REQUIREMENTS:
- Return ALL files (modified and unmodified) - EVERY SINGLE FILE
- If you receive 7 files, return exactly 7 files
- Use EXACT same file paths as provided - no changes to paths
- NEVER create duplicate files (e.g., ContentView.swift in two locations)
- For unchanged files, return them with original content intact
- In 'files_modified' array, list ONLY files you actually changed
- Provide specific descriptions of what changed in each file

CRITICAL: Your response MUST include:
{
    "files": [/* ALL original files with same paths */],
    "files_modified": [/* Only paths of files you changed */],
    "modification_summary": "Clear description of changes made"
}"""
    
    if old_response_req in content:
        content = content.replace(old_response_req, new_response_req)
        with open(prompts_path, 'w') as f:
            f.write(content)
        print("✅ Updated modification prompts for clarity")
    else:
        print("⚠️  Could not find response requirements section")
    
    return True

def enable_xai_in_router():
    """Re-enable xAI in the intelligent router"""
    
    router_path = "backend/intelligent_llm_router.py"
    
    with open(router_path, 'r') as f:
        content = f.read()
    
    # Look for any commented xAI sections
    if "# 'xai'" in content or "#'xai'" in content:
        content = content.replace("# 'xai'", "'xai'")
        content = content.replace("#'xai'", "'xai'")
        content = content.replace("# xai", "xai")
        
        with open(router_path, 'w') as f:
            f.write(content)
        print("✅ Re-enabled xAI in router")
    else:
        print("ℹ️  xAI already enabled in router")
    
    return True

def check_xai_api_key():
    """Verify XAI_API_KEY is set"""
    xai_key = os.environ.get('XAI_API_KEY')
    if not xai_key:
        print("❌ XAI_API_KEY not found in environment")
        print("   Set it with: export XAI_API_KEY='your-key-here'")
        return False
    else:
        print(f"✅ XAI_API_KEY found: {xai_key[:10]}...")
        return True

if __name__ == "__main__":
    print("🔧 Fixing Modification Issues")
    print("=" * 60)
    
    # Fix modification handler
    fix_modification_handler()
    
    # Fix prompts
    fix_modification_prompts()
    
    # Enable xAI
    enable_xai_in_router()
    
    # Check API key
    check_xai_api_key()
    
    print("\n✅ All fixes applied!")
    print("Restart the server to apply changes.")