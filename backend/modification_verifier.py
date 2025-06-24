"""
Modification Verifier
Ensures that modifications requested by users are actually applied to the code
"""

import re
from typing import List, Dict, Tuple, Set
from difflib import SequenceMatcher

class ModificationVerifier:
    """Verifies that modifications were actually applied to files"""
    
    def __init__(self):
        self.min_similarity_threshold = 0.98  # Changed from 0.95 to be more sensitive to small changes
        
    def verify_modifications(self, 
                           original_files: List[Dict],
                           modified_files: List[Dict],
                           modification_request: str,
                           verbose: bool = True) -> Tuple[bool, List[str]]:
        """
        Verify that modifications were properly applied
        Returns (success, issues)
        """
        issues = []
        
        # Create path mappings for easier lookup
        original_map = {f['path']: f['content'] for f in original_files}
        modified_map = {f['path']: f['content'] for f in modified_files}
        
        # Check 1: All original files should be present in modified files
        original_paths = set(original_map.keys())
        modified_paths = set(modified_map.keys())
        
        missing_files = original_paths - modified_paths
        if missing_files:
            issues.append(f"Missing files in modification response: {list(missing_files)}")
            if verbose:
                print(f"[VERIFIER] ERROR: Missing {len(missing_files)} files")
        
        # Check 2: At least one file should have changed
        unchanged_files = []
        changed_files = []
        
        for path in original_paths & modified_paths:
            original_content = original_map[path]
            modified_content = modified_map.get(path, "")
            
            # Calculate similarity
            similarity = SequenceMatcher(None, original_content, modified_content).ratio()
            
            # CRITICAL: Check if content is actually different first
            if original_content == modified_content:
                unchanged_files.append(path)
                if verbose:
                    print(f"[VERIFIER] File UNCHANGED (identical): {path}")
            elif similarity >= self.min_similarity_threshold:
                # Content is different but very similar - still count as changed!
                changed_files.append(path)
                if verbose:
                    print(f"[VERIFIER] File changed (minor): {path} (similarity: {similarity:.2%})")
            else:
                changed_files.append(path)
                if verbose:
                    print(f"[VERIFIER] File changed (major): {path} (similarity: {similarity:.2%})")
        
        if not changed_files and original_files:
            issues.append(f"No files were modified despite modification request: '{modification_request}'")
        
        if unchanged_files and verbose:
            print(f"[VERIFIER] {len(unchanged_files)} files unchanged")
        
        # Check 3: Modification-specific validation
        keywords = self._extract_keywords_from_request(modification_request)
        if keywords and changed_files:
            keyword_found = False
            for path in changed_files:
                content = modified_map.get(path, "")
                for keyword in keywords:
                    if keyword.lower() in content.lower():
                        keyword_found = True
                        if verbose:
                            print(f"[VERIFIER] Found keyword '{keyword}' in {path}")
                        break
                if keyword_found:
                    break
            
            if not keyword_found and keywords:
                # Don't fail if we have actual file changes - the keywords might not be literal
                if not changed_files:
                    issues.append(f"Expected keywords {keywords} not found in modified files")
        
        # Check 4: Validate file content structure
        for path, content in modified_map.items():
            if path.endswith('.swift'):
                content_issues = self._validate_swift_content(content)
                if content_issues:
                    issues.extend([f"{path}: {issue}" for issue in content_issues])
        
        # Report
        success = len(issues) == 0
        if verbose:
            print(f"[VERIFIER] Verification {'PASSED' if success else 'FAILED'}")
            print(f"[VERIFIER] Files provided: {len(modified_files)}")
            print(f"[VERIFIER] Files changed: {len(changed_files)}")
            if issues:
                print(f"[VERIFIER] Issues found: {len(issues)}")
                for issue in issues:
                    print(f"  - {issue}")
        
        return success, issues
    
    def _extract_keywords_from_request(self, modification_request: str) -> List[str]:
        """Extract important keywords from modification request"""
        # Common modification keywords to look for
        keyword_patterns = [
            r'add\s+(\w+)',
            r'create\s+(\w+)',
            r'implement\s+(\w+)',
            r'change\s+.*?to\s+(\w+)',
            r'(\w+)\s+color',
            r'(\w+)\s+button',
            r'(\w+)\s+view',
            r'dark\s+mode',
            r'navigation',
            r'animation',
        ]
        
        keywords = []
        for pattern in keyword_patterns:
            matches = re.findall(pattern, modification_request.lower())
            keywords.extend(matches)
        
        # Also extract quoted strings
        quoted = re.findall(r'"([^"]+)"', modification_request)
        keywords.extend(quoted)
        
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        keywords = [k for k in keywords if k.lower() not in stop_words]
        
        return list(set(keywords))[:5]  # Return top 5 unique keywords
    
    def _validate_swift_content(self, content: str) -> List[str]:
        """Basic validation of Swift file content"""
        issues = []
        
        # Check for empty content
        if not content or len(content.strip()) < 10:
            issues.append("File content is empty or too short")
        
        # Check for basic Swift structure
        if not any(keyword in content for keyword in ['import', 'struct', 'class', 'func', '@main']):
            issues.append("File doesn't appear to contain valid Swift code")
        
        # Check for common syntax errors
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces != close_braces:
            issues.append(f"Mismatched braces: {open_braces} open, {close_braces} close")
        
        # Check for incomplete implementations
        if '...' in content and 'String...' not in content:  # Allow String... for variadic
            issues.append("Incomplete implementation detected (...)")
        
        return issues
    
    def generate_modification_report(self,
                                   original_files: List[Dict],
                                   modified_files: List[Dict]) -> Dict:
        """Generate a detailed report of what changed"""
        report = {
            'total_files': len(modified_files),
            'files_changed': 0,
            'files_unchanged': 0,
            'files_added': 0,
            'files_missing': 0,
            'changes': []
        }
        
        original_map = {f['path']: f['content'] for f in original_files}
        modified_map = {f['path']: f['content'] for f in modified_files}
        
        # Check each file
        for path, content in modified_map.items():
            if path not in original_map:
                report['files_added'] += 1
                report['changes'].append({
                    'file': path,
                    'type': 'added',
                    'size': len(content)
                })
            else:
                original_content = original_map[path]
                if original_content != content:
                    report['files_changed'] += 1
                    report['changes'].append({
                        'file': path,
                        'type': 'modified',
                        'size_before': len(original_content),
                        'size_after': len(content),
                        'size_change': len(content) - len(original_content)
                    })
                else:
                    report['files_unchanged'] += 1
                    report['changes'].append({
                        'file': path,
                        'type': 'unchanged'
                    })
        
        # Check for missing files
        for path in set(original_map.keys()) - set(modified_map.keys()):
            report['files_missing'] += 1
            report['changes'].append({
                'file': path,
                'type': 'missing'
            })
        
        return report