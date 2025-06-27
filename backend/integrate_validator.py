#!/usr/bin/env python3
"""
Script to integrate Swift validator into the main system
"""

import os

def add_validator_integration():
    """Add Swift validator integration to main.py"""
    
    # Read current main.py
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Check if already integrated
    if 'swift_validator' in content:
        print("Swift validator already integrated")
        return
    
    # Find the imports section
    imports_end = content.find('# Initialize services')
    if imports_end == -1:
        print("Could not find initialization section")
        return
    
    # Add import
    new_import = "from swift_validator import SwiftValidator, integrate_with_build_service as integrate_validator\n"
    
    # Find where to add the import (after other local imports)
    last_import = content.rfind('from automatic_ssl_fixer', 0, imports_end)
    if last_import != -1:
        # Find end of this line
        line_end = content.find('\n', last_import)
        content = content[:line_end+1] + new_import + content[line_end+1:]
    
    # Add integration code after build service initialization
    build_service_init = content.find('build_service = BuildService()')
    if build_service_init != -1:
        # Find the next suitable place to add integration
        ssl_integration = content.find('if auto_ssl_fixer and integrate_with_build_service:', build_service_init)
        if ssl_integration != -1:
            # Find the end of the SSL integration block
            ssl_block_end = content.find('print("✓ Automatic SSL Fixer integrated with BuildService")', ssl_integration)
            if ssl_block_end != -1:
                # Find the newline after this print
                newline_pos = content.find('\n', ssl_block_end)
                
                # Add validator integration
                validator_integration = '''
# Integrate Swift validator with build service
try:
    integrate_validator(build_service)
    print("✓ Swift Validator integrated with BuildService")
except Exception as e:
    print(f"⚠️  Could not integrate Swift validator: {e}")
'''
                content = content[:newline_pos+1] + validator_integration + content[newline_pos+1:]
    
    # Write updated content
    with open('main_with_validator.py', 'w') as f:
        f.write(content)
    
    print("Created main_with_validator.py with Swift validator integration")
    print("\nTo apply the changes:")
    print("1. Review main_with_validator.py")
    print("2. If it looks good: mv main_with_validator.py main.py")

if __name__ == "__main__":
    add_validator_integration()