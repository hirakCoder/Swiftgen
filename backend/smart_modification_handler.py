"""
Smart Modification Handler for SwiftGen
Handles intelligent context management and modification tracking
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib
from collections import defaultdict

class SmartModificationHandler:
    """Handles modifications with intelligent context management"""
    
    MAX_CONTEXT_SIZE = 20 * 1024  # 20KB limit for context
    
    def __init__(self):
        self.modification_history = defaultdict(list)
        self.issue_patterns = {
            'ssl_error': ['ssl', 'certificate', 'transport security', 'cleartext', 'https failed'],
            'crash': ['crash', 'crashed', 'freezing', 'not responding'],
            'api_error': ['api', 'network', 'failed to fetch', 'connection refused'],
            'ui_bug': ['button not working', 'ui broken', 'layout issue', 'display problem']
        }
    
    def prepare_modification_context(self, files: List[Dict[str, str]], modification: str) -> Dict[str, Any]:
        """Prepare context for modification with intelligent selection"""
        print(f"[SMART MOD] Preparing context for: {modification[:100]}...")
        
        # Analyze modification to determine relevant files
        relevant_files = self._select_relevant_files(files, modification)
        
        # Build context within size limit
        context = {
            'modification': modification,
            'files': [],
            'total_size': 0,
            'truncated': False
        }
        
        for file_info in relevant_files:
            file_size = len(file_info.get('content', ''))
            
            if context['total_size'] + file_size > self.MAX_CONTEXT_SIZE:
                # Truncate or summarize large files
                truncated_content = self._truncate_content(
                    file_info['content'], 
                    self.MAX_CONTEXT_SIZE - context['total_size']
                )
                
                context['files'].append({
                    'name': file_info['name'],
                    'content': truncated_content,
                    'truncated': True
                })
                context['truncated'] = True
                break
            else:
                context['files'].append({
                    'name': file_info['name'],
                    'content': file_info['content'],
                    'truncated': False
                })
                context['total_size'] += file_size
        
        print(f"[SMART MOD] Context prepared: {len(context['files'])} files, {context['total_size']} bytes")
        return context
    
    def _select_relevant_files(self, files: List[Dict[str, str]], modification: str) -> List[Dict[str, str]]:
        """Select files most relevant to the modification"""
        modification_lower = modification.lower()
        
        # Score files based on relevance
        scored_files = []
        
        for file_info in files:
            score = 0
            file_name = file_info.get('name', '').lower()
            content_preview = file_info.get('content', '')[:1000].lower()
            
            # Check file name relevance
            if 'contentview' in file_name and 'view' in modification_lower:
                score += 10
            if 'model' in file_name and any(word in modification_lower for word in ['data', 'model', 'state']):
                score += 8
            if 'app' in file_name and file_name.endswith('app.swift'):
                score += 5  # Always somewhat relevant
            
            # Check content relevance
            mod_keywords = modification_lower.split()
            for keyword in mod_keywords:
                if len(keyword) > 3:  # Skip short words
                    if keyword in content_preview:
                        score += 2
            
            # Check for UI-related modifications
            if any(ui_word in modification_lower for ui_word in ['button', 'text', 'color', 'view', 'ui', 'display']):
                if any(ui_element in content_preview for ui_element in ['button', 'text', 'vstack', 'hstack', 'view']):
                    score += 3
            
            if score > 0:
                scored_files.append((score, file_info))
        
        # Sort by score and return top files
        scored_files.sort(key=lambda x: x[0], reverse=True)
        
        # Always include main app file if it exists
        main_app_file = next((f for f in files if f.get('name', '').endswith('App.swift')), None)
        relevant = [f[1] for f in scored_files[:5]]  # Top 5 most relevant
        
        if main_app_file and main_app_file not in relevant:
            relevant.append(main_app_file)
        
        return relevant
    
    def _truncate_content(self, content: str, max_size: int) -> str:
        """Intelligently truncate content to fit size limit"""
        if len(content) <= max_size:
            return content
        
        # Try to truncate at a reasonable boundary
        truncated = content[:max_size]
        
        # Find last complete function or struct
        last_brace = truncated.rfind('}')
        if last_brace > max_size * 0.7:  # If we have at least 70% of content
            truncated = truncated[:last_brace + 1]
        
        return truncated + "\n// ... (truncated for context limit)"
    
    def detect_and_handle_issue(self, modification: str, project_path: str) -> Dict[str, Any]:
        """Detect if the modification is an issue report (SSL, crash, etc.)"""
        modification_lower = modification.lower()
        
        for issue_type, keywords in self.issue_patterns.items():
            if any(keyword in modification_lower for keyword in keywords):
                print(f"[SMART MOD] Detected {issue_type} issue")
                return {
                    'is_issue': True,
                    'issue_type': issue_type,
                    'suggested_action': self._get_issue_solution(issue_type, modification)
                }
        
        return {'is_issue': False}
    
    def _get_issue_solution(self, issue_type: str, modification: str) -> str:
        """Get suggested solution for detected issue"""
        solutions = {
            'ssl_error': "Add NSAppTransportSecurity settings to Info.plist for HTTP connections or implement proper HTTPS",
            'crash': "Add error handling and optional unwrapping for potential nil values",
            'api_error': "Implement proper network error handling and retry logic",
            'ui_bug': "Review SwiftUI view hierarchy and state management"
        }
        
        return solutions.get(issue_type, "Review and fix the reported issue")
    
    def validate_and_fix_swift_syntax(self, content: str) -> Tuple[str, List[str]]:
        """Validate and fix common SwiftUI syntax issues"""
        fixes_applied = []
        
        # Fix 1: NavigationView deprecation
        if '@main' in content and 'NavigationView' in content:
            content = content.replace('NavigationView {', 'NavigationStack {')
            fixes_applied.append("Updated NavigationView to NavigationStack (iOS 16+)")
        
        # Fix 2: Dismiss pattern
        if 'dismiss()' in content and '@Environment(\\.presentationMode)' in content:
            old_pattern = r'@Environment\(\\\.presentationMode\)\s+var\s+\w+:\s*Binding<PresentationMode>'
            new_pattern = '@Environment(\\.dismiss) var dismiss'
            if re.search(old_pattern, content):
                content = re.sub(old_pattern, new_pattern, content)
                
                # Also fix the dismiss call
                content = re.sub(r'(\w+)\.wrappedValue\.dismiss\(\)', 'dismiss()', content)
                fixes_applied.append("Updated dismiss pattern to iOS 15+ syntax")
        
        # Fix 3: Remove trailing commas in parameter lists
        content = re.sub(r',(\s*)\)', r'\1)', content)
        
        # Fix 4: Fix multiline string literals
        content = re.sub(r'"""(\s*\n)?([^"]*?)"""', lambda m: '"""' + m.group(2) + '"""', content)
        
        return content, fixes_applied
    
    def track_modification_outcome(self, project_id: str, modification: str, success: bool, details: Dict[str, Any] = None):
        """Track modification history for learning"""
        self.modification_history[project_id].append({
            'timestamp': datetime.now().isoformat(),
            'modification': modification[:200],  # Truncate for storage
            'success': success,
            'details': details or {},
            'hash': hashlib.md5(modification.encode()).hexdigest()
        })
        
        # Keep only last 10 modifications per project
        if len(self.modification_history[project_id]) > 10:
            self.modification_history[project_id] = self.modification_history[project_id][-10:]
    
    def _generate_issue_key(self, issue_type: str, description: str) -> str:
        """Generate a unique key for an issue"""
        # Create a hash of the issue type and key parts of the description
        key_parts = [issue_type]
        
        # Extract key identifiers from the description
        if 'ssl' in issue_type:
            # Look for domain names or URLs
            url_pattern = r'https?://[^\s]+'
            urls = re.findall(url_pattern, description)
            key_parts.extend(urls[:2])  # Max 2 URLs
        
        # Create hash
        key_string = '|'.join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()[:8]
    
    def get_modification_suggestions(self, project_id: str, current_modification: str) -> List[str]:
        """Get suggestions based on modification history"""
        suggestions = []
        
        # Check if similar modifications were successful before
        if project_id in self.modification_history:
            successful_mods = [
                m for m in self.modification_history[project_id] 
                if m['success']
            ]
            
            # Simple similarity check (can be enhanced with better NLP)
            current_words = set(current_modification.lower().split())
            for mod in successful_mods:
                past_words = set(mod['modification'].lower().split())
                similarity = len(current_words & past_words) / max(len(current_words), len(past_words))
                
                if similarity > 0.5:
                    suggestions.append(f"Similar successful modification: {mod['modification']}")
        
        return suggestions[:3]  # Return top 3 suggestions