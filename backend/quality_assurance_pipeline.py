"""
Quality Assurance Pipeline for SwiftGen AI
Comprehensive validation to ensure generated apps will build successfully
"""

import re
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class ValidationResult:
    """Result of a validation check"""
    def __init__(self, success: bool, errors: List[str] = None, warnings: List[str] = None, validator: str = ""):
        self.success = success
        self.errors = errors or []
        self.warnings = warnings or []
        self.validator = validator
        self.timestamp = datetime.now().isoformat()

class BaseValidator:
    """Base class for all validators"""
    def __init__(self):
        self.name = self.__class__.__name__

    async def validate(self, generated_code: Dict) -> ValidationResult:
        """Override this method in subclasses"""
        raise NotImplementedError

class DependencyValidator(BaseValidator):
    """Validates that no phantom dependencies exist"""

    def __init__(self):
        super().__init__()
        self.phantom_patterns = [
            r'\bclass\s+\w+Service\b',
            r'\bstruct\s+\w+Service\b',
            r'import\s+(?!SwiftUI|Foundation|Combine|UIKit|AVFoundation|MapKit|PhotosUI)\w+',
            r'@Dependency\(',
            r'DependencyContainer',
            r'\.shared\.',  # Singleton patterns that might not exist
        ]

    async def validate(self, generated_code: Dict) -> ValidationResult:
        errors = []
        warnings = []

        if not generated_code.get("files"):
            return ValidationResult(False, ["No files to validate"], validator=self.name)

        for file in generated_code["files"]:
            content = file.get("content", "")
            path = file.get("path", "")

            # Check for phantom dependencies
            for pattern in self.phantom_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    for match in matches:
                        # Allow self-contained services defined in the same file
                        if "Service" in match and f"class {match.split()[-1]}" in content:
                            continue
                        # Allow services defined in other files in the project
                        if "Service" in match:
                            service_name = match.split()[-1] if ' ' in match else match
                            # Check if service is defined in any other file
                            service_defined = any(
                                service_name in f.get("content", "") 
                                for f in generated_code.get("files", [])
                            )
                            if service_defined:
                                continue
                        # Skip common iOS imports
                        if match.startswith("import") and any(
                            allowed in match for allowed in 
                            ["CoreLocation", "CoreData", "CloudKit", "StoreKit", "HealthKit"]
                        ):
                            continue
                        errors.append(f"{path}: Found phantom dependency: {match}")

            # Check for references to undefined types
            type_references = re.findall(r':\s*(\w+)(?:\s*{)?', content)
            struct_definitions = re.findall(r'struct\s+(\w+)', content)
            class_definitions = re.findall(r'class\s+(\w+)', content)
            enum_definitions = re.findall(r'enum\s+(\w+)', content)

            defined_types = set(struct_definitions + class_definitions + enum_definitions)

            # Add Swift built-in types and common framework types
            built_in_types = {
                # Swift Standard Library
                'String', 'Int', 'Double', 'Float', 'Bool', 'Date', 'UUID', 'URL',
                'Array', 'Dictionary', 'Set', 'Optional', 'Any', 'AnyObject', 'Void',
                'Data', 'TimeInterval', 'CGFloat', 'CGPoint', 'CGSize', 'CGRect',
                # SwiftUI
                'View', 'some', 'ObservableObject', 'Published', 'State', 'Binding',
                'StateObject', 'ObservedObject', 'EnvironmentObject', 'Environment',
                'Color', 'Image', 'Text', 'Button', 'VStack', 'HStack', 'ZStack',
                'List', 'ForEach', 'NavigationStack', 'NavigationView', 'Scene',
                'ScrollView', 'Form', 'Section', 'Picker', 'Toggle', 'TextField',
                'SecureField', 'TextEditor', 'DatePicker', 'Slider', 'Stepper',
                'TabView', 'Sheet', 'Alert', 'ActionSheet', 'GeometryReader',
                # Combine
                'PassthroughSubject', 'CurrentValueSubject', 'AnyCancellable',
                'Publisher', 'Cancellable', 'Future', 'Just',
                # Common patterns
                'Codable', 'Encodable', 'Decodable', 'Identifiable', 'Hashable',
                'Equatable', 'Comparable', 'CustomStringConvertible',
                # Async
                'Task', 'MainActor', 'async', 'await',
                # Core Data
                'NSManagedObject', 'NSPersistentContainer', 'NSManagedObjectContext'
            }

            for type_ref in type_references:
                if type_ref not in defined_types and type_ref not in built_in_types:
                    if not type_ref.endswith('View') and not type_ref.endswith('Model'):
                        warnings.append(f"{path}: Possible undefined type: {type_ref}")

        return ValidationResult(len(errors) == 0, errors, warnings, self.name)

