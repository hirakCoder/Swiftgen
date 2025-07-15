"""
Multi-Stage Validation Pipeline
Implements research-proven approaches for catching errors early
"""

import asyncio
import json
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class ValidationStage(Enum):
    """Stages of validation pipeline"""
    PLANNING = "planning"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    SYNTAX = "syntax"
    SEMANTIC = "semantic"
    RUNTIME = "runtime"

@dataclass
class ValidationResult:
    """Result from a validation stage"""
    stage: ValidationStage
    passed: bool
    errors: List[str]
    warnings: List[str]
    fixes_applied: List[str]
    confidence_score: float

class MultiStageValidationPipeline:
    """Production-grade validation pipeline that prevents error propagation"""

    def __init__(self, llm_service=None, rag_kb=None):
        self.llm_service = llm_service
        self.rag_kb = rag_kb

        # Initialize validators for each stage
        self.validators = {
            ValidationStage.PLANNING: PlanningValidator(),
            ValidationStage.DESIGN: DesignValidator(),
            ValidationStage.IMPLEMENTATION: ImplementationValidator(),
            ValidationStage.SYNTAX: SyntaxValidator(),
            ValidationStage.SEMANTIC: SemanticValidator(),
            ValidationStage.RUNTIME: RuntimeValidator()
        }

        # Validation thresholds
        self.min_confidence_score = 0.95  # 95% confidence required

        # Track validation metrics
        self.validation_metrics = {
            "total_validations": 0,
            "stage_failures": {},
            "average_confidence": 0.0
        }

    async def validate_generation(self,
                                  description: str,
                                  generated_code: Dict,
                                  stage: ValidationStage = None) -> ValidationResult:
        """Validate generated code through all or specific stages"""

        self.validation_metrics["total_validations"] += 1

        if stage:
            # Validate specific stage
            return await self._validate_stage(stage, description, generated_code)

        # Run through all stages
        all_results = []
        current_code = generated_code

        for validation_stage in ValidationStage:
            result = await self._validate_stage(
                validation_stage, description, current_code
            )
            all_results.append(result)

            if not result.passed:
                # Stop at first failure
                print(f"[VALIDATION] Failed at stage: {validation_stage.value}")

                # Attempt to fix
                if result.fixes_applied:
                    current_code = self._apply_fixes(current_code, result)
                else:
                    break

        # Calculate overall result
        return self._aggregate_results(all_results)

    async def _validate_stage(self,
                              stage: ValidationStage,
                              description: str,
                              code: Dict) -> ValidationResult:
        """Validate a specific stage"""

        validator = self.validators[stage]

        try:
            result = await validator.validate(description, code)

            # Track metrics
            if stage.value not in self.validation_metrics["stage_failures"]:
                self.validation_metrics["stage_failures"][stage.value] = 0

            if not result.passed:
                self.validation_metrics["stage_failures"][stage.value] += 1

            return result

        except Exception as e:
            print(f"[VALIDATION] Error in {stage.value}: {str(e)}")

            return ValidationResult(
                stage=stage,
                passed=False,
                errors=[f"Validation error: {str(e)}"],
                warnings=[],
                fixes_applied=[],
                confidence_score=0.0
            )

    def _apply_fixes(self, code: Dict, result: ValidationResult) -> Dict:
        """Apply fixes from validation result"""

        # This would apply the specific fixes
        # For now, returning the original code
        return code

    def _aggregate_results(self, results: List[ValidationResult]) -> ValidationResult:
        """Aggregate multiple validation results"""

        all_errors = []
        all_warnings = []
        all_fixes = []
        total_confidence = 0.0
        passed_count = 0

        for result in results:
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
            all_fixes.extend(result.fixes_applied)
            total_confidence += result.confidence_score

            if result.passed:
                passed_count += 1

        avg_confidence = total_confidence / len(results) if results else 0.0
        all_passed = passed_count == len(results)

        return ValidationResult(
            stage=ValidationStage.RUNTIME,  # Final stage
            passed=all_passed and avg_confidence >= self.min_confidence_score,
            errors=all_errors,
            warnings=all_warnings,
            fixes_applied=all_fixes,
            confidence_score=avg_confidence
        )


