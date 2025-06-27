#!/usr/bin/env python3
"""
UI Training Pipeline - Specialized training for Apple HIG compliant UI generation
Trains models to understand and generate beautiful iOS interfaces
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
from datetime import datetime

from llama_finetuning_pipeline import LlamaFineTuner, CodeLlamaFineTuner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UIModelFineTuner(CodeLlamaFineTuner):
    """Specialized fine-tuner for UI/UX code generation"""
    
    def __init__(self, output_dir: str = "swift_ui_model"):
        super().__init__(output_dir)
        
        # UI-specific training parameters
        self.ui_training_config = {
            "learning_rate": 1e-4,  # Lower for fine details
            "num_epochs": 5,        # More epochs for UI patterns
            "batch_size": 2,        # Smaller batch for quality
            "max_length": 3072      # Longer for complete UI code
        }
        
        # Apple HIG principles to embed
        self.hig_principles = [
            "Clarity: Use legible text, clear icons, and appropriate spacing",
            "Deference: UI should never compete with content",
            "Depth: Use visual layers and motion to convey hierarchy",
            "Direct manipulation: Immediate, visible response to user actions",
            "Consistency: Familiar UI elements behave in expected ways",
            "Feedback: Acknowledge actions and show results",
            "Metaphors: Virtual objects behave like physical ones",
            "User control: People initiate and control actions"
        ]
    
    def prepare_ui_training_data(self, ui_data_path: str, general_data_path: str) -> str:
        """Prepare specialized UI training data"""
        output_file = "ui_training_prompts.jsonl"
        training_examples = []
        
        # Load UI-specific data
        if Path(ui_data_path).exists():
            ui_data = self._load_ui_data(ui_data_path)
            training_examples.extend(ui_data)
        
        # Load general Swift data and filter for UI
        if Path(general_data_path).exists():
            general_data = self._filter_ui_from_general(general_data_path)
            training_examples.extend(general_data)
        
        # Add Apple HIG examples
        hig_examples = self._create_hig_examples()
        training_examples.extend(hig_examples)
        
        # Add UI pattern examples
        pattern_examples = self._create_ui_pattern_examples()
        training_examples.extend(pattern_examples)
        
        # Save combined training data
        with open(output_file, 'w') as f:
            for example in training_examples:
                f.write(json.dumps(example) + '\n')
        
        logger.info(f"Created UI training file with {len(training_examples)} examples")
        return output_file
    
    def _load_ui_data(self, ui_data_path: str) -> List[Dict]:
        """Load UI-specific training data"""
        examples = []
        ui_dir = Path(ui_data_path)
        
        for category_dir in ui_dir.iterdir():
            if category_dir.is_dir():
                for json_file in category_dir.glob("*.json"):
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                        
                        # Create multiple training variations
                        prompts = self._generate_ui_prompts(data)
                        for prompt in prompts:
                            examples.append({
                                "prompt": prompt,
                                "completion": data["content"],
                                "metadata": {
                                    "category": data["category"],
                                    "ui_patterns": data.get("ui_patterns", {}),
                                    "source": data.get("repo", "unknown")
                                }
                            })
        
        return examples
    
    def _generate_ui_prompts(self, data: Dict) -> List[str]:
        """Generate various UI-focused prompts"""
        category = data.get("category", "general")
        patterns = data.get("ui_patterns", {})
        
        prompts = []
        
        # Category-specific prompts
        if category == "navigation_patterns":
            prompts.extend([
                "Create a SwiftUI navigation interface following Apple HIG",
                "Design a navigation pattern with smooth transitions",
                "Build an iOS navigation structure with proper hierarchy"
            ])
        elif category == "animations":
            prompts.extend([
                "Add beautiful animations to this SwiftUI view",
                "Create smooth, natural animations following iOS design",
                "Implement gesture-driven animations for iOS"
            ])
        elif category == "form_components":
            prompts.extend([
                "Design a form interface following Apple's guidelines",
                "Create an accessible input form for iOS",
                "Build a beautiful settings screen with proper controls"
            ])
        
        # Pattern-specific prompts
        if patterns.get("uses_sf_symbols"):
            prompts.append("Create UI using SF Symbols for consistency")
        if patterns.get("has_dark_mode"):
            prompts.append("Design adaptive UI supporting dark and light modes")
        if patterns.get("is_accessible"):
            prompts.append("Build accessible UI with VoiceOver support")
        
        # General UI prompts
        prompts.extend([
            f"Create a beautiful {category.replace('_', ' ')} for iOS",
            f"Design {category.replace('_', ' ')} following Apple HIG"
        ])
        
        return prompts
    
    def _create_hig_examples(self) -> List[Dict]:
        """Create examples demonstrating Apple HIG principles"""
        examples = []
        
        # Clarity principle example
        examples.append({
            "prompt": "Create a clear, readable UI with proper typography and spacing",
            "completion": """struct ClearUIExample: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Main Title")
                .font(.largeTitle)
                .fontWeight(.bold)
                .accessibilityAddTraits(.isHeader)
            
            Text("Subtitle with additional context")
                .font(.title3)
                .foregroundStyle(.secondary)
            
            Text("Body text with comfortable reading experience. Proper line spacing and margins ensure content is easy to scan and understand.")
                .font(.body)
                .lineSpacing(4)
                .fixedSize(horizontal: false, vertical: true)
            
            HStack(spacing: 12) {
                Image(systemName: "info.circle")
                    .font(.callout)
                    .foregroundStyle(.blue)
                
                Text("Information with clear visual hierarchy")
                    .font(.callout)
            }
            .padding()
            .background(Color(.systemGray6))
            .clipShape(RoundedRectangle(cornerRadius: 8))
        }
        .padding()
    }
}"""
        })
        
        # Direct manipulation example
        examples.append({
            "prompt": "Implement direct manipulation with immediate visual feedback",
            "completion": """struct DirectManipulationExample: View {
    @State private var offset = CGSize.zero
    @State private var isDragging = false
    
    var body: some View {
        RoundedRectangle(cornerRadius: 20)
            .fill(isDragging ? Color.accentColor : Color.accentColor.opacity(0.8))
            .frame(width: 120, height: 120)
            .scaleEffect(isDragging ? 1.1 : 1.0)
            .shadow(radius: isDragging ? 10 : 5)
            .offset(offset)
            .animation(.spring(response: 0.3, dampingFraction: 0.6), value: isDragging)
            .gesture(
                DragGesture()
                    .onChanged { value in
                        if !isDragging {
                            withAnimation(.easeOut(duration: 0.2)) {
                                isDragging = true
                            }
                            HapticFeedback.impact(.light)
                        }
                        offset = value.translation
                    }
                    .onEnded { _ in
                        withAnimation(.spring()) {
                            isDragging = false
                            offset = .zero
                        }
                        HapticFeedback.impact(.medium)
                    }
            )
            .accessibilityLabel("Draggable object")
            .accessibilityHint("Double tap and hold to drag")
    }
}"""
        })
        
        # Depth and hierarchy example
        examples.append({
            "prompt": "Design UI with visual depth and clear hierarchy",
            "completion": """struct DepthHierarchyExample: View {
    @Environment(\\.colorScheme) var colorScheme
    
    var body: some View {
        ZStack {
            // Background layer
            Color(.systemBackground)
            
            // Content layers with depth
            VStack(spacing: 20) {
                // Primary card - highest elevation
                CardView(
                    title: "Primary Action",
                    subtitle: "Most important content",
                    elevation: .high,
                    accentColor: .accentColor
                )
                
                // Secondary cards - medium elevation
                HStack(spacing: 16) {
                    CardView(
                        title: "Option A",
                        subtitle: "Secondary",
                        elevation: .medium
                    )
                    
                    CardView(
                        title: "Option B",
                        subtitle: "Secondary",
                        elevation: .medium
                    )
                }
                
                // Tertiary content - low elevation
                VStack(spacing: 12) {
                    ForEach(0..<3) { index in
                        ListRow(
                            title: "Item \\(index + 1)",
                            elevation: .low
                        )
                    }
                }
            }
            .padding()
        }
    }
}

