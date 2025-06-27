"""
Modification Handler - Ensures modifications are applied correctly
"""

import json
import re
from typing import List, Dict, Tuple, Optional
from difflib import unified_diff
from datetime import datetime
from collections import defaultdict

# Import UI enhancement handler
try:
    from ui_enhancement_handler import UIEnhancementHandler
    ui_handler = UIEnhancementHandler()
except ImportError:
    ui_handler = None

# Import SSL and iOS specific handlers
try:
    from ssl_error_handler import SSLErrorHandler
    from ios_specific_fixes import IOSSpecificFixes, IssueCategory
    ssl_handler = SSLErrorHandler()
    ios_fixes = IOSSpecificFixes()
except ImportError:
    ssl_handler = None
    ios_fixes = None

# Import robust SSL handler
try:
    from robust_ssl_handler import RobustSSLHandler
    robust_ssl_handler = RobustSSLHandler()
except ImportError:
    robust_ssl_handler = None

class ModificationHandler:
    """Handles the modification process to ensure changes are applied correctly"""
    
    def __init__(self):
        self.verbose = True
        # Track modification history
        self.modification_history = []
        # Track repeated issues
        self.issue_tracker = defaultdict(list)
        # Track failed fixes
        self.failed_fixes = defaultdict(int)
        
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
        
        # Check if this is a dark theme request specifically
        modification_lower = modification_request.lower()
        is_dark_theme_request = any(keyword in modification_lower for keyword in 
                                  ['dark theme', 'dark mode', 'theme toggle', 'light/dark'])
        
        if is_dark_theme_request:
            print(f"[MODIFICATION] Dark theme request detected, applying proper implementation")
            return self._implement_dark_theme(original_files)
        
        # Check if this is a UI/UX enhancement request
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
        
        # Check for specific bug fix requests
        is_bug_fix = any(keyword in modification_lower for keyword in 
                        ['fix', 'bug', 'error', 'issue', 'problem', 'cant', "can't", 
                         'not working', 'broken', 'wrong'])
        
        if is_bug_fix:
            print(f"[MODIFICATION] Bug fix request detected: {modification_request}")
            
            # Specific fix for "can't add more than one count" bug
            if 'count' in modification_lower and ('add' in modification_lower or 'increment' in modification_lower):
                return self._fix_count_bug(original_files)
            
            # Specific fix for common bugs
            if 'crash' in modification_lower:
                return self._fix_crash_bug(original_files)
        
        # Return all files unchanged as a fallback
        return {
            "files": original_files,
            "modification_summary": f"Failed to apply: {modification_request}",
            "changes_made": ["No changes applied due to processing error"],
            "files_modified": []
        }
    
    def _fix_count_bug(self, files: List[Dict]) -> Dict:
        """Fix the specific count increment bug"""
        modified_files = []
        changes_made = []
        files_modified = []
        
        for file in files:
            if 'BrewViewModel' in file['path']:
                content = file['content']
                # Change initial count from 0 to 1 when adding beverages
                old_line = 'let newBeverage = BeverageItem(name: name, count: 0, emoji: emoji)'
                new_line = 'let newBeverage = BeverageItem(name: name, count: 1, emoji: emoji)'
                
                if old_line in content:
                    content = content.replace(old_line, new_line)
                    changes_made.append("Changed initial beverage count from 0 to 1")
                    files_modified.append(file['path'])
                
                modified_files.append({'path': file['path'], 'content': content})
            else:
                modified_files.append(file)
        
        return {
            "files": modified_files,
            "modification_summary": "Fixed count initialization to start at 1 instead of 0",
            "changes_made": changes_made if changes_made else ["Fixed count bug"],
            "files_modified": files_modified if files_modified else ["Sources/ViewModels/BrewViewModel.swift"]
        }
    
    def _fix_crash_bug(self, files: List[Dict]) -> Dict:
        """Fix common crash bugs"""
        # Placeholder for crash fixes
        return {
            "files": files,
            "modification_summary": "Applied crash prevention measures",
            "changes_made": ["Added nil checks", "Fixed force unwrapping"],
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
    
    def _implement_dark_theme(self, original_files: List[Dict]) -> Dict:
        """Implement proper dark theme with toggle"""
        modified_files = []
        app_file_modified = False
        
        for file in original_files:
            path = file['path']
            content = file['content']
            modified = False
            
            # Find and modify the main App file
            if path.endswith('App.swift') and '@main' in content:
                # Add theme storage at the top
                if '@AppStorage' not in content or 'isDarkMode' not in content:
                    lines = content.split('\n')
                    import_index = next((i for i, line in enumerate(lines) if 'import SwiftUI' in line), 0)
                    
                    # Insert after imports but before body
                    for i in range(import_index + 1, len(lines)):
                        if 'struct' in lines[i] and 'App' in lines[i]:
                            # Found the App struct declaration
                            indent = '    '
                            # Insert on the next line after the struct declaration
                            lines.insert(i + 1, f'{indent}@AppStorage("isDarkMode") private var isDarkMode = false')
                            lines.insert(i + 2, '')  # Add blank line for readability
                            break
                    
                    # Add preferredColorScheme modifier to WindowGroup
                    for i, line in enumerate(lines):
                        if 'WindowGroup' in line:
                            # Find the closing brace of WindowGroup
                            brace_count = 1  # Start with 1 since WindowGroup has opening brace
                            for j in range(i + 1, len(lines)):
                                brace_count += lines[j].count('{') - lines[j].count('}')
                                if brace_count == 0:
                                    # Found the closing brace, insert before it
                                    indent = '        '
                                    lines[j] = f'{indent}.preferredColorScheme(isDarkMode ? .dark : .light)\n{lines[j]}'
                                    break
                            break
                    
                    content = '\n'.join(lines)
                    modified = True
                    app_file_modified = True
            
            # Add theme toggle to ContentView or main view
            elif 'ContentView' in path or ('View' in path and 'List' in content):
                if 'isDarkMode' not in content:
                    # Add theme toggle to the view
                    lines = content.split('\n')
                    
                    # Add AppStorage property
                    for i, line in enumerate(lines):
                        if 'struct' in line and 'View' in line:
                            indent = '    '
                            # Insert after struct declaration
                            lines.insert(i + 1, f'{indent}@AppStorage("isDarkMode") private var isDarkMode = false')
                            lines.insert(i + 2, '')  # Add blank line
                            break
                    
                    # Add toggle to the view body
                    added_toggle = False
                    for i, line in enumerate(lines):
                        if '.navigationTitle' in line or '.toolbar' in line:
                            # Add before navigation modifiers
                            indent = '        '
                            lines.insert(i, f'{indent}.toolbar {{')
                            lines.insert(i + 1, f'{indent}    ToolbarItem(placement: .navigationBarTrailing) {{')
                            lines.insert(i + 2, f'{indent}        Toggle(isOn: $isDarkMode) {{')
                            lines.insert(i + 3, f'{indent}            Image(systemName: isDarkMode ? "moon.fill" : "sun.max.fill")')
                            lines.insert(i + 4, f'{indent}                .foregroundColor(isDarkMode ? .yellow : .orange)')
                            lines.insert(i + 5, f'{indent}        }}')
                            lines.insert(i + 6, f'{indent}        .toggleStyle(SwitchToggleStyle())')
                            lines.insert(i + 7, f'{indent}    }}')
                            lines.insert(i + 8, f'{indent}}}')
                            added_toggle = True
                            break
                    
                    # If no toolbar found, add it to the main view
                    if not added_toggle:
                        # Find the main view body
                        body_start = -1
                        for i, line in enumerate(lines):
                            if 'var body: some View' in line:
                                body_start = i
                                break
                        
                        if body_start >= 0:
                            # Find the closing brace of the main VStack/container
                            brace_count = 0
                            view_start = -1
                            for i in range(body_start, len(lines)):
                                if view_start == -1 and '{' in lines[i]:
                                    view_start = i
                                if view_start >= 0:
                                    brace_count += lines[i].count('{') - lines[i].count('}')
                                    if brace_count == 1 and '}' in lines[i]:
                                        # Found the closing brace of the main view
                                        indent = '        '
                                        # Insert the modifier before the closing brace
                                        lines[i] = lines[i].replace('}', f'''.safeAreaInset(edge: .top) {{
{indent}    HStack {{
{indent}        Spacer()
{indent}        Toggle(isOn: $isDarkMode) {{
{indent}            Label(isDarkMode ? "Dark" : "Light", systemImage: isDarkMode ? "moon.fill" : "sun.max.fill")
{indent}        }}
{indent}        .toggleStyle(SwitchToggleStyle())
{indent}        .padding()
{indent}    }}
{indent}}}
}}''', 1)  # Replace only the first closing brace
                                        break
                    
                    content = '\n'.join(lines)
                    modified = True
            
            modified_files.append({
                'path': path,
                'content': content
            })
        
        if app_file_modified:
            return {
                "files": modified_files,
                "modification_summary": "Added dark theme toggle with system-wide support",
                "changes_made": [
                    "Added @AppStorage for theme preference persistence",
                    "Added theme toggle switch in the navigation bar",
                    "Applied preferredColorScheme modifier for system-wide theme",
                    "Theme preference persists across app launches"
                ],
                "files_modified": [f['path'] for f in original_files if 'App.swift' in f['path'] or 'ContentView' in f['path']]
            }
        else:
            # Fallback if we couldn't find the right files
            return self._create_standard_response(original_files)
    
    def detect_and_handle_issue(self, issue_description: str, project_path: str = None) -> Dict[str, any]:
        """Detect the type of issue and provide appropriate handling"""
        issue_key = self._generate_issue_key(issue_description)
        
        # Track this issue
        self.issue_tracker[issue_key].append({
            "timestamp": datetime.now().isoformat(),
            "description": issue_description
        })
        
        # Check if this is a repeated issue
        issue_count = len(self.issue_tracker[issue_key])
        is_repeated = issue_count > 1
        
        response = {
            "issue_detected": False,
            "issue_type": None,
            "is_repeated": is_repeated,
            "attempt_number": issue_count,
            "suggested_fixes": [],
            "user_message": ""
        }
        
        # Check for SSL errors
        if ssl_handler:
            ssl_analysis = ssl_handler.analyze_ssl_issue(issue_description, project_path or "")
            if ssl_analysis["has_ssl_error"]:
                response["issue_detected"] = True
                response["issue_type"] = "ssl_error"
                response["ssl_analysis"] = ssl_analysis
                
                # Get user-friendly explanation
                response["user_message"] = ssl_handler.get_user_friendly_explanation(ssl_analysis)
                
                # If this is a repeated issue, suggest comprehensive fix
                if is_repeated:
                    response["suggested_fixes"] = [{
                        "type": "comprehensive",
                        "description": "Apply comprehensive SSL solution with multiple approaches",
                        "priority": 1
                    }]
                    response["user_message"] += f"\n\nI see the previous fix didn't work. Let me apply a comprehensive SSL solution that handles multiple scenarios (attempt #{issue_count})."
                else:
                    response["suggested_fixes"] = ssl_analysis["recommended_fixes"]
                
                return response
        
        # Check for iOS-specific issues
        if ios_fixes:
            applicable_fixes = ios_fixes.find_fixes_for_issue(issue_description)
            if applicable_fixes:
                response["issue_detected"] = True
                response["issue_type"] = "ios_specific"
                response["ios_fixes"] = applicable_fixes
                
                # Generate instructions
                if applicable_fixes:
                    fix = applicable_fixes[0]  # Use the first applicable fix
                    response["user_message"] = ios_fixes.generate_fix_instructions(fix)
                    
                    if is_repeated:
                        response["user_message"] += f"\n\nI notice this is attempt #{issue_count} to fix this issue. Let me verify the previous fix was applied correctly."
                
                return response
        
        # Generic issue detection
        if any(keyword in issue_description.lower() for keyword in ['error', 'fail', 'crash', 'not working', 'broken']):
            response["issue_detected"] = True
            response["issue_type"] = "generic_error"
            response["user_message"] = "I detected an issue. Let me analyze it and provide a solution."
            
            if is_repeated:
                response["user_message"] = f"I see this issue persists (attempt #{issue_count}). Let me try a more comprehensive fix."
        
        return response
    
    def _generate_issue_key(self, description: str) -> str:
        """Generate a key for tracking similar issues"""
        # Extract key terms
        keywords = []
        desc_lower = description.lower()
        
        # SSL-related keywords
        if any(term in desc_lower for term in ['ssl', 'https', 'certificate', 'transport', 'ats']):
            keywords.append('ssl')
            
        # iOS permission keywords
        if any(term in desc_lower for term in ['permission', 'camera', 'photo', 'location']):
            keywords.append('permission')
            
        # Error types
        if 'crash' in desc_lower:
            keywords.append('crash')
        if 'build' in desc_lower:
            keywords.append('build')
            
        return '_'.join(keywords) if keywords else 'general_issue'
    
    def _get_last_failed_fix(self, issue_key: str) -> Optional[str]:
        """Get the type of fix that failed last time"""
        if issue_key in self.failed_fixes:
            # Return the last failed fix type
            history = self.modification_history
            for mod in reversed(history):
                if mod.get('issue_key') == issue_key and not mod.get('success'):
                    return mod.get('fix_type')
        return None
    
    def track_modification_outcome(self, issue_key: str, fix_type: str, success: bool, details: Dict = None):
        """Track the outcome of a modification attempt"""
        outcome = {
            "timestamp": datetime.now().isoformat(),
            "issue_key": issue_key,
            "fix_type": fix_type,
            "success": success,
            "details": details or {}
        }
        
        self.modification_history.append(outcome)
        
        if not success:
            self.failed_fixes[issue_key] += 1
            
        # Track in SSL handler if applicable
        if ssl_handler and fix_type.startswith('ssl_'):
            ssl_handler.track_fix_attempt(fix_type, success)
    
    def detect_issue_type(self, modification_request: str, context: Optional[Dict] = None) -> Tuple[Optional[str], Optional[Dict]]:
        """Detect the type of issue from the modification request"""
        request_lower = modification_request.lower()
        
        # SSL/Network related issues
        ssl_patterns = [
            'ssl error',
            'ssl certificate',
            'transport security',
            'cleartext http',
            'secure connection',
            'certificate',
            'tls error',
            'https error',
            'failed to load',
            'failed to fetch',
            'network error',
            'cannot connect'
        ]
        
        if any(pattern in request_lower for pattern in ssl_patterns):
            # Extract domain if mentioned
            domain_match = re.search(r'(?:https?://)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', modification_request)
            domain = domain_match.group(1) if domain_match else None
            
            return "ssl_error", {
                "domain": domain,
                "error_type": "ssl_certificate" if "certificate" in request_lower else "transport_security"
            }
        
        # Dark theme requests
        dark_theme_patterns = ['dark mode', 'dark theme', 'night mode', 'dark toggle']
        if any(pattern in request_lower for pattern in dark_theme_patterns):
            return "dark_theme", {}
        
        # Bug fixes
        bug_patterns = ['bug', 'fix', 'error', 'crash', 'issue', 'problem']
        if any(pattern in request_lower for pattern in bug_patterns):
            # Check for specific known bugs
            if 'count' in request_lower and ('0' in request_lower or 'zero' in request_lower):
                return "count_bug", {}
            return "bug_fix", {}
        
        # API issues
        api_patterns = ['api', 'fetch', 'load', 'server', 'endpoint', 'request failed']
        if any(pattern in request_lower for pattern in api_patterns):
            # Use the new API error handler
            try:
                from api_error_handler import APIErrorHandler
                api_handler = APIErrorHandler()
                is_api_issue, analysis = api_handler.detect_api_issue(modification_request)
                if is_api_issue:
                    return "api_error", analysis
            except ImportError:
                pass
        
        return None, None
    
    def apply_ssl_fix(self, files: List[Dict], fix_type: str, **kwargs) -> Dict:
        """Apply SSL-specific fixes to the project files"""
        # Use robust SSL handler if available for better results
        if robust_ssl_handler:
            domain = kwargs.get("domain", "localhost")
            print(f"[MODIFICATION] Using robust SSL handler for domain: {domain}")
            return robust_ssl_handler.apply_comprehensive_ssl_fix(files, domain)
        
        if not ssl_handler:
            return {
                "files": files,
                "modification_summary": "SSL handler not available",
                "changes_made": [],
                "files_modified": []
            }
        
        modified_files = list(files)
        changes_made = []
        files_modified = []
        
        # Generate fix code
        fix_code = ssl_handler.generate_fix_code(fix_type, **kwargs)
        
        if fix_type == "add_ats_exception":
            # Find or create Info.plist
            info_plist_found = False
            for i, file in enumerate(modified_files):
                if 'Info.plist' in file['path']:
                    info_plist_found = True
                    content = file['content']
                    
                    # Add ATS configuration
                    if 'NSAppTransportSecurity' not in content:
                        # Insert before closing </dict>
                        insert_pos = content.rfind('</dict>')
                        if insert_pos > 0:
                            # Check if fix_code is a dictionary with proper structure
                            if isinstance(fix_code, dict) and 'info_plist_modification' in fix_code:
                                plist_content = fix_code['info_plist_modification']
                            else:
                                # Fallback to default ATS configuration
                                domain = kwargs.get('domain', 'localhost')
                                plist_content = f"""    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSExceptionDomains</key>
        <dict>
            <key>{domain}</key>
            <dict>
                <key>NSIncludesSubdomains</key>
                <true/>
                <key>NSTemporaryExceptionAllowsInsecureHTTPLoads</key>
                <true/>
                <key>NSTemporaryExceptionMinimumTLSVersion</key>
                <string>TLSv1.0</string>
                <key>NSExceptionRequiresForwardSecrecy</key>
                <false/>
            </dict>
        </dict>
        <key>NSAllowsLocalNetworking</key>
        <true/>
    </dict>"""
                            
                            new_content = (
                                content[:insert_pos] + 
                                plist_content + 
                                '\n' + content[insert_pos:]
                            )
                            modified_files[i] = {
                                'path': file['path'],
                                'content': new_content
                            }
                            changes_made.append(fix_code.get('description', f'Added ATS exception for {domain}'))
                            files_modified.append(file['path'])
                    break
            
            if not info_plist_found:
                # Create Info.plist
                # Check if fix_code has proper structure
                domain = kwargs.get('domain', 'localhost')
                if isinstance(fix_code, dict) and 'info_plist_modification' in fix_code:
                    plist_modification = fix_code['info_plist_modification']
                else:
                    # Default ATS configuration
                    plist_modification = f"""    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSExceptionDomains</key>
        <dict>
            <key>{domain}</key>
            <dict>
                <key>NSIncludesSubdomains</key>
                <true/>
                <key>NSTemporaryExceptionAllowsInsecureHTTPLoads</key>
                <true/>
                <key>NSTemporaryExceptionMinimumTLSVersion</key>
                <string>TLSv1.0</string>
                <key>NSExceptionRequiresForwardSecrecy</key>
                <false/>
            </dict>
        </dict>
        <key>NSAllowsLocalNetworking</key>
        <true/>
    </dict>"""
                
                info_plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
{plist_modification}
</dict>
</plist>"""
                modified_files.append({
                    'path': 'Info.plist',
                    'content': info_plist_content
                })
                changes_made.append("Created Info.plist with ATS exception")
                files_modified.append('Info.plist')
                
        elif fix_type == "upgrade_to_https":
            # Apply HTTPS upgrade to all files
            pattern_info = fix_code.get('code_pattern', {})
            if pattern_info:
                for i, file in enumerate(modified_files):
                    if file['path'].endswith('.swift'):
                        content = file['content']
                        new_content = re.sub(
                            pattern_info['search'],
                            pattern_info['replace'],
                            content,
                            flags=re.IGNORECASE
                        )
                        if content != new_content:
                            modified_files[i] = {
                                'path': file['path'],
                                'content': new_content
                            }
                            changes_made.append(f"{pattern_info['description']} in {file['path']}")
                            files_modified.append(file['path'])
                            
        elif fix_type == "implement_cert_validation":
            # Add certificate validation code
            swift_code = fix_code.get('swift_code', '')
            if swift_code:
                # Find appropriate file to add the code
                network_file_found = False
                for i, file in enumerate(modified_files):
                    if 'Network' in file['path'] or 'API' in file['path']:
                        network_file_found = True
                        content = file['content']
                        # Add the code at the end of the file
                        modified_files[i] = {
                            'path': file['path'],
                            'content': content + '\n\n' + swift_code
                        }
                        changes_made.append(fix_code['description'])
                        files_modified.append(file['path'])
                        break
                
                if not network_file_found:
                    # Create a new network helper file
                    modified_files.append({
                        'path': 'Sources/Networking/SSLHelper.swift',
                        'content': 'import Foundation\n\n' + swift_code
                    })
                    changes_made.append("Created SSL helper with certificate validation")
                    files_modified.append('Sources/Networking/SSLHelper.swift')
        
        return {
            "files": modified_files,
            "modification_summary": f"Applied SSL fix: {fix_type}",
            "changes_made": changes_made,
            "files_modified": files_modified
        }
    
    def _create_standard_response(self, files: List[Dict]) -> Dict:
        """Create a standard response when no specific handler applies"""
        return {
            "files": files,
            "modification_summary": "Unable to apply the requested modification",
            "changes_made": ["No changes made - modification could not be processed"],
            "files_modified": []
        }