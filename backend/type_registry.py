#!/usr/bin/env python3
"""
Type Registry - Tracks actual type names vs expected names
Prevents build errors from type name mismatches
"""

import json
import os
import re
from typing import Dict, List, Set, Optional
import logging

logger = logging.getLogger(__name__)

class TypeRegistry:
    """Registry to track Swift type names and their mappings"""
    
    def __init__(self, registry_file: str = "type_registry.json"):
        self.registry_file = registry_file
        self.registry = self._load_registry()
        
        # Common naming patterns that LLMs use
        self.common_patterns = {
            "Error handling views": {
                "expected": ["ErrorView", "ErrorDisplay", "ErrorMessage"],
                "actual": "AppErrorView"
            },
            "Result display views": {
                "expected": ["ResultView", "ResultDisplay", "OutputView"],
                "actual": "OperationResultView"
            },
            "Input views": {
                "expected": ["InputView", "UserInputView"],
                "actual": "CurrencyInputView"
            }
        }
    
    def _load_registry(self) -> Dict[str, Dict]:
        """Load the type registry from file"""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "type_mappings": {},
            "app_types": {}
        }
    
    def _save_registry(self):
        """Save the registry to file"""
        try:
            with open(self.registry_file, 'w') as f:
                json.dump(self.registry, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save type registry: {e}")
    
    def register_app_types(self, app_name: str, swift_files: List[Dict]):
        """Register all types defined in an app"""
        app_types = set()
        
        for file in swift_files:
            content = file.get("content", "")
            
            # Find struct definitions
            structs = re.findall(r'struct\s+(\w+)(?:\s*:|\s*{)', content)
            app_types.update(structs)
            
            # Find class definitions
            classes = re.findall(r'class\s+(\w+)(?:\s*:|\s*{)', content)
            app_types.update(classes)
            
            # Find enum definitions
            enums = re.findall(r'enum\s+(\w+)(?:\s*:|\s*{)', content)
            app_types.update(enums)
        
        # Store app types
        self.registry["app_types"][app_name] = list(app_types)
        
        # Update mappings based on common patterns
        for pattern_group, pattern_info in self.common_patterns.items():
            actual = pattern_info["actual"]
            if actual in app_types:
                for expected in pattern_info["expected"]:
                    self.registry["type_mappings"][expected] = actual
        
        self._save_registry()
        logger.info(f"Registered {len(app_types)} types for app {app_name}")
    
    def get_actual_type(self, expected_type: str) -> Optional[str]:
        """Get the actual type name for an expected type"""
        return self.registry["type_mappings"].get(expected_type)
    
    def update_mapping(self, expected: str, actual: str):
        """Update a type mapping"""
        self.registry["type_mappings"][expected] = actual
        self._save_registry()
    
    def fix_type_references(self, content: str, errors: List[str]) -> str:
        """Fix type references based on registry"""
        fixed_content = content
        
        for error in errors:
            if "cannot find" in error and "in scope" in error:
                # Extract the type name from error
                match = re.search(r"cannot find '(\w+)' in scope", error)
                if match:
                    expected_type = match.group(1)
                    actual_type = self.get_actual_type(expected_type)
                    
                    if actual_type:
                        # Replace all occurrences
                        fixed_content = re.sub(rf'\b{expected_type}\b', actual_type, fixed_content)
                        logger.info(f"Fixed type reference: {expected_type} -> {actual_type}")
        
        return fixed_content
    
    def learn_from_error(self, error: str, fixed_content: str, original_content: str):
        """Learn type mappings from successful fixes"""
        if "cannot find" in error and "in scope" in error:
            # Extract the missing type
            match = re.search(r"cannot find '(\w+)' in scope", error)
            if match:
                missing_type = match.group(1)
                
                # Find what it was replaced with
                # Look for the pattern where missing_type was used in original
                # and see what it became in fixed
                original_uses = re.findall(rf'\b{missing_type}\b', original_content)
                if original_uses:
                    # Find the corresponding position in fixed content
                    # This is simplified - in practice would need more sophisticated diffing
                    for pattern_group, pattern_info in self.common_patterns.items():
                        if missing_type in pattern_info["expected"]:
                            actual = pattern_info["actual"]
                            if actual in fixed_content:
                                self.update_mapping(missing_type, actual)
                                logger.info(f"Learned mapping: {missing_type} -> {actual}")
                                break