struct CardView: View {
    let title: String
    let subtitle: String
    let elevation: Elevation
    var accentColor: Color = .primary
    
    @Environment(\\.colorScheme) var colorScheme
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.headline)
                .foregroundStyle(accentColor)
            
            Text(subtitle)
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(colorScheme == .dark ? Color(.systemGray6) : .white)
                .shadow(
                    color: elevation.shadowColor,
                    radius: elevation.shadowRadius,
                    y: elevation.shadowY
                )
        )
    }
}

enum Elevation {
    case low, medium, high
    
    var shadowColor: Color {
        switch self {
        case .low: return .black.opacity(0.05)
        case .medium: return .black.opacity(0.1)
        case .high: return .black.opacity(0.15)
        }
    }
    
    var shadowRadius: CGFloat {
        switch self {
        case .low: return 2
        case .medium: return 5
        case .high: return 10
        }
    }
    
    var shadowY: CGFloat {
        switch self {
        case .low: return 1
        case .medium: return 3
        case .high: return 5
        }
    }
}"""
        })
        
        return examples
    
    def _create_ui_pattern_examples(self) -> List[Dict]:
        """Create examples of common UI patterns"""
        examples = []
        
        # Search interface pattern
        examples.append({
            "prompt": "Create a search interface following iOS design patterns",
            "completion": """struct SearchInterfaceExample: View {
    @State private var searchText = ""
    @State private var isSearching = false
    @State private var searchResults: [SearchResult] = []
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // Search results or content
                if searchText.isEmpty {
                    // Default content
                    ScrollView {
                        LazyVStack(spacing: 16) {
                            ForEach(recentSearches) { item in
                                RecentSearchRow(item: item)
                                    .onTapGesture {
                                        searchText = item.query
                                        performSearch()
                                    }
                            }
                        }
                        .padding()
                    }
                } else {
                    // Search results
                    if isSearching {
                        ProgressView("Searching...")
                            .frame(maxWidth: .infinity, maxHeight: .infinity)
                    } else {
                        ScrollView {
                            LazyVStack(spacing: 12) {
                                ForEach(searchResults) { result in
                                    SearchResultRow(result: result)
                                }
                            }
                            .padding()
                        }
                    }
                }
            }
            .navigationTitle("Search")
            .searchable(
                text: $searchText,
                placement: .navigationBarDrawer(displayMode: .always),
                prompt: "Search for items"
            )
            .onSubmit(of: .search) {
                performSearch()
            }
            .onChange(of: searchText) { newValue in
                if newValue.isEmpty {
                    searchResults = []
                }
            }
        }
    }
    
    func performSearch() {
        guard !searchText.isEmpty else { return }
        
        withAnimation {
            isSearching = true
        }
        
        // Simulate search
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            withAnimation {
                isSearching = false
                searchResults = generateMockResults()
            }
        }
    }
}"""
        })
        
        # Settings screen pattern
        examples.append({
            "prompt": "Design a settings screen with proper grouping and controls",
            "completion": """struct SettingsScreenExample: View {
    @AppStorage("notificationsEnabled") private var notificationsEnabled = true
    @AppStorage("soundEnabled") private var soundEnabled = true
    @AppStorage("hapticEnabled") private var hapticEnabled = true
    @AppStorage("appearanceMode") private var appearanceMode = "system"
    
    @State private var showingResetAlert = false
    
    var body: some View {
        NavigationStack {
            Form {
                // User section
                Section {
                    HStack {
                        Image(systemName: "person.crop.circle.fill")
                            .font(.system(size: 50))
                            .foregroundStyle(.gray)
                        
                        VStack(alignment: .leading) {
                            Text("John Doe")
                                .font(.headline)
                            Text("john.doe@example.com")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                        
                        Spacer()
                        
                        Image(systemName: "chevron.right")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                    .padding(.vertical, 8)
                }
                
                // Notifications section
                Section("Notifications") {
                    Toggle("Enable Notifications", isOn: $notificationsEnabled)
                    
                    if notificationsEnabled {
                        Toggle("Sound", isOn: $soundEnabled)
                            .foregroundStyle(notificationsEnabled ? .primary : .secondary)
                        
                        Toggle("Haptic Feedback", isOn: $hapticEnabled)
                            .foregroundStyle(notificationsEnabled ? .primary : .secondary)
                    }
                }
                
                // Appearance section
                Section("Appearance") {
                    Picker("Mode", selection: $appearanceMode) {
                        Text("System").tag("system")
                        Text("Light").tag("light")
                        Text("Dark").tag("dark")
                    }
                    .pickerStyle(.menu)
                }
                
                // About section
                Section("About") {
                    HStack {
                        Text("Version")
                        Spacer()
                        Text("1.0.0")
                            .foregroundStyle(.secondary)
                    }
                    
                    Link(destination: URL(string: "https://example.com/privacy")!) {
                        HStack {
                            Text("Privacy Policy")
                            Spacer()
                            Image(systemName: "arrow.up.right.square")
                                .font(.caption)
                        }
                    }
                    
                    Link(destination: URL(string: "https://example.com/terms")!) {
                        HStack {
                            Text("Terms of Service")
                            Spacer()
                            Image(systemName: "arrow.up.right.square")
                                .font(.caption)
                        }
                    }
                }
                
                // Actions section
                Section {
                    Button("Reset All Settings") {
                        showingResetAlert = true
                    }
                    .foregroundStyle(.red)
                }
            }
            .navigationTitle("Settings")
            .alert("Reset Settings?", isPresented: $showingResetAlert) {
                Button("Cancel", role: .cancel) {}
                Button("Reset", role: .destructive) {
                    resetSettings()
                }
            } message: {
                Text("This will reset all settings to their default values.")
            }
        }
    }
    
    func resetSettings() {
        notificationsEnabled = true
        soundEnabled = true
        hapticEnabled = true
        appearanceMode = "system"
    }
}"""
        })
        
        return examples
    
    def _filter_ui_from_general(self, general_data_path: str) -> List[Dict]:
        """Filter UI-related code from general Swift data"""
        examples = []
        
        with open(general_data_path, 'r') as f:
            for line in f:
                data = json.loads(line)
                content = data.get("completion", "")
                
                # Check if content has UI elements
                if self._is_ui_code(content):
                    # Create UI-focused prompts
                    examples.append({
                        "prompt": "Create beautiful iOS UI with SwiftUI",
                        "completion": content
                    })
        
        return examples
    
    def _is_ui_code(self, content: str) -> bool:
        """Check if code contains UI elements"""
        ui_indicators = [
            "struct.*View", "class.*ViewController",
            "NavigationView", "NavigationStack", "TabView",
            "List", "Form", "VStack", "HStack", "ZStack",
            ".animation", ".transition", ".gesture",
            "@State", "@Binding", "@Environment"
        ]
        
        return any(re.search(pattern, content) for pattern in ui_indicators)


def create_ui_focused_model():
    """Create a UI-focused fine-tuned model"""
    logger.info("Creating UI-focused model training pipeline...")
    
    # Initialize UI fine-tuner
    ui_tuner = UIModelFineTuner()
    
    # Prepare training data
    ui_training_file = ui_tuner.prepare_ui_training_data(
        ui_data_path="ui_training_data",
        general_data_path="swift_training_prompts.jsonl"
    )
    
    # Train the model
    logger.info("Starting UI model training...")
    ui_tuner.train(ui_training_file)
    
    logger.info("UI model training complete!")
    

if __name__ == "__main__":
    create_ui_focused_model()