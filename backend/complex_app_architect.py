"""
Complex App Architect for SwiftGen AI
Plans and structures complex applications before generation to ensure success
"""

import re
from typing import Dict, List, Optional, Tuple

class ComplexAppArchitect:
    """Architect for planning complex app structures before generation"""
    
    def __init__(self):
        # Define app complexity patterns
        self.complexity_indicators = {
            "high": [
                "delivery", "uber", "doordash", "ecommerce", "marketplace",
                "social media", "instagram", "facebook", "twitter",
                "banking", "finance", "trading", "healthcare", "medical"
            ],
            "medium": [
                "todo", "notes", "calendar", "weather", "news",
                "recipe", "fitness", "habit", "budget", "expense"
            ],
            "low": [
                "calculator", "timer", "counter", "converter",
                "flashcard", "quiz", "dice", "coin"
            ]
        }
        
        # Define required components for complex apps
        self.app_requirements = {
            "ride_sharing": {
                "models": [
                    "User", "Driver", "Ride", "Location", "Vehicle",
                    "Payment", "Rating", "Route", "Fare"
                ],
                "views": [
                    "ContentView", "MapView", "RideRequestView", "DriverView",
                    "RideTrackingView", "PaymentView", "RideHistoryView",
                    "ProfileView", "SettingsView", "RatingView"
                ],
                "viewmodels": [
                    "MapViewModel", "RideViewModel", "DriverViewModel",
                    "LocationViewModel", "PaymentViewModel"
                ],
                "services": [
                    "LocationService", "RideService", "DriverService",
                    "PaymentService", "AuthService", "NavigationService"
                ],
                "features": [
                    "real-time location tracking", "driver matching", "fare calculation",
                    "route optimization", "payment processing", "ratings and reviews"
                ]
            },
            "food_delivery": {
                "models": [
                    "Restaurant", "MenuItem", "Order", "Cart", "User",
                    "Address", "Payment", "Review", "Category"
                ],
                "views": [
                    "ContentView", "RestaurantListView", "RestaurantDetailView",
                    "MenuView", "CartView", "CheckoutView", "OrderTrackingView",
                    "AccountView", "AddressView", "PaymentView", "SearchView"
                ],
                "viewmodels": [
                    "RestaurantViewModel", "CartViewModel", "OrderViewModel",
                    "UserViewModel", "SearchViewModel"
                ],
                "services": [
                    "RestaurantService", "OrderService", "AuthService",
                    "PaymentService", "LocationService", "NetworkService"
                ],
                "features": [
                    "search and filtering", "cart management", "order tracking",
                    "user authentication", "payment processing", "location services"
                ]
            },
            "social_media": {
                "models": [
                    "User", "Post", "Comment", "Like", "Follow",
                    "Message", "Story", "Notification"
                ],
                "views": [
                    "ContentView", "FeedView", "ProfileView", "PostDetailView",
                    "CreatePostView", "MessagesView", "DiscoverView",
                    "NotificationsView", "SettingsView"
                ],
                "viewmodels": [
                    "FeedViewModel", "ProfileViewModel", "PostViewModel",
                    "MessagingViewModel", "NotificationViewModel"
                ],
                "services": [
                    "AuthService", "PostService", "UserService",
                    "MessagingService", "NotificationService", "MediaService"
                ],
                "features": [
                    "real-time feed", "user interactions", "messaging",
                    "media upload", "notifications", "user discovery"
                ]
            },
            "ecommerce": {
                "models": [
                    "Product", "Category", "Cart", "Order", "User",
                    "Review", "Wishlist", "Payment", "Address"
                ],
                "views": [
                    "ContentView", "ProductListView", "ProductDetailView",
                    "CartView", "CheckoutView", "OrderHistoryView",
                    "ProfileView", "WishlistView", "SearchView", "CategoryView"
                ],
                "viewmodels": [
                    "ProductViewModel", "CartViewModel", "OrderViewModel",
                    "UserViewModel", "SearchViewModel"
                ],
                "services": [
                    "ProductService", "CartService", "OrderService",
                    "AuthService", "PaymentService", "SearchService"
                ],
                "features": [
                    "product catalog", "shopping cart", "secure checkout",
                    "order management", "user accounts", "search and filters"
                ]
            }
        }
    
    def analyze_complexity(self, description: str) -> str:
        """Determine app complexity level"""
        description_lower = description.lower()
        
        # Check for high complexity indicators
        for indicator in self.complexity_indicators["high"]:
            if indicator in description_lower:
                return "high"
        
        # Check for medium complexity
        for indicator in self.complexity_indicators["medium"]:
            if indicator in description_lower:
                return "medium"
        
        return "low"
    
    def identify_app_type(self, description: str) -> str:
        """Identify the specific type of complex app"""
        description_lower = description.lower()
        
        # Ride sharing app patterns (check before food delivery since "uber" might match both)
        if any(word in description_lower for word in ["ride", "taxi", "driver", "uber", "lyft", "cab"]) and \
           not any(word in description_lower for word in ["food", "delivery", "restaurant"]):
            return "ride_sharing"
        
        # Food delivery app patterns
        if any(word in description_lower for word in ["food", "delivery", "restaurant", "doordash", "uber eats"]):
            return "food_delivery"
        
        # Social media patterns
        if any(word in description_lower for word in ["social", "instagram", "facebook", "twitter", "post", "follow"]):
            return "social_media"
        
        # E-commerce patterns (including Amazon)
        if any(word in description_lower for word in ["shop", "ecommerce", "product", "buy", "sell", "marketplace", "amazon", "store"]):
            return "ecommerce"
        
        return "general"
    
    def create_architecture_plan(self, description: str, app_name: str) -> Dict:
        """Create a detailed architecture plan for the app"""
        complexity = self.analyze_complexity(description)
        app_type = self.identify_app_type(description)
        
        plan = {
            "app_name": app_name,
            "complexity": complexity,
            "app_type": app_type,
            "file_structure": self._generate_file_structure(app_type, complexity),
            "technical_requirements": self._get_technical_requirements(app_type, complexity),
            "implementation_notes": self._get_implementation_notes(app_type)
        }
        
        return plan
    
    def _generate_file_structure(self, app_type: str, complexity: str) -> Dict:
        """Generate the complete file structure for the app"""
        if complexity == "low":
            return {
                "Sources/App.swift": "Main app entry point",
                "Sources/ContentView.swift": "Main view"
            }
        
        # Get requirements for this app type
        requirements = self.app_requirements.get(app_type, self._get_default_requirements())
        
        file_structure = {
            "Sources/App.swift": "Main app entry point with proper initialization"
        }
        
        # Add models
        for model in requirements.get("models", []):
            file_structure[f"Sources/Models/{model}.swift"] = f"{model} data model with Codable and Identifiable"
        
        # Add views
        for view in requirements.get("views", []):
            file_structure[f"Sources/Views/{view}.swift"] = f"{view} SwiftUI implementation"
        
        # Add view models
        for vm in requirements.get("viewmodels", []):
            file_structure[f"Sources/ViewModels/{vm}.swift"] = f"{vm} with ObservableObject"
        
        # Add services
        for service in requirements.get("services", []):
            file_structure[f"Sources/Services/{service}.swift"] = f"{service} implementation"
        
        # Add common utilities
        file_structure["Sources/Utils/Extensions.swift"] = "Common extensions"
        file_structure["Sources/Utils/Constants.swift"] = "App constants and configuration"
        
        return file_structure
    
    def _get_technical_requirements(self, app_type: str, complexity: str) -> List[str]:
        """Get technical requirements for the app"""
        base_requirements = [
            "iOS 16.0+ target",
            "SwiftUI framework",
            "MVVM architecture",
            "Async/await for networking",
            "Proper error handling",
            "Loading states"
        ]
        
        if complexity == "high":
            base_requirements.extend([
                "Dependency injection",
                "Protocol-oriented design",
                "Comprehensive error recovery",
                "Offline support consideration",
                "Performance optimization",
                "Memory management"
            ])
        
        # Add app-specific requirements
        if app_type == "ride_sharing":
            base_requirements.extend([
                "MapKit integration for real-time tracking",
                "Core Location for GPS",
                "WebSocket for live updates",
                "Background location updates",
                "Push notifications for ride status"
            ])
        elif app_type == "food_delivery":
            base_requirements.extend([
                "Location services integration",
                "Real-time order tracking",
                "Cart persistence",
                "Search and filtering"
            ])
        elif app_type == "social_media":
            base_requirements.extend([
                "Real-time updates",
                "Media handling",
                "Infinite scrolling",
                "Push notifications setup"
            ])
        
        return base_requirements
    
    def _get_implementation_notes(self, app_type: str) -> str:
        """Get implementation notes for the app type"""
        notes = {
            "ride_sharing": """
Key Implementation Details:
1. MapView must show real-time location of user and nearby drivers
2. Implement driver matching based on proximity and availability
3. Use Core Location for continuous location updates
4. Calculate fare based on distance and time
5. Show route preview before ride confirmation
6. Real-time tracking during active ride
7. Payment integration with multiple options
8. Driver and rider rating system after ride completion
9. Trip history with receipts
10. Handle background location updates properly
""",
            "food_delivery": """
Key Implementation Details:
1. Restaurant model must include menu items as a relationship
2. Cart should persist using @AppStorage
3. Use TabView for main navigation (Browse, Search, Cart, Account)
4. Implement proper navigation from list -> detail -> cart flow
5. Mock data should include at least 10 restaurants with varied cuisines
6. Each restaurant needs 5-10 menu items with prices
7. Cart must update in real-time across all views
8. Include search by restaurant name and cuisine type
9. Add loading and empty states for all list views
""",
            "social_media": """
Key Implementation Details:
1. Use ScrollView with LazyVStack for feed performance
2. Implement pull-to-refresh for feed updates
3. Like/comment counts should update immediately
4. Profile view should show user's posts
5. Include image placeholders for all media
6. Mock data should include varied post types
7. Implement proper navigation stack
8. Add loading states for all async operations
""",
            "ecommerce": """
Key Implementation Details:
1. Product grid layout with 2 columns
2. Cart badge on tab bar showing item count
3. Wishlist functionality with heart icons
4. Search with real-time filtering
5. Category-based navigation
6. Product details with image carousel placeholder
7. Reviews section with ratings
8. Proper checkout flow with steps
"""
        }
        
        return notes.get(app_type, "Follow standard SwiftUI best practices")
    
    def _get_default_requirements(self) -> Dict:
        """Get default requirements for general complex apps"""
        return {
            "models": ["Item", "User", "Settings"],
            "views": ["ContentView", "ListView", "DetailView", "SettingsView"],
            "viewmodels": ["MainViewModel", "SettingsViewModel"],
            "services": ["DataService", "NetworkService"],
            "features": ["basic CRUD", "settings", "data persistence"]
        }
    
    def create_enhanced_prompt(self, description: str, app_name: str) -> str:
        """Create an enhanced prompt with architectural guidance"""
        plan = self.create_architecture_plan(description, app_name)
        
        # For complex apps, we need a more concise prompt to avoid token limits
        # Focus on the most critical files first
        
        if plan["complexity"] == "high":
            # Create a focused prompt for essential files only
            prompt = f"""Create a {plan['app_type'].replace('_', ' ')} iOS app called "{app_name}".

DESCRIPTION: {description}

Create these ESSENTIAL files for a working MVP:

CORE FILES (MUST CREATE ALL):
1. Sources/App.swift - Main app with TabView navigation
2. Sources/Models/Restaurant.swift - Include name, cuisine, rating, image, menuItems array
3. Sources/Models/MenuItem.swift - Include name, description, price, category
4. Sources/Models/Cart.swift - Singleton with @Published items, addItem, removeItem, total
5. Sources/Views/ContentView.swift - TabView with 4 tabs
6. Sources/Views/RestaurantListView.swift - List of restaurants with search
7. Sources/Views/RestaurantDetailView.swift - Show restaurant info and menu
8. Sources/Views/CartView.swift - Show cart items with checkout button
9. Sources/ViewModels/RestaurantViewModel.swift - ObservableObject with restaurants array
10. Sources/ViewModels/CartViewModel.swift - ObservableObject managing cart state

REQUIREMENTS:
- iOS 16.0+ SwiftUI
- Use @StateObject/@ObservedObject properly
- Include mock data (10+ restaurants)
- Cart persists with @AppStorage
- All navigation must work
- MVVM architecture

Each file must be complete and functional. Start with App.swift."""
        else:
            # Use the original detailed prompt for simpler apps
            file_list = "\n".join([f"- {path}" for path in list(plan["file_structure"].keys())[:20]])
            prompt = f"""Create a {plan['app_type'].replace('_', ' ')} iOS app called "{app_name}".

{description}

Required files:
{file_list}

Requirements:
- iOS 16.0+ SwiftUI
- Complete implementation
- All files must compile"""
        
        return prompt