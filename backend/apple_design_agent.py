#!/usr/bin/env python3
"""
Apple Design Agent - Specialized agent for iOS UI/UX following Apple HIG
Ensures all generated UI code follows Apple's Human Interface Guidelines
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import re

from specialized_agents import BaseAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AppleDesignAgent(BaseAgent):
    """Specialized in creating beautiful iOS UIs following Apple HIG"""
    
    def __init__(self, model=None):
        super().__init__("AppleDesignAgent", model)
        self.expertise_areas = [
            "ui", "design", "interface", "layout", "style",
            "theme", "appearance", "look", "beautiful", "modern"
        ]
        
        # Apple HIG principles
        self.design_principles = {
            "clarity": "Deference to content, clarity, and depth",
            "deference": "UI helps users understand and interact with content",
            "depth": "Visual layers and realistic motion convey hierarchy",
            "consistency": "Familiar standards and paradigms",
            "direct_manipulation": "Direct manipulation of onscreen content",
            "feedback": "Immediate feedback for user actions",
            "metaphors": "Users learn more quickly when virtual objects behave like real ones",
            "user_control": "People initiate and control actions"
        }
        
        # iOS design patterns
        self.ui_patterns = {
            "navigation": {
                "patterns": ["NavigationStack", "TabView", "SplitView"],
                "guidelines": "Use standard navigation patterns for familiarity"
            },
            "lists": {
                "patterns": ["List", "Form", "ForEach with proper spacing"],
                "guidelines": "Lists should be scannable with clear hierarchy"
            },
            "modals": {
                "patterns": [".sheet", ".fullScreenCover", ".popover"],
                "guidelines": "Use modals sparingly for focused tasks"
            },
            "controls": {
                "patterns": ["Button", "Toggle", "Picker", "Slider"],
                "guidelines": "Controls should be at least 44x44 points"
            },
            "gestures": {
                "patterns": ["onTapGesture", "DragGesture", "LongPressGesture"],
                "guidelines": "Gestures should be discoverable and reversible"
            }
        }
        
        # Apple color palette
        self.system_colors = {
            "primary": [".blue", ".green", ".indigo", ".mint", ".pink", ".purple", ".red", ".teal", ".cyan"],
            "semantic": [".primary", ".secondary", ".accentColor"],
            "adaptive": ["Color(.systemBackground)", "Color(.label)", "Color(.systemGray)"]
        }
        
        # Typography guidelines
        self.typography = {
            "large_title": ".largeTitle",
            "title": ".title",
            "title2": ".title2",
            "title3": ".title3",
            "headline": ".headline",
            "body": ".body",
            "callout": ".callout",
            "subheadline": ".subheadline",
            "footnote": ".footnote",
            "caption": ".caption",
            "caption2": ".caption2"
        }
        
        # Spacing and layout
        self.spacing = {
            "compact": 8,
            "regular": 16,
            "loose": 24,
            "extra_loose": 32
        }
        
        # Animation guidelines
        self.animations = {
            "spring": ".spring(response: 0.35, dampingFraction: 0.8)",
            "smooth": ".easeInOut(duration: 0.3)",
            "bouncy": ".interpolatingSpring(stiffness: 180, damping: 15)",
            "subtle": ".easeOut(duration: 0.2)"
        }
    
    async def can_handle(self, request: Dict) -> float:
        """Check if this is a UI/design request"""
        description = request.get("description", "").lower()
        modification = request.get("modification", "").lower()
        
        # Check for UI/design keywords
        ui_keywords = [
            "ui", "design", "beautiful", "modern", "clean",
            "interface", "layout", "style", "theme", "color",
            "animation", "gesture", "navigation", "appearance"
        ]
        
        if any(keyword in description + modification for keyword in ui_keywords):
            return 0.95
        
        # Check if it's a general app request (we can enhance UI)
        if request.get("files") or "app" in description:
            return 0.7
        
        return 0.3
    
    async def process(self, request: Dict) -> Dict:
        """Process UI/design requests"""
        request_type = self._determine_request_type(request)
        
        if request_type == "new_ui":
            return await self._create_new_ui(request)
        elif request_type == "enhance_ui":
            return await self._enhance_existing_ui(request)
        elif request_type == "fix_ui":
            return await self._fix_ui_issues(request)
        else:
            return await self._apply_design_system(request)
    
    def _determine_request_type(self, request: Dict) -> str:
        """Determine what type of UI work is needed"""
        if request.get("files"):
            if "enhance" in request.get("modification", "").lower():
                return "enhance_ui"
            elif "fix" in request.get("modification", "").lower():
                return "fix_ui"
            else:
                return "apply_design"
        else:
            return "new_ui"
    
    async def _create_new_ui(self, request: Dict) -> Dict:
        """Create new UI from scratch"""
        app_type = request.get("app_type", "general")
        description = request.get("description", "")
        
        self.log_action("Creating new UI", {
            "app_type": app_type,
            "description": description[:100]
        })
        
        # Generate UI based on app type
        if "todo" in description.lower():
            ui_code = self._generate_todo_ui()
        elif "weather" in description.lower():
            ui_code = self._generate_weather_ui()
        elif "social" in description.lower():
            ui_code = self._generate_social_ui()
        else:
            ui_code = self._generate_modern_ui(app_type, description)
        
        return {
            "success": True,
            "files": ui_code,
            "design_patterns": ["Apple HIG compliant", "Accessibility ready"],
            "agent": self.name
        }
    
    def _generate_modern_ui(self, app_type: str, description: str) -> List[Dict]:
        """Generate modern UI following Apple HIG"""
        app_name = "ModernApp"
        
        # Main app file with proper theming
        app_file = f"""import SwiftUI

