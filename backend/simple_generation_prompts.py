#!/usr/bin/env python3
"""
Simple Generation Prompts - Generate SIMPLE, WORKING iOS apps
CRITICAL: Focus on simplicity over complexity to ensure build success
"""

def get_simple_generation_prompt(description: str, app_name: str) -> str:
    """Get a prompt that generates SIMPLE, WORKING iOS apps"""
    
    return f"""You are an expert iOS developer. Generate a SIMPLE, WORKING iOS app that WILL BUILD SUCCESSFULLY.

APP REQUEST: {description}
APP NAME: {app_name}

CRITICAL REQUIREMENTS:
1. Use ONLY iOS 16+ SwiftUI patterns
2. Keep architecture SIMPLE - NO complex dependency injection
3. Maximum 2-3 Swift files total  
4. NO protocols, repositories, or dependency containers
5. Use @State and @Published for state management
6. ALL code must be self-contained and buildable

FORBIDDEN PATTERNS (WILL CAUSE BUILD FAILURES):
❌ Complex dependency injection (@Dependency, DependencyContainer)
❌ Protocol/Implementation patterns (UserRepositoryProtocol, UserRepositoryImpl)
❌ Multiple ViewModels for the same view
❌ Complex architecture folders (Architecture/, Data/, etc.)
❌ @Environment with custom types
❌ Third-party dependencies
❌ Core Data (PersistenceController, NSManagedObject, @FetchRequest)
❌ .xcdatamodeld files

REQUIRED PATTERNS (GUARANTEE SUCCESS):
✅ Simple @StateObject view models
✅ Direct property initialization
✅ Self-contained Swift files
✅ Standard SwiftUI components only
✅ Basic navigation with NavigationStack

Generate EXACTLY 2 files:
1. App.swift - Main app entry point
2. ContentView.swift - Main view with all functionality

The app should be functional but SIMPLE. Focus on core features only.

Return ONLY valid JSON:
{{
    "app_name": "{app_name}",
    "files": [
        {{
            "path": "Sources/App.swift",
            "content": "// Complete App.swift content here"
        }},
        {{
            "path": "Sources/ContentView.swift", 
            "content": "// Complete ContentView.swift content here"
        }}
    ],
    "features": ["List 2-3 core features"],
    "generated_by_llm": "llm_name"
}}

REMEMBER: Simple, working app is better than complex, broken app."""

def get_simple_modification_prompt(app_name: str, original_description: str, modification: str, current_files: list) -> str:
    """Get a prompt for simple modifications that won't break the build"""
    
    current_files_summary = "\n".join([f"File: {f.get('path', 'unknown')}\nContent: {f.get('content', '')[:500]}..." for f in current_files[:3]])
    
    return f"""You are modifying an iOS app. Keep modifications SIMPLE to avoid build failures.

CURRENT APP: {app_name}
ORIGINAL DESCRIPTION: {original_description}
MODIFICATION REQUEST: {modification}

CURRENT FILES:
{current_files_summary}

CRITICAL MODIFICATION RULES:
1. Keep the SAME simple architecture
2. NO new complex patterns or dependencies
3. Maintain existing @StateObject and @State patterns
4. Only modify existing functionality or add simple features
5. NEVER introduce protocols, repositories, or dependency injection
6. Keep maximum 2-3 files total

MODIFICATION APPROACH:
- For UI changes: Modify ContentView.swift only
- For new features: Add to existing ViewModel or create simple @State properties
- For dark mode: Add simple @AppStorage toggle
- For better UX: Improve existing UI, don't restructure

Return ONLY valid JSON with ALL files (modified and unmodified):
{{
    "app_name": "{app_name}",
    "files": [
        {{
            "path": "Sources/App.swift",
            "content": "// Complete updated App.swift"
        }},
        {{
            "path": "Sources/ContentView.swift",
            "content": "// Complete updated ContentView.swift"
        }}
    ],
    "modification_summary": "Brief description of changes made",
    "modified_by_llm": "llm_name"
}}

REMEMBER: Simple modifications that work are better than complex ones that break."""

def get_fallback_app_prompt(app_name: str, description: str) -> str:
    """Get a prompt for creating a guaranteed working fallback app"""
    
    return f"""Create the SIMPLEST possible working iOS app as a fallback.

APP NAME: {app_name}
BASED ON: {description}

REQUIREMENTS:
- Exactly 2 files
- Basic counter or list functionality
- No external dependencies
- Guaranteed to build and run
- Modern SwiftUI (iOS 16+)

Return ONLY valid JSON:
{{
    "app_name": "{app_name}",
    "files": [
        {{
            "path": "Sources/App.swift",
            "content": "import SwiftUI\\n\\n@main\\nstruct {app_name.replace(' ', '')}App: App {{\\n    var body: some Scene {{\\n        WindowGroup {{\\n            ContentView()\\n        }}\\n    }}\\n}}"
        }},
        {{
            "path": "Sources/ContentView.swift",
            "content": "// Simple working ContentView here"
        }}
    ],
    "features": ["Basic functionality", "Guaranteed to work"]
}}"""

def get_error_analysis_prompt(errors: list) -> str:
    """Analyze errors and suggest simple fixes"""
    
    error_text = "\n".join(errors[:5])  # Top 5 errors
    
    return f"""Analyze these Swift build errors and suggest the SIMPLEST fix:

ERRORS:
{error_text}

Provide a simple analysis focusing on:
1. Root cause (missing imports, syntax, etc.)
2. Simple fix (one-line changes preferred)
3. Prevention strategy

Return analysis as JSON:
{{
    "root_cause": "Brief description",
    "simple_fix": "Specific fix to apply",
    "prevention": "How to avoid this in future"
}}"""