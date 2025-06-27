#!/usr/bin/env python3
"""
Hybrid Template System - Combines smart templates with LLM generation
Ensures variety while maintaining code quality
"""

import json
import random
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re

class VarietyEngine:
    """Ensures generated apps are unique even for similar requests"""
    
    def __init__(self, history_file: str = "generation_history.json"):
        self.history_file = Path(history_file)
        self.history = self._load_history()
        
        # Variation strategies
        self.color_schemes = [
            {"primary": "blue", "secondary": "indigo", "accent": "purple"},
            {"primary": "green", "secondary": "mint", "accent": "teal"},
            {"primary": "orange", "secondary": "red", "accent": "pink"},
            {"primary": "purple", "secondary": "pink", "accent": "indigo"},
            {"primary": "cyan", "secondary": "blue", "accent": "indigo"},
            {"primary": "yellow", "secondary": "orange", "accent": "red"}
        ]
        
        self.layout_styles = [
            "vertical_stack",
            "horizontal_stack", 
            "grid",
            "list",
            "tab_view",
            "navigation_split"
        ]
        
        self.animation_styles = [
            "spring",
            "easeInOut",
            "linear",
            "bouncy",
            "smooth"
        ]
        
        self.ui_patterns = [
            "cards",
            "rounded_rectangles",
            "circles",
            "minimal",
            "neumorphic",
            "material"
        ]
    
    def _load_history(self) -> Dict:
        """Load generation history"""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return {"requests": {}}
    
    def _save_history(self):
        """Save generation history"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def get_request_signature(self, app_type: str, description: str, user_id: str = "default") -> str:
        """Create signature for a request"""
        normalized_desc = description.lower().strip()
        signature = f"{user_id}:{app_type}:{normalized_desc}"
        return hashlib.md5(signature.encode()).hexdigest()
    
    def get_variations(self, signature: str) -> Dict:
        """Get variations for this request signature"""
        if signature not in self.history["requests"]:
            self.history["requests"][signature] = {
                "count": 0,
                "variations_used": []
            }
        
        request_data = self.history["requests"][signature]
        count = request_data["count"]
        
        # Select variations that haven't been used
        available_colors = [c for c in self.color_schemes 
                          if str(c) not in request_data["variations_used"]]
        if not available_colors:
            available_colors = self.color_schemes
            request_data["variations_used"] = []
        
        # Select variation
        color_scheme = random.choice(available_colors)
        layout = self.layout_styles[count % len(self.layout_styles)]
        animation = self.animation_styles[count % len(self.animation_styles)]
        ui_pattern = self.ui_patterns[count % len(self.ui_patterns)]
        
        # Update history
        request_data["count"] += 1
        request_data["variations_used"].append(str(color_scheme))
        self._save_history()
        
        return {
            "color_scheme": color_scheme,
            "layout_style": layout,
            "animation_style": animation,
            "ui_pattern": ui_pattern,
            "variation_number": count + 1
        }


class SmartTemplate:
    """Base class for smart templates"""
    
    def __init__(self, template_name: str):
        self.template_name = template_name
        self.placeholders = {}
    
    def set_variation(self, variations: Dict):
        """Apply variations to template"""
        self.variations = variations
    
    def fill(self, **kwargs) -> str:
        """Fill template with provided values"""
        raise NotImplementedError
    
    def get_swift_code(self) -> List[Dict[str, str]]:
        """Get Swift files for this template"""
        raise NotImplementedError


class TodoAppTemplate(SmartTemplate):
    """Smart template for Todo apps with variations"""
    
    def __init__(self):
        super().__init__("TodoApp")
        self.features = {
            "basic": ["add", "delete", "complete"],
            "intermediate": ["add", "delete", "complete", "edit", "categories"],
            "advanced": ["add", "delete", "complete", "edit", "categories", "due_dates", "priorities", "search"]
        }
    
    def get_swift_code(self, app_name: str, complexity: str = "basic") -> List[Dict[str, str]]:
        """Generate Todo app with variations"""
        colors = self.variations["color_scheme"]
        layout = self.variations["layout_style"]
        ui_pattern = self.variations["ui_pattern"]
        
        # App.swift
        app_file = f"""import SwiftUI