@main
struct {app_name}App: App {{
    @StateObject private var appState = AppState()
    @Environment(\\.colorScheme) var colorScheme
    
    var body: some Scene {{
        WindowGroup {{
            ContentView()
                .environmentObject(appState)
                .tint(.accentColor)
                .preferredColorScheme(appState.userPreferredColorScheme)
        }}
    }}
}}

// MARK: - App State
class AppState: ObservableObject {{
    @Published var userPreferredColorScheme: ColorScheme? = nil
    @Published var hapticFeedbackEnabled = true
    @Published var reduceMotion = false
    
    init() {{
        loadUserPreferences()
    }}
    
    func loadUserPreferences() {{
        // Load from UserDefaults
    }}
}}"""

        # Beautiful content view with modern design
        content_view = """import SwiftUI

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    @Environment(\\.colorScheme) var colorScheme
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            HomeView()
                .tabItem {
                    Label("Home", systemImage: "house.fill")
                }
                .tag(0)
            
            ExploreView()
                .tabItem {
                    Label("Explore", systemImage: "safari.fill")
                }
                .tag(1)
            
            ProfileView()
                .tabItem {
                    Label("Profile", systemImage: "person.crop.circle.fill")
                }
                .tag(2)
        }
        .accentColor(Color.accentColor)
    }
}

// MARK: - Home View
struct HomeView: View {
    @State private var searchText = ""
    @State private var showingDetail = false
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    // Hero Section
                    HeroCard()
                        .padding(.horizontal)
                    
                    // Feature Cards
                    VStack(alignment: .leading, spacing: 16) {
                        Text("Featured")
                            .font(.title2.bold())
                            .padding(.horizontal)
                        
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 16) {
                                ForEach(0..<5) { index in
                                    FeatureCard(index: index)
                                        .onTapGesture {
                                            withAnimation(.spring()) {
                                                showingDetail = true
                                            }
                                        }
                                }
                            }
                            .padding(.horizontal)
                        }
                    }
                    
                    // Content Grid
                    ContentGrid()
                        .padding(.horizontal)
                }
                .padding(.vertical)
            }
            .navigationTitle("Home")
            .searchable(text: $searchText, prompt: "Search")
            .sheet(isPresented: $showingDetail) {
                DetailView()
            }
        }
    }
}

