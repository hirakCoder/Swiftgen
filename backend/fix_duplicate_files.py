#!/usr/bin/env python3
"""Fix duplicate file issue in modification handler"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def add_deduplication_to_handler():
    """Add file deduplication logic to OptimizedModificationHandler"""
    
    handler_path = "backend/optimized_modification_handler.py"
    
    # Read the current file
    with open(handler_path, 'r') as f:
        content = f.read()
    
    # Add deduplication method
    dedup_method = '''
    def _deduplicate_files(self, files: List[Dict]) -> List[Dict]:
        """Remove duplicate files, keeping only the most specific path"""
        seen_names = {}
        deduped_files = []
        
        # Sort files by path depth (deeper paths first)
        sorted_files = sorted(files, key=lambda f: f['path'].count('/'), reverse=True)
        
        for file in sorted_files:
            filename = os.path.basename(file['path'])
            
            if filename not in seen_names:
                seen_names[filename] = file['path']
                deduped_files.append(file)
            else:
                # Log the duplicate that was skipped
                logger.warning(f"[OPTIMIZED] Skipping duplicate file: {file['path']} (keeping {seen_names[filename]})")
        
        return deduped_files
'''
    
    # Find where to insert the method (before the _analyze_modification_intent method)
    insert_pos = content.find('    def _analyze_modification_intent')
    if insert_pos == -1:
        print("❌ Could not find insertion point")
        return False
    
    # Insert the deduplication method
    content = content[:insert_pos] + dedup_method + '\n' + content[insert_pos:]
    
    # Now update the return statement to use deduplication
    # Find the return statement with final_files
    return_pattern = '''return {
                    "success": True,
                    "files": final_files,'''
    
    deduped_return = '''# Deduplicate files before returning
                final_files = self._deduplicate_files(final_files)
                logger.info(f"[OPTIMIZED] Returning {len(final_files)} files after deduplication")
                
                return {
                    "success": True,
                    "files": final_files,'''
    
    content = content.replace(return_pattern, deduped_return)
    
    # Also add import for os at the top if not present
    if 'import os' not in content:
        imports_end = content.find('logger = logging.getLogger')
        content = content[:imports_end] + 'import os\n\n' + content[imports_end:]
    
    # Write the updated file
    with open(handler_path, 'w') as f:
        f.write(content)
    
    print("✅ Added deduplication to OptimizedModificationHandler")
    return True

if __name__ == "__main__":
    add_deduplication_to_handler()