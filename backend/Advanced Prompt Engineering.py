"""
Advanced Prompt Engineering for SwiftGen AI
Implements state-of-the-art prompting techniques for consistent quality
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import hashlib

class AdvancedPromptEngineering:
    """Advanced prompt engineering techniques for production-quality generation"""

    def __init__(self, rag_kb=None):
        self.rag_kb = rag_kb

        # Prompt templates for different stages
        self.prompt_templates = {
            "analysis": self._load_analysis_template(),
            "generation": self._load_generation_template(),
            "validation": self._load_validation_template(),
            "healing": self._load_healing_template()
        }

        # Few-shot examples for different app types
        self.few_shot_examples = self._load_few_shot_examples()

        # Chain-of-thought prompting patterns
        self.cot_patterns = self._load_cot_patterns()

        # Constraint library
        self.constraints = SwiftConstraintsLibrary()

        # Track prompt effectiveness
        self.prompt_metrics = PromptOptimizer()

    def create_multi_stage_prompt(self, description: str, app_name: str,
                                  stage: str = "generation") -> str:
        """Create a multi-stage prompt with advanced techniques"""

        prompt_hash = hashlib.md5(f"{description}{app_name}{stage}".encode()).hexdigest()[:8]

        if stage == "analysis":
            return self._create_analysis_prompt(description, app_name)
        elif stage == "generation":
            return self._create_generation_prompt(description, app_name, prompt_hash)
        elif stage == "validation":
            return self._create_validation_prompt(description, app_name)
        elif stage == "healing":
            return self._create_healing_prompt(description, app_name)
        else:
            return self._create_generation_prompt(description, app_name, prompt_hash)

    def _create_generation_prompt(self, description: str, app_name: str,
                                  prompt_hash: str) -> str:
        """Create generation prompt with all advanced techniques"""

        # Get optimization suggestions from past runs
        suggestions = self.prompt_metrics.get_optimization_suggestions(prompt_hash)

        # Build the ultimate prompt
        prompt_parts = []

        # 1. Role-based prompting with expertise
        prompt_parts.append(self._get_expert_role())

        # 2. Chain-of-thought reasoning
        prompt_parts.append(self._get_cot_reasoning(description))

        # 3. Few-shot examples
        prompt_parts.append(self._get_relevant_examples(description))

        # 4. Explicit constraints
        prompt_parts.append(self.constraints.get_all_constraints())

        # 5. Self-consistency checks
        prompt_parts.append(self._get_self_consistency_instructions())

        # 6. Output format specification
        prompt_parts.append(self._get_output_format(app_name))

        # 7. Anti-hallucination rules
        prompt_parts.append(self._get_anti_hallucination_rules())

        # 8. Quality checkpoints
        prompt_parts.append(self._get_quality_checkpoints())

        # Apply optimization suggestions
        if suggestions:
            prompt_parts.append("\nADDITIONAL FOCUS AREAS:")
            prompt_parts.extend(f"- {suggestion}" for suggestion in suggestions)

        return "\n\n".join(prompt_parts)

    def _get_expert_role(self) -> str:
        """Define expert role with specific expertise"""

        return """You are a Senior iOS Developer at Apple with 15+ years of experience.
You specialize in:
- SwiftUI and modern iOS development patterns
- Production-ready, scalable app architecture
- Apple Human Interface Guidelines
- Performance optimization and accessibility
- Creating unique, innovative user experiences

You NEVER create generic or template-based apps. Each app you build is a unique masterpiece."""

    def _get_cot_reasoning(self, description: str) -> str:
        """Chain-of-thought reasoning structure"""

        return f"""Before generating code, think through these steps:

1. UNDERSTAND THE REQUEST:
   - What is the core purpose of this app?
   - Who is the target user?
   - What makes this app unique?

2. DESIGN THE ARCHITECTURE:
   - What data models are needed?
   - What views and navigation structure?
   - What state management approach?

3. PLAN UNIQUE FEATURES:
   - What innovative UI elements can enhance the experience?
   - What delightful animations or interactions?
   - What accessibility features?

4. IMPLEMENT WITH QUALITY:
   - Ensure every file has proper imports
   - Use modern iOS 16+ patterns
   - Handle all edge cases
   - Make it production-ready

