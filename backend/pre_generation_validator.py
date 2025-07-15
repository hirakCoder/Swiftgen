"""
Pre-Generation Validator
Validates and fixes common issues before code generation
"""

import re
from typing import Dict, List, Tuple

class PreGenerationValidator:
    """Validates and fixes generation requests before they reach the LLM"""
    
    def __init__(self, rag_kb=None):
        # Store RAG knowledge base
        self.rag_kb = rag_kb
        
        # Import comprehensive validator if available
        try:
            from comprehensive_code_validator import ComprehensiveCodeValidator
            self.comprehensive_validator = ComprehensiveCodeValidator()
        except:
            self.comprehensive_validator = None
            
        self.reserved_types = {
            'Task', 'State', 'Action', 'Result', 'Error', 'Never',
            'Any', 'AnyObject', 'Void', 'Bool', 'Int', 'Double', 
            'Float', 'String', 'Array', 'Dictionary', 'Set', 'Optional',
            'Data', 'URL', 'Date', 'UUID', 'Timer', 'Bundle', 'Notification',
            'View', 'Text', 'Image', 'Button', 'Color', 'Font', 'Animation'
        }
        
        # Common problematic app types that use reserved names
        self.problematic_app_types = {
            'todo': ['Task', 'State'],
            'task': ['Task', 'State'],
            'game': ['State', 'Action'],
            'state': ['State'],
            'action': ['Action'],
            'timer': ['Timer'],
            'calendar': ['Date'],
            'photo': ['Image'],
            'color': ['Color'],
            'data': ['Data']
        }
        
        # Replacement suggestions
        self.replacements = {
            'Task': 'TodoItem',
            'State': 'AppState',
            'Action': 'AppAction',
            'Result': 'AppResult',
            'Error': 'AppError',
            'Data': 'AppData',
            'URL': 'Link',
            'Date': 'EventDate',
            'UUID': 'Identifier',
            'Timer': 'AppTimer',
            'Image': 'Photo',
            'Color': 'Theme',
            'View': 'Screen'
        }
    
    def validate_and_enhance_prompt(self, app_name: str, description: str) -> Tuple[str, str]:
        """Validate and enhance the generation prompt to avoid common issues"""
        
        enhanced_description = description
        app_name_lower = app_name.lower()
        description_lower = description.lower()
        
        # Build comprehensive warnings
        warnings = []
        
        # Query RAG for similar app patterns if available
        if self.rag_kb:
            # Search for similar apps and patterns
            similar_apps = self.rag_kb.search(f"{app_name} {description}", k=3)
            
            # Extract patterns and potential issues
            rag_warnings = []
            rag_patterns = []
            
            for result in similar_apps:
                if result.get('severity') in ['critical', 'important']:
                    # Check for naming conflicts
                    if 'reserved-types' in result.get('tags', []):
                        solutions = result.get('solutions', [])
                        for solution in solutions:
                            if solution not in rag_warnings:
                                rag_warnings.append(solution)
                    
                    # Check for architecture patterns
                    if 'architecture' in result.get('tags', []):
                        content = result.get('content', '')
                        if 'MVVM' in content and 'mvvm' not in rag_patterns:
                            rag_patterns.append('mvvm')
                        if 'Observable' in content and 'observable' not in rag_patterns:
                            rag_patterns.append('observable')
            
            # Add RAG-based warnings
            warnings.extend(rag_warnings)
        
        # Check if this is a TODO/Task app
        is_todo_app = any(word in app_name_lower or word in description_lower 
                         for word in ['todo', 'task', 'to-do', 'to do'])
        
        if is_todo_app:
            warnings.append("For task/todo models, use 'TodoItem' NOT 'Task' (Task is a Swift generic type)")
        
        # Check for other problematic patterns
        for app_type, reserved_list in self.problematic_app_types.items():
            if app_type in app_name_lower or app_type in description_lower:
                for reserved_type in reserved_list:
                    if reserved_type in self.replacements:
                        warnings.append(f"Use '{self.replacements[reserved_type]}' instead of '{reserved_type}'")
        
        # Check for timer apps
        if 'timer' in app_name_lower or 'timer' in description_lower:
            warnings.append("Use 'AppTimer' or 'CountdownTimer' NOT 'Timer' (Timer is a Foundation type)")
        
        # Check for photo/image apps
        if any(word in app_name_lower or word in description_lower for word in ['photo', 'image', 'camera']):
            warnings.append("Use 'Photo' or 'Picture' NOT 'Image' for your model (Image is a SwiftUI type)")
        
        # Check for data processing apps
        if any(word in app_name_lower or word in description_lower for word in ['data', 'analytics', 'chart']):
            warnings.append("Use 'AppData' or 'ChartData' NOT 'Data' (Data is a Foundation type)")
        
        # Add comprehensive type safety rules
        if warnings:
            enhanced_description += """

CRITICAL TYPE SAFETY RULES:
"""
            for warning in warnings:
                enhanced_description += f"\n- {warning}"
                
        # Always add general reserved type warning
        enhanced_description += """

RESERVED TYPES TO AVOID:
- Generic Types: Task<>, Result<>, Publisher<> (use TodoItem, AppResult, etc.)
- Foundation Types: Data, URL, Date, UUID, Timer (prefix with App or use descriptive names)
- SwiftUI Types: View, Text, Image, Button, Color (use Screen, Label, Photo, etc.)
- Swift Types: Error, State, Action, Never (use AppError, AppState, AppAction)
- For TODO apps: MUST use "TodoItem" NOT "Task"
- For TIMER apps: MUST use "AppTimer" or "CountdownTimer" NOT "Timer"
- For CALCULATOR apps: MUST use "CalculatorModel" NOT "Calculator" if needed

MANDATORY: Always prefix custom types to avoid conflicts (AppTimer, TodoItem, WeatherData, etc.)!"""
        
        return app_name, enhanced_description
    
    def validate_generated_code(self, generated_code: Dict) -> Tuple[bool, List[str]]:
        """Validate generated code for common issues"""
        issues = []
        
        if not generated_code or "files" not in generated_code:
            issues.append("No files generated")
            return False, issues
        
        # Check each file for reserved types
        for file in generated_code.get("files", []):
            content = file.get("content", "")
            path = file.get("path", "")
            
            # Check for reserved type definitions
            for reserved in self.reserved_types:
                # Check for struct/class/enum definitions
                if re.search(rf'\b(struct|class|enum)\s+{reserved}\b', content):
                    issues.append(f"{path}: Defines reserved type '{reserved}'")
                    
        return len(issues) == 0, issues
    
    def fix_reserved_types_in_code(self, generated_code: Dict) -> Dict:
        """Fix reserved type issues in generated code"""
        
        if not generated_code or "files" not in generated_code:
            return generated_code
        
        fixed_code = generated_code.copy()
        fixed_files = []
        
        for file in generated_code.get("files", []):
            content = file.get("content", "")
            path = file.get("path", "")
            
            # Apply replacements
            fixed_content = self._apply_type_replacements(content)
            
            fixed_files.append({
                "path": path,
                "content": fixed_content
            })
        
        fixed_code["files"] = fixed_files
        return fixed_code
    
    def _apply_type_replacements(self, content: str) -> str:
        """Apply type replacements to content"""
        
        # Replace type definitions
        for reserved, replacement in self.replacements.items():
            # Type definitions
            content = re.sub(rf'\b(struct|class|enum)\s+{reserved}\b', 
                           rf'\1 {replacement}', content)
            
            # Type annotations
            content = re.sub(rf':\s*{reserved}\b', f': {replacement}', content)
            content = re.sub(rf':\s*\[{reserved}\]', f': [{replacement}]', content)
            
            # Generic parameters
            content = re.sub(rf'<{reserved}>', f'<{replacement}>', content)
            
            # Array declarations
            content = re.sub(rf'\[{reserved}\]', f'[{replacement}]', content)
            
        return content
    
    def get_architecture_guidance(self, app_name: str, description: str) -> str:
        """Get architectural guidance from RAG based on app type"""
        
        if not self.rag_kb:
            return ""
        
        guidance = []
        
        # Search for architecture patterns
        arch_results = self.rag_kb.search(f"architecture {description}", k=2)
        
        for result in arch_results:
            if 'architecture' in result.get('tags', []):
                # Extract relevant patterns
                content = result.get('content', '')
                
                # Determine which architecture fits
                if 'simple' in description.lower() or 'basic' in description.lower():
                    if 'MVC' in content:
                        guidance.append("Use simple MVC pattern for this basic app")
                elif 'complex' in description.lower() or 'advanced' in description.lower():
                    if 'MVVM' in content:
                        guidance.append("Use MVVM pattern with ViewModels for complex state management")
                    if 'Coordinator' in content:
                        guidance.append("Consider Coordinator pattern for complex navigation")
                
                # Add best practices
                if 'best-practices' in result.get('tags', []):
                    solutions = result.get('solutions', [])
                    guidance.extend(solutions[:2])  # Add top 2 solutions
        
        return "\n".join(guidance) if guidance else ""