// MARK: - Components
struct HeroCard: View {
    @Environment(\\.colorScheme) var colorScheme
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Gradient background
            LinearGradient(
                colors: [.accentColor, .accentColor.opacity(0.7)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .frame(height: 200)
            .overlay(
                VStack(alignment: .leading, spacing: 8) {
                    Text("Welcome")
                        .font(.largeTitle.bold())
                        .foregroundStyle(.white)
                    
                    Text("Discover amazing content")
                        .font(.title3)
                        .foregroundStyle(.white.opacity(0.9))
                    
                    Spacer()
                    
                    Button(action: {}) {
                        Label("Get Started", systemImage: "arrow.forward")
                            .font(.headline)
                            .padding(.horizontal, 20)
                            .padding(.vertical, 12)
                            .background(.white)
                            .foregroundStyle(.accentColor)
                            .clipShape(Capsule())
                    }
                }
                .padding(24)
                .frame(maxWidth: .infinity, alignment: .leading)
            )
            .clipShape(RoundedRectangle(cornerRadius: 20))
            .shadow(color: .black.opacity(0.1), radius: 10, y: 5)
        }
    }
}

struct FeatureCard: View {
    let index: Int
    @Environment(\\.colorScheme) var colorScheme
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Placeholder image
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.accentColor.opacity(0.2))
                .frame(width: 160, height: 100)
                .overlay(
                    Image(systemName: "star.fill")
                        .font(.largeTitle)
                        .foregroundStyle(.accentColor)
                )
            
            VStack(alignment: .leading, spacing: 4) {
                Text("Feature \\(index + 1)")
                    .font(.headline)
                
                Text("Amazing content here")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(colorScheme == .dark ? Color(.systemGray6) : .white)
                .shadow(color: .black.opacity(0.05), radius: 8, y: 4)
        )
    }
}

struct ContentGrid: View {
    let columns = [
        GridItem(.flexible()),
        GridItem(.flexible())
    ]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Browse")
                .font(.title2.bold())
            
            LazyVGrid(columns: columns, spacing: 16) {
                ForEach(0..<6) { index in
                    GridCard(index: index)
                }
            }
        }
    }
}

struct GridCard: View {
    let index: Int
    @Environment(\\.colorScheme) var colorScheme
    @State private var isPressed = false
    
    var body: some View {
        VStack(spacing: 12) {
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.accentColor.opacity(0.1))
                .frame(height: 120)
                .overlay(
                    Image(systemName: "app.fill")
                        .font(.largeTitle)
                        .foregroundStyle(.accentColor)
                )
            
            Text("Item \\(index + 1)")
                .font(.headline)
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(colorScheme == .dark ? Color(.systemGray6) : .white)
                .shadow(color: .black.opacity(0.05), radius: 8, y: 4)
        )
        .scaleEffect(isPressed ? 0.95 : 1.0)
        .onTapGesture {
            withAnimation(.spring(response: 0.3, dampingFraction: 0.6)) {
                isPressed = true
            }
            
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                withAnimation(.spring(response: 0.3, dampingFraction: 0.6)) {
                    isPressed = false
                }
            }
        }
    }
}

// MARK: - Other Views
struct ExploreView: View {
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    ForEach(0..<10) { _ in
                        ExploreRow()
                    }
                }
                .padding()
            }
            .navigationTitle("Explore")
        }
    }
}

struct ExploreRow: View {
    @Environment(\\.colorScheme) var colorScheme
    
    var body: some View {
        HStack(spacing: 16) {
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.accentColor.opacity(0.2))
                .frame(width: 80, height: 80)
            
            VStack(alignment: .leading, spacing: 4) {
                Text("Discover Something New")
                    .font(.headline)
                
                Text("Explore amazing content and features")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
            }
            
            Spacer()
            
            Image(systemName: "chevron.right")
                .foregroundStyle(.secondary)
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(colorScheme == .dark ? Color(.systemGray6) : .white)
        )
    }
}