@main
struct {app_name}App: App {{
    @StateObject private var todoManager = TodoManager()
    
    var body: some Scene {{
        WindowGroup {{
            ContentView()
                .environmentObject(todoManager)
                .tint(.{colors['primary']})
        }}
    }}
}}"""
        
        # Model based on complexity
        if complexity == "basic":
            model_content = self._basic_todo_model()
        elif complexity == "intermediate":
            model_content = self._intermediate_todo_model()
        else:
            model_content = self._advanced_todo_model()
        
        # ContentView with layout variation
        if layout == "vertical_stack":
            content_view = self._vertical_stack_layout(colors, ui_pattern)
        elif layout == "grid":
            content_view = self._grid_layout(colors, ui_pattern)
        else:
            content_view = self._list_layout(colors, ui_pattern)
        
        # TodoManager
        manager_content = self._todo_manager(complexity)
        
        files = [
            {"path": "Sources/App.swift", "content": app_file},
            {"path": "Sources/Models/TodoItem.swift", "content": model_content},
            {"path": "Sources/Views/ContentView.swift", "content": content_view},
            {"path": "Sources/ViewModels/TodoManager.swift", "content": manager_content}
        ]
        
        # Add additional views based on complexity
        if complexity != "basic":
            files.append({
                "path": "Sources/Views/TodoRowView.swift",
                "content": self._todo_row_view(colors, ui_pattern)
            })
        
        if complexity == "advanced":
            files.append({
                "path": "Sources/Views/TodoDetailView.swift",
                "content": self._todo_detail_view(colors)
            })
        
        return files
    
    def _basic_todo_model(self) -> str:
        return """import Foundation

struct TodoItem: Identifiable, Codable {
    let id = UUID()
    var title: String
    var isCompleted: Bool = false
    var createdAt = Date()
}"""
    
    def _intermediate_todo_model(self) -> str:
        return """import Foundation

struct TodoItem: Identifiable, Codable {
    let id = UUID()
    var title: String
    var description: String = ""
    var isCompleted: Bool = false
    var category: TodoCategory = .personal
    var createdAt = Date()
    var updatedAt = Date()
}

enum TodoCategory: String, CaseIterable, Codable {
    case personal = "Personal"
    case work = "Work"
    case shopping = "Shopping"
    case health = "Health"
    case other = "Other"
    
    var icon: String {
        switch self {
        case .personal: return "person.fill"
        case .work: return "briefcase.fill"
        case .shopping: return "cart.fill"
        case .health: return "heart.fill"
        case .other: return "folder.fill"
        }
    }
}"""
    
    def _advanced_todo_model(self) -> str:
        return """import Foundation

struct TodoItem: Identifiable, Codable {
    let id = UUID()
    var title: String
    var description: String = ""
    var isCompleted: Bool = false
    var category: TodoCategory = .personal
    var priority: TodoPriority = .medium
    var dueDate: Date?
    var tags: [String] = []
    var createdAt = Date()
    var updatedAt = Date()
}

enum TodoCategory: String, CaseIterable, Codable {
    case personal = "Personal"
    case work = "Work"
    case shopping = "Shopping"
    case health = "Health"
    case other = "Other"
    
    var icon: String {
        switch self {
        case .personal: return "person.fill"
        case .work: return "briefcase.fill"
        case .shopping: return "cart.fill"
        case .health: return "heart.fill"
        case .other: return "folder.fill"
        }
    }
}

enum TodoPriority: String, CaseIterable, Codable {
    case low = "Low"
    case medium = "Medium"
    case high = "High"
    case urgent = "Urgent"
    
