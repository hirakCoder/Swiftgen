"""
RAG Knowledge Base for SwiftGen AI
Provides intelligent context and solutions for Swift/SwiftUI development
"""

import os
import json
import numpy as np
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import hashlib
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import asyncio
import aiohttp
import base64


class RAGKnowledgeBase:
    """Retrieval-Augmented Generation system for Swift/SwiftUI knowledge"""
    
    def __init__(self, knowledge_dir: str = "swift_knowledge"):
        self.knowledge_dir = knowledge_dir
        self.patterns_dir = os.path.join(knowledge_dir, "patterns")
        self.frameworks_dir = os.path.join(knowledge_dir, "frameworks")
        self.solutions_dir = os.path.join(knowledge_dir, "solutions")
        
        # Initialize embedding model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize vector stores
        self.dimension = 384  # Dimension for all-MiniLM-L6-v2
        self.index = None
        self.metadata = []
        self.documents = []
        
        # Load or create index
        self.index_path = os.path.join(knowledge_dir, "faiss_index.pkl")
        self.metadata_path = os.path.join(knowledge_dir, "metadata.pkl")
        
        self._initialize_index()
        self._load_knowledge_base()
        
        # GitHub token for accessing repositories (if available)
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        
        # Auto-update knowledge base with latest sources
        self._auto_update_knowledge()
        
    def _auto_update_knowledge(self):
        """Automatically update knowledge base with latest information"""
        try:
            # Try to get the current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Schedule the update task
                loop.create_task(self._update_github_knowledge())
            else:
                # If no running loop, skip auto-update
                print("[RAG] Skipping auto-update - no running event loop")
        except Exception as e:
            print(f"[RAG] Auto-update skipped: {e}")
        
    def _initialize_index(self):
        """Initialize FAISS index"""
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            # Load existing index
            with open(self.index_path, 'rb') as f:
                self.index = pickle.load(f)
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
            print(f"[RAG] Loaded existing index with {len(self.metadata)} documents")
        else:
            # Create new index
            self.index = faiss.IndexFlatL2(self.dimension)
            print("[RAG] Created new FAISS index")
            
    def _save_index(self):
        """Save FAISS index and metadata"""
        os.makedirs(self.knowledge_dir, exist_ok=True)
        with open(self.index_path, 'wb') as f:
            pickle.dump(self.index, f)
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
            
    def _load_knowledge_base(self):
        """Load all knowledge files and build/update index"""
        # Create default knowledge if directories are empty
        self._ensure_default_knowledge()
        
        # Load patterns
        self._load_knowledge_from_dir(self.patterns_dir, "pattern")
        
        # Load frameworks
        self._load_knowledge_from_dir(self.frameworks_dir, "framework")
        
        # Load solutions
        self._load_knowledge_from_dir(self.solutions_dir, "solution")
        
        print(f"[RAG] Total documents in knowledge base: {len(self.metadata)}")
        
    def _ensure_default_knowledge(self):
        """Create default knowledge files if they don't exist"""
        # Naming conflicts pattern
        naming_conflicts_path = os.path.join(self.patterns_dir, "naming_conflicts.json")
        if not os.path.exists(naming_conflicts_path):
            os.makedirs(self.patterns_dir, exist_ok=True)
            naming_conflicts = {
                "title": "Avoiding Swift Reserved Type Conflicts",
                "content": """
                    CRITICAL: Never use these as struct/class names:
                    - Task → Use TodoItem, UserTask, WorkItem, ActivityItem
                    - State → Use AppState, ViewState, FeatureState, UIState
                    - Action → Use AppAction, ViewAction, FeatureAction, UserAction
                    - Result → Use OperationResult, ProcessResult
                    - Error → Use AppError, ValidationError
                    
                    Example fixes:
                    // WRONG
                    struct Task {
                        let id: UUID
                        let title: String
                    }
                    
                    // CORRECT
                    struct TodoItem {
                        let id: UUID
                        let title: String
                    }
                    
                    // For state management
                    struct AppState {
                        var todos: [TodoItem] = []
                        var isLoading = false
                    }
                    
                    // For actions
                    enum AppAction {
                        case addTodo(TodoItem)
                        case deleteTodo(UUID)
                        case toggleComplete(UUID)
                    }
                """,
                "tags": ["naming", "reserved-types", "conflicts", "Task", "State", "Action"],
                "severity": "critical",
                "solutions": [
                    "Always use semantic names that describe the purpose",
                    "Add prefixes or suffixes to avoid conflicts",
                    "Use type aliases if needed for clarity"
                ]
            }
            with open(naming_conflicts_path, 'w') as f:
                json.dump(naming_conflicts, f, indent=2)
                
        # Modern SwiftUI patterns
        modern_swiftui_path = os.path.join(self.patterns_dir, "modern_swiftui.json")
        if not os.path.exists(modern_swiftui_path):
            modern_swiftui = {
                "title": "Modern SwiftUI Patterns for iOS 16+",
                "content": """
                    Essential iOS 16+ patterns:
                    
                    1. Navigation:
                    // WRONG (deprecated)
                    NavigationView {
                        content
                    }
                    
                    // CORRECT
                    NavigationStack {
                        content
                    }
                    
                    2. Dismissal:
                    // WRONG (deprecated)
                    @Environment(\.presentationMode) var presentationMode
                    presentationMode.wrappedValue.dismiss()
                    
                    // CORRECT
                    @Environment(\.dismiss) private var dismiss
                    dismiss()
                    
                    3. Async/Await:
                    .task {
                        await loadData()
                    }
                    
                    4. New modifiers:
                    .scrollDismissesKeyboard(.interactively)
                    .textFieldStyle(.roundedBorder)
                    .presentationDetents([.medium, .large])
                """,
                "tags": ["swiftui", "ios16", "modern", "navigation", "dismiss"],
                "severity": "important",
                "solutions": [
                    "Always target iOS 16.0 minimum",
                    "Use NavigationStack for all navigation",
                    "Prefer @Environment(\\.dismiss) over presentationMode"
                ]
            }
            with open(modern_swiftui_path, 'w') as f:
                json.dump(modern_swiftui, f, indent=2)
                
        # Error handling patterns
        error_handling_path = os.path.join(self.patterns_dir, "error_handling.json")
        if not os.path.exists(error_handling_path):
            error_handling = {
                "title": "Swift Error Handling Best Practices",
                "content": """
                    Proper error handling patterns:
                    
                    1. Define custom errors:
                    enum AppError: LocalizedError {
                        case networkError(String)
                        case validationError(String)
                        case unknownError
                        
                        var errorDescription: String? {
                            switch self {
                            case .networkError(let message):
                                return "Network Error: \\(message)"
                            case .validationError(let message):
                                return "Validation Error: \\(message)"
                            case .unknownError:
                                return "An unknown error occurred"
                            }
                        }
                    }
                    
                    2. Use Result type:
                    func fetchData() async -> Result<[TodoItem], AppError> {
                        do {
                            let items = try await api.fetchTodos()
                            return .success(items)
                        } catch {
                            return .failure(.networkError(error.localizedDescription))
                        }
                    }
                    
                    3. Handle in UI:
                    @State private var errorMessage: String?
                    @State private var showError = false
                    
                    .alert("Error", isPresented: $showError) {
                        Button("OK") { }
                    } message: {
                        Text(errorMessage ?? "Unknown error")
                    }
                """,
                "tags": ["error-handling", "Result", "LocalizedError", "best-practices"],
                "severity": "important",
                "solutions": [
                    "Always use Result type for operations that can fail",
                    "Provide user-friendly error messages",
                    "Never force unwrap optionals"
                ]
            }
            with open(error_handling_path, 'w') as f:
                json.dump(error_handling, f, indent=2)
                
        # SwiftUI components
        swiftui_components_path = os.path.join(self.frameworks_dir, "swiftui_components.json")
        if not os.path.exists(swiftui_components_path):
            os.makedirs(self.frameworks_dir, exist_ok=True)
            swiftui_components = {
                "title": "Essential SwiftUI Components",
                "content": """
                    Common SwiftUI components and their proper usage:
                    
                    1. Lists:
                    List {
                        ForEach(items) { item in
                            ItemRow(item: item)
                        }
                        .onDelete(perform: deleteItems)
                        .onMove(perform: moveItems)
                    }
                    .listStyle(.insetGrouped)
                    
                    2. Forms:
                    Form {
                        Section("User Info") {
                            TextField("Name", text: $name)
                            DatePicker("Birthday", selection: $birthday, displayedComponents: .date)
                        }
                        
                        Section {
                            Toggle("Enable Notifications", isOn: $notificationsEnabled)
                        }
                    }
                    
                    3. Buttons with proper styling:
                    Button(action: performAction) {
                        Label("Save", systemImage: "checkmark.circle.fill")
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                    
                    4. Async Image loading:
                    AsyncImage(url: URL(string: imageURL)) { image in
                        image
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                    } placeholder: {
                        ProgressView()
                    }
                """,
                "tags": ["swiftui", "components", "List", "Form", "Button", "AsyncImage"],
                "severity": "normal",
                "solutions": [
                    "Use semantic colors and SF Symbols",
                    "Apply proper styling with modifiers",
                    "Handle loading and error states"
                ]
            }
            with open(swiftui_components_path, 'w') as f:
                json.dump(swiftui_components, f, indent=2)
                
        # Common build errors solutions
        common_errors_path = os.path.join(self.solutions_dir, "common_errors.json")
        if not os.path.exists(common_errors_path):
            os.makedirs(self.solutions_dir, exist_ok=True)
            common_errors = {
                "title": "Common Swift Build Errors and Solutions",
                "content": """
                    Solutions for frequent build errors:
                    
                    1. "Cannot find type 'Task' in scope"
                    - Solution: Task is a reserved Swift type. Use TodoItem, UserTask, or WorkItem instead
                    
                    2. "Single-quoted string literal found"
                    - Solution: Replace all single quotes ' with double quotes "
                    - Example: Text('Hello') → Text("Hello")
                    
                    3. "Value of type 'Environment<Binding<PresentationMode>>' has no member 'dismiss'"
                    - Solution: Use @Environment(\\.dismiss) instead of presentationMode
                    
                    4. "NavigationView is deprecated"
                    - Solution: Use NavigationStack for iOS 16+
                    
                    5. "Missing argument for parameter in call"
                    - Check all function calls have required parameters
                    - Ensure proper initialization of structs/classes
                    
                    6. "Cannot convert value of type"
                    - Check type compatibility
                    - Use proper type casting or conversion
                """,
                "tags": ["errors", "build-errors", "solutions", "debugging"],
                "severity": "critical",
                "solutions": [
                    "Always check for reserved type conflicts",
                    "Use consistent quote style (double quotes)",
                    "Update to modern SwiftUI APIs"
                ]
            }
            with open(common_errors_path, 'w') as f:
                json.dump(common_errors, f, indent=2)
                
    def _load_knowledge_from_dir(self, directory: str, category: str):
        """Load knowledge files from a directory"""
        if not os.path.exists(directory):
            return
            
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                file_path = os.path.join(directory, filename)
                try:
                    with open(file_path, 'r') as f:
                        knowledge = json.load(f)
                        self._add_document(knowledge, category, filename)
                except Exception as e:
                    print(f"[RAG] Error loading {file_path}: {e}")
                    
    def _add_document(self, knowledge: Dict, category: str, filename: str):
        """Add a document to the knowledge base"""
        # Create document ID
        doc_id = hashlib.md5(f"{category}_{filename}".encode()).hexdigest()
        
        # Check if document already exists
        existing_ids = [m['id'] for m in self.metadata]
        if doc_id in existing_ids:
            return
            
        # Prepare text for embedding
        text = f"{knowledge.get('title', '')}\n{knowledge.get('content', '')}"
        tags = ' '.join(knowledge.get('tags', []))
        full_text = f"{text}\n{tags}"
        
        # Generate embedding
        embedding = self.model.encode([full_text])[0]
        
        # Add to index
        self.index.add(np.array([embedding]))
        
        # Store metadata
        metadata = {
            'id': doc_id,
            'category': category,
            'filename': filename,
            'title': knowledge.get('title', ''),
            'content': knowledge.get('content', ''),
            'tags': knowledge.get('tags', []),
            'severity': knowledge.get('severity', 'normal'),
            'solutions': knowledge.get('solutions', [])
        }
        self.metadata.append(metadata)
        
        # Save index
        self._save_index()
        
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for relevant knowledge based on query"""
        if not self.metadata:
            return []
            
        # Generate query embedding
        query_embedding = self.model.encode([query])[0]
        
        # Search in FAISS
        distances, indices = self.index.search(np.array([query_embedding]), k)
        
        # Retrieve results
        results = []
        for idx in indices[0]:
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result['relevance_score'] = float(1 / (1 + distances[0][len(results)]))
                results.append(result)
                
        return results
        
    def get_context_for_error(self, error_message: str) -> str:
        """Get relevant context for a specific error"""
        results = self.search(error_message, k=3)
        
        if not results:
            return ""
            
        context = "Based on the knowledge base, here are relevant solutions:\n\n"
        
        for i, result in enumerate(results, 1):
            context += f"{i}. {result['title']}\n"
            if result['solutions']:
                context += "   Solutions:\n"
                for solution in result['solutions']:
                    context += f"   - {solution}\n"
            context += "\n"
            
        return context
        
    def get_pattern_guidance(self, pattern_type: str) -> str:
        """Get guidance for specific patterns"""
        results = self.search(pattern_type, k=3)
        
        if not results:
            return ""
            
        guidance = ""
        for result in results:
            if result['category'] == 'pattern':
                guidance += f"### {result['title']}\n{result['content']}\n\n"
                
        return guidance
        
    def add_learned_solution(self, error: str, solution: str, success: bool):
        """Add a learned solution to the knowledge base"""
        if not success:
            return
            
        # Create solution document
        solution_doc = {
            "title": f"Learned Solution: {error[:50]}...",
            "content": f"Error: {error}\n\nSolution: {solution}",
            "tags": ["learned", "auto-generated", "solution"],
            "severity": "normal",
            "solutions": [solution]
        }
        
        # Save to solutions directory
        filename = f"learned_{hashlib.md5(error.encode()).hexdigest()[:8]}.json"
        file_path = os.path.join(self.solutions_dir, filename)
        
        with open(file_path, 'w') as f:
            json.dump(solution_doc, f, indent=2)
            
        # Add to index
        self._add_document(solution_doc, "solution", filename)
        
        print(f"[RAG] Added learned solution for: {error[:50]}...")
        
    def get_naming_alternatives(self, reserved_type: str) -> List[str]:
        """Get naming alternatives for reserved types"""
        alternatives = {
            "Task": ["TodoItem", "UserTask", "WorkItem", "ActivityItem", "Assignment"],
            "State": ["AppState", "ViewState", "FeatureState", "UIState", "ScreenState"],
            "Action": ["AppAction", "ViewAction", "FeatureAction", "UserAction", "Command"],
            "Result": ["OperationResult", "ProcessResult", "Outcome", "Response"],
            "Error": ["AppError", "ValidationError", "FailureReason", "Issue"]
        }
        
        return alternatives.get(reserved_type, [f"Custom{reserved_type}"])
        
    async def _update_github_knowledge(self):
        """Update knowledge base with latest GitHub repositories and Apple guidelines"""
        print("[RAG] Updating knowledge base with latest GitHub repositories...")
        
        # High-quality SwiftUI repositories to learn from
        repos_to_analyze = [
            "apple/swift",
            "apple/swift-collections", 
            "apple/swift-algorithms",
            "pointfreeco/swift-composable-architecture",
            "pointfreeco/swiftui-navigation",
            "SwiftUIX/SwiftUIX",
            "siteline/SwiftUI-Introspect",
            "apple/swift-async-algorithms",
            "apple/swift-package-manager"
        ]
        
        # Apple documentation sources
        apple_docs = [
            "https://developer.apple.com/documentation/swiftui",
            "https://developer.apple.com/documentation/swift",
            "https://developer.apple.com/app-store/review/guidelines/",
            "https://developer.apple.com/design/human-interface-guidelines/"
        ]
        
        for repo in repos_to_analyze:
            try:
                await self._analyze_github_repo(repo)
            except Exception as e:
                print(f"[RAG] Failed to analyze {repo}: {e}")
                
        # Update with Apple documentation
        await self._update_apple_guidelines()
        
    async def _analyze_github_repo(self, repo_path: str):
        """Analyze a GitHub repository for SwiftUI patterns"""
        headers = {}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
            
        base_url = f"https://api.github.com/repos/{repo_path}"
        
        async with aiohttp.ClientSession() as session:
            # Get repository information
            async with session.get(f"{base_url}", headers=headers) as response:
                if response.status != 200:
                    return
                    
                repo_info = await response.json()
                
            # Get Swift files from the repository
            async with session.get(f"{base_url}/contents", headers=headers) as response:
                if response.status == 200:
                    contents = await response.json()
                    
                    # Find Swift files and analyze patterns
                    for item in contents:
                        if item["type"] == "file" and item["name"].endswith(".swift"):
                            await self._analyze_swift_file_from_github(session, item["download_url"], repo_path)
                            
    async def _analyze_swift_file_from_github(self, session: aiohttp.ClientSession, 
                                             file_url: str, repo_path: str):
        """Analyze a Swift file from GitHub for patterns"""
        try:
            async with session.get(file_url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Extract patterns and best practices
                    patterns = self._extract_swift_patterns(content)
                    
                    if patterns:
                        # Add to knowledge base
                        knowledge_doc = {
                            "title": f"Swift Patterns from {repo_path}",
                            "content": patterns,
                            "tags": ["github", "patterns", "swift", repo_path.split("/")[1]],
                            "severity": "normal",
                            "solutions": [f"Patterns learned from {repo_path}"],
                            "source": "github",
                            "repo": repo_path
                        }
                        
                        # Save to patterns directory
                        filename = f"github_{repo_path.replace('/', '_')}.json"
                        file_path = os.path.join(self.patterns_dir, filename)
                        
                        with open(file_path, 'w') as f:
                            json.dump(knowledge_doc, f, indent=2)
                            
                        # Add to index
                        self._add_document(knowledge_doc, "pattern", filename)
                        
        except Exception as e:
            print(f"[RAG] Error analyzing Swift file: {e}")
            
    def _extract_swift_patterns(self, content: str) -> str:
        """Extract useful Swift/SwiftUI patterns from code"""
        patterns = []
        
        # Common patterns to look for
        if "@Published" in content:
            patterns.append("Uses @Published for observable properties")
            
        if "@StateObject" in content:
            patterns.append("Uses @StateObject for view-owned objects")
            
        if "@ObservedObject" in content:
            patterns.append("Uses @ObservedObject for injected objects")
            
        if "NavigationStack" in content:
            patterns.append("Uses modern NavigationStack")
            
        if "@Environment(\\.dismiss)" in content:
            patterns.append("Uses modern dismiss environment")
            
        if "async/await" in content:
            patterns.append("Uses modern async/await patterns")
            
        # Extract struct/class patterns (avoiding reserved types)
        import re
        struct_matches = re.findall(r'struct\s+(\w+)', content)
        for struct_name in struct_matches:
            if struct_name not in ["Task", "State", "Action", "Result", "Error"]:
                patterns.append(f"Defines struct {struct_name}")
                
        if patterns:
            return "\\n".join(patterns)
        return ""
        
    async def _update_apple_guidelines(self):
        """Update with Apple's latest guidelines and best practices"""
        
        # Apple HIG patterns
        hig_patterns = {
            "title": "Apple Human Interface Guidelines for iOS",
            "content": """
                Essential Apple HIG compliance patterns:
                
                1. Accessibility:
                - Minimum touch target: 44x44 points
                - Support VoiceOver with proper labels
                - Dynamic Type support for text scaling
                - High contrast color support
                
                2. Navigation:
                - Use NavigationStack for iOS 16+
                - Clear navigation hierarchy
                - Consistent back button behavior
                
                3. Layout:
                - Safe area respect
                - Adaptive layouts for all screen sizes
                - Proper spacing and margins
                
                4. Performance:
                - Lazy loading for large data sets
                - Efficient list rendering
                - Proper memory management
                
                5. App Store Requirements:
                - Privacy manifest if needed
                - Proper app metadata
                - Screenshot requirements
                - Age-appropriate content ratings
            """,
            "tags": ["apple", "hig", "guidelines", "app-store", "accessibility"],
            "severity": "important",
            "solutions": [
                "Follow Apple HIG for all UI decisions",
                "Test with VoiceOver enabled",
                "Support Dynamic Type",
                "Use system colors and fonts"
            ]
        }
        
        app_store_guidelines = {
            "title": "App Store Review Guidelines Compliance",
            "content": """
                Critical App Store compliance requirements:
                
                1. Content Policy:
                - No inappropriate content
                - Accurate app description
                - Proper content ratings
                
                2. Technical Requirements:
                - No crashes or bugs
                - Complete app functionality
                - Proper error handling
                - iOS version compatibility
                
                3. Privacy:
                - Privacy policy if collecting data
                - Proper permission requests
                - Data handling transparency
                
                4. Performance:
                - Fast launch times
                - Responsive UI
                - Efficient resource usage
                
                5. Design:
                - Native iOS look and feel
                - Proper navigation patterns
                - Apple HIG compliance
            """,
            "tags": ["app-store", "compliance", "review", "guidelines"],
            "severity": "critical",
            "solutions": [
                "Test thoroughly before submission",
                "Follow all technical guidelines",
                "Include proper privacy information",
                "Use native iOS patterns only"
            ]
        }
        
        ios_patterns = {
            "title": "iOS 16+ Modern SwiftUI Patterns",
            "content": """
                Essential iOS 16+ patterns for SwiftUI:
                
                1. Navigation:
                NavigationStack {
                    // Content
                }
                .navigationDestination(for: ItemType.self) { item in
                    DetailView(item: item)
                }
                
                2. Dismissal:
                @Environment(\\.dismiss) private var dismiss
                Button("Close") { dismiss() }
                
                3. Sheets and Presentations:
                .sheet(isPresented: $showSheet) {
                    SheetView()
                        .presentationDetents([.medium, .large])
                }
                
                4. Async Operations:
                .task {
                    await loadData()
                }
                
                5. Modern Form Patterns:
                Form {
                    Section("User Info") {
                        TextField("Name", text: $name)
                    }
                }
                .formStyle(.grouped)
                
                6. Search:
                .searchable(text: $searchText)
                
                7. Pull to Refresh:
                .refreshable {
                    await refreshData()
                }
            """,
            "tags": ["ios16", "swiftui", "modern", "patterns"],
            "severity": "important",
            "solutions": [
                "Always target iOS 16+ for new apps",
                "Use modern SwiftUI APIs",
                "Prefer new navigation patterns",
                "Implement proper async handling"
            ]
        }
        
        # Save all guidelines
        guidelines = [hig_patterns, app_store_guidelines, ios_patterns]
        
        for guideline in guidelines:
            filename = f"apple_{guideline['title'].lower().replace(' ', '_')}.json"
            file_path = os.path.join(self.frameworks_dir, filename)
            
            with open(file_path, 'w') as f:
                json.dump(guideline, f, indent=2)
                
            self._add_document(guideline, "framework", filename)
            
        print("[RAG] Updated Apple guidelines and iOS patterns")
        
    def get_app_store_compliance_check(self, files: List[Dict]) -> Dict[str, List[str]]:
        """Check files for App Store compliance issues"""
        issues = {
            "critical": [],
            "warnings": [],
            "recommendations": []
        }
        
        for file in files:
            content = file.get("content", "")
            path = file.get("path", "")
            
            # Check for reserved type usage
            if any(f"struct {reserved}" in content for reserved in ["Task", "State", "Action"]):
                issues["critical"].append(f"{path}: Uses Swift reserved types")
                
            # Check for deprecated patterns
            if "@Environment(\\.presentationMode)" in content:
                issues["warnings"].append(f"{path}: Uses deprecated presentationMode")
                
            # Check for accessibility
            if "Button(" in content and "accessibilityLabel" not in content:
                issues["recommendations"].append(f"{path}: Consider adding accessibility labels")
                
            # Check for proper error handling
            if "try!" in content:
                issues["warnings"].append(f"{path}: Uses force try - should handle errors properly")
                
        return issues