struct ProfileView: View {
    @State private var notificationsEnabled = true
    @State private var darkModeEnabled = false
    
    var body: some View {
        NavigationStack {
            Form {
                Section {
                    HStack {
                        Circle()
                            .fill(Color.accentColor.opacity(0.2))
                            .frame(width: 60, height: 60)
                            .overlay(
                                Image(systemName: "person.fill")
                                    .font(.title)
                                    .foregroundStyle(.accentColor)
                            )
                        
                        VStack(alignment: .leading) {
                            Text("User Name")
                                .font(.headline)
                            Text("user@example.com")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                    }
                    .padding(.vertical, 8)
                }
                
                Section("Preferences") {
                    Toggle("Notifications", isOn: $notificationsEnabled)
                    Toggle("Dark Mode", isOn: $darkModeEnabled)
                }
                
                Section("About") {
                    HStack {
                        Text("Version")
                        Spacer()
                        Text("1.0.0")
                            .foregroundStyle(.secondary)
                    }
                }
            }
            .navigationTitle("Profile")
        }
    }
}

struct DetailView: View {
    @Environment(\\.dismiss) var dismiss
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    // Hero image
                    RoundedRectangle(cornerRadius: 20)
                        .fill(LinearGradient(
                            colors: [.accentColor, .accentColor.opacity(0.7)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        ))
                        .frame(height: 300)
                        .overlay(
                            Image(systemName: "star.fill")
                                .font(.system(size: 80))
                                .foregroundStyle(.white)
                        )
                    
                    VStack(alignment: .leading, spacing: 16) {
                        Text("Amazing Feature")
                            .font(.largeTitle.bold())
                        
                        Text("This is a detailed view showcasing beautiful design patterns and smooth animations following Apple's Human Interface Guidelines.")
                            .font(.body)
                            .foregroundStyle(.secondary)
                        
                        // Action buttons
                        HStack(spacing: 12) {
                            Button(action: {}) {
                                Label("Share", systemImage: "square.and.arrow.up")
                                    .frame(maxWidth: .infinity)
                            }
                            .buttonStyle(.bordered)
                            
                            Button(action: {}) {
                                Label("Save", systemImage: "bookmark")
                                    .frame(maxWidth: .infinity)
                            }
                            .buttonStyle(.borderedProminent)
                        }
                        .padding(.top)
                    }
                    .padding()
                }
            }
            .navigationTitle("Details")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }
}"""

        # Accessibility extensions
        accessibility_extensions = """import SwiftUI

// MARK: - Accessibility Extensions
extension View {
    /// Add accessibility label and hint
    func accessibilityElement(label: String, hint: String? = nil) -> some View {
        self
            .accessibilityLabel(label)
            .accessibilityHint(hint ?? "")
    }
    
    /// Mark as decorative (ignored by VoiceOver)
    func decorative() -> some View {
        self.accessibilityHidden(true)
    }
    
    /// Add accessibility action
    func accessibilityAction(label: String, action: @escaping () -> Void) -> some View {
        self.accessibilityAction(named: Text(label), action)
    }
}

// MARK: - Haptic Feedback
struct HapticFeedback {
    static func impact(_ style: UIImpactFeedbackGenerator.FeedbackStyle = .medium) {
        let generator = UIImpactFeedbackGenerator(style: style)
        generator.prepare()
        generator.impactOccurred()
    }
    
    static func notification(_ type: UINotificationFeedbackGenerator.FeedbackType) {
        let generator = UINotificationFeedbackGenerator()
        generator.prepare()
        generator.notificationOccurred(type)
    }
    
    static func selection() {
        let generator = UISelectionFeedbackGenerator()
        generator.prepare()
        generator.selectionChanged()
    }
}

// MARK: - Design System
struct DesignSystem {
    // Spacing
    static let spacing = Spacing()
    
    struct Spacing {
        let xs: CGFloat = 4
        let sm: CGFloat = 8
        let md: CGFloat = 16
        let lg: CGFloat = 24
        let xl: CGFloat = 32
        let xxl: CGFloat = 48
    }
    