    var color: String {
        switch self {
        case .low: return "gray"
        case .medium: return "blue"
        case .high: return "orange"
        case .urgent: return "red"
        }
    }
}"""
    
    def _vertical_stack_layout(self, colors: Dict, ui_pattern: str) -> str:
        return f"""import SwiftUI

struct ContentView: View {{
    @EnvironmentObject var todoManager: TodoManager
    @State private var newTodoTitle = ""
    @State private var showingAddSheet = false
    
    var body: some View {{
        NavigationStack {{
            VStack(spacing: 20) {{
                // Header
                {self._header_section(colors, ui_pattern)}
                
                // Todo List
                ScrollView {{
                    VStack(spacing: 12) {{
                        ForEach(todoManager.todos) {{ todo in
                            {self._todo_item_view(ui_pattern, colors)}
                        }}
                    }}
                    .padding(.horizontal)
                }}
                
                // Add Button
                {self._add_button(colors, ui_pattern)}
            }}
            .navigationTitle("My Tasks")
            .sheet(isPresented: $showingAddSheet) {{
                AddTodoSheet()
            }}
        }}
    }}
}}"""
    
    def _grid_layout(self, colors: Dict, ui_pattern: str) -> str:
        return f"""import SwiftUI

struct ContentView: View {{
    @EnvironmentObject var todoManager: TodoManager
    @State private var showingAddSheet = false
    
    let columns = [
        GridItem(.flexible()),
        GridItem(.flexible())
    ]
    
    var body: some View {{
        NavigationStack {{
            ScrollView {{
                LazyVGrid(columns: columns, spacing: 16) {{
                    ForEach(todoManager.todos) {{ todo in
                        {self._grid_todo_item(ui_pattern, colors)}
                    }}
                }}
                .padding()
            }}
            .navigationTitle("Tasks Grid")
            .toolbar {{
                ToolbarItem(placement: .primaryAction) {{
                    Button(action: {{ showingAddSheet = true }}) {{
                        Image(systemName: "plus.circle.fill")
                            .foregroundStyle(.{colors['primary']})
                    }}
                }}
            }}
            .sheet(isPresented: $showingAddSheet) {{
                AddTodoSheet()
            }}
        }}
    }}
}}"""
    
    def _list_layout(self, colors: Dict, ui_pattern: str) -> str:
        return f"""import SwiftUI

struct ContentView: View {{
    @EnvironmentObject var todoManager: TodoManager
    @State private var showingAddSheet = false
    @State private var searchText = ""
    
    var filteredTodos: [TodoItem] {{
        if searchText.isEmpty {{
            return todoManager.todos
        }} else {{
            return todoManager.todos.filter {{ $0.title.localizedCaseInsensitiveContains(searchText) }}
        }}
    }}
    
    var body: some View {{
        NavigationStack {{
            List {{
                ForEach(filteredTodos) {{ todo in
                    {self._list_row_item(ui_pattern, colors)}
                }}
                .onDelete(perform: todoManager.deleteTodos)
            }}
            .searchable(text: $searchText)
            .navigationTitle("Todo List")
            .toolbar {{
                ToolbarItem(placement: .primaryAction) {{
                    Button(action: {{ showingAddSheet = true }}) {{
                        Label("Add Todo", systemImage: "plus.circle.fill")
                            .foregroundStyle(.{colors['primary']})
                    }}
                }}
            }}
            .sheet(isPresented: $showingAddSheet) {{
                AddTodoSheet()
            }}
        }}
    }}
}}"""
    
    def _todo_manager(self, complexity: str) -> str:
        base = """import SwiftUI
import Combine

@MainActor
class TodoManager: ObservableObject {
    @Published var todos: [TodoItem] = []
    
    init() {
        loadTodos()
    }
    
    func addTodo(_ todo: TodoItem) {
        todos.append(todo)
        saveTodos()
    }
    
    func toggleTodo(_ todo: TodoItem) {
        if let index = todos.firstIndex(where: { $0.id == todo.id }) {
            todos[index].isCompleted.toggle()
            saveTodos()
        }
    }
    
