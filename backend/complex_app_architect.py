"""
Complex App Architect - Orchestrates generation of complex multi-user apps
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from complex_app_templates import ComplexAppTemplates, AppType, UserRole

logger = logging.getLogger(__name__)

@dataclass
class ComplexAppSpec:
    """Specification for a complex app"""
    app_type: AppType
    app_name: str
    user_roles: List[UserRole]
    core_features: List[str]
    screens: Dict[UserRole, List[str]]
    models: List[str]
    
class ComplexAppArchitect:
    """Orchestrates the generation of complex iOS apps"""
    
    def __init__(self):
        self.templates = ComplexAppTemplates()
        
    def analyze_complexity(self, description: str) -> str:
        """Analyze app complexity from description"""
        description_lower = description.lower()
        
        # High complexity indicators
        high_indicators = [
            'real-time', 'location tracking', 'payment', 'multi-user',
            'chat', 'messaging', 'delivery tracking', 'driver', 'restaurant',
            'marketplace', 'social network', 'live', 'streaming'
        ]
        
        # Medium complexity indicators
        medium_indicators = [
            'login', 'authentication', 'profile', 'api', 'database',
            'search', 'filter', 'notifications', 'settings'
        ]
        
        high_count = sum(1 for indicator in high_indicators if indicator in description_lower)
        medium_count = sum(1 for indicator in medium_indicators if indicator in description_lower)
        
        if high_count >= 3:
            return "high"
        elif high_count >= 1 or medium_count >= 3:
            return "medium"
        else:
            return "low"
            
    def identify_app_type(self, description: str) -> str:
        """Identify the type of app from description"""
        app_type = self.templates.detect_app_type(description)
        if app_type:
            return app_type.value
        return "general"
        
    def create_enhanced_prompt(self, description: str, app_name: str) -> str:
        """Create an enhanced prompt for complex app generation"""
        
        # Detect app type
        app_type = self.templates.detect_app_type(description)
        if not app_type:
            return description  # Fallback to original description
            
        # Get template data
        template = self.templates.templates.get(app_type)
        if not template:
            return description
            
        # Sanitize the description
        sanitized_desc = self.templates.sanitize_app_request(description)
        
        # Build enhanced prompt
        enhanced_prompt = f"""
Create a comprehensive {template['description']} iOS app named {app_name}.

IMPORTANT LEGAL REQUIREMENTS:
- Use ONLY generic branding and naming
- Do NOT use any copyrighted terms or trademarks
- Create original UI designs and color schemes
- Implement common features found in {app_type.value} apps

APP ARCHITECTURE:
- Pattern: MVVM + Clean Architecture
- Navigation: Coordinator pattern with role-based flows
- State Management: @StateObject, @EnvironmentObject, and Combine
- Dependency Injection: DIContainer pattern
- Error Handling: Comprehensive error handling with user feedback

USER ROLES:
"""
        
        # Add user roles
        for role in template['roles']:
            role_name = role.value.capitalize()
            enhanced_prompt += f"\n{role_name}:\n"
            if role in template['core_screens']:
                screens = template['core_screens'][role]
                enhanced_prompt += f"- Screens: {', '.join(screens[:5])}\n"
                
        enhanced_prompt += f"""
CORE FEATURES:
"""
        # Add features
        for feature in template['features'][:7]:  # Limit to 7 features
            enhanced_prompt += f"- {feature}\n"
            
        enhanced_prompt += f"""
DATA MODELS:
- {', '.join(template['models'][:8])}

TECHNICAL REQUIREMENTS:
1. Use SwiftUI with iOS 16.0 minimum deployment
2. Implement proper loading states and error handling
3. Use async/await for all asynchronous operations
4. Add @MainActor to all ViewModels
5. Create mock services for demonstration
6. Use SF Symbols for icons
7. Implement proper data validation

