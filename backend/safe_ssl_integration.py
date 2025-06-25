"""
Safe SSL Integration Wrapper
Ensures SSL fixes don't break JSON parsing or builds
"""
import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def validate_files_json(files: List[Dict]) -> bool:
    """Validate that files structure is valid JSON-serializable"""
    try:
        # Test JSON serialization
        json.dumps(files)
        
        # Check each file has required fields
        for file in files:
            if not isinstance(file, dict):
                return False
            if 'path' not in file or 'content' not in file:
                return False
            if not isinstance(file['path'], str) or not isinstance(file['content'], str):
                return False
        
        return True
    except Exception as e:
        logger.error(f"Files validation failed: {e}")
        return False


def safe_integrate_ssl_fixer(auto_ssl_fixer, build_service=None, modification_handler=None):
    """Safely integrate SSL fixer with validation checks"""
    
    if not auto_ssl_fixer:
        logger.warning("No SSL fixer instance provided")
        return
    
    # Wrap the SSL fixer's apply_automatic_fixes method
    original_apply_fixes = auto_ssl_fixer.apply_automatic_fixes
    
    def safe_apply_fixes(files: List[Dict]) -> Dict[str, Any]:
        """Apply SSL fixes with JSON validation"""
        try:
            # Validate input
            if not validate_files_json(files):
                logger.error("Invalid files structure, skipping SSL fixes")
                return {
                    'success': False,
                    'files': files,
                    'fixes_applied': [],
                    'error': 'Invalid files structure'
                }
            
            # Apply fixes
            result = original_apply_fixes(files)
            
            # Validate output
            if result.get('success') and 'files' in result:
                if not validate_files_json(result['files']):
                    logger.error("SSL fixer produced invalid JSON, reverting")
                    return {
                        'success': False,
                        'files': files,  # Return original files
                        'fixes_applied': [],
                        'error': 'SSL fixer produced invalid JSON'
                    }
            
            return result
            
        except Exception as e:
            logger.error(f"SSL fixer failed: {e}")
            return {
                'success': False,
                'files': files,
                'fixes_applied': [],
                'error': str(e)
            }
    
    # Replace the method with safe version
    auto_ssl_fixer.apply_automatic_fixes = safe_apply_fixes
    
    # Now integrate with services
    if build_service:
        try:
            from automatic_ssl_fixer import integrate_with_build_service
            integrate_with_build_service(build_service)
            logger.info("✓ SSL Fixer safely integrated with build service")
        except Exception as e:
            logger.error(f"Failed to integrate with build service: {e}")
    
    if modification_handler:
        try:
            from automatic_ssl_fixer import integrate_with_modification_handler
            integrate_with_modification_handler(modification_handler)
            logger.info("✓ SSL Fixer safely integrated with modification handler")
        except Exception as e:
            logger.error(f"Failed to integrate with modification handler: {e}")


def test_ssl_fixer_safety(auto_ssl_fixer):
    """Test SSL fixer with various edge cases"""
    test_cases = [
        # Valid case
        [
            {'path': 'ContentView.swift', 'content': 'let url = "https://api.example.com"'},
            {'path': 'Info.plist', 'content': '<plist></plist>'}
        ],
        # Missing fields
        [
            {'path': 'test.swift'},  # Missing content
        ],
        # Invalid types
        [
            {'path': 123, 'content': 'test'},  # Invalid path type
        ],
        # Empty list
        [],
    ]
    
    results = []
    for i, test_files in enumerate(test_cases):
        try:
            result = auto_ssl_fixer.apply_automatic_fixes(test_files)
            results.append({
                'test': i,
                'success': result.get('success', False),
                'error': result.get('error')
            })
        except Exception as e:
            results.append({
                'test': i,
                'success': False,
                'error': str(e)
            })
    
    return results