class NamingConflictValidator(BaseValidator):
    """Validates that no reserved types are used"""

    def __init__(self):
        super().__init__()
        self.reserved_types = {
            'Task', 'State', 'Action', 'Result', 'Error', 'Never'
        }

    async def validate(self, generated_code: Dict) -> ValidationResult:
        errors = []

        for file in generated_code.get("files", []):
            content = file.get("content", "")
            path = file.get("path", "")

            for reserved in self.reserved_types:
                # Check for struct/class/enum definitions
                if re.search(rf'\b(struct|class|enum)\s+{reserved}\b', content):
                    errors.append(f"{path}: Reserved type conflict: {reserved}")

                # Check for extensions
                if re.search(rf'\bextension\s+{reserved}\b', content):
                    errors.append(f"{path}: Extension of reserved type: {reserved}")

        return ValidationResult(len(errors) == 0, errors, validator=self.name)

class ArchitectureValidator(BaseValidator):
    """Validates architectural consistency and simplicity"""

    def __init__(self):
        super().__init__()
        self.max_files = 100  # Support real apps with many files
        self.max_file_size = 5000  # Support larger files for complex logic
        self.required_files = ["App.swift"]

    async def validate(self, generated_code: Dict) -> ValidationResult:
        errors = []
        warnings = []

        files = generated_code.get("files", [])

        # Check file count
        if len(files) > self.max_files:
            warnings.append(f"Too many files: {len(files)} (max: {self.max_files})")

        # Check for required files
        file_paths = [f.get("path", "") for f in files]

        for required in self.required_files:
            if not any(required in path for path in file_paths):
                errors.append(f"Missing required file: {required}")

        # Check file sizes
        for file in files:
            content = file.get("content", "")
            lines = content.count('\n')
            if lines > self.max_file_size:
                warnings.append(f"{file.get('path', '')}: File too large ({lines} lines)")

        # Check for @main
        has_main = any("@main" in f.get("content", "") for f in files)
        if not has_main:
            errors.append("Missing @main app entry point")

        # Check for over-engineering
        total_content = " ".join(f.get("content", "") for f in files)

        complexity_indicators = [
            "Protocol",
            "Dependency",
            "Repository",
            "Coordinator",
            "Router",
            "Interactor",
            "Presenter"
        ]

        complexity_score = sum(1 for indicator in complexity_indicators if indicator in total_content)
        if complexity_score > 3:
            warnings.append(f"Potentially over-engineered (complexity score: {complexity_score})")

        return ValidationResult(len(errors) == 0, errors, warnings, self.name)

class AppleGuidelinesValidator(BaseValidator):
    """Validates compliance with Apple Human Interface Guidelines"""

    async def validate(self, generated_code: Dict) -> ValidationResult:
        errors = []
        warnings = []

        for file in generated_code.get("files", []):
            content = file.get("content", "")
            path = file.get("path", "")

            # Check for deprecated APIs
            deprecated_patterns = [
                (r'NavigationView\s*{', "NavigationView is deprecated, use NavigationStack"),
                (r'@Environment\(\\.presentationMode\)', "@Environment(\\.presentationMode) is deprecated, use @Environment(\\.dismiss)"),
                (r'UIApplication\.shared\.keyWindow', "keyWindow is deprecated"),
            ]

            for pattern, message in deprecated_patterns:
                if re.search(pattern, content):
                    warnings.append(f"{path}: {message}")

            # Check for accessibility
            if "Image(" in content and ".accessibilityLabel" not in content:
                warnings.append(f"{path}: Images should have accessibility labels")

            # Check for force unwrapping
            if "!" in content and not content.count("!") == content.count("!="):
                warnings.append(f"{path}: Avoid force unwrapping")

        return ValidationResult(True, errors, warnings, self.name)