    func deleteTodos(at offsets: IndexSet) {
        todos.remove(atOffsets: offsets)
        saveTodos()
    }"""
        
        if complexity != "basic":
            base += """
    
    func updateTodo(_ todo: TodoItem) {
        if let index = todos.firstIndex(where: { $0.id == todo.id }) {
            todos[index] = todo
            todos[index].updatedAt = Date()
            saveTodos()
        }
    }
    
    func todosByCategory(_ category: TodoCategory) -> [TodoItem] {
        todos.filter { $0.category == category }
    }"""
        
        if complexity == "advanced":
            base += """
    
    func todosByPriority(_ priority: TodoPriority) -> [TodoItem] {
        todos.filter { $0.priority == priority }
    }
    
    func overdueTodos() -> [TodoItem] {
        let now = Date()
        return todos.filter { todo in
            if let dueDate = todo.dueDate {
                return dueDate < now && !todo.isCompleted
            }
            return false
        }
    }
    
    func searchTodos(query: String) -> [TodoItem] {
        todos.filter { todo in
            todo.title.localizedCaseInsensitiveContains(query) ||
            todo.description.localizedCaseInsensitiveContains(query) ||
            todo.tags.contains { $0.localizedCaseInsensitiveContains(query) }
        }
    }"""
        
        base += """
    
    private func saveTodos() {
        if let encoded = try? JSONEncoder().encode(todos) {
            UserDefaults.standard.set(encoded, forKey: "todos")
        }
    }
    
