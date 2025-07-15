#!/usr/bin/env python3
"""World-class fixes for SwiftGen - Fix critical issues properly"""

import os
import re

def fix_1_swift_syntax_validation():
    """Add Swift syntax validation to catch JavaScript patterns"""
    
    print("🔧 Fix 1: Swift Syntax Validation")
    
    # Create swift_syntax_validator.py
    validator_content = '''"""Swift Syntax Validator - Catches and fixes common syntax errors"""

import re
from typing import List, Dict, Tuple

class SwiftSyntaxValidator:
    """Validates and fixes Swift syntax issues"""
    
    @staticmethod
    def validate_and_fix_swift_syntax(code: str) -> Tuple[str, List[str]]:
        """Validate Swift syntax and fix common issues"""
        issues = []
        fixed_code = code
        
        # Fix 1: this. -> self.
        if "this." in code:
            issues.append("Found JavaScript 'this' syntax - fixed to 'self'")
            fixed_code = re.sub(r'\\bthis\\.', 'self.', fixed_code)
        
        # Fix 2: Haptic feedback API
        if "UIImpactFeedbackGenerator.FeedbackStyle.success" in code:
            issues.append("Fixed invalid haptic feedback style")
            fixed_code = fixed_code.replace(
                "UIImpactFeedbackGenerator.FeedbackStyle.success",
                "UIImpactFeedbackGenerator.FeedbackStyle.medium"
            )
        
        # Fix 3: var in struct initializers
        init_pattern = r'init\\([^)]*\\)\\s*{([^}]+)}'
        def fix_init(match):
            body = match.group(1)
            if 'this.' in body:
                body = body.replace('this.', 'self.')
            return f'init{match.group(0)[4:].replace(body, body)}'
        
        fixed_code = re.sub(init_pattern, fix_init, fixed_code, flags=re.DOTALL)
        
        # Fix 4: Common iOS API mistakes
        api_fixes = {
            ".systemGroupedBackground": ".systemBackground",
            "Color.systemBlue": "Color.blue",
            "withAnimation(.easeInOut)": "withAnimation(.easeInOut(duration: 0.3))",
        }
        
        for wrong, correct in api_fixes.items():
            if wrong in fixed_code:
                issues.append(f"Fixed API usage: {wrong} -> {correct}")
                fixed_code = fixed_code.replace(wrong, correct)
        
        return fixed_code, issues
    
    @staticmethod
    def validate_files(files: List[Dict]) -> List[Dict]:
        """Validate and fix all Swift files"""
        fixed_files = []
        total_issues = []
        
        for file in files:
            if file['path'].endswith('.swift'):
                content = file.get('content', '')
                fixed_content, issues = SwiftSyntaxValidator.validate_and_fix_swift_syntax(content)
                
                if issues:
                    total_issues.extend([f"{file['path']}: {issue}" for issue in issues])
                    file['content'] = fixed_content
                
            fixed_files.append(file)
        
        if total_issues:
            print(f"[SYNTAX] Fixed {len(total_issues)} Swift syntax issues")
            for issue in total_issues[:5]:
                print(f"  - {issue}")
        
        return fixed_files
'''
    
    with open('backend/swift_syntax_validator.py', 'w') as f:
        f.write(validator_content)
    
    # Update main.py to use the validator
    main_path = 'backend/main.py'
    with open(main_path, 'r') as f:
        content = f.read()
    
    # Add import
    if 'from swift_syntax_validator import SwiftSyntaxValidator' not in content:
        import_pos = content.find('from enhanced_claude_service')
        content = content[:import_pos] + 'from swift_syntax_validator import SwiftSyntaxValidator\n' + content[import_pos:]
    
    # Add validation after generation
    validation_code = '''
            # Validate and fix Swift syntax
            try:
                from swift_syntax_validator import SwiftSyntaxValidator
                if "files" in generated_code:
                    generated_code["files"] = SwiftSyntaxValidator.validate_files(generated_code["files"])
            except Exception as e:
                print(f"[MAIN] Swift syntax validation error: {e}")
'''
    
    # Find where to insert (after generated_code is created)
    insert_marker = "# Post-generation validation"
    if insert_marker in content:
        pos = content.find(insert_marker)
        content = content[:pos] + validation_code + "\\n" + content[pos:]
    
    with open(main_path, 'w') as f:
        f.write(content)
    
    print("✅ Added Swift syntax validation")

