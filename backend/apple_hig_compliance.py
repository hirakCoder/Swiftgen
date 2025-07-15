"""
Apple Human Interface Guidelines Compliance Module
Ensures all generated iOS apps follow Apple's best practices
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ComplianceIssue:
    """Represents a compliance issue found in the code"""
    severity: str  # "error", "warning", "info"
    category: str
    message: str
    line_number: Optional[int] = None
    suggested_fix: Optional[str] = None

class AppleHIGCompliance:
    """Validates and enforces Apple Human Interface Guidelines"""
    
    def __init__(self):
        self.ios_version = "17.0"  # Default target
        
    def validate_files(self, files: List[Dict[str, str]]) -> Tuple[bool, List[ComplianceIssue]]:
        """Validate all files for Apple HIG compliance"""
        issues = []
        
        for file in files:
            if file['path'].endswith('.swift'):
                file_issues = self.validate_swift_file(file['content'], file['path'])
                issues.extend(file_issues)
        
        # Return compliance status
        has_errors = any(issue.severity == "error" for issue in issues)
        return not has_errors, issues
    
    def validate_swift_file(self, content: str, filename: str) -> List[ComplianceIssue]:
        """Validate a single Swift file"""
        issues = []
        lines = content.split('\n')
        
        # Run all validation checks
        issues.extend(self.check_navigation_patterns(content, lines))
        issues.extend(self.check_color_usage(content, lines))
        issues.extend(self.check_typography(content, lines))
        issues.extend(self.check_spacing_layout(content, lines))
        issues.extend(self.check_accessibility(content, lines))
        issues.extend(self.check_animations(content, lines))
        issues.extend(self.check_state_management(content, lines))
        issues.extend(self.check_tap_targets(content, lines))
        
        return issues
    
    def check_navigation_patterns(self, content: str, lines: List[str]) -> List[ComplianceIssue]:
        """Check for proper navigation patterns"""
        issues = []
        
        # Check for deprecated NavigationView
        if "NavigationView" in content and float(self.ios_version) >= 16.0:
            for i, line in enumerate(lines):
                if "NavigationView" in line:
                    issues.append(ComplianceIssue(
                        severity="error",
                        category="Navigation",
                        message="NavigationView is deprecated in iOS 16+. Use NavigationStack instead.",
                        line_number=i + 1,
                        suggested_fix=line.replace("NavigationView", "NavigationStack")
                    ))
        
        # Check for proper navigation destination usage
        if "NavigationLink" in content and "navigationDestination" not in content:
            issues.append(ComplianceIssue(
                severity="warning",
                category="Navigation",
                message="Consider using navigationDestination for programmatic navigation in iOS 16+",
                suggested_fix="Add .navigationDestination(for: Type.self) { item in ... }"
            ))
        
        return issues
    
    def check_color_usage(self, content: str, lines: List[str]) -> List[ComplianceIssue]:
        """Check for proper color usage"""
        issues = []
        
        # Check for hardcoded colors
        hardcoded_patterns = [
            r'Color\(red:.*green:.*blue:',
            r'Color\(#[0-9a-fA-F]{6}\)',
            r'Color\(".*"\)',
            r'UIColor\('
        ]
        
        for pattern in hardcoded_patterns:
            for i, line in enumerate(lines):
                if re.search(pattern, line):
                    issues.append(ComplianceIssue(
                        severity="warning",
                        category="Colors",
                        message="Use semantic colors (.primary, .secondary, .accentColor) instead of hardcoded values",
                        line_number=i + 1,
                        suggested_fix="Replace with Color.primary, Color.secondary, or Color.accentColor"
                    ))
        
        # Check for dark mode support
        if ".colorScheme" not in content and ".preferredColorScheme" not in content:
            issues.append(ComplianceIssue(
                severity="warning",
                category="Colors",
                message="Consider adding dark mode support with .preferredColorScheme modifier",
                suggested_fix="Add @Environment(\\.colorScheme) var colorScheme"
            ))
        
        return issues
    
    def check_typography(self, content: str, lines: List[str]) -> List[ComplianceIssue]:
        """Check for proper typography usage"""
        issues = []
        
        # Check for hardcoded font sizes
        if re.search(r'\.font\(\.system\(size:\s*\d+', content):
            for i, line in enumerate(lines):
                if re.search(r'\.font\(\.system\(size:\s*\d+', line):
                    issues.append(ComplianceIssue(
                        severity="warning",
                        category="Typography",
                        message="Use Dynamic Type (.title, .headline, .body) instead of fixed sizes",
                        line_number=i + 1,
                        suggested_fix="Replace with .font(.title), .font(.headline), or .font(.body)"
                    ))
        
        # Check for accessibility support
        if ".dynamicTypeSize" not in content:
            issues.append(ComplianceIssue(
                severity="info",
                category="Typography",
                message="Consider limiting Dynamic Type sizes with .dynamicTypeSize(...sizeLimit)",
                suggested_fix="Add .dynamicTypeSize(...DynamicTypeSize.xxxLarge) to main view"
            ))
        
        return issues
    
    def check_spacing_layout(self, content: str, lines: List[str]) -> List[ComplianceIssue]:
        """Check for proper spacing and layout"""
        issues = []
        
        # Check for non-standard spacing
        non_standard_spacing = re.findall(r'\.padding\((\d+)\)', content)
        for spacing in non_standard_spacing:
            spacing_val = int(spacing)
            if spacing_val not in [4, 8, 12, 16, 20, 24, 32, 40]:
                issues.append(ComplianceIssue(
                    severity="info",
                    category="Spacing",
                    message=f"Non-standard spacing {spacing}. Use multiples of 4 or 8 (8, 16, 24, 32)",
                    suggested_fix="Use standard spacing values: 8, 16, 24, 32"
                ))
        
        # Check for safe area usage
        if "ignoresSafeArea" in content:
            issues.append(ComplianceIssue(
                severity="warning",
                category="Layout",
                message="Be careful with ignoresSafeArea - ensure content doesn't overlap system UI",
                suggested_fix="Use .ignoresSafeArea(.keyboard) or specific edges only"
            ))
        
        return issues
    
    def check_accessibility(self, content: str, lines: List[str]) -> List[ComplianceIssue]:
        """Check for accessibility compliance"""
        issues = []
        
        # Check buttons for accessibility labels
        button_lines = [i for i, line in enumerate(lines) if "Button(" in line or "Button {" in line]
        for line_num in button_lines:
            # Check next few lines for accessibility
            check_range = lines[line_num:min(line_num + 10, len(lines))]
            check_text = '\n'.join(check_range)
            
            if ".accessibilityLabel" not in check_text and "Text(" not in check_text:
                issues.append(ComplianceIssue(
                    severity="error",
                    category="Accessibility",
                    message="Button must have accessibility label",
                    line_number=line_num + 1,
                    suggested_fix="Add .accessibilityLabel(\"description\") to the button"
                ))
        
        # Check images for accessibility
        if "Image(" in content:
            image_lines = [i for i, line in enumerate(lines) if "Image(" in line]
            for line_num in image_lines:
                check_range = lines[line_num:min(line_num + 5, len(lines))]
                check_text = '\n'.join(check_range)
                
                if ".accessibilityLabel" not in check_text:
                    issues.append(ComplianceIssue(
                        severity="warning",
                        category="Accessibility",
                        message="Image should have accessibility label",
                        line_number=line_num + 1,
                        suggested_fix="Add .accessibilityLabel(\"image description\")"
                    ))
        
        return issues
    
    def check_animations(self, content: str, lines: List[str]) -> List[ComplianceIssue]:
        """Check for proper animation usage"""
        issues = []
        
        # Check for spring animations
        if ".animation(" in content and ".spring" not in content:
            issues.append(ComplianceIssue(
                severity="info",
                category="Animations",
                message="Consider using spring animations for more natural motion",
                suggested_fix="Use .animation(.spring(response: 0.4, dampingFraction: 0.8))"
            ))
        
        # Check for reduce motion support
        if ".animation" in content and "reduceMotion" not in content:
            issues.append(ComplianceIssue(
                severity="warning",
                category="Animations",
                message="Consider respecting Reduce Motion accessibility setting",
                suggested_fix="Add @Environment(\\.accessibilityReduceMotion) var reduceMotion"
            ))
        
        return issues
    
    def check_state_management(self, content: str, lines: List[str]) -> List[ComplianceIssue]:
        """Check for modern state management patterns"""
        issues = []
        
        # Check for ObservableObject usage in iOS 17+
        if float(self.ios_version) >= 17.0 and "ObservableObject" in content:
            for i, line in enumerate(lines):
                if "ObservableObject" in line:
                    issues.append(ComplianceIssue(
                        severity="warning",
                        category="State Management",
                        message="Consider using @Observable macro instead of ObservableObject in iOS 17+",
                        line_number=i + 1,
                        suggested_fix="Replace 'class ViewModel: ObservableObject' with '@Observable class ViewModel'"
                    ))
        
        # Check for @MainActor usage
        if "class" in content and "ViewModel" in content and "@MainActor" not in content:
            issues.append(ComplianceIssue(
                severity="warning",
                category="Concurrency",
                message="ViewModels should be marked with @MainActor for UI safety",
                suggested_fix="Add @MainActor before class declaration"
            ))
        
        return issues
    
    def check_tap_targets(self, content: str, lines: List[str]) -> List[ComplianceIssue]:
        """Check for minimum tap target sizes"""
        issues = []
        
        # Check for custom tap targets
        if ".onTapGesture" in content:
            tap_lines = [i for i, line in enumerate(lines) if ".onTapGesture" in line]
            for line_num in tap_lines:
                # Look backwards for frame modifiers
                check_start = max(0, line_num - 10)
                check_range = lines[check_start:line_num]
                check_text = '\n'.join(check_range)
                
                if ".frame(" not in check_text or "44" not in check_text:
                    issues.append(ComplianceIssue(
                        severity="warning",
                        category="Interaction",
                        message="Ensure tap targets are at least 44x44 points",
                        line_number=line_num + 1,
                        suggested_fix="Add .frame(minWidth: 44, minHeight: 44) before .onTapGesture"
                    ))
        
        return issues
    
    def fix_compliance_issues(self, files: List[Dict[str, str]], issues: List[ComplianceIssue]) -> List[Dict[str, str]]:
        """Automatically fix compliance issues where possible"""
        fixed_files = []
        
        for file in files:
            content = file['content']
            lines = content.split('\n')
            
            # Apply fixes for issues in this file
            for issue in issues:
                if issue.suggested_fix and issue.line_number:
                    # Simple line replacement fixes
                    if issue.category == "Navigation" and "NavigationView" in lines[issue.line_number - 1]:
                        lines[issue.line_number - 1] = lines[issue.line_number - 1].replace(
                            "NavigationView", "NavigationStack"
                        )
                    
                    # Add more automated fixes as needed
            
            fixed_files.append({
                'path': file['path'],
                'content': '\n'.join(lines)
            })
        
        return fixed_files
    
    def generate_compliance_report(self, issues: List[ComplianceIssue]) -> str:
        """Generate a compliance report"""
        if not issues:
            return "✅ All Apple HIG compliance checks passed!"
        
        report = "# Apple HIG Compliance Report\n\n"
        
        # Group by severity
        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]
        info = [i for i in issues if i.severity == "info"]
        
        if errors:
            report += f"## ❌ Errors ({len(errors)})\n"
            for issue in errors:
                report += f"- **{issue.category}**: {issue.message}"
                if issue.line_number:
                    report += f" (line {issue.line_number})"
                report += "\n"
        
        if warnings:
            report += f"\n## ⚠️ Warnings ({len(warnings)})\n"
            for issue in warnings:
                report += f"- **{issue.category}**: {issue.message}"
                if issue.line_number:
                    report += f" (line {issue.line_number})"
                report += "\n"
        
        if info:
            report += f"\n## ℹ️ Suggestions ({len(info)})\n"
            for issue in info:
                report += f"- **{issue.category}**: {issue.message}\n"
        
        return report