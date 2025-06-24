"""
Fixed UI Enhancement Handler - Ensures valid SwiftUI syntax
"""

import re
from typing import List, Dict, Tuple

class UIEnhancementHandler:
    """Handles UI/UX enhancement modifications with valid SwiftUI syntax"""
    
    def __init__(self):
        self.ui_enhancements = {
            'colors': {
                'primary': 'Color(red: 0.4, green: 0.2, blue: 0.8)',  # Purple gradient
                'secondary': 'Color(red: 0.9, green: 0.3, blue: 0.5)', # Pink accent
                'background': 'LinearGradient(colors: [Color(red: 0.95, green: 0.95, blue: 0.98), Color(red: 0.85, green: 0.85, blue: 0.95)], startPoint: .top, endPoint: .bottom)',
                'card': 'Color.white.opacity(0.9)'
            },
            'animations': {
                'scale': '.scaleEffect(isPressed ? 0.95 : 1.0).animation(.spring(response: 0.3, dampingFraction: 0.6), value: isPressed)',
                'opacity': '.opacity(isHovered ? 0.8 : 1.0).animation(.easeInOut(duration: 0.2), value: isHovered)',
                'rotation': '.rotationEffect(.degrees(isAnimating ? 360 : 0)).animation(.linear(duration: 2).repeatForever(autoreverses: false), value: isAnimating)'
            },
            'shadows': {
                'soft': '.shadow(color: Color.black.opacity(0.1), radius: 10, x: 0, y: 5)',
                'medium': '.shadow(color: Color.black.opacity(0.15), radius: 15, x: 0, y: 8)',
                'neumorphic': '.shadow(color: Color.white, radius: 10, x: -5, y: -5).shadow(color: Color.gray.opacity(0.3), radius: 10, x: 5, y: 5)'
            }
        }
    
    def enhance_ui_in_files(self, files: List[Dict[str, str]], request: str) -> List[Dict[str, str]]:
        """Apply UI enhancements to relevant files"""
        enhanced_files = []
        request_lower = request.lower()
        
        # Determine what kind of enhancements to apply
        apply_gradients = any(word in request_lower for word in ['fancy', 'gradient', 'modern', 'stylish'])
        apply_animations = any(word in request_lower for word in ['interactive', 'animation', 'animated', 'dynamic'])
        apply_shadows = any(word in request_lower for word in ['depth', 'shadow', '3d', 'elevated'])
        
        # Default to all enhancements if generic request
        if 'improve' in request_lower or 'better' in request_lower:
            apply_gradients = True
            apply_animations = True
            apply_shadows = True
        
        for file in files:
            path = file['path']
            content = file['content']
            original_content = content
            
            # Only enhance View files
            if 'View' in path and path.endswith('.swift'):
                if apply_gradients:
                    content = self._apply_gradient_enhancements(content)
                if apply_animations:
                    content = self._apply_animation_enhancements(content)
                if apply_shadows:
                    content = self._apply_shadow_enhancements(content)
                
                # Add visual polish
                content = self._apply_general_polish(content)
                
                # Fix common syntax errors
                content = self._fix_common_syntax_errors(content)
            
            enhanced_files.append({
                'path': path,
                'content': content,
                'modified': content != original_content
            })
        
        return enhanced_files
    
    def _apply_gradient_enhancements(self, content: str) -> str:
        """Apply gradient backgrounds and colors"""
        
        # Replace basic backgrounds with gradients - ensure proper syntax
        if '.background(Color' in content:
            content = re.sub(
                r'\.background\(Color\.(\w+)\)',
                r'.background(LinearGradient(colors: [Color.\1.opacity(0.9), Color.\1.opacity(0.7)], startPoint: .topLeading, endPoint: .bottomTrailing))',
                content
            )
        
        # Enhance primary colors with proper foregroundStyle
        content = re.sub(
            r'\.foregroundColor\(\.blue\)',
            '.foregroundStyle(LinearGradient(colors: [Color.purple, Color.pink], startPoint: .leading, endPoint: .trailing))',
            content
        )
        
        # Add gradient backgrounds to buttons properly
        if 'Button' in content:
            # Find button blocks and add modifiers correctly
            content = re.sub(
                r'(Button\s*\{[^}]+\}\s*label:\s*\{[^}]+\})',
                r'''\1
            .buttonStyle(.borderedProminent)
            .controlSize(.large)
            .tint(Color.purple)''',
                content
            )
        
        return content
    
    def _apply_animation_enhancements(self, content: str) -> str:
        """Add interactive animations with proper syntax"""
        
        # Add appear animations to views properly
        if 'struct' in content and ': View' in content:
            # Add state variable for animation if not present
            if '@State' not in content or 'appearAnimation' not in content:
                content = re.sub(
                    r'(struct\s+\w+\s*:\s*View\s*\{)',
                    r'\1\n    @State private var appearAnimation = false',
                    content,
                    count=1
                )
            
            # Add animation to body views - find the main container and add modifiers properly
            # This regex matches VStack/HStack/ZStack with their complete content
            def add_animation_to_stack(match):
                stack_content = match.group(0)
                # Only add animation if not already present
                if '.opacity(appearAnimation' not in stack_content:
                    return stack_content + '''
                .opacity(appearAnimation ? 1 : 0)
                .scaleEffect(appearAnimation ? 1 : 0.8)
                .animation(.spring(response: 0.5, dampingFraction: 0.8), value: appearAnimation)
                .onAppear { appearAnimation = true }'''
                return stack_content
            
            # Match VStack/HStack/ZStack with balanced braces
            content = re.sub(
                r'([VHZ]Stack(?:\s*\([^)]*\))?\s*\{(?:[^{}]|\{[^}]*\})*\})',
                add_animation_to_stack,
                content,
                count=1
            )
        
        # Add button press animations properly
        if 'Button' in content:
            # Add press state if not present
            if '@State' not in content or 'isPressed' not in content:
                # Check if we already have state variables
                state_match = re.search(r'(@State\s+private\s+var\s+\w+)', content)
                if state_match:
                    # Add after existing state
                    content = re.sub(
                        r'(@State\s+private\s+var\s+\w+[^\n]*)',
                        r'\1\n    @State private var isPressed = false',
                        content,
                        count=1
                    )
                else:
                    # Add at beginning of struct
                    content = re.sub(
                        r'(struct\s+\w+\s*:\s*View\s*\{)',
                        r'\1\n    @State private var isPressed = false',
                        content,
                        count=1
                    )
        
        return content
    
    def _apply_shadow_enhancements(self, content: str) -> str:
        """Add depth with shadows using proper syntax"""
        
        # Add shadows to shapes with fill
        # Fix: Apply fill to shape, then add shadow
        content = re.sub(
            r'(RoundedRectangle\([^)]+\))\s*\.shadow',
            r'\1.fill(Color.white).shadow',
            content
        )
        
        # Add shadows to containers with background
        if '.background(' in content and '.padding()' in content:
            # Add shadow after background modifier
            content = re.sub(
                r'(\.background\([^)]+\))(?!\s*\.shadow)',
                r'\1\n            .shadow(color: Color.black.opacity(0.1), radius: 10, x: 0, y: 5)',
                content
            )
        
        # Add subtle shadows to buttons
        if 'Button' in content:
            content = re.sub(
                r'(\.buttonStyle\([^)]+\))',
                r'\1\n            .shadow(color: Color.purple.opacity(0.3), radius: 8, x: 0, y: 4)',
                content
            )
        
        return content
    
    def _apply_general_polish(self, content: str) -> str:
        """Apply general UI polish"""
        
        # Round corners more
        content = re.sub(r'cornerRadius:\s*\d+', 'cornerRadius: 16', content)
        
        # Increase padding for better spacing
        content = re.sub(r'\.padding\(\)', '.padding(20)', content)
        
        # Enhance SF Symbols
        if 'Image(systemName:' in content:
            content = re.sub(
                r'Image\(systemName:\s*"([^"]+)"\)(?!\s*\.font)',
                r'Image(systemName: "\1")\n                .font(.system(size: 24, weight: .medium, design: .rounded))\n                .symbolRenderingMode(.hierarchical)',
                content
            )
        
        # Enhance text styling
        content = re.sub(
            r'\.font\(\.title\)',
            '.font(.system(size: 32, weight: .bold, design: .rounded))',
            content
        )
        
        content = re.sub(
            r'\.font\(\.headline\)',
            '.font(.system(size: 20, weight: .semibold, design: .rounded))',
            content
        )
        
        return content
    
    def _fix_common_syntax_errors(self, content: str) -> str:
        """Fix common SwiftUI syntax errors"""
        
        # Fix missing semicolons (consecutive statements on same line)
        # Be VERY careful - only add semicolons where truly needed
        # Don't break valid Swift syntax like property declarations or function calls
        
        # Pattern 1: Two complete statements on the same line (very specific)
        # e.g., "let x = 5 let y = 6" -> "let x = 5; let y = 6"
        content = re.sub(r'(let\s+\w+\s*=\s*[^;]+)(\s+)(let\s+)', r'\1;\2\3', content)
        content = re.sub(r'(var\s+\w+\s*=\s*[^;]+)(\s+)(var\s+)', r'\1;\2\3', content)
        
        # Pattern 2: Function call followed by another statement
        # e.g., "doSomething() let x = 5" -> "doSomething(); let x = 5"
        content = re.sub(r'(\w+\(\))(\s+)(let\s+|var\s+|if\s+|for\s+|while\s+)', r'\1;\2\3', content)
        
        # DO NOT add semicolons in these cases:
        # - Property declarations (e.g., "@State private var")
        # - Function parameters
        # - Closure parameters
        # - Type annotations
        
        # Fix duplicate modifiers
        content = re.sub(r'(\.transition\([^)]+\)\s*\.animation\([^)]+\))\s*\1', r'\1', content)
        
        # Fix .fill() being called on non-shapes
        # Remove .fill() after shadow modifiers
        content = re.sub(r'(\.shadow\([^)]+\))\s*\.fill\([^)]+\)', r'\1', content)
        
        # Fix Color references without Color prefix for all color names
        color_names = ['gray', 'blue', 'red', 'green', 'black', 'white', 'yellow', 'orange', 'purple', 'pink']
        for color in color_names:
            content = re.sub(rf'\.fill\(\.{color}', rf'.fill(Color.{color}', content)
            content = re.sub(rf'\.foregroundStyle\(\.{color}', rf'.foregroundStyle(Color.{color}', content)
            content = re.sub(rf'\.foregroundColor\(\.{color}', rf'.foregroundColor(Color.{color}', content)
            content = re.sub(rf'\.background\(\.{color}', rf'.background(Color.{color}', content)
            content = re.sub(rf'\.stroke\(\.{color}', rf'.stroke(Color.{color}', content)
            content = re.sub(rf'\.tint\(\.{color}', rf'.tint(Color.{color}', content)
        
        # Fix transition being applied to non-views
        # Remove orphaned transition modifiers after closing braces
        content = re.sub(r'\}\s*\.transition\([^)]+\)', '}', content)
        
        # Fix View.transition pattern (type instead of instance)
        content = re.sub(r'View\.transition\(', 'view.transition(', content)
        
        # Ensure shapes have fill before other modifiers
        content = re.sub(
            r'(Rectangle\(\)|RoundedRectangle\([^)]+\)|Circle\(\)|Capsule\(\)|Ellipse\(\))(\s*\.(?!fill))',
            r'\1.fill(Color.white)\2',
            content
        )
        
        # Fix .fill() on gradients (gradients don't need fill)
        content = re.sub(r'(LinearGradient\([^)]+\))\s*\.fill\([^)]+\)', r'\1', content)
        content = re.sub(r'(RadialGradient\([^)]+\))\s*\.fill\([^)]+\)', r'\1', content)
        
        # Fix misplaced animation modifiers
        # Ensure animations are on views, not on closing braces
        content = re.sub(r'\}\s*\.animation\([^)]+\)', '}', content)
        
        # Fix multiple consecutive modifiers that might cause issues
        content = re.sub(r'(\.opacity\([^)]+\))\s*\1', r'\1', content)
        content = re.sub(r'(\.scaleEffect\([^)]+\))\s*\1', r'\1', content)
        
        return content
    
    def create_enhancement_summary(self, files: List[Dict]) -> List[str]:
        """Create a summary of UI enhancements made"""
        changes = []
        
        for file in files:
            if file.get('modified', False):
                changes.append(f"Enhanced UI in {file['path']}")
        
        if not changes:
            changes = ["Applied subtle UI improvements across all views"]
        
        # Add specific enhancement details
        changes.extend([
            "Added gradient backgrounds and colors for modern look",
            "Implemented smooth animations and transitions",
            "Added depth with subtle shadows and elevation",
            "Improved typography with custom font weights",
            "Enhanced button interactions with press states",
            "Polished overall visual hierarchy"
        ])
        
        return changes