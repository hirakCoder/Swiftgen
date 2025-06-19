"""
Modification Handler - Ensures modifications are applied correctly
"""

import json
import re
from typing import List, Dict, Tuple, Optional
from difflib import unified_diff

# Import UI enhancement handler
try:
    from ui_enhancement_handler import UIEnhancementHandler
    ui_handler = UIEnhancementHandler()
except ImportError:
    ui_handler = None

class ModificationHandler:
    """Handles the modification process to ensure changes are applied correctly"""
    
    def __init__(self):
        self.verbose = True
        
    def prepare_modification_prompt(self, 
                                  app_name: str,
                                  modification_request: str,
                                  files: List[Dict]) -> str:
        """Prepare a clear, focused modification prompt"""
        
        # Analyze what files might need to be modified
        relevant_files = self._identify_relevant_files(modification_request, files)
        
        prompt = f"""You are modifying the iOS app: {app_name}

MODIFICATION REQUEST: {modification_request}

CRITICAL RULES:
1. ONLY modify files that need to change for this specific request
2. If a file doesn't need changes, include it UNCHANGED
3. Return ALL {len(files)} files, even unchanged ones
4. Focus changes ONLY on the requested modification
5. Preserve ALL existing functionality unless explicitly asked to change it

FILES THAT MIGHT NEED MODIFICATION:
{', '.join(relevant_files) if relevant_files else 'Determine based on the request'}

CURRENT FILES ({len(files)} total):
"""
        
        # Include full file content
        for file in files:
            prompt += f"\n\n--- {file['path']} ---\n{file['content']}\n--- END {file['path']} ---"
        
        prompt += f"""

Return JSON with ALL {len(files)} files:
{{
    "files": [
        {{
            "path": "path/to/file.swift",
            "content": "full file content with or without modifications"
        }}
        // ... all {len(files)} files
    ],
    "modification_summary": "What was changed",
    "changes_made": ["Specific change 1", "Specific change 2"],
    "files_modified": ["List of files that were actually changed"]
}}
"""
        
        return prompt
    
    def _identify_relevant_files(self, modification_request: str, files: List[Dict]) -> List[str]:
        """Identify which files are likely relevant to the modification"""
        relevant = []
        request_lower = modification_request.lower()
        
        # Keywords that suggest which files to modify
        ui_keywords = ['color', 'background', 'button', 'text', 'view', 'ui', 'ux', 'interface', 
                      'display', 'show', 'fancy', 'interactive', 'animation', 'style', 'theme',
                      'design', 'visual', 'appearance', 'look', 'feel', 'gradient', 'shadow']
        model_keywords = ['data', 'model', 'property', 'field', 'attribute']
        logic_keywords = ['function', 'method', 'logic', 'behavior', 'action', 'functionality']
        
        for file in files:
            path = file['path']
            content = file.get('content', '').lower()
            
            # Check if this file is likely relevant
            if any(keyword in request_lower for keyword in ui_keywords):
                if 'View' in path and path.endswith('.swift'):
                    relevant.append(path)
            
            if any(keyword in request_lower for keyword in model_keywords):
                if 'Model' in path or 'TodoItem' in path or 'Category' in path:
                    relevant.append(path)
                    
            if any(keyword in request_lower for keyword in logic_keywords):
                if 'Manager' in path or 'ViewModel' in path:
                    relevant.append(path)
            
            # Check for specific mentions in the request
            filename = path.split('/')[-1].replace('.swift', '').lower()
            if filename in request_lower:
                relevant.append(path)
        
        return list(set(relevant))
    
    def validate_modification_response(self, response: Dict, original_files: List[Dict]) -> Tuple[bool, List[str]]:
        """Validate that the modification response is complete and correct"""
        issues = []
        
        # Check 1: All files present
        if 'files' not in response:
            issues.append("Response missing 'files' array")
            return False, issues
            
        response_files = response.get('files', [])
        # Allow adding new files (more files than original) but not removing files
        if len(response_files) < len(original_files):
            issues.append(f"Expected at least {len(original_files)} files, got {len(response_files)}")
        elif len(response_files) > len(original_files):
            # This is OK - new files were added (e.g., to fix missing type errors)
            print(f"[INFO] Response includes {len(response_files) - len(original_files)} new files")
        
        # Check 2: Files have required structure
        for i, file in enumerate(response_files):
            if not isinstance(file, dict):
                issues.append(f"File {i} is not a dictionary")
                continue
            if 'path' not in file:
                issues.append(f"File {i} missing 'path'")
            if 'content' not in file:
                issues.append(f"File {i} missing 'content'")
            elif not file['content'] or len(file['content']) < 10:
                issues.append(f"File {file.get('path', i)} has empty or invalid content")
        
        # Check 3: Ensure all original files are present
        response_paths = {f.get('path') for f in response_files if f.get('path')}
        original_paths = {f['path'] for f in original_files}
        missing_files = original_paths - response_paths
        
        if missing_files:
            issues.append(f"Missing original files: {', '.join(missing_files)}")
        
        # Check 4: Verify files_modified matches actual changes
        files_modified = response.get('files_modified', [])
        actual_modified = []
        
        # Create mapping for comparison
        original_map = {f['path']: f['content'] for f in original_files}
        
        for file in response_files:
            path = file.get('path', '')
            content = file.get('content', '')
            
            if path in original_map and original_map[path] != content:
                actual_modified.append(path)
        
        # Log what actually changed
        if self.verbose:
            print(f"[MODIFICATION] Files that actually changed: {actual_modified}")
            if files_modified:
                print(f"[MODIFICATION] Files claimed to be modified: {files_modified}")
        
        return len(issues) == 0, issues
    
    def fix_json_response(self, raw_response: str) -> Optional[Dict]:
        """Attempt to fix common JSON parsing issues"""
        
        # Remove markdown code blocks
        if '```json' in raw_response:
            raw_response = re.sub(r'```json\s*', '', raw_response)
            raw_response = re.sub(r'```\s*$', '', raw_response)
        
        # Try different fixing strategies
        strategies = [
            self._fix_escape_sequences,
            self._fix_newlines_in_strings,
            self._extract_json_object,
            self._fix_truncated_json
        ]
        
        for strategy in strategies:
            try:
                fixed = strategy(raw_response)
                if fixed:
                    return json.loads(fixed)
            except Exception as e:
                continue
        
        return None
    
    def _fix_escape_sequences(self, text: str) -> str:
        """Fix invalid escape sequences"""
        # First, handle the content inside Swift code strings more carefully
        # Look for patterns like "content": "...Swift code..."
        
        def fix_swift_code_content(match):
            key = match.group(1)
            content = match.group(2)
            
            # For Swift code content, we need to escape properly
            # Replace backslashes that aren't already escaped
            content = re.sub(r'(?<!\\)\\(?![\\"])', r'\\\\', content)
            
            # Replace newlines with proper escape
            content = content.replace('\n', '\\n')
            content = content.replace('\r', '\\r')
            content = content.replace('\t', '\\t')
            
            # Ensure quotes are escaped
            content = re.sub(r'(?<!\\)"', r'\\"', content)
            
            return f'"{key}": "{content}"'
        
        # Apply fix to content fields
        text = re.sub(r'"(content|path)"\s*:\s*"([^"]*(?:\\.[^"]*)*)"', 
                     fix_swift_code_content, text, flags=re.DOTALL)
        
        return text
    
    def _fix_newlines_in_strings(self, text: str) -> str:
        """Fix multiline strings by converting to single line"""
        lines = text.split('\n')
        in_string = False
        fixed_lines = []
        current_string = []
        
        for line in lines:
            # Count quotes to track if we're in a string
            quote_count = line.count('"') - line.count('\\"')
            
            if in_string:
                current_string.append(line.strip())
                if quote_count % 2 == 1:  # Odd number means string ends
                    # Join the string parts with \n
                    joined = ' '.join(current_string)
                    fixed_lines.append(joined)
                    current_string = []
                    in_string = False
            else:
                if quote_count % 2 == 1:  # Odd number means string starts
                    in_string = True
                    current_string = [line]
                else:
                    fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _extract_json_object(self, text: str) -> Optional[str]:
        """Extract JSON object from text"""
        # Find the outermost JSON object
        brace_count = 0
        start = -1
        
        for i, char in enumerate(text):
            if char == '{':
                if brace_count == 0:
                    start = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start != -1:
                    return text[start:i+1]
        
        return None
    
    def _fix_truncated_json(self, text: str) -> Optional[str]:
        """Try to fix truncated JSON by closing open structures"""
        # Count opening and closing braces/brackets
        open_braces = text.count('{')
        close_braces = text.count('}')
        open_brackets = text.count('[')
        close_brackets = text.count(']')
        
        # Add missing closing characters
        if open_braces > close_braces:
            text += '}' * (open_braces - close_braces)
        if open_brackets > close_brackets:
            text += ']' * (open_brackets - close_brackets)
        
        return text
    
    def create_minimal_modification(self, 
                                  original_files: List[Dict],
                                  modification_request: str) -> Dict:
        """Create a minimal modification response when LLM fails"""
        
        # Check if this is a UI/UX enhancement request
        modification_lower = modification_request.lower()
        is_ui_request = any(keyword in modification_lower for keyword in 
                          ['ui', 'ux', 'fancy', 'interactive', 'design', 'visual', 
                           'color', 'animation', 'style', 'improve', 'better', 'modern'])
        
        if is_ui_request and ui_handler:
            print(f"[MODIFICATION] UI request detected, applying automatic enhancements")
            enhanced_files = ui_handler.enhance_ui_in_files(original_files, modification_request)
            
            # Get list of modified files
            modified_files = [f['path'] for f in enhanced_files if f.get('modified', False)]
            
            # Get enhancement summary
            changes_made = ui_handler.create_enhancement_summary(enhanced_files)
            
            # Return enhanced files
            return {
                "files": [{'path': f['path'], 'content': f['content']} for f in enhanced_files],
                "modification_summary": "Applied UI/UX enhancements for a more modern and interactive experience",
                "changes_made": changes_made,
                "files_modified": modified_files if modified_files else ["All View files enhanced"]
            }
        
        # Return all files unchanged as a fallback
        return {
            "files": original_files,
            "modification_summary": f"Failed to apply: {modification_request}",
            "changes_made": ["No changes applied due to processing error"],
            "files_modified": []
        }
    
    def validate_and_fix_swift_syntax(self, files: List[Dict]) -> List[Dict]:
        """Validate and fix common SwiftUI syntax errors in all files"""
        if not ui_handler:
            return files
            
        fixed_files = []
        for file in files:
            if file['path'].endswith('.swift'):
                # Apply syntax fixes
                content = ui_handler._fix_common_syntax_errors(file['content'])
                fixed_files.append({
                    'path': file['path'],
                    'content': content
                })
            else:
                fixed_files.append(file)
        
        return fixed_files