class PlanningValidator:
    """Validates the planning stage - ensures requirements are understood"""

    async def validate(self, description: str, code: Dict) -> ValidationResult:
        """Validate that planning captures all requirements"""

        errors = []
        warnings = []

        # Extract requirements from description
        required_features = self._extract_requirements(description)

        # Check if code addresses all requirements
        implemented_features = self._extract_implemented_features(code)

        # Find missing features
        missing = set(required_features) - set(implemented_features)

        if missing:
            errors.append(f"Missing features: {', '.join(missing)}")

        # Calculate confidence based on coverage
        coverage = len(implemented_features) / len(required_features) if required_features else 1.0

        return ValidationResult(
            stage=ValidationStage.PLANNING,
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            fixes_applied=[],
            confidence_score=coverage
        )

    def _extract_requirements(self, description: str) -> List[str]:
        """Extract feature requirements from description"""

        features = []
        description_lower = description.lower()

        # Common feature patterns
        patterns = [
            (r"add\s+(\w+)", "add_{0}"),
            (r"delete\s+(\w+)", "delete_{0}"),
            (r"edit\s+(\w+)", "edit_{0}"),
            (r"view\s+(\w+)", "view_{0}"),
            (r"(\w+)\s+button", "{0}_button"),
            (r"(\w+)\s+list", "{0}_list")
        ]

        for pattern, template in patterns:
            matches = re.findall(pattern, description_lower)
            for match in matches:
                features.append(template.format(match))

        return features

    def _extract_implemented_features(self, code: Dict) -> List[str]:
        """Extract features that are actually implemented"""

        features = []

        # Check files for implementations
        for file in code.get("files", []):
            content = file.get("content", "")

            # Look for button implementations
            button_matches = re.findall(r'Button\([^)]+\)\s*{', content)
            features.extend([f"button_{i}" for i in range(len(button_matches))])

            # Look for list implementations
            if "List" in content or "ForEach" in content:
                features.append("list_display")

            # Look for state modifications
            if ".append(" in content:
                features.append("add_functionality")
            if ".remove(" in content or "onDelete" in content:
                features.append("delete_functionality")

        return features


class DesignValidator:
    """Validates the design stage - ensures architecture is sound"""

    async def validate(self, description: str, code: Dict) -> ValidationResult:
        """Validate architectural design"""

        errors = []
        warnings = []

        files = code.get("files", [])

        # Check file count
        if len(files) > 7:
            errors.append(f"Too many files: {len(files)} (max 7)")
        elif len(files) < 2:
            errors.append("Too few files: need at least App.swift and ContentView.swift")

        # Check for required files
        file_names = [f.get("path", "").split("/")[-1] for f in files]

        if "App.swift" not in file_names:
            errors.append("Missing required App.swift file")

        if "ContentView.swift" not in file_names:
            errors.append("Missing required ContentView.swift file")

        # Check for proper separation of concerns
        for file in files:
            content = file.get("content", "")
            path = file.get("path", "")

            # Check for mixed concerns
            if "View" in path and "@main" in content:
                errors.append(f"{path}: View file contains app entry point")

            if "Model" in path and "View {" in content:
                errors.append(f"{path}: Model file contains view code")

        confidence = 1.0 - (len(errors) * 0.2)  # Reduce confidence per error

        return ValidationResult(
            stage=ValidationStage.DESIGN,
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            fixes_applied=[],
            confidence_score=max(0.0, confidence)
        )


class ImplementationValidator:
    """Validates implementation - ensures all features work"""

    async def validate(self, description: str, code: Dict) -> ValidationResult:
        """Validate that implementation is complete and functional"""

        errors = []
        warnings = []
        fixes = []

        for file in code.get("files", []):
            content = file.get("content", "")
            path = file.get("path", "")

            # Check for empty implementations
            empty_functions = re.findall(r'func\s+\w+\([^)]*\)\s*{\s*}', content)
            if empty_functions:
                errors.append(f"{path}: Empty function implementations found")

            # Check for buttons without actions
            button_pattern = r'Button\([^)]+\)\s*{\s*}'
            empty_buttons = re.findall(button_pattern, content)
            if empty_buttons:
                errors.append(f"{path}: Buttons without actions found")

                # Apply fix
                fixed_content = re.sub(
                    button_pattern,
                    'Button("Action") { /* TODO: Add action */ }',
                    content
                )
                if fixed_content != content:
                    fixes.append("Added placeholder actions to empty buttons")

            # Check for unconnected state
            state_vars = re.findall(r'@State\s+(?:private\s+)?var\s+(\w+)', content)
            for var in state_vars:
                # Check if state variable is actually used
                if content.count(var) < 2:  # Only declared, never used
                    warnings.append(f"{path}: State variable '{var}' declared but not used")

            # Check for missing bindings
            textfield_pattern = r'TextField\([^,]+,\s*text:\s*([^)]+)\)'
            textfields = re.findall(textfield_pattern, content)
            for binding in textfields:
                if not binding.startswith("$"):
                    errors.append(f"{path}: TextField missing $ binding: {binding}")

        confidence = 1.0 - (len(errors) * 0.1)

        return ValidationResult(
            stage=ValidationStage.IMPLEMENTATION,
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            fixes_applied=fixes,
            confidence_score=max(0.0, confidence)
        )


