#!/usr/bin/env python3
"""
Swift Validator Integration Module
Integrates the swift_validator into existing error recovery systems
"""

import logging
from typing import Tuple, List, Dict

logger = logging.getLogger(__name__)

def add_swift_validator_to_recovery_system(error_recovery_system):
    """Add swift validator recovery method to error recovery system"""
    
    # Import here to avoid circular dependencies
    from swift_validator import SwiftValidator
    
    # Create validator instance
    error_recovery_system.swift_validator = SwiftValidator()
    
    # Add the recovery method
    async def _swift_validator_recovery(self, errors: List[str], swift_files: List[Dict], 
                                       error_analysis: Dict, is_modification: bool) -> Tuple[bool, List[Dict]]:
        """Use swift_validator for deterministic syntax fixes"""
        if not hasattr(self, 'swift_validator') or not self.swift_validator:
            return False, swift_files
        
        self.logger.info("Attempting Swift validator recovery for syntax errors")
        
        # Check if we have syntax-related errors
        syntax_error_keywords = [
            'conform to', 'Hashable', 'Identifiable', 'expected', 'cannot find',
            'consecutive statements', 'semicolon', 'no exact matches'
        ]
        
        has_syntax_errors = any(
            any(keyword in error for keyword in syntax_error_keywords)
            for error in errors
        )
        
        if not has_syntax_errors:
            self.logger.info("No syntax errors detected, skipping validator recovery")
            return False, swift_files
        
        modified_files = list(swift_files)
        any_changes = False
        fixes_applied = []
        
        # Process each Swift file
        for i, file in enumerate(modified_files):
            if file['path'].endswith('.swift'):
                try:
                    # First apply auto-fixes
                    content, auto_fixes = self.swift_validator.apply_auto_fixes(file['content'])
                    
                    if auto_fixes:
                        modified_files[i]['content'] = content
                        fixes_applied.extend(auto_fixes)
                        any_changes = True
                    
                    # Then check for specific error fixes
                    # Pass the content to avoid file path issues
                    fixed, updated_content, error_fixes = self.swift_validator.fix_build_errors(
                        file['path'], errors, content=modified_files[i]['content']
                    )
                    
                    if fixed:
                        modified_files[i]['content'] = updated_content
                        fixes_applied.extend(error_fixes)
                        any_changes = True
                        
                except Exception as e:
                    self.logger.warning(f"Swift validator error on {file['path']}: {e}")
        
        if any_changes:
            self.logger.info(f"Swift validator applied {len(fixes_applied)} fixes:")
            for fix in fixes_applied[:5]:  # Log first 5 fixes
                self.logger.info(f"  - {fix}")
            
        return any_changes, modified_files
    
    # Bind the method to the instance
    import types
    error_recovery_system._swift_validator_recovery = types.MethodType(
        _swift_validator_recovery, error_recovery_system
    )
    
    # Update recovery strategies to include validator
    original_strategies = error_recovery_system._get_dynamic_recovery_strategies()
    
    def _get_dynamic_recovery_strategies_with_validator(self):
        """Get recovery strategies in optimal order"""
        strategies = [
            # 1. Swift validator first - most accurate, non-destructive
            self._swift_validator_recovery,
            # 2. Dependencies early - adds missing imports
            self._dependency_recovery,
            # 3. Pattern-based - now with non-destructive fixes
            self._pattern_based_recovery,
            # 4. Swift syntax - specific Swift fixes
            self._swift_syntax_recovery,
            # 5. RAG - knowledge-based fixes
            self._rag_based_recovery,
            # 6. LLM last - expensive but handles complex cases
            self._llm_based_recovery
        ]
        return strategies
    
    # Replace the method
    error_recovery_system._get_dynamic_recovery_strategies = types.MethodType(
        _get_dynamic_recovery_strategies_with_validator, error_recovery_system
    )
    
    # Refresh strategies
    error_recovery_system.recovery_strategies = error_recovery_system._get_dynamic_recovery_strategies()
    
    logger.info("Swift validator integrated into error recovery system")


def enhance_build_service_validation(build_service):
    """Enhance build service with swift validator"""
    
    from swift_validator import SwiftValidator
    
    # Add validator to build service
    build_service.swift_validator = SwiftValidator()
    
    # Store original validation method
    original_validate = build_service._validate_swift_syntax
    
    def _validate_swift_syntax_enhanced(self, swift_files: List[Dict]) -> List[str]:
        """Enhanced Swift syntax validation using swift_validator"""
        errors = []
        
        # First try swift_validator for each file
        if hasattr(self, 'swift_validator') and self.swift_validator:
            for file in swift_files:
                # Create a temporary file for validation
                import tempfile
                import os
                
                try:
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.swift', delete=False) as tmp:
                        tmp.write(file['content'])
                        tmp_path = tmp.name
                    
                    # Validate the file
                    valid, file_errors = self.swift_validator.validate_swift_file(tmp_path)
                    
                    if not valid:
                        # Clean up error messages to use actual file path
                        for error in file_errors:
                            clean_error = error.replace(tmp_path, file['path'])
                            errors.append(clean_error)
                    
                    # Clean up temp file
                    os.unlink(tmp_path)
                    
                except Exception as e:
                    logger.warning(f"Validator error for {file['path']}: {e}")
        
        # If no validator or it found no errors, use original validation
        if not errors and original_validate:
            errors = original_validate(swift_files)
        
        return errors
    
    # Replace the method
    import types
    build_service._validate_swift_syntax = types.MethodType(
        _validate_swift_syntax_enhanced, build_service
    )
    
    logger.info("Swift validator integrated into build service")


def integrate_swift_validator(error_recovery_system=None, build_service=None, 
                            self_healing_generator=None):
    """Main integration function"""
    
    integrated_components = []
    
    try:
        # Integrate with error recovery system
        if error_recovery_system:
            add_swift_validator_to_recovery_system(error_recovery_system)
            integrated_components.append("error_recovery_system")
        
        # Integrate with build service
        if build_service:
            enhance_build_service_validation(build_service)
            integrated_components.append("build_service")
            
            # Also integrate with build service's error recovery if it has one
            if hasattr(build_service, 'error_recovery_system') and build_service.error_recovery_system:
                add_swift_validator_to_recovery_system(build_service.error_recovery_system)
                integrated_components.append("build_service.error_recovery_system")
        
        # Integrate with self-healing generator if provided
        if self_healing_generator:
            from swift_validator import SwiftValidator
            self_healing_generator.swift_validator = SwiftValidator()
            integrated_components.append("self_healing_generator")
        
        logger.info(f"Swift validator integrated into: {', '.join(integrated_components)}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to integrate swift validator: {e}")
        return False


# Helper function for main.py integration
def integrate_validator_with_main_services(build_service, self_healing_generator=None):
    """Integrate validator with main.py services"""
    
    # Get error recovery system from build service
    error_recovery = None
    if hasattr(build_service, 'error_recovery_system'):
        error_recovery = build_service.error_recovery_system
    
    # Integrate
    success = integrate_swift_validator(
        error_recovery_system=error_recovery,
        build_service=build_service,
        self_healing_generator=self_healing_generator
    )
    
    if success:
        print("✓ Swift Validator integrated successfully")
    else:
        print("⚠️  Swift Validator integration had issues")
    
    return success