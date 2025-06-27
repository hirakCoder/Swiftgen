#!/usr/bin/env python3
"""
Add Swift Validator integration to main.py
This script updates main.py to include the swift validator
"""

import re

def update_main_py():
    """Update main.py to include swift validator integration"""
    
    # Read current main.py
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Check if already integrated
    if 'swift_validator_integration' in content:
        print("✓ Swift validator already integrated in main.py")
        return True
    
    # Find where to add import (after other local imports)
    import_pattern = r'(from automatic_ssl_fixer import.*\n)'
    import_match = re.search(import_pattern, content)
    
    if import_match:
        # Add import after automatic_ssl_fixer import
        new_import = "from swift_validator_integration import integrate_validator_with_main_services\n"
        content = content[:import_match.end()] + new_import + content[import_match.end():]
    else:
        print("⚠️  Could not find appropriate place for import")
        return False
    
    # Find where to add integration (after self_healing_generator initialization)
    integration_pattern = r'(self_healing_generator = SelfHealingGenerator\([^)]+\)\n)'
    integration_match = re.search(integration_pattern, content)
    
    if integration_match:
        # Add integration code
        integration_code = '''
# Integrate Swift validator for syntax validation and fixes
try:
    integrate_validator_with_main_services(
        build_service=build_service,
        self_healing_generator=self_healing_generator
    )
except Exception as e:
    print(f"⚠️  Could not integrate Swift validator: {e}")
    # System continues to work without validator
'''
        content = content[:integration_match.end()] + integration_code + content[integration_match.end():]
    else:
        print("⚠️  Could not find self_healing_generator initialization")
        # Try alternative location - after build service initialization
        alt_pattern = r'(build_service = BuildService\(\)\n)'
        alt_match = re.search(alt_pattern, content)
        
        if alt_match:
            # Find the SSL fixer integration block
            ssl_end = content.find('print("✓ Automatic SSL Fixer integrated with BuildService")', alt_match.end())
            if ssl_end != -1:
                # Find the newline after this
                newline_pos = content.find('\n', ssl_end)
                integration_code = '''
# Integrate Swift validator for syntax validation and fixes
try:
    integrate_validator_with_main_services(
        build_service=build_service,
        self_healing_generator=self_healing_generator if 'self_healing_generator' in locals() else None
    )
except Exception as e:
    print(f"⚠️  Could not integrate Swift validator: {e}")
    # System continues to work without validator
'''
                content = content[:newline_pos+1] + integration_code + content[newline_pos+1:]
            else:
                print("⚠️  Could not find suitable integration point")
                return False
    
    # Write updated content
    with open('main_with_validator.py', 'w') as f:
        f.write(content)
    
    print("✅ Created main_with_validator.py")
    print("\nNext steps:")
    print("1. Review the changes: diff main.py main_with_validator.py")
    print("2. Test the integration: python3 main_with_validator.py")
    print("3. If tests pass: mv main_with_validator.py main.py")
    
    return True

if __name__ == "__main__":
    update_main_py()