    // Corner Radius
    static let cornerRadius = CornerRadius()
    
    struct CornerRadius {
        let small: CGFloat = 8
        let medium: CGFloat = 12
        let large: CGFloat = 20
        let full: CGFloat = .infinity
    }
    
    // Shadows
    static func shadow(intensity: ShadowIntensity) -> some View {
        switch intensity {
        case .light:
            return Color.black.opacity(0.05)
        case .medium:
            return Color.black.opacity(0.1)
        case .heavy:
            return Color.black.opacity(0.2)
        }
    }
    
    enum ShadowIntensity {
        case light, medium, heavy
    }
}"""

        # Theme manager
        theme_manager = """import SwiftUI

// MARK: - Theme Manager
class ThemeManager: ObservableObject {
    @Published var currentTheme: Theme = .system
    @Published var accentColor: Color = .blue
    
    enum Theme: String, CaseIterable {
        case light = "Light"
        case dark = "Dark"
        case system = "System"
        
        var colorScheme: ColorScheme? {
            switch self {
            case .light: return .light
            case .dark: return .dark
            case .system: return nil
            }
        }
    }
    
    func applyTheme() {
        // Save to UserDefaults
        UserDefaults.standard.set(currentTheme.rawValue, forKey: "theme")
        UserDefaults.standard.set(accentColor.description, forKey: "accentColor")
    }
}

// MARK: - Custom Modifiers
struct CardStyle: ViewModifier {
    @Environment(\\.colorScheme) var colorScheme
    
    func body(content: Content) -> some View {
        content
            .padding()
            .background(
                RoundedRectangle(cornerRadius: DesignSystem.cornerRadius.medium)
                    .fill(colorScheme == .dark ? Color(.systemGray6) : .white)
                    .shadow(
                        color: colorScheme == .dark ? .clear : .black.opacity(0.05),
                        radius: 8,
                        y: 4
                    )
            )
    }
}

extension View {
    func cardStyle() -> some View {
        modifier(CardStyle())
    }
}

