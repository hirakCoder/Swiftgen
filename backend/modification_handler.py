"""
Modification Handler - Ensures modifications are applied correctly
"""

import json
import re
from typing import List, Dict, Tuple, Optional
from difflib import unified_diff

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
        ui_keywords = ['color', 'background', 'button', 'text', 'view', 'ui', 'interface', 'display', 'show']
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
        if len(response_files) != len(original_files):
            issues.append(f"Expected {len(original_files)} files, got {len(response_files)}")
        
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
        
        # Check 3: Verify files_modified matches actual changes
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
        # Replace invalid escapes with valid ones
        text = text.replace('\\n', '\\\\n')
        text = text.replace('\\t', '\\\\t')
        text = text.replace('\\"', '\\\\"')
        
        # Handle actual newlines in strings
        # This is a complex regex that finds strings and fixes their content
        def fix_string_content(match):
            content = match.group(1)
            # Replace actual newlines with \n
            content = content.replace('\n', '\\n')
            content = content.replace('\t', '\\t')
            return f'"{content}"'
        
        # Find strings and fix them
        text = re.sub(r'"([^"]*)"', fix_string_content, text)
        
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
        
        # Return all files unchanged as a fallback
        return {
            "files": original_files,
            "modification_summary": f"Failed to apply: {modification_request}",
            "changes_made": ["No changes applied due to processing error"],
            "files_modified": []
        }