    private func loadTodos() {
        if let data = UserDefaults.standard.data(forKey: "todos"),
           let decoded = try? JSONDecoder().decode([TodoItem].self, from: data) {
            todos = decoded
        }
    }
}"""
        
        return base
    
    def _header_section(self, colors: Dict, ui_pattern: str) -> str:
        if ui_pattern == "neumorphic":
            return f"""
                RoundedRectangle(cornerRadius: 20)
                    .fill(Color(UIColor.systemBackground))
                    .frame(height: 100)
                    .shadow(color: .gray.opacity(0.4), radius: 10, x: 5, y: 5)
                    .shadow(color: .white.opacity(0.8), radius: 10, x: -5, y: -5)
                    .overlay(
                        VStack {{
                            Text("Today's Tasks")
                                .font(.title2.bold())
                            Text("\\(todoManager.todos.filter {{ !$0.isCompleted }}.count) remaining")
                                .foregroundStyle(.{colors['secondary']})
                        }}
                    )
                    .padding(.horizontal)"""
        else:
            return f"""
                HStack {{
                    VStack(alignment: .leading) {{
                        Text("Today")
                            .font(.largeTitle.bold())
                        Text("\\(todoManager.todos.filter {{ !$0.isCompleted }}.count) tasks remaining")
                            .foregroundStyle(.{colors['secondary']})
                    }}
                    Spacer()
                    Circle()
                        .fill(.{colors['primary']}.gradient)
                        .frame(width: 60, height: 60)
                        .overlay(
                            Text("\\(Int(todoManager.completionRate * 100))%")
                                .foregroundStyle(.white)
                                .font(.caption.bold())
                        )
                }}
                .padding(.horizontal)"""
    
    def _todo_item_view(self, ui_pattern: str, colors: Dict) -> str:
        if ui_pattern == "cards":
            return f"""
                            HStack {{
                                Circle()
                                    .fill(todo.isCompleted ? Color.{colors['primary']} : Color.clear)
                                    .overlay(
                                        Circle()
                                            .stroke(Color.{colors['primary']}, lineWidth: 2)
                                    )
                                    .frame(width: 24, height: 24)
                                    .onTapGesture {{
                                        withAnimation(.spring()) {{
                                            todoManager.toggleTodo(todo)
                                        }}
                                    }}
                                
                                Text(todo.title)
                                    .strikethrough(todo.isCompleted)
                                    .foregroundStyle(todo.isCompleted ? .gray : .primary)
                                
                                Spacer()
                                
                                Button(action: {{
                                    todoManager.deleteTodo(todo)
                                }}) {{
                                    Image(systemName: "trash")
                                        .foregroundStyle(.red)
                                }}
                            }}
                            .padding()
                            .background(
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(Color(UIColor.secondarySystemBackground))
                            )"""
        else:
            return f"""
                            TodoRowView(todo: todo)
                                .onTapGesture {{
                                    todoManager.toggleTodo(todo)
                                }}"""
    
    def _grid_todo_item(self, ui_pattern: str, colors: Dict) -> str:
        return f"""
                        RoundedRectangle(cornerRadius: 16)
                            .fill(Color(UIColor.secondarySystemBackground))
                            .frame(height: 120)
                            .overlay(
                                VStack(alignment: .leading, spacing: 8) {{
                                    HStack {{
                                        Image(systemName: todo.isCompleted ? "checkmark.circle.fill" : "circle")
                                            .foregroundStyle(.{colors['primary']})
                                        Spacer()
                                        Menu {{
                                            Button("Toggle") {{ todoManager.toggleTodo(todo) }}
                                            Button("Delete", role: .destructive) {{ 
                                                todoManager.deleteTodo(todo) 
                                            }}
                                        }} label: {{
                                            Image(systemName: "ellipsis")
                                        }}
                                    }}
                                    
                                    Text(todo.title)
                                        .font(.headline)
                                        .lineLimit(2)
                                        .strikethrough(todo.isCompleted)
                                    
                                    Spacer()
                                    
                                    Text(todo.createdAt, style: .time)
                                        .font(.caption)
                                        .foregroundStyle(.secondary)
                                }}
                                .padding()
                            )"""
    
    def _list_row_item(self, ui_pattern: str, colors: Dict) -> str:
        return f"""
                    HStack {{
                        Image(systemName: todo.isCompleted ? "checkmark.circle.fill" : "circle")
                            .foregroundStyle(.{colors['primary']})
                            .onTapGesture {{
                                todoManager.toggleTodo(todo)
                            }}
                        
                        VStack(alignment: .leading) {{
                            Text(todo.title)
                                .strikethrough(todo.isCompleted)
                            if !todo.description.isEmpty {{
                                Text(todo.description)
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                            }}
                        }}
                        
                        Spacer()
                        
                        if let category = todo.category {{
                            Image(systemName: category.icon)
                                .foregroundStyle(.{colors['secondary']})
                        }}
                    }}
                    .padding(.vertical, 4)"""
    
    def _add_button(self, colors: Dict, ui_pattern: str) -> str:
        return f"""
                Button(action: {{ showingAddSheet = true }}) {{
                    Label("Add Task", systemImage: "plus")
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.{colors['primary']})
                        .foregroundStyle(.white)
                        .cornerRadius(12)
                }}
                .padding()"""
    
    def _todo_row_view(self, colors: Dict, ui_pattern: str) -> str:
        return f"""import SwiftUI

struct TodoRowView: View {{
    let todo: TodoItem
    @EnvironmentObject var todoManager: TodoManager
    
    var body: some View {{
        HStack {{
            Image(systemName: todo.isCompleted ? "checkmark.circle.fill" : "circle")
                .foregroundStyle(.{colors['primary']})
                .font(.title3)
            
            VStack(alignment: .leading, spacing: 4) {{
                Text(todo.title)
                    .font(.headline)
                    .strikethrough(todo.isCompleted)
                
                if let category = todo.category {{
                    Label(category.rawValue, systemImage: category.icon)
                        .font(.caption)
                        .foregroundStyle(.{colors['secondary']})
                }}
            }}
            
            Spacer()
            
            if let priority = todo.priority {{
                Circle()
                    .fill(Color(priority.color))
                    .frame(width: 8, height: 8)
            }}
        }}
        .padding(.vertical, 8)
        .contentShape(Rectangle())
    }}
}}"""
    
    def _todo_detail_view(self, colors: Dict) -> str:
        return f"""import SwiftUI