// MARK: - Animated Button Style
struct AnimatedButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed ? 0.95 : 1.0)
            .opacity(configuration.isPressed ? 0.8 : 1.0)
            .animation(.spring(response: 0.3, dampingFraction: 0.6), value: configuration.isPressed)
    }
}"""

        return [
            {"path": "Sources/App.swift", "content": app_file},
            {"path": "Sources/Views/ContentView.swift", "content": content_view},
            {"path": "Sources/Extensions/AccessibilityExtensions.swift", "content": accessibility_extensions},
            {"path": "Sources/Managers/ThemeManager.swift", "content": theme_manager}
        ]
    
    async def _enhance_existing_ui(self, request: Dict) -> Dict:
        """Enhance existing UI with modern Apple design"""
        files = request.get("files", [])
        enhancements_made = []
        
        for file in files:
            if file["path"].endswith(".swift") and "View" in file["content"]:
                # Apply UI enhancements
                enhanced_content = self._apply_ui_enhancements(file["content"])
                file["content"] = enhanced_content
                enhancements_made.append(f"Enhanced {file['path']} with modern UI")
        
        return {
            "success": True,
            "files": files,
            "changes_made": enhancements_made,
            "agent": self.name
        }
    
    def _apply_ui_enhancements(self, content: str) -> str:
        """Apply specific UI enhancements to code"""
        # Add proper spacing
        content = self._add_proper_spacing(content)
        
        # Enhance colors
        content = self._enhance_colors(content)
        
        # Add animations
        content = self._add_smooth_animations(content)
        
        # Improve typography
        content = self._improve_typography(content)
        
        # Add accessibility
        content = self._add_accessibility(content)
        
        return content
    
    def _add_proper_spacing(self, content: str) -> str:
        """Add proper spacing following Apple guidelines"""
        # Replace hardcoded spacing with design system values
        replacements = [
            (r'\.padding\((\d+)\)', lambda m: f'.padding({self._get_design_spacing(int(m.group(1)))})'),
            (r'spacing:\s*(\d+)', lambda m: f'spacing: {self._get_design_spacing(int(m.group(1)))}')
        ]
        
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def _get_design_spacing(self, value: int) -> str:
        """Convert spacing to design system values"""
        if value <= 4:
            return "DesignSystem.spacing.xs"
        elif value <= 8:
            return "DesignSystem.spacing.sm"
        elif value <= 16:
            return "DesignSystem.spacing.md"
        elif value <= 24:
            return "DesignSystem.spacing.lg"
        else:
            return "DesignSystem.spacing.xl"
    
    def _enhance_colors(self, content: str) -> str:
        """Enhance colors to use system colors"""
        # Replace basic colors with system colors
        color_replacements = {
            r'Color\.blue': 'Color.accentColor',
            r'Color\.black': 'Color(.label)',
            r'Color\.white': 'Color(.systemBackground)',
            r'Color\.gray': 'Color(.systemGray)',
            r'\.foregroundColor\(': '.foregroundStyle('
        }
        
        for pattern, replacement in color_replacements.items():
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def _add_smooth_animations(self, content: str) -> str:
        """Add smooth animations to interactions"""
        # Add animations to state changes
        if "withAnimation" not in content and "@State" in content:
            # Find button actions and wrap with animation
            content = re.sub(
                r'(Button\s*\([^{]+\)\s*\{)([^}]+)(\})',
                r'\1 withAnimation(.spring()) { \2 } \3',
                content
            )
        
        return content
    
    def _improve_typography(self, content: str) -> str:
        """Improve typography using system fonts"""
        # Replace generic font sizes with semantic sizes
        font_replacements = {
            r'\.font\(\.system\(size:\s*3[2-9]\)\)': '.font(.largeTitle)',
            r'\.font\(\.system\(size:\s*2[4-9]\)\)': '.font(.title)',
            r'\.font\(\.system\(size:\s*2[0-3]\)\)': '.font(.title2)',
            r'\.font\(\.system\(size:\s*1[7-9]\)\)': '.font(.headline)',
            r'\.font\(\.system\(size:\s*1[4-6]\)\)': '.font(.body)',
            r'\.font\(\.system\(size:\s*1[0-3]\)\)': '.font(.caption)'
        }
        
        for pattern, replacement in font_replacements.items():
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def _add_accessibility(self, content: str) -> str:
        """Add basic accessibility features"""
        # Add accessibility labels to images
        content = re.sub(
            r'Image\(systemName:\s*"([^"]+)"\)',
            r'Image(systemName: "\1")\n                .accessibilityLabel("\1")',
            content
        )
        
        # Add accessibility to buttons without labels
        content = re.sub(
            r'Button\(action:([^{]+)\)\s*\{([^}]+)\}',
            lambda m: self._add_button_accessibility(m.group(0), m.group(2)),
            content
        )
        
        return content
    
    def _add_button_accessibility(self, button_code: str, button_content: str) -> str:
        """Add accessibility to buttons"""
        if "accessibilityLabel" not in button_code:
            # Try to extract meaningful label from content
            if "Text(" in button_content:
                return button_code
            else:
                return button_code.rstrip('}') + '\n    .accessibilityLabel("Button")' + '}'
        return button_code
    
    def _generate_todo_ui(self) -> List[Dict]:
        """Generate beautiful todo UI"""
        # Implementation would generate a modern todo UI
        # Using the patterns from the UI training data
        return self._generate_modern_ui("todo", "Beautiful todo list app")
    
    def _generate_weather_ui(self) -> List[Dict]:
        """Generate beautiful weather UI"""
        # Implementation would generate a modern weather UI
        return self._generate_modern_ui("weather", "Beautiful weather app")
    
    def _generate_social_ui(self) -> List[Dict]:
        """Generate beautiful social UI"""
        # Implementation would generate a modern social UI
        return self._generate_modern_ui("social", "Beautiful social app")