For this app: "{description}"

Now implement following this thought process."""

    def _get_self_consistency_instructions(self) -> str:
        """Self-consistency and verification instructions"""

        return """SELF-VERIFICATION CHECKLIST:
Before finalizing your response, verify:
□ Every Swift file starts with required imports
□ No single quotes used for strings (only double quotes)
□ No reserved type names (Task, State, Action)
□ All user interactions have implementations
□ Unique visual design specific to this app
□ Smooth animations and transitions
□ Proper error handling
□ Accessibility features included"""

    def _get_output_format(self, app_name: str) -> str:
        """Explicit output format specification"""

        safe_name = re.sub(r'[^a-zA-Z0-9]', '', app_name)

        return f"""OUTPUT FORMAT (JSON ONLY):
{{
    "app_name": "{app_name}",
    "bundle_id": "com.swiftgen.{safe_name.lower()[:20]}",
    "description": "Brief description of your unique implementation",
    "files": [
        {{
            "path": "Sources/App.swift",
            "content": "// COMPLETE Swift code with ALL imports"
        }},
        {{
            "path": "Sources/ContentView.swift", 
            "content": "// COMPLETE implementation"
        }}
        // Add all necessary files
    ],
    "features": ["List of implemented unique features"],
    "unique_elements": ["What makes this app special"],
    "technical_highlights": ["Advanced techniques used"]
}}

CRITICAL: Return ONLY the JSON, no explanatory text before or after."""

    def _get_anti_hallucination_rules(self) -> str:
        """Rules to prevent hallucination and ensure accuracy"""

        return """ANTI-HALLUCINATION RULES:
1. DO NOT reference files you haven't created
2. DO NOT use placeholder or TODO comments
3. DO NOT create empty implementations
4. DO NOT import non-existent modules
5. DO NOT use external dependencies
6. ONLY use standard iOS frameworks (SwiftUI, Foundation, Combine)
7. ENSURE all code compiles without errors
8. IMPLEMENT all features completely"""

    def _get_quality_checkpoints(self) -> str:
        """Quality checkpoints for self-validation"""

        return """QUALITY CHECKPOINTS:
✓ Unique Design: Is this app visually distinctive?
✓ Complete Features: Are all requested features implemented?
✓ Smooth UX: Are animations and transitions polished?
✓ Error Free: Will this compile without any errors?
✓ Best Practices: Does this follow iOS best practices?
✓ Accessibility: Can users with disabilities use this app?
✓ Performance: Is the code optimized for performance?"""

    def _create_validation_prompt(self, description: str, app_name: str) -> str:
        """Create prompt for code validation"""

        return f"""Validate this iOS app code for production readiness.

App: {app_name}
Description: {description}

Check for:
1. Syntax Errors:
   - Balanced braces {{}}
   - All strings use double quotes "
   - No unterminated strings
   
2. Swift-Specific:
   - No reserved type names (Task, State, Action)
   - Proper optional handling (no force unwrap)
   - Modern iOS 16+ APIs used
   
3. Functionality:
   - All buttons have actions
   - All state changes update UI
   - All user inputs handled

If you find ANY errors, return:
{{
    "has_errors": true,
    "errors": ["description of each error"],
    "fixed_code": "corrected version"
}}

If no errors found:
{{
    "has_errors": false,
    "validation_passed": true
}}"""

    def _create_healing_prompt(self, description: str, app_name: str) -> str:
        """Create prompt for healing/fixing code"""

        return f"""Fix these iOS app compilation errors while maintaining all functionality.

App: {app_name}
Original Purpose: {description}

REQUIREMENTS:
1. Fix ALL compilation errors
2. Ensure proper imports in every file
3. Maintain the unique design and features
4. Keep the same user experience
5. Use iOS 16+ patterns

Return the complete fixed code in the same JSON format."""

    def _create_analysis_prompt(self, description: str, app_name: str) -> str:
        """Create prompt for requirement analysis"""

        return f"""Analyze this iOS app request and identify key requirements.

Request: "{description}"
App Name: {app_name}

Identify:
1. Core Features Needed
2. UI/UX Requirements
3. Data Models Required
4. Technical Challenges
5. Unique Opportunities