def fix_2_chat_intent_detection():
    """Fix chat handler to properly detect modifications"""
    
    print("\\n🔧 Fix 2: Chat Intent Detection")
    
    # Update llm_chat_handler.py
    handler_path = 'backend/llm_chat_handler.py'
    
    if os.path.exists(handler_path):
        with open(handler_path, 'r') as f:
            content = f.read()
        
        # Add better intent detection
        intent_detection = '''
    def _detect_modification_intent(self, message: str, session_id: str = None) -> bool:
        """Detect if message is a modification request"""
        message_lower = message.lower()
        
        # Check if we have an active project in session
        if session_id and hasattr(self, 'active_projects'):
            if session_id in self.active_projects:
                # If there's an active project, assume modification unless clearly new app
                new_app_keywords = ['create new', 'build new', 'make new', 'start over']
                if not any(keyword in message_lower for keyword in new_app_keywords):
                    return True
        
        # Modification keywords
        mod_keywords = [
            'add', 'change', 'modify', 'update', 'fix', 'remove', 'delete',
            'make it', 'can you', 'please add', 'i want', 'implement',
            'dark mode', 'swipe', 'gesture', 'color', 'button', 'feature'
        ]
        
        # Check for modification intent
        for keyword in mod_keywords:
            if keyword in message_lower:
                # But not if they're asking to create/build
                if not any(word in message_lower for word in ['create', 'build', 'make me']):
                    return True
        
        return False
'''
        
        # Insert the method
        if '_detect_modification_intent' not in content:
            # Find class definition
            class_pos = content.find('class LLMChatHandler')
            if class_pos > 0:
                # Find end of __init__ or first method
                init_end = content.find('\\n\\n    def', class_pos)
                if init_end > 0:
                    content = content[:init_end] + '\\n' + intent_detection + content[init_end:]
        
        # Update handle_user_message to use intent detection
        handle_method = content.find('async def handle_user_message')
        if handle_method > 0:
            # Add modification detection logic
            detection_logic = '''
        # Check if this is a modification request
        if self._detect_modification_intent(message, session_id):
            # Check for active project
            project_id = None
            if session_id and hasattr(self, 'active_projects'):
                project_id = self.active_projects.get(session_id)
            
            if project_id:
                # Route to modification
                return {
                    "response": f"I'll help you modify the app. Let me make those changes...",
                    "action": "modify",
                    "project_id": project_id,
                    "modification": message
                }
'''
            # Insert before LLM analysis
            llm_pos = content.find('# Let the LLM analyze', handle_method)
            if llm_pos > 0:
                content = content[:llm_pos] + detection_logic + '\\n\\n        ' + content[llm_pos:]
        
        with open(handler_path, 'w') as f:
            f.write(content)
        
        print("✅ Fixed chat intent detection")
    else:
        print("⚠️  llm_chat_handler.py not found")

def fix_3_ios_api_knowledge():
    """Update prompts with correct iOS API usage"""
    
    print("\\n🔧 Fix 3: iOS API Knowledge")
    
    prompts_path = 'backend/enhanced_prompts.py'
    
    with open(prompts_path, 'r') as f:
        content = f.read()
    
    # Add iOS API corrections
    ios_api_section = '''
iOS API CORRECTIONS - MUST FOLLOW:
1. **Haptic Feedback**: 
   - Use `.light`, `.medium`, or `.heavy` (NOT `.success`)
   - Example: UIImpactFeedbackGenerator(style: .medium)
   
2. **Swift Syntax**:
   - ALWAYS use `self.property` in initializers (NOT `this.property`)
   - Swift is NOT JavaScript!
   
3. **Colors**:
   - Use Color.blue, Color.red (NOT Color.systemBlue)
   - Use Color(.systemBackground) for system colors
   
4. **Animations**:
   - Include duration: withAnimation(.easeInOut(duration: 0.3))
   - NOT just withAnimation(.easeInOut)

CORRECT SWIFT INIT EXAMPLE:
```swift
init(id: UUID = UUID(), name: String) {
    self.id = id      // NOT this.id
    self.name = name  // NOT this.name
}
```
'''
    
    # Insert after CRITICAL SYNTAX RULES
    insert_pos = content.find('CRITICAL SYNTAX RULES')
    if insert_pos > 0:
        # Find end of that section
        next_section = content.find('\\n\\nHIG-COMPLIANT', insert_pos)
        if next_section > 0:
            content = content[:next_section] + '\\n\\n' + ios_api_section + content[next_section:]
    
    with open(prompts_path, 'w') as f:
        f.write(content)
    
    print("✅ Updated iOS API knowledge in prompts")

