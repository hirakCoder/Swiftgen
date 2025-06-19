"""
Complex App Templates for SwiftGen AI
Provides architecture templates and patterns for complex multi-user apps
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class AppType(Enum):
    FOOD_DELIVERY = "food_delivery"
    RIDE_SHARING = "ride_sharing"
    SOCIAL_MEDIA = "social_media"
    ECOMMERCE = "ecommerce"
    FITNESS = "fitness"
    BANKING = "banking"

class UserRole(Enum):
    CUSTOMER = "customer"
    DRIVER = "driver"
    RESTAURANT = "restaurant"
    ADMIN = "admin"
    VENDOR = "vendor"

@dataclass
class AppArchitecture:
    """Defines the architecture for a complex app"""
    app_type: AppType
    user_roles: List[UserRole]
    core_features: List[str]
    navigation_pattern: str
    state_management: str
    data_persistence: str
    
class ComplexAppTemplates:
    """Templates for generating complex iOS apps"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
        
    def _initialize_templates(self) -> Dict[AppType, Dict[str, Any]]:
        """Initialize app templates with copyright-free implementations"""
        return {
            AppType.FOOD_DELIVERY: {
                "name": "DeliveryApp",
                "description": "Multi-role food delivery platform",
                "roles": [UserRole.CUSTOMER, UserRole.RESTAURANT, UserRole.DRIVER],
                "core_screens": {
                    UserRole.CUSTOMER: [
                        "HomeView", "RestaurantListView", "MenuView", 
                        "CartView", "CheckoutView", "OrderTrackingView",
                        "ProfileView", "OrderHistoryView"
                    ],
                    UserRole.RESTAURANT: [
                        "DashboardView", "MenuManagementView", "OrdersView",
                        "AnalyticsView", "SettingsView"
                    ],
                    UserRole.DRIVER: [
                        "AvailabilityView", "OrderRequestView", "NavigationView",
                        "EarningsView", "DeliveryHistoryView"
                    ]
                },
                "models": [
                    "User", "Restaurant", "MenuItem", "Order", 
                    "OrderItem", "DeliveryAddress", "Payment",
                    "Review", "DeliveryTask"
                ],
                "features": [
                    "Real-time order tracking",
                    "Location-based restaurant search",
                    "Multiple payment methods",
                    "Rating and review system",
                    "Push notifications",
                    "Order history",
                    "Promotional offers"
                ]
            },
            
            AppType.RIDE_SHARING: {
                "name": "RideApp",
                "description": "Transportation service platform",
                "roles": [UserRole.CUSTOMER, UserRole.DRIVER],
                "core_screens": {
                    UserRole.CUSTOMER: [
                        "MapView", "RideRequestView", "RideDetailsView",
                        "PaymentView", "RideHistoryView", "ProfileView"
                    ],
                    UserRole.DRIVER: [
                        "DriverMapView", "RideRequestsView", "NavigationView",
                        "EarningsView", "DriverProfileView"
                    ]
                },
                "models": [
                    "User", "Driver", "Ride", "Location",
                    "Payment", "Vehicle", "Rating"
                ],
                "features": [
                    "Real-time location tracking",
                    "Dynamic pricing",
                    "Route optimization",
                    "In-app messaging",
                    "Payment integration",
                    "Driver ratings"
                ]
            }
        }
    
    def get_architecture_template(self, app_type: AppType) -> str:
        """Generate MVVM + Clean Architecture template"""
        return '''
// MARK: - Domain Layer

protocol {name}Repository {
    func fetch{name}s() async throws -> [{name}]
    func create{name}(_ item: {name}) async throws -> {name}
    func update{name}(_ item: {name}) async throws -> {name}
    func delete{name}(_ id: String) async throws
}

// MARK: - Use Cases

class Fetch{name}sUseCase {
    private let repository: {name}Repository
    
    init(repository: {name}Repository) {
        self.repository = repository
    }
    
    func execute() async throws -> [{name}] {
        return try await repository.fetch{name}s()
    }
}

// MARK: - Data Layer

class {name}RepositoryImpl: {name}Repository {
    private let networkService: NetworkService
    private let cacheService: CacheService
    
    init(networkService: NetworkService, cacheService: CacheService) {
        self.networkService = networkService
        self.cacheService = cacheService
    }
    
    func fetch{name}s() async throws -> [{name}] {
        // Try cache first
        if let cached = try? await cacheService.get{name}s() {
            return cached
        }
        
        // Fetch from network
        let items = try await networkService.fetch{name}s()
        try? await cacheService.save{name}s(items)
        return items
    }
}

// MARK: - Presentation Layer

@MainActor
class {name}ViewModel: ObservableObject {
    @Published var items: [{name}] = []
    @Published var isLoading = false
    @Published var error: Error?
    
    private let useCase: Fetch{name}sUseCase
    
    init(useCase: Fetch{name}sUseCase) {
        self.useCase = useCase
    }
    
    func loadItems() async {
        isLoading = true
        error = nil
        
        do {
            items = try await useCase.execute()
        } catch {
            self.error = error
        }
        
        isLoading = false
    }
}
'''

    def get_navigation_coordinator(self, app_type: AppType) -> str:
        """Generate role-based navigation coordinator"""
        template = self.templates.get(app_type)
        if not template:
            return ""
            
        return f'''
import SwiftUI

// MARK: - Navigation Coordinator

enum AppRoute: Hashable {{
    case login
    case roleSelection
    case customerFlow
    case driverFlow
    case restaurantFlow
}}

@MainActor
class AppCoordinator: ObservableObject {{
    @Published var path = NavigationPath()
    @Published var currentUser: User?
    
    func navigate(to route: AppRoute) {{
        path.append(route)
    }}
    
    func navigateToRoleBasedHome() {{
        guard let user = currentUser else {{
            navigate(to: .login)
            return
        }}
        
        switch user.role {{
        case .customer:
            navigate(to: .customerFlow)
        case .driver:
            navigate(to: .driverFlow)
        case .restaurant:
            navigate(to: .restaurantFlow)
        default:
            navigate(to: .roleSelection)
        }}
    }}
    
    func popToRoot() {{
        path.removeLast(path.count)
    }}
}}

// MARK: - Root Navigation View

struct RootNavigationView: View {{
    @StateObject private var coordinator = AppCoordinator()
    @StateObject private var authService = AuthenticationService()
    
    var body: some View {{
        NavigationStack(path: $coordinator.path) {{
            SplashView()
                .navigationDestination(for: AppRoute.self) {{ route in
                    switch route {{
                    case .login:
                        LoginView()
                            .environmentObject(coordinator)
                            .environmentObject(authService)
                    case .roleSelection:
                        RoleSelectionView()
                            .environmentObject(coordinator)
                    case .customerFlow:
                        CustomerTabView()
                            .environmentObject(coordinator)
                    case .driverFlow:
                        DriverTabView()
                            .environmentObject(coordinator)
                    case .restaurantFlow:
                        RestaurantTabView()
                            .environmentObject(coordinator)
                    }}
                }}
        }}
        .environmentObject(coordinator)
    }}
}}
'''

    def get_dependency_injection_container(self) -> str:
        """Generate DI container for complex apps"""
        return '''
import Foundation

// MARK: - Dependency Injection Container

class DIContainer {
    static let shared = DIContainer()
    
    private init() {}
    
    // MARK: - Network Services
    
    lazy var networkService: NetworkService = {
        NetworkServiceImpl()
    }()
    
    lazy var locationService: LocationService = {
        LocationServiceImpl()
    }()
    
    // MARK: - Persistence
    
    lazy var coreDataManager: CoreDataManager = {
        CoreDataManager()
    }()
    
    lazy var userDefaultsService: UserDefaultsService = {
        UserDefaultsServiceImpl()
    }()
    
    // MARK: - Repositories
    
    lazy var userRepository: UserRepository = {
        UserRepositoryImpl(
            networkService: networkService,
            coreDataManager: coreDataManager
        )
    }()
    
    lazy var orderRepository: OrderRepository = {
        OrderRepositoryImpl(
            networkService: networkService,
            coreDataManager: coreDataManager
        )
    }()
    
    // MARK: - Use Cases
    
    func makeLoginUseCase() -> LoginUseCase {
        LoginUseCase(userRepository: userRepository)
    }
    
    func makeFetchOrdersUseCase() -> FetchOrdersUseCase {
        FetchOrdersUseCase(orderRepository: orderRepository)
    }
    
    // MARK: - ViewModels
    
    func makeLoginViewModel() -> LoginViewModel {
        LoginViewModel(loginUseCase: makeLoginUseCase())
    }
    
    func makeOrderListViewModel() -> OrderListViewModel {
        OrderListViewModel(fetchOrdersUseCase: makeFetchOrdersUseCase())
    }
}

// MARK: - Service Locator Pattern

protocol ServiceLocating {
    func resolve<T>(_ type: T.Type) -> T
}

extension DIContainer: ServiceLocating {
    func resolve<T>(_ type: T.Type) -> T {
        switch type {
        case is NetworkService.Type:
            return networkService as! T
        case is LocationService.Type:
            return locationService as! T
        default:
            fatalError("Service \\(type) not registered")
        }
    }
}
'''

    def get_mock_services(self, app_type: AppType) -> str:
        """Generate mock services for testing"""
        return '''
import Foundation
import Combine

// MARK: - Mock Network Service

class MockNetworkService: NetworkService {
    var shouldFail = false
    var delay: TimeInterval = 0.5
    
    func fetch<T: Decodable>(_ endpoint: Endpoint) async throws -> T {
        // Simulate network delay
        try await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
        
        if shouldFail {
            throw NetworkError.serverError(500, "Mock server error")
        }
        
        // Return mock data based on type
        if T.self == [Restaurant].self {
            return mockRestaurants() as! T
        } else if T.self == [Order].self {
            return mockOrders() as! T
        }
        
        throw NetworkError.invalidResponse
    }
    
    private func mockRestaurants() -> [Restaurant] {
        return [
            Restaurant(
                id: "1",
                name: "Pizza Palace",
                cuisine: "Italian",
                rating: 4.5,
                deliveryTime: "25-35 min",
                deliveryFee: 2.99,
                imageURL: "pizza_palace",
                isOpen: true
            ),
            Restaurant(
                id: "2",
                name: "Burger Barn",
                cuisine: "American",
                rating: 4.2,
                deliveryTime: "20-30 min",
                deliveryFee: 1.99,
                imageURL: "burger_barn",
                isOpen: true
            )
        ]
    }
    
    private func mockOrders() -> [Order] {
        return [
            Order(
                id: "order1",
                restaurantName: "Pizza Palace",
                items: ["Margherita Pizza", "Caesar Salad"],
                total: 25.99,
                status: .delivered,
                orderDate: Date().addingTimeInterval(-86400)
            )
        ]
    }
}

// MARK: - Mock Location Service

class MockLocationService: LocationService {
    @Published var currentLocation: Location?
    
    func requestLocationPermission() async -> Bool {
        return true
    }
    
    func startLocationUpdates() {
        // Simulate location updates
        currentLocation = Location(
            latitude: 37.7749,
            longitude: -122.4194,
            address: "San Francisco, CA"
        )
    }
    
    func calculateRoute(from: Location, to: Location) async -> Route? {
        return Route(
            distance: 5.2,
            duration: 15,
            polylinePoints: []
        )
    }
}
'''

    def detect_app_type(self, description: str) -> Optional[AppType]:
        """Detect app type from user description"""
        description_lower = description.lower()
        
        # Food delivery keywords
        if any(keyword in description_lower for keyword in 
               ['doordash', 'uber eats', 'food delivery', 'restaurant delivery', 
                'grubhub', 'meal delivery', 'food ordering']):
            return AppType.FOOD_DELIVERY
            
        # Ride sharing keywords
        if any(keyword in description_lower for keyword in 
               ['uber', 'lyft', 'taxi', 'ride sharing', 'ride hailing',
                'transportation', 'driver app']):
            return AppType.RIDE_SHARING
            
        # Social media keywords
        if any(keyword in description_lower for keyword in 
               ['instagram', 'twitter', 'social media', 'social network',
                'posts', 'followers', 'feed']):
            return AppType.SOCIAL_MEDIA
            
        # E-commerce keywords
        if any(keyword in description_lower for keyword in 
               ['amazon', 'shopping', 'ecommerce', 'marketplace',
                'products', 'cart', 'checkout']):
            return AppType.ECOMMERCE
            
        return None
        
    def sanitize_app_request(self, description: str) -> str:
        """Remove copyrighted terms and replace with generic ones"""
        replacements = {
            'doordash': 'food delivery app',
            'ubereats': 'food delivery app',
            'uber eats': 'food delivery app',
            'uber': 'ride sharing app',
            'lyft': 'ride sharing app',
            'instagram': 'social media app',
            'twitter': 'social media app',
            'amazon': 'shopping app',
            'like': 'similar to',
            'clone': 'app inspired by'
        }
        
        sanitized = description.lower()
        for term, replacement in replacements.items():
            sanitized = sanitized.replace(term, replacement)
            
        return sanitized