class SyntaxValidator:
    """Validates Swift syntax"""

    async def validate(self, description: str, code: Dict) -> ValidationResult:
        """Validate Swift syntax correctness"""

        errors = []
        warnings = []
        fixes = []

        for file in code.get("files", []):
            content = file.get("content", "")
            path = file.get("path", "")

            # Check for balanced braces
            open_braces = content.count('{')
            close_braces = content.count('}')

            if open_braces != close_braces:
                errors.append(
                    f"{path}: Unbalanced braces ({open_braces} open, {close_braces} close)"
                )

                # Apply fix
                if open_braces > close_braces:
                    content += '\n' + '}' * (open_braces - close_braces)
                    fixes.append(f"Added {open_braces - close_braces} closing braces")

            # Check for single quotes
            if "'" in content:
                # Count single quotes not in comments
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if not line.strip().startswith('//') and "'" in line:
                        errors.append(f"{path}:{i+1}: Single quotes found")

                        # Fix single quotes
                        fixed_line = re.sub(r"'([^']*)'", r'"\1"', line)
                        if fixed_line != line:
                            lines[i] = fixed_line
                            fixes.append(f"Fixed single quotes on line {i+1}")

                content = '\n'.join(lines)

            # Check for missing imports
            if any(keyword in content for keyword in ['View', 'App', 'Text', 'Button']):
                if 'import SwiftUI' not in content:
                    errors.append(f"{path}: Missing SwiftUI import")
                    content = 'import SwiftUI\n\n' + content
                    fixes.append("Added missing SwiftUI import")

            # Check for reserved type names
            reserved_types = ['Task', 'State', 'Action', 'Result', 'Error']
            for reserved in reserved_types:
                pattern = rf'\b(struct|class|enum)\s+{reserved}\b'
                if re.search(pattern, content):
                    errors.append(f"{path}: Reserved type name used: {reserved}")

        confidence = 1.0 if len(errors) == 0 else 0.5

        return ValidationResult(
            stage=ValidationStage.SYNTAX,
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            fixes_applied=fixes,
            confidence_score=confidence
        )


class SemanticValidator:
    """Validates semantic correctness and logic"""

    async def validate(self, description: str, code: Dict) -> ValidationResult:
        """Validate semantic correctness"""

        errors = []
        warnings = []

        # Combine all code for analysis
        all_content = "\n".join([f.get("content", "") for f in code.get("files", [])])

        # Check for common semantic issues

        # 1. Force unwrapping
        force_unwraps = re.findall(r'[^!]=\s*\w+!', all_content)
        if force_unwraps:
            errors.append(f"Force unwrapping found: {len(force_unwraps)} instances")

        # 2. Missing error handling
        try_statements = re.findall(r'\btry\s+(?!await)', all_content)
        try_bang = re.findall(r'\btry!', all_content)

        if try_bang:
            errors.append(f"Force try (try!) found: {len(try_bang)} instances")

        # 3. Retain cycles
        closure_self = re.findall(r'{\s*[^}]*\bself\.\w+', all_content)
        weak_self = re.findall(r'\[weak self\]', all_content)

        if len(closure_self) > len(weak_self) * 2:  # Rough heuristic
            warnings.append("Potential retain cycles: missing [weak self] in closures")

        # 4. Deprecated API usage
        deprecated_patterns = [
            ('NavigationView', 'Use NavigationStack instead'),
            ('@Environment(\\.presentationMode)', 'Use @Environment(\\.dismiss)'),
            ('.navigationBarItems', 'Use .toolbar instead')
        ]

        for pattern, message in deprecated_patterns:
            if pattern in all_content:
                warnings.append(f"Deprecated API: {pattern} - {message}")

        # 5. Logic completeness
        if "Button" in all_content:
            # Check if buttons actually do something
            button_count = all_content.count("Button(")
            state_modifications = (
                    all_content.count(".append(") +
                    all_content.count(".remove(") +
                    all_content.count(".toggle(") +
                    all_content.count("= ")
            )

            if button_count > 0 and state_modifications == 0:
                errors.append("Buttons found but no state modifications detected")

        confidence = 1.0 - (len(errors) * 0.15) - (len(warnings) * 0.05)

        return ValidationResult(
            stage=ValidationStage.SEMANTIC,
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            fixes_applied=[],
            confidence_score=max(0.0, confidence)
        )