Return structured analysis to guide implementation."""

    def _load_analysis_template(self) -> str:
        """Load analysis phase template"""

        return """Analyze the request systematically:
- Target audience and use case
- Essential features vs nice-to-have
- Technical requirements and constraints
- Opportunities for innovation"""

    def _load_generation_template(self) -> str:
        """Load generation phase template"""

        return """Generate production-ready code:
- Start with architecture design
- Implement core functionality first
- Add polish and animations
- Ensure accessibility
- Optimize performance"""

    def _load_validation_template(self) -> str:
        """Load validation phase template"""

        return """Validate code quality:
- Syntax and compilation checks
- Best practices adherence
- User experience completeness
- Performance considerations
- Security and privacy"""

    def _load_healing_template(self) -> str:
        """Load healing phase template"""

        return """Fix issues while preserving intent:
- Understand the original goal
- Fix compilation errors
- Maintain functionality
- Improve code quality
- Document changes"""

    def _load_cot_patterns(self) -> Dict:
        """Load chain-of-thought patterns"""

        return {
            "architecture": "First, I'll design the overall architecture...",
            "features": "Next, I'll implement each feature systematically...",
            "polish": "Finally, I'll add polish and refinements...",
            "review": "Let me review and ensure everything works..."
        }

    def _load_few_shot_examples(self) -> Dict:
        """Load few-shot examples for different app types"""

        return {
            "todo": {
                "description": "A unique todo app with gesture-based priority",
                "key_patterns": [
                    "Swipe gestures for priority setting",
                    "Celebration animations on completion",
                    "Color-coded priority system",
                    "Smooth spring animations"
                ]
            },
            "calculator": {
                "description": "A calculator with neumorphic design",
                "key_patterns": [
                    "Neumorphic button design",
                    "Haptic feedback integration",
                    "Calculation history display",
                    "Smooth press animations"
                ]
            },
            "timer": {
                "description": "A timer with circular progress",
                "key_patterns": [
                    "Circular progress animation",
                    "Gradient background transitions",
                    "Quick preset buttons",
                    "Visual completion feedback"
                ]
            }
        }

    def _get_relevant_examples(self, description: str) -> str:
        """Get relevant few-shot examples based on description"""

        # Detect app type
        app_type = self._detect_app_type(description)

        if app_type in self.few_shot_examples:
            example = self.few_shot_examples[app_type]
            return f"""
EXAMPLE OF EXCELLENCE:
A similar app that demonstrates unique implementation:

{example['description']}

Key patterns used:
{chr(10).join(f'- {pattern}' for pattern in example['key_patterns'])}

Your implementation should be equally unique and polished."""

        return "Create something unique and memorable, not a generic template."

    def _detect_app_type(self, description: str) -> str:
        """Detect app type from description"""

        desc_lower = description.lower()

        if any(word in desc_lower for word in ["todo", "task", "list", "checklist"]):
            return "todo"
        elif any(word in desc_lower for word in ["calculator", "calculate", "math"]):
            return "calculator"
        elif any(word in desc_lower for word in ["timer", "countdown", "stopwatch"]):
            return "timer"
        else:
            return "generic"


class SwiftConstraintsLibrary:
    """Library of Swift-specific constraints and patterns"""

    def get_all_constraints(self) -> str:
        """Get all constraints formatted for prompts"""

        return f"""
MANDATORY SWIFT CONSTRAINTS:

{self.get_import_rules()}

{self.get_naming_rules()}

{self.get_syntax_rules()}

{self.get_ios16_patterns()}

{self.get_forbidden_patterns()}

{self.get_required_patterns()}"""

    def get_import_rules(self) -> str:
        """Get import rules"""

        return """IMPORT RULES (CRITICAL):
1. EVERY Swift file MUST start with necessary imports
2. Check what each file uses and add ALL required imports:
   - SwiftUI: for ANY View, Text, Button, VStack, Color, etc.
   - Foundation: for UUID, Date, URL, Timer, etc.
   - Combine: for @Published, ObservableObject, etc.
3. ViewModels referencing SwiftUI types MUST import SwiftUI
4. Order: SwiftUI first, then Foundation, then Combine"""

    def get_naming_rules(self) -> str:
        """Get naming rules"""

        return """NAMING RULES:
