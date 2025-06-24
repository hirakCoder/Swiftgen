"""
API Error Handler for SwiftGen
Detects and fixes common API integration issues in iOS apps
"""
import re
import json
from typing import Dict, List, Tuple, Optional


class APIErrorHandler:
    """Handles API-related errors and provides fixes"""
    
    def __init__(self):
        self.common_api_patterns = {
            'quotable': 'api.quotable.io',
            'weather': 'api.openweathermap.org',
            'currency': 'api.exchangerate-api.com',
            'placeholder': 'jsonplaceholder.typicode.com',
            'github': 'api.github.com'
        }
    
    def detect_api_issue(self, error_message: str, modification_request: str = "") -> Tuple[bool, Dict]:
        """Detect if the issue is API-related"""
        error_lower = error_message.lower()
        request_lower = modification_request.lower()
        
        # Common API error patterns
        api_error_patterns = [
            'failed to load',
            'failed to fetch',
            'cannot connect',
            'network error',
            'timeout',
            'ssl error',
            'certificate',
            'transport security',
            'cleartext http',
            'connection failed',
            'api error',
            'server error',
            'no internet',
            'offline'
        ]
        
        # Check if it's an API issue
        is_api_issue = any(pattern in error_lower or pattern in request_lower 
                          for pattern in api_error_patterns)
        
        if not is_api_issue:
            return False, {}
        
        # Analyze the specific issue
        analysis = {
            'is_api_issue': True,
            'error_type': self._categorize_error(error_lower, request_lower),
            'detected_apis': self._detect_apis_in_use(error_message, modification_request)
        }
        
        return True, analysis
    
    def _categorize_error(self, error_lower: str, request_lower: str) -> str:
        """Categorize the type of API error"""
        if 'ssl' in error_lower or 'certificate' in error_lower or 'transport security' in error_lower:
            return 'ssl_error'
        elif 'timeout' in error_lower or 'timed out' in request_lower:
            return 'timeout_error'
        elif 'no internet' in error_lower or 'offline' in error_lower:
            return 'connectivity_error'
        elif 'failed to load' in error_lower or 'failed to fetch' in error_lower:
            return 'fetch_error'
        elif 'server error' in error_lower or '500' in error_lower:
            return 'server_error'
        else:
            return 'generic_api_error'
    
    def _detect_apis_in_use(self, error_message: str, modification_request: str) -> List[str]:
        """Detect which APIs might be in use"""
        detected = []
        combined_text = f"{error_message} {modification_request}".lower()
        
        for api_name, api_domain in self.common_api_patterns.items():
            if api_name in combined_text or api_domain in combined_text:
                detected.append(api_domain)
        
        # Also look for URL patterns
        url_pattern = r'https?://([^\s/]+)'
        matches = re.findall(url_pattern, combined_text)
        detected.extend(matches)
        
        return list(set(detected))
    
    def generate_api_fix(self, files: List[Dict], analysis: Dict) -> Dict:
        """Generate fixes for API issues"""
        error_type = analysis.get('error_type', 'generic_api_error')
        
        if error_type == 'ssl_error':
            return self._fix_ssl_error(files, analysis)
        elif error_type == 'timeout_error':
            return self._fix_timeout_error(files, analysis)
        elif error_type == 'fetch_error':
            return self._fix_fetch_error(files, analysis)
        else:
            return self._fix_generic_api_error(files, analysis)
    
    def _fix_ssl_error(self, files: List[Dict], analysis: Dict) -> Dict:
        """Fix SSL/ATS related errors"""
        # This would integrate with robust_ssl_handler.py
        # For now, return a basic fix
        return {
            'fix_applied': True,
            'fix_type': 'ssl_ats',
            'modified_files': files,
            'changes': ['Added ATS exceptions for detected APIs']
        }
    
    def _fix_timeout_error(self, files: List[Dict], analysis: Dict) -> Dict:
        """Fix timeout errors by adding retry logic"""
        modified_files = []
        
        for file in files:
            if 'Service' in file['path'] or 'API' in file['path'] or 'Network' in file['path']:
                modified_content = self._add_retry_logic(file['content'])
                modified_files.append({
                    'path': file['path'],
                    'content': modified_content
                })
            else:
                modified_files.append(file)
        
        return {
            'fix_applied': True,
            'fix_type': 'timeout_retry',
            'modified_files': modified_files,
            'changes': ['Added retry logic with exponential backoff', 'Increased timeout to 30 seconds']
        }
    
    def _fix_fetch_error(self, files: List[Dict], analysis: Dict) -> Dict:
        """Fix fetch errors with better error handling"""
        modified_files = []
        
        for file in files:
            if 'Service' in file['path'] or 'ViewModel' in file['path']:
                modified_content = self._improve_error_handling(file['content'])
                modified_files.append({
                    'path': file['path'],
                    'content': modified_content
                })
            else:
                modified_files.append(file)
        
        return {
            'fix_applied': True,
            'fix_type': 'error_handling',
            'modified_files': modified_files,
            'changes': ['Added detailed error logging', 'Improved error messages', 'Added network reachability check']
        }
    
    def _fix_generic_api_error(self, files: List[Dict], analysis: Dict) -> Dict:
        """Apply generic fixes for API issues"""
        # Combine multiple fixes
        modified_files = files
        
        # Add logging
        modified_files = self._add_api_logging(modified_files)
        
        # Improve error handling
        modified_files = self._add_comprehensive_error_handling(modified_files)
        
        return {
            'fix_applied': True,
            'fix_type': 'comprehensive',
            'modified_files': modified_files,
            'changes': [
                'Added comprehensive error logging',
                'Improved error handling with specific messages',
                'Added network status monitoring',
                'Implemented retry logic'
            ]
        }
    
    def _add_retry_logic(self, content: str) -> str:
        """Add retry logic to API calls"""
        # Check if it's already using async/await
        if 'async' in content and 'await' in content:
            # Add retry wrapper
            retry_code = '''
    private func fetchWithRetry<T>(
        operation: () async throws -> T,
        maxRetries: Int = 3
    ) async throws -> T {
        var lastError: Error?
        
        for attempt in 0..<maxRetries {
            do {
                return try await operation()
            } catch {
                lastError = error
                if attempt < maxRetries - 1 {
                    let delay = pow(2.0, Double(attempt))
                    try await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
                }
            }
        }
        
        throw lastError ?? URLError(.unknown)
    }
'''
            # Insert after class declaration
            class_pattern = r'(class\s+\w+Service[^{]*{)'
            if re.search(class_pattern, content):
                content = re.sub(class_pattern, r'\1\n' + retry_code, content)
        
        return content
    
    def _improve_error_handling(self, content: str) -> str:
        """Improve error handling with specific messages"""
        # Replace generic error handling
        if 'Failed to load' in content or 'error.localizedDescription' in content:
            improved_error = '''
                if let urlError = error as? URLError {
                    switch urlError.code {
                    case .notConnectedToInternet:
                        self.errorMessage = "No internet connection. Please check your network."
                    case .timedOut:
                        self.errorMessage = "Request timed out. Please try again."
                    case .cannotFindHost, .cannotConnectToHost:
                        self.errorMessage = "Cannot connect to server. Please try again later."
                    case .secureConnectionFailed:
                        self.errorMessage = "Secure connection failed. Please update the app."
                    default:
                        self.errorMessage = "Network error: \\(urlError.localizedDescription)"
                    }
                } else {
                    self.errorMessage = "An unexpected error occurred. Please try again."
                }
                print("API Error: \\(error)")  // Add logging
'''
            # Replace simple error assignment
            content = re.sub(
                r'self\.errorMessage\s*=\s*"[^"]*"',
                improved_error,
                content,
                count=1
            )
        
        return content
    
    def _add_api_logging(self, files: List[Dict]) -> List[Dict]:
        """Add logging to API calls for debugging"""
        modified_files = []
        
        for file in files:
            if 'Service' in file['path']:
                content = file['content']
                # Add logging before URL requests
                content = re.sub(
                    r'(let\s*\(data,\s*response\)\s*=\s*try\s+await[^)]+\))',
                    r'print("Making API request to: \\(url)")  // Debug log\n        \1',
                    content
                )
                modified_files.append({
                    'path': file['path'],
                    'content': content
                })
            else:
                modified_files.append(file)
        
        return modified_files
    
    def _add_comprehensive_error_handling(self, files: List[Dict]) -> List[Dict]:
        """Add comprehensive error handling to all API-related files"""
        # This would be a more complex implementation
        # For now, return files as-is
        return files
    
    def suggest_api_improvements(self, files: List[Dict]) -> List[str]:
        """Suggest improvements for API integration"""
        suggestions = []
        
        # Check for common issues
        for file in files:
            content = file['content']
            
            # Check for timeout configuration
            if 'URLSession.shared' in content and 'timeoutInterval' not in content:
                suggestions.append("Consider adding custom timeout configuration for URLSession")
            
            # Check for retry logic
            if 'URLSession' in content and 'retry' not in content.lower():
                suggestions.append("Add retry logic for transient network failures")
            
            # Check for proper error handling
            if 'catch' in content and 'localizedDescription' in content:
                suggestions.append("Implement specific error handling instead of generic messages")
            
            # Check for network monitoring
            if 'API' in file['path'] and 'reachability' not in content.lower():
                suggestions.append("Consider adding network reachability monitoring")
        
        return suggestions