def fix_4_modification_feedback():
    """Ensure modification feedback is clear and specific"""
    
    print("\\n🔧 Fix 4: Modification Feedback")
    
    # Already partially fixed in optimized_modification_handler.py
    # Let's ensure it's working in the UI notification
    
    main_path = 'backend/main.py'
    with open(main_path, 'r') as f:
        content = f.read()
    
    # Find the modification complete section
    mod_complete = content.find('Changes Applied:')
    if mod_complete > 0:
        # Ensure we're getting the right data
        enhancement = '''
            # Enhanced modification feedback
            files_modified = modified_code.get("files_modified", [])
            
            # If we have specific file changes, show them
            if files_modified:
                file_list = '\\n'.join(f"📄 {f}" for f in files_modified[:5])
                enhanced_message = f"""✅ {app_name} has been modified successfully!

📝 Files Modified ({len(files_modified)}):
{file_list}

💡 Changes Applied:
{changes_text}

🤖 Modified by: {llm_used.upper()}"""
                detailed_message = enhanced_message
'''
        # Find where detailed_message is created
        detailed_msg_pos = content.find('detailed_message = f"""✅', mod_complete - 500)
        if detailed_msg_pos > 0:
            # Insert before
            content = content[:detailed_msg_pos] + enhancement + '\\n            else:\\n                ' + content[detailed_msg_pos:]
    
    with open(main_path, 'w') as f:
        f.write(content)
    
    print("✅ Enhanced modification feedback")

def fix_5_api_overload_handling():
    """Add better API overload handling"""
    
    print("\\n🔧 Fix 5: API Overload Handling")
    
    # Update enhanced_claude_service.py
    service_path = 'backend/enhanced_claude_service.py'
    
    with open(service_path, 'r') as f:
        content = f.read()
    
    # Add exponential backoff
    backoff_code = '''
    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff with jitter"""
        base_delay = 2.0
        max_delay = 30.0
        jitter = 0.1
        
        delay = min(base_delay * (2 ** attempt), max_delay)
        # Add jitter to prevent thundering herd
        delay += delay * (random.random() * jitter * 2 - jitter)
        
        return delay
'''
    
    # Add import for random
    if 'import random' not in content:
        import_pos = content.find('import json')
        content = content[:import_pos] + 'import random\\n' + content[import_pos:]
    
    # Insert backoff method
    if '_calculate_backoff' not in content:
        init_end = content.find('async def generate_ios_app')
        if init_end > 0:
            content = content[:init_end] + backoff_code + '\\n\\n    ' + content[init_end:]
    
    # Update retry logic to use backoff
    retry_logic = '''
                    # Calculate backoff delay
                    delay = self._calculate_backoff(retry_count)
                    
                    if self.progress_callback:
                        await self.progress_callback(f"⏳ API is busy. Retrying in {delay:.1f} seconds...")
                    
                    await asyncio.sleep(delay)
'''
    
    # Find retry section
    retry_pos = content.find('await asyncio.sleep(5.0)')
    if retry_pos > 0:
        # Replace fixed delay with backoff
        end_pos = content.find('\\n', retry_pos)
        content = content[:retry_pos - 50] + retry_logic + content[end_pos:]
    
    with open(service_path, 'w') as f:
        f.write(content)
    
    print("✅ Added exponential backoff for API overload")

def main():
    """Apply all world-class fixes"""
    
    print("🌟 Applying World-Class Fixes")
    print("=" * 60)
    
    # Apply fixes in order
    fix_1_swift_syntax_validation()
    fix_2_chat_intent_detection()
    fix_3_ios_api_knowledge()
    fix_4_modification_feedback()
    fix_5_api_overload_handling()
    
    print("\\n✅ All fixes applied!")
    print("\\n⚠️  IMPORTANT: Restart the server to apply changes")
    print("\\nWhat we fixed:")
    print("1. Swift syntax validation (no more 'this.' errors)")
    print("2. Chat intent detection (modifications route correctly)")
    print("3. iOS API knowledge (correct haptic feedback)")
    print("4. Clear modification feedback")
    print("5. Better API overload handling")

if __name__ == "__main__":
    main()