STRUCTURE:
Create a complete app with:
1. App.swift with role-based navigation
2. Models for all entities
3. ViewModels with business logic
4. Views for each screen
5. Mock services for data
6. Proper error handling
7. Loading and empty states

The app should be fully functional with mock data and demonstrate all core features.
"""
        
        return enhanced_prompt
        
    def generate_app_structure(self, app_type: AppType) -> Dict[str, Any]:
        """Generate the file structure for a complex app"""
        
        template = self.templates.templates.get(app_type)
        if not template:
            return {}
            
        structure = {
            "app_name": template['name'],
            "folders": {
                "App": ["App.swift", "AppCoordinator.swift", "DIContainer.swift"],
                "Domain": {
                    "Models": [f"{model}.swift" for model in template['models'][:5]],
                    "UseCases": ["LoginUseCase.swift", "FetchDataUseCase.swift"],
                    "Repositories": ["UserRepository.swift", "DataRepository.swift"]
                },
                "Data": {
                    "Network": ["NetworkService.swift", "Endpoint.swift", "NetworkError.swift"],
                    "Persistence": ["CoreDataManager.swift", "UserDefaultsService.swift"],
                    "Repositories": ["UserRepositoryImpl.swift", "DataRepositoryImpl.swift"]
                },
                "Presentation": {
                    "ViewModels": [],
                    "Views": {
                        "Common": ["LoadingView.swift", "ErrorView.swift", "EmptyStateView.swift"],
                        "Authentication": ["LoginView.swift", "SignUpView.swift"],
                    },
                    "Components": ["CustomButton.swift", "CustomTextField.swift"]
                },
                "Services": ["LocationService.swift", "NotificationService.swift"],
                "Mock": ["MockNetworkService.swift", "MockData.swift"]
            }
        }
        
        # Add role-specific views
        for role in template['roles']:
            if role in template['core_screens']:
                role_folder = f"{role.value.capitalize()}Views"
                structure["folders"]["Presentation"]["Views"][role_folder] = [
                    f"{screen}.swift" for screen in template['core_screens'][role][:5]
                ]
                
        return structure
        
    def create_architecture_files(self, app_type: AppType) -> List[Dict[str, str]]:
        """Create the core architecture files for the app"""
        files = []
        
        # Get templates
        architecture_template = self.templates.get_architecture_template(app_type)
        navigation_template = self.templates.get_navigation_coordinator(app_type)
        di_template = self.templates.get_dependency_injection_container()
        mock_template = self.templates.get_mock_services(app_type)
        
        # Create core files
        files.extend([
            {
                "path": "Sources/App/AppCoordinator.swift",
                "content": navigation_template
            },
            {
                "path": "Sources/App/DIContainer.swift", 
                "content": di_template
            },
            {
                "path": "Sources/Services/MockNetworkService.swift",
                "content": mock_template
            }
        ])
        
        return files
        
    def validate_complex_app_generation(self, generated_code: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate that generated code meets complex app requirements"""
        issues = []
        
        # Check for required files
        files = generated_code.get('files', [])
        file_paths = [f['path'] for f in files]
        
        # Required patterns
        required_patterns = [
            'Coordinator',  # Navigation coordinator
            'ViewModel',    # ViewModels
            'Repository',   # Repository pattern
            'UseCase',      # Use cases
            'Service',      # Services
            'Mock'          # Mock data
        ]
        
        for pattern in required_patterns:
            if not any(pattern in path for path in file_paths):
                issues.append(f"Missing {pattern} implementation")
                
        # Check for role-based navigation
        app_content = next((f['content'] for f in files if 'App.swift' in f['path']), '')
        if 'navigationDestination' not in app_content:
            issues.append("Missing role-based navigation implementation")
            
        # Check for proper architecture
        has_clean_arch = any('Domain' in path or 'Data' in path or 'Presentation' in path 
                           for path in file_paths)
        if not has_clean_arch:
            issues.append("Missing Clean Architecture layer separation")
            
        return len(issues) == 0, issues