class BuildabilityValidator(BaseValidator):
    """Validates that code will actually compile - ENHANCED VERSION"""

    async def validate(self, generated_code: Dict) -> ValidationResult:
        errors = []
        warnings = []

        for file in generated_code.get("files", []):
            content = file.get("content", "")
            path = file.get("path", "")

            # CRITICAL FIX: Check for missing imports FIRST
            # This is the main issue causing build failures
            self._check_and_fix_imports(file, errors, warnings)

            # Check for balanced braces
            open_braces = content.count('{')
            close_braces = content.count('}')
            if open_braces != close_braces:
                errors.append(f"{path}: Unbalanced braces ({open_braces} open, {close_braces} close)")

            # Check for string literal issues
            # Count quotes (excluding escaped ones)
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if not line.strip().startswith('//'):
                    # Simple quote balance check
                    quote_count = line.count('"') - line.count('\\"')
                    if quote_count % 2 != 0:
                        errors.append(f"{path}:{i+1}: Possible unterminated string literal")

            # Check for common syntax errors
            syntax_patterns = [
                (r',,', "Double comma"),
                (r';;', "Double semicolon"),
                (r'{\s*}', "Empty braces (possible missing implementation)"),
                (r'func\s+\w+\([^)]*\)\s*$', "Function without body"),
            ]

            for pattern, description in syntax_patterns:
                if re.search(pattern, content, re.MULTILINE):
                    warnings.append(f"{path}: {description}")

        return ValidationResult(len(errors) == 0, errors, warnings, self.name)

    def _check_and_fix_imports(self, file: Dict, errors: List[str], warnings: List[str]):
        """Check and fix missing imports - THIS IS THE KEY FIX"""
        content = file.get("content", "")
        path = file.get("path", "")

        # Determine what imports are needed based on content
        needs_swiftui = False
        needs_foundation = False
        needs_combine = False

        # SwiftUI indicators
        swiftui_keywords = [
            'View', 'Text', 'Button', '@State', '@Binding', '@Published',
            '@ObservedObject', '@StateObject', '@Environment', 'VStack', 'HStack',
            'List', 'ForEach', 'NavigationStack', 'NavigationView', 'Sheet',
            'Alert', 'Toggle', 'TextField', 'Image', 'Color', '@Observable',
            'some View', 'body:', '.padding', '.frame', '.foregroundColor',
            '.background', '.onAppear', '.onChange', '.task', 'GeometryReader',
            'ScrollView', 'Spacer', 'Divider', 'Picker', 'DatePicker',
            '.sheet', '.alert', '.toolbar', '.navigationTitle'
        ]

        # Check for SwiftUI usage - be thorough!
        for keyword in swiftui_keywords:
            if keyword in content:
                needs_swiftui = True
                break

        # Special check for View protocol conformance
        if re.search(r'struct\s+\w+\s*:\s*View', content):
            needs_swiftui = True

        # Foundation indicators
        foundation_keywords = ['UUID', 'Date', 'URL', 'Data', 'JSONEncoder', 'JSONDecoder',
                               'DateFormatter', 'NumberFormatter', 'UserDefaults']
        for keyword in foundation_keywords:
            if keyword in content:
                needs_foundation = True
                break

        # Combine indicators
        combine_keywords = ['@Published', 'ObservableObject', 'PassthroughSubject',
                            'CurrentValueSubject', 'Cancellable']
        for keyword in combine_keywords:
            if keyword in content:
                needs_combine = True
                break

        # Check what's already imported
        has_swiftui = 'import SwiftUI' in content
        has_foundation = 'import Foundation' in content
        has_combine = 'import Combine' in content

        # Auto-fix missing imports instead of reporting as errors
        missing_imports = []

        if needs_swiftui and not has_swiftui:
            missing_imports.append("import SwiftUI")

        if needs_foundation and not has_foundation:
            missing_imports.append("import Foundation")

        if needs_combine and not has_combine:
            missing_imports.append("import Combine")

        # CRITICAL: Actually fix the imports in the file content
        if missing_imports:
            # Add imports at the beginning of the file
            import_statements = '\n'.join(missing_imports) + '\n'
            if content.startswith('import'):
                # Add after existing imports
                lines = content.split('\n')
                import_end = 0
                for i, line in enumerate(lines):
                    if line.startswith('import'):
                        import_end = i + 1
                    elif import_end > 0 and line.strip():
                        break
                lines.insert(import_end, '\n'.join(missing_imports))
                file["content"] = '\n'.join(lines)
            else:
                # Add at the beginning
                file["content"] = import_statements + '\n' + content
            
            # Log as warnings instead of errors since we fixed them
            for imp in missing_imports:
                warnings.append(f"{path}: Auto-added missing {imp}")
