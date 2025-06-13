"""
Advanced App Generator for SwiftGen AI
Supports complex, real-world applications with proper architecture
"""

import json
from typing import Dict, List, Optional
from datetime import datetime

class AdvancedAppGenerator:
    """Generator for complex, production-ready iOS applications"""
    
    def __init__(self, llm_service=None):
        self.llm_service = llm_service
        
        # App complexity templates - only include implemented ones
        self.app_templates = {
            "social_media": self._social_media_template,
            # More templates will be added as implemented
        }
        
    async def generate_advanced_app(self, description: str, app_name: str) -> Dict:
        """Generate a complex app with proper architecture"""
        
        # Detect app type from description
        app_type = self._detect_app_type(description)
        
        # Get enhanced prompt for complex apps
        enhanced_prompt = self._build_advanced_prompt(description, app_name, app_type)
        
        # Generate with LLM
        if self.llm_service:
            result = await self.llm_service.generate_ios_app_multi_llm(
                description=enhanced_prompt,
                app_name=app_name
            )
            
            # Enhance with architectural components
            if result and "files" in result:
                result = self._enhance_architecture(result, app_type)
                
            return result
        else:
            # Fallback to template
            return self._generate_from_template(app_type, app_name, description)
    
    def _detect_app_type(self, description: str) -> str:
        """Detect the type of app from description"""
        description_lower = description.lower()
        
        # Keywords for different app types
        type_keywords = {
            "social_media": ["social", "chat", "message", "friend", "post", "share", "follow"],
            "ecommerce": ["shop", "buy", "sell", "product", "cart", "payment", "store"],
            "productivity": ["task", "todo", "note", "calendar", "reminder", "organize"],
            "finance": ["bank", "money", "budget", "expense", "investment", "crypto"],
            "healthcare": ["health", "medical", "doctor", "patient", "medicine", "fitness"],
            "education": ["learn", "course", "study", "quiz", "exam", "tutorial"],
            "entertainment": ["game", "music", "video", "movie", "play", "fun"],
            "travel": ["trip", "hotel", "flight", "booking", "destination", "travel"],
            "fitness": ["workout", "exercise", "gym", "training", "health", "diet"],
            "news": ["news", "article", "blog", "read", "magazine", "publication"]
        }
        
        # Score each type
        scores = {}
        for app_type, keywords in type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in description_lower)
            if score > 0:
                scores[app_type] = score
        
        # Return highest scoring type or default
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        return "productivity"  # Default
    
    def _build_advanced_prompt(self, description: str, app_name: str, app_type: str) -> str:
        """Build enhanced prompt for complex apps"""
        
        architecture_requirements = {
            "social_media": """
- User authentication and profile management
- Real-time messaging with WebSocket support
- Feed with infinite scrolling
- Push notifications
- Image/video upload and processing
- User discovery and follow system
- Privacy settings
""",
            "ecommerce": """
- Product catalog with search and filters
- Shopping cart with persistence
- Secure payment integration
- Order tracking
- User reviews and ratings
- Wishlist functionality
- Inventory management
""",
            "finance": """
- Secure authentication with biometrics
- Account overview and transactions
- Budget tracking and analytics
- Bill payments and transfers
- Investment portfolio
- Spending insights with charts
- Data encryption
""",
            "healthcare": """
- HIPAA-compliant data handling
- Appointment scheduling
- Medical records management
- Prescription tracking
- Telemedicine support
- Health metrics tracking
- Emergency contacts
""",
            "productivity": """
- Task management with priorities
- Calendar integration
- Collaboration features
- File attachments
- Reminders and notifications
- Search and filtering
- Data sync across devices
"""
        }
        
        arch_req = architecture_requirements.get(app_type, "")
        
        return f"""
Create a production-ready {app_type.replace('_', ' ')} iOS app called "{app_name}".

{description}

ARCHITECTURAL REQUIREMENTS:
{arch_req}

TECHNICAL REQUIREMENTS:
1. Use MVVM architecture with clear separation of concerns
2. Implement proper error handling and loading states
3. Use async/await for all asynchronous operations
4. Include unit testable code structure
5. Support offline functionality where applicable
6. Implement proper data caching
7. Use dependency injection for services
8. Follow SOLID principles

FILE STRUCTURE:
- App.swift (main app entry)
- Models/ (data models)
- Views/ (SwiftUI views)
- ViewModels/ (business logic)
- Services/ (API, data, auth services)
- Utils/ (helpers and extensions)
- Resources/ (assets and configs)

Create all necessary files for a complete, working application.
"""
    
    def _enhance_architecture(self, result: Dict, app_type: str) -> Dict:
        """Enhance generated code with architectural components"""
        
        # Add common services if not present
        files = result.get("files", [])
        file_paths = [f.get("path", "") for f in files]
        
        # Add NetworkService if needed
        if not any("NetworkService" in path for path in file_paths):
            if any("API" in str(f.get("content", "")) for f in files):
                files.append(self._create_network_service())
        
        # Add DataStore if needed
        if not any("DataStore" in path for path in file_paths):
            if any("@AppStorage" in str(f.get("content", "")) for f in files):
                files.append(self._create_data_store())
        
        # Add AuthService for certain app types
        if app_type in ["social_media", "ecommerce", "finance", "healthcare"]:
            if not any("AuthService" in path for path in file_paths):
                files.append(self._create_auth_service())
        
        result["files"] = files
        return result
    
    def _create_network_service(self) -> Dict:
        """Create a reusable network service"""
        return {
            "path": "Sources/Services/NetworkService.swift",
            "content": """import Foundation

class NetworkService {
    static let shared = NetworkService()
    private init() {}
    
    enum NetworkError: Error {
        case invalidURL
        case noData
        case decodingError
        case serverError(Int)
    }
    
    func fetch<T: Decodable>(_ type: T.Type, from endpoint: String) async throws -> T {
        guard let url = URL(string: endpoint) else {
            throw NetworkError.invalidURL
        }
        
        let (data, response) = try await URLSession.shared.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.serverError(0)
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            throw NetworkError.serverError(httpResponse.statusCode)
        }
        
        do {
            return try JSONDecoder().decode(T.self, from: data)
        } catch {
            throw NetworkError.decodingError
        }
    }
    
    func post<T: Encodable, R: Decodable>(_ data: T, to endpoint: String, expecting: R.Type) async throws -> R {
        guard let url = URL(string: endpoint) else {
            throw NetworkError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(data)
        
        let (responseData, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw NetworkError.serverError((response as? HTTPURLResponse)?.statusCode ?? 0)
        }
        
        return try JSONDecoder().decode(R.self, from: responseData)
    }
}
"""
        }
    
    def _create_data_store(self) -> Dict:
        """Create a data persistence service"""
        return {
            "path": "Sources/Services/DataStore.swift",
            "content": """import Foundation
import SwiftUI

class DataStore: ObservableObject {
    static let shared = DataStore()
    
    @AppStorage("user_preferences") private var userPreferencesData: Data = Data()
    @Published var userPreferences: UserPreferences = UserPreferences()
    
    private init() {
        loadPreferences()
    }
    
    func save<T: Codable>(_ object: T, for key: String) {
        if let encoded = try? JSONEncoder().encode(object) {
            UserDefaults.standard.set(encoded, forKey: key)
        }
    }
    
    func load<T: Codable>(_ type: T.Type, for key: String) -> T? {
        guard let data = UserDefaults.standard.data(forKey: key),
              let decoded = try? JSONDecoder().decode(T.self, from: data) else {
            return nil
        }
        return decoded
    }
    
    private func loadPreferences() {
        if let decoded = try? JSONDecoder().decode(UserPreferences.self, from: userPreferencesData) {
            userPreferences = decoded
        }
    }
    
    func savePreferences() {
        if let encoded = try? JSONEncoder().encode(userPreferences) {
            userPreferencesData = encoded
        }
    }
}

struct UserPreferences: Codable {
    var theme: String = "system"
    var notifications: Bool = true
    var language: String = "en"
}
"""
        }
    
    def _create_auth_service(self) -> Dict:
        """Create an authentication service"""
        return {
            "path": "Sources/Services/AuthService.swift",
            "content": """import Foundation
import LocalAuthentication

class AuthService: ObservableObject {
    static let shared = AuthService()
    
    @Published var isAuthenticated = false
    @Published var currentUser: User?
    
    private init() {}
    
    func signIn(email: String, password: String) async throws {
        // In production, this would call your backend API
        // For demo, we'll simulate authentication
        try await Task.sleep(nanoseconds: 1_000_000_000) // 1 second delay
        
        // Simulate successful authentication
        await MainActor.run {
            self.currentUser = User(
                id: UUID().uuidString,
                email: email,
                name: "Demo User"
            )
            self.isAuthenticated = true
        }
        
        // Save auth token
        UserDefaults.standard.set(true, forKey: "isAuthenticated")
    }
    
    func signOut() {
        currentUser = nil
        isAuthenticated = false
        UserDefaults.standard.removeObject(forKey: "isAuthenticated")
    }
    
    func checkBiometricAuthentication() async -> Bool {
        let context = LAContext()
        var error: NSError?
        
        guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else {
            return false
        }
        
        do {
            let success = try await context.evaluatePolicy(
                .deviceOwnerAuthenticationWithBiometrics,
                localizedReason: "Authenticate to access your account"
            )
            return success
        } catch {
            return false
        }
    }
}

struct User: Codable, Identifiable {
    let id: String
    let email: String
    let name: String
}
"""
        }
    
    def _social_media_template(self, app_name: str, description: str) -> Dict:
        """Template for social media apps"""
        return {
            "files": [
                {
                    "path": "Sources/App.swift",
                    "content": f"""import SwiftUI

@main
struct {app_name.replace(' ', '')}App: App {{
    @StateObject private var authService = AuthService.shared
    @StateObject private var dataStore = DataStore.shared
    
    var body: some Scene {{
        WindowGroup {{
            ContentView()
                .environmentObject(authService)
                .environmentObject(dataStore)
        }}
    }}
}}"""
                },
                self._create_auth_service(),
                self._create_network_service(),
                self._create_data_store(),
                # Add more social media specific files...
            ],
            "bundle_id": f"com.swiftgen.{app_name.lower().replace(' ', '')}",
            "features": [
                "User Authentication",
                "Real-time Messaging",
                "Social Feed",
                "User Profiles",
                "Media Sharing"
            ],
            "app_name": app_name
        }
    
    # Additional templates will be implemented as needed
    # def _ecommerce_template(self, app_name: str, description: str) -> Dict:
    #     """Template for e-commerce apps"""
    #     pass
    
    def _generate_from_template(self, app_type: str, app_name: str, description: str) -> Dict:
        """Generate app from template if LLM fails"""
        template_func = self.app_templates.get(app_type)
        if template_func:
            return template_func(app_name, description)
        
        # Default template
        return {
            "files": [
                {
                    "path": "Sources/App.swift",
                    "content": f"""import SwiftUI

@main
struct {app_name.replace(' ', '')}App: App {{
    var body: some Scene {{
        WindowGroup {{
            ContentView()
        }}
    }}
}}"""
                },
                {
                    "path": "Sources/ContentView.swift",
                    "content": """import SwiftUI

struct ContentView: View {
    var body: some View {
        NavigationStack {
            Text("Welcome to \\(Bundle.main.displayName ?? "App")")
                .font(.largeTitle)
                .padding()
        }
    }
}"""
                }
            ],
            "bundle_id": f"com.swiftgen.{app_name.lower().replace(' ', '')}",
            "app_name": app_name
        }