struct TodoDetailView: View {{
    @Binding var todo: TodoItem
    @Environment(\\.dismiss) var dismiss
    
    var body: some View {{
        NavigationStack {{
            Form {{
                Section("Task Details") {{
                    TextField("Title", text: $todo.title)
                    TextField("Description", text: $todo.description, axis: .vertical)
                        .lineLimit(3...6)
                }}
                
                Section("Organization") {{
                    Picker("Category", selection: $todo.category) {{
                        ForEach(TodoCategory.allCases, id: \\.self) {{ category in
                            Label(category.rawValue, systemImage: category.icon)
                                .tag(category)
                        }}
                    }}
                    
                    Picker("Priority", selection: $todo.priority) {{
                        ForEach(TodoPriority.allCases, id: \\.self) {{ priority in
                            Text(priority.rawValue)
                                .tag(priority)
                        }}
                    }}
                }}
                
                Section("Schedule") {{
                    DatePicker("Due Date", selection: Binding(
                        get: {{ todo.dueDate ?? Date() }},
                        set: {{ todo.dueDate = $0 }}
                    ), displayedComponents: [.date, .hourAndMinute])
                    
                    Toggle("Has Due Date", isOn: Binding(
                        get: {{ todo.dueDate != nil }},
                        set: {{ newValue in
                            if newValue {{
                                todo.dueDate = Date()
                            }} else {{
                                todo.dueDate = nil
                            }}
                        }}
                    ))
                }}
            }}
            .navigationTitle("Edit Task")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {{
                ToolbarItem(placement: .cancellationAction) {{
                    Button("Cancel") {{ dismiss() }}
                }}
                ToolbarItem(placement: .confirmationAction) {{
                    Button("Save") {{
                        todo.updatedAt = Date()
                        dismiss()
                    }}
                    .foregroundStyle(.{colors['primary']})
                }}
            }}
        }}
    }}
}}"""


class HybridCodeGenerator:
    """Combines templates with LLM generation for variety"""
    
    def __init__(self, llm_model=None):
        self.variety_engine = VarietyEngine()
        self.llm_model = llm_model
        
        # Available templates
        self.templates = {
            "todo": TodoAppTemplate(),
            # Add more templates: calculator, weather, notes, etc.
        }
    
    def generate_app(self, app_type: str, app_name: str, description: str, 
                    user_id: str = "default") -> List[Dict[str, str]]:
        """Generate app with variety"""
        # Get request signature
        signature = self.variety_engine.get_request_signature(app_type, description, user_id)
        
        # Get variations
        variations = self.variety_engine.get_variations(signature)
        
        # Check if we have a template
        if app_type.lower() in self.templates:
            template = self.templates[app_type.lower()]
            template.set_variation(variations)
            
            # Determine complexity based on description
            complexity = self._determine_complexity(description)
            
            # Generate base code from template
            files = template.get_swift_code(app_name, complexity)
            
            # If LLM available, enhance with custom features
            if self.llm_model and self._needs_llm_enhancement(description):
                files = self._enhance_with_llm(files, description, variations)
            
            return files
        else:
            # Use pure LLM generation with variation hints
            if self.llm_model:
                return self._generate_with_llm(app_type, app_name, description, variations)
            else:
                raise ValueError(f"No template available for {app_type} and no LLM configured")
    
    def _determine_complexity(self, description: str) -> str:
        """Determine app complexity from description"""
        description_lower = description.lower()
        
        advanced_keywords = ["priority", "categories", "tags", "search", "filter", "sort",
                           "due date", "reminder", "notification", "sync", "cloud"]
        intermediate_keywords = ["edit", "update", "category", "group", "organize"]
        
        if any(keyword in description_lower for keyword in advanced_keywords):
            return "advanced"
        elif any(keyword in description_lower for keyword in intermediate_keywords):
            return "intermediate"
        else:
            return "basic"
    
    def _needs_llm_enhancement(self, description: str) -> bool:
        """Check if description requires LLM enhancement"""
        # Keywords that indicate custom features
        custom_keywords = ["api", "integrate", "custom", "special", "unique",
                         "firebase", "database", "login", "authentication"]
        
        return any(keyword in description.lower() for keyword in custom_keywords)
    
    def _enhance_with_llm(self, files: List[Dict], description: str, 
                         variations: Dict) -> List[Dict]:
        """Enhance template code with LLM-generated features"""
        # Extract custom requirements
        custom_features = self._extract_custom_features(description)
        
        if self.llm_model:
            # Generate enhancement code
            prompt = f"""
            Enhance this Swift app with these custom features: {custom_features}
            Use this color scheme: {variations['color_scheme']}
            Current files: {len(files)}
            
            Return only the new or modified code needed for the features.
            """
            
            # Get LLM enhancement
            enhancement = self.llm_model.generate_swift_code(prompt)
            
            # Merge enhancement with template code
            return self._merge_code(files, enhancement)
        
        return files
    
    def _extract_custom_features(self, description: str) -> List[str]:
        """Extract custom feature requirements from description"""
        features = []
        
        # API integration
        if "api" in description.lower() or "weather" in description.lower():
            features.append("API integration")
        
        # Authentication
        if any(word in description.lower() for word in ["login", "sign in", "auth"]):
            features.append("User authentication")
        
        # Database
        if any(word in description.lower() for word in ["database", "firebase", "cloud"]):
            features.append("Cloud storage")
        
        return features
    
    def _generate_with_llm(self, app_type: str, app_name: str, 
                          description: str, variations: Dict) -> List[Dict]:
        """Generate complete app using LLM with variation hints"""
        if not self.llm_model:
            raise ValueError("No LLM model configured")
        
        prompt = f"""
        Create a {app_type} iOS app called {app_name}.
        Description: {description}
        
        Use these design variations:
        - Colors: {variations['color_scheme']}
        - Layout: {variations['layout_style']}
        - UI Pattern: {variations['ui_pattern']}
        - Animation: {variations['animation_style']}
        
        Generate complete Swift code for iOS 16.0.
        """
        
        code = self.llm_model.generate_swift_code(prompt)
        
        # Parse code into files
        return self._parse_llm_code(code)
    
    def _merge_code(self, template_files: List[Dict], enhancement: str) -> List[Dict]:
        """Merge LLM enhancement with template files"""
        # Simple merge strategy - this would be more sophisticated in production
        # For now, just append enhancement as a new file
        if enhancement:
            template_files.append({
                "path": "Sources/Extensions/CustomFeatures.swift",
                "content": enhancement
            })
        
        return template_files
    
    def _parse_llm_code(self, code: str) -> List[Dict]:
        """Parse LLM-generated code into file structure"""
        # Simple parser - would be more robust in production
        files = []
        
        # Look for file markers
        file_pattern = r"// File: (.+\.swift)\n(.*?)(?=// File:|$)"
        matches = re.findall(file_pattern, code, re.DOTALL)
        
        if matches:
            for filename, content in matches:
                files.append({
                    "path": f"Sources/{filename}",
                    "content": content.strip()
                })
        else:
            # Single file output
            files.append({
                "path": "Sources/App.swift",
                "content": code
            })
        
        return files


# Example usage
if __name__ == "__main__":
    # Initialize generator
    generator = HybridCodeGenerator()
    
    # Generate todo app with variations
    files1 = generator.generate_app(
        app_type="todo",
        app_name="TaskMaster",
        description="A simple todo list app",
        user_id="user123"
    )
    
    print(f"Generated {len(files1)} files for first request")
    
    # Same user, same request - should get different variation
    files2 = generator.generate_app(
        app_type="todo",
        app_name="TaskMaster",
        description="A simple todo list app",
        user_id="user123"
    )
    
    print(f"Generated {len(files2)} files for second request")
    print("Variations are different:", files1[0]["content"] != files2[0]["content"])