class QualityAssurancePipeline:
    """Main pipeline that runs all validators"""

    def __init__(self, rag_kb=None):
        self.rag_kb = rag_kb
        self.validators = [
            DependencyValidator(),
            NamingConflictValidator(),
            ArchitectureValidator(),
            AppleGuidelinesValidator(),
            BuildabilityValidator()
        ]

        # Track validation history
        self.validation_history = []

    async def validate(self, generated_code: Dict) -> ValidationResult:
        """Run all validators and aggregate results"""

        all_errors = []
        all_warnings = []
        failed_validators = []

        print("[QA PIPELINE] Starting validation...")

        for validator in self.validators:
            print(f"[QA PIPELINE] Running {validator.name}...")
            result = await validator.validate(generated_code)

            if not result.success:
                failed_validators.append(validator.name)
                all_errors.extend([f"[{validator.name}] {error}" for error in result.errors])

            all_warnings.extend([f"[{validator.name}] {warning}" for warning in result.warnings])

        # Record validation result
        validation_record = {
            "timestamp": datetime.now().isoformat(),
            "success": len(all_errors) == 0,
            "error_count": len(all_errors),
            "warning_count": len(all_warnings),
            "failed_validators": failed_validators
        }

        self.validation_history.append(validation_record)

        # Update RAG knowledge base with patterns
        if self.rag_kb and all_errors:
            self._record_validation_failure(generated_code, all_errors)

        print(f"[QA PIPELINE] Validation complete: {len(all_errors)} errors, {len(all_warnings)} warnings")

        return ValidationResult(
            success=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings,
            validator="QualityAssurancePipeline"
        )

    def _record_validation_failure(self, generated_code: Dict, errors: List[str]):
        """Record validation failures for learning"""

        if not self.rag_kb:
            return

        # Create a failure pattern document
        failure_doc = {
            "title": f"Validation Failure: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "content": f"Validation failed with {len(errors)} errors:\n" + "\n".join(errors[:10]),
            "tags": ["validation", "failure"] + [e.split(']')[0].strip('[') for e in errors[:5]],
            "severity": "error",
            "solutions": ["Fix validation errors before generation"]
        }

        try:
            filename = f"validation_failure_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(self.rag_kb.solutions_dir, filename)

            with open(filepath, 'w') as f:
                import json
                json.dump(failure_doc, f, indent=2)

            self.rag_kb._add_document(failure_doc, "solution", filename)
        except Exception as e:
            print(f"[QA PIPELINE] Failed to record validation failure: {e}")

    def get_validation_stats(self) -> Dict:
        """Get validation statistics"""

        if not self.validation_history:
            return {
                "total_validations": 0,
                "success_rate": 0,
                "common_failures": []
            }

        total = len(self.validation_history)
        successes = sum(1 for v in self.validation_history if v["success"])

        # Find common failing validators
        all_failures = []
        for record in self.validation_history:
            all_failures.extend(record.get("failed_validators", []))

        from collections import Counter
        failure_counts = Counter(all_failures)

        return {
            "total_validations": total,
            "success_rate": (successes / total * 100) if total > 0 else 0,
            "common_failures": failure_counts.most_common(3),
            "recent_trends": self._analyze_recent_trends()
        }

    def _analyze_recent_trends(self) -> Dict:
        """Analyze recent validation trends"""

        recent = self.validation_history[-20:]  # Last 20 validations
        if not recent:
            return {}

        recent_success_rate = sum(1 for v in recent if v["success"]) / len(recent) * 100
        avg_errors = sum(v["error_count"] for v in recent) / len(recent)
        avg_warnings = sum(v["warning_count"] for v in recent) / len(recent)

        return {
            "recent_success_rate": recent_success_rate,
            "avg_errors_per_validation": avg_errors,
            "avg_warnings_per_validation": avg_warnings
        }