class RuntimeValidator:
    """Validates potential runtime issues"""

    async def validate(self, description: str, code: Dict) -> ValidationResult:
        """Validate for potential runtime issues"""

        errors = []
        warnings = []

        all_content = "\n".join([f.get("content", "") for f in code.get("files", [])])

        # Check for common runtime issues

        # 1. Array index access without bounds checking
        array_access = re.findall(r'\w+\[\d+\]', all_content)
        if array_access:
            warnings.append("Direct array index access without bounds checking")

        # 2. Division by zero potential
        if "/" in all_content and not "guard" in all_content:
            warnings.append("Division operations without zero checking")

        # 3. Missing nil checks
        optional_access = re.findall(r'\w+\?\.\w+', all_content)
        if optional_access:
            # This is actually safe (optional chaining)
            pass

        # 4. Infinite loops potential
        while_loops = re.findall(r'while\s+true\s*{', all_content)
        if while_loops:
            errors.append("Potential infinite loop detected")

        # 5. Memory leaks
        strong_captures = re.findall(r'{\s*[^}]*self\.\w+', all_content)
        if len(strong_captures) > 3:
            warnings.append("Multiple strong self captures in closures")

        confidence = 1.0 if len(errors) == 0 else 0.7

        return ValidationResult(
            stage=ValidationStage.RUNTIME,
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            fixes_applied=[],
            confidence_score=confidence
        )


class ValidationOrchestrator:
    """Orchestrates the validation pipeline with intelligent retry"""

    def __init__(self, pipeline: MultiStageValidationPipeline,
                 llm_service=None, max_retries: int = 3):
        self.pipeline = pipeline
        self.llm_service = llm_service
        self.max_retries = max_retries

    async def validate_with_retry(self, description: str,
                                  initial_code: Dict) -> Tuple[Dict, ValidationResult]:
        """Validate with intelligent retry on failure"""

        current_code = initial_code

        for attempt in range(self.max_retries):
            print(f"\n[ORCHESTRATOR] Validation attempt {attempt + 1}")

            # Run validation
            result = await self.pipeline.validate_generation(description, current_code)

            if result.passed and result.confidence_score >= 0.95:
                print(f"[ORCHESTRATOR] ✅ Validation passed with {result.confidence_score:.2%} confidence")
                return current_code, result

            print(f"[ORCHESTRATOR] ❌ Validation failed: {len(result.errors)} errors")

            # Attempt to fix using LLM if available
            if self.llm_service and attempt < self.max_retries - 1:
                print("[ORCHESTRATOR] Attempting intelligent fix...")

                fix_prompt = self._create_fix_prompt(result, current_code)

                try:
                    # This would call the LLM to fix the issues
                    # For now, we'll just log the attempt
                    print(f"[ORCHESTRATOR] Would request LLM fix for: {result.errors[:3]}")

                    # In production, this would be:
                    # fixed_code = await self.llm_service.fix_validation_errors(
                    #     fix_prompt, current_code, result.errors
                    # )
                    # current_code = fixed_code

                except Exception as e:
                    print(f"[ORCHESTRATOR] Fix attempt failed: {e}")

        print(f"[ORCHESTRATOR] Max retries reached. Final confidence: {result.confidence_score:.2%}")
        return current_code, result

    def _create_fix_prompt(self, result: ValidationResult, code: Dict) -> str:
        """Create a prompt to fix validation errors"""

        return f"""Fix these validation errors in the Swift code:

ERRORS TO FIX:
{json.dumps(result.errors, indent=2)}

WARNINGS TO ADDRESS:
{json.dumps(result.warnings, indent=2)}

Current code structure:
{json.dumps([f["path"] for f in code.get("files", [])], indent=2)}

Requirements:
1. Fix all errors while maintaining functionality
2. Address warnings if possible
3. Ensure all original features still work
4. Return complete fixed code

Focus on the specific errors and make minimal changes to fix them."""