1. NEVER use these reserved names:
   - struct/class Task → use TodoItem, UserTask, WorkItem
   - struct/class State → use AppState, ViewState, UIState  
   - struct/class Action → use AppAction, UserAction, ViewAction
2. Use descriptive, specific names
3. Follow Swift naming conventions (camelCase, PascalCase)
4. Avoid generic names like "Model", "Data", "Manager\""""

    def get_syntax_rules(self) -> str:
        """Get syntax rules"""

        return """SYNTAX RULES:
1. Strings: ALWAYS use double quotes " never single quotes '
2. Optionals: Use if let or guard let (never force unwrap with !)
3. Arrays: Initialize as var items: [Type] = []
4. Closures: Use trailing closure syntax
5. Properties: Prefer computed properties over functions for simple getters"""

    def get_ios16_patterns(self) -> str:
        """Get iOS 16+ patterns"""

        return """iOS 16+ PATTERNS:
1. Navigation: NavigationStack not NavigationView
2. Dismissal: @Environment(\.dismiss) not presentationMode
3. Lists: .listStyle(.plain) or .listStyle(.insetGrouped)
4. Sheets: .sheet(isPresented:) with proper state
5. Animations: .animation(.spring(), value:) with explicit values"""

    def get_forbidden_patterns(self) -> str:
        """Get forbidden patterns"""

        return """FORBIDDEN PATTERNS:
1. NO external dependencies or import of non-standard libraries
2. NO force unwrapping (!)
3. NO single quotes for strings
4. NO empty implementations or TODO comments
5. NO references to files not being created
6. NO complex async operations without proper handling"""

    def get_required_patterns(self) -> str:
        """Get required patterns"""

        return """REQUIRED PATTERNS:
1. @main struct for app entry point
2. Proper view modifiers for layout
3. State management with @State, @StateObject, @ObservedObject
4. Gesture handling for interactive elements
5. Animations for state changes
6. Accessibility labels for UI elements"""


class PromptOptimizer:
    """Track and optimize prompt effectiveness"""

    def __init__(self):
        self.success_metrics = {}
        self.failure_patterns = {}

    def record_outcome(self, prompt_hash: str, success: bool,
                       errors: List[str] = None):
        """Record outcome of a prompt"""

        if prompt_hash not in self.success_metrics:
            self.success_metrics[prompt_hash] = {
                "attempts": 0,
                "successes": 0,
                "failures": 0,
                "error_types": {}
            }

        metrics = self.success_metrics[prompt_hash]
        metrics["attempts"] += 1

        if success:
            metrics["successes"] += 1
        else:
            metrics["failures"] += 1

            # Categorize errors
            if errors:
                for error in errors:
                    error_type = self._categorize_error(error)
                    metrics["error_types"][error_type] = metrics["error_types"].get(error_type, 0) + 1

    def _categorize_error(self, error: str) -> str:
        """Categorize error type"""

        error_lower = error.lower()

        if "import" in error_lower:
            return "missing_import"
        elif "task" in error_lower or "state" in error_lower:
            return "reserved_type"
        elif "'" in error or "single quote" in error_lower:
            return "single_quotes"
        elif "force unwrap" in error_lower:
            return "force_unwrap"
        else:
            return "other"

    def get_optimization_suggestions(self, prompt_hash: str) -> List[str]:
        """Get suggestions for improving a prompt"""

        if prompt_hash not in self.success_metrics:
            return []

        metrics = self.success_metrics[prompt_hash]
        suggestions = []

        # Analyze error patterns
        if metrics["attempts"] > 0:
            success_rate = metrics["successes"] / metrics["attempts"]

            if success_rate < 0.95:  # Below 95% success
                # Most common errors
                for error_type, count in sorted(
                        metrics["error_types"].items(),
                        key=lambda x: x[1],
                        reverse=True
                )[:3]:
                    if error_type == "missing_import":
                        suggestions.append("Triple-check that EVERY file has necessary imports at the top")
                    elif error_type == "reserved_type":
                        suggestions.append("Be extra careful to avoid Task/State/Action as type names")
                    elif error_type == "single_quotes":
                        suggestions.append("Ensure ALL strings use double quotes, check every string literal")
                    elif error_type == "force_unwrap":
                        suggestions.append("Use safe unwrapping with if let or guard let")

        return suggestions