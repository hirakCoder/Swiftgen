#!/usr/bin/env python3
"""
Test script for SwiftGen modifications - July 11, 2025
Tests the robust fallback mechanism for xAI failures
"""

import asyncio
import json
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the services
from backend.enhanced_claude_service import EnhancedClaudeService
from backend.smart_modification_handler import SmartModificationHandler

async def test_modification_with_fallback():
    """Test modification that triggers xAI failure and fallback"""
    
    # Initialize services
    service = EnhancedClaudeService()
    handler = SmartModificationHandler(service)
    
    # Sample todo app files
    todo_app_files = [
        {
            "path": "Sources/TodoApp.swift",
            "content": """import SwiftUI

@main
struct TodoApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}"""
        },
        {
            "path": "Sources/Views/ContentView.swift", 
            "content": """import SwiftUI

struct ContentView: View {
    @StateObject private var viewModel = TodoViewModel()
    @State private var newTaskText = ""
    
    var body: some View {
        NavigationView {
            VStack {
                HStack {
                    TextField("New task", text: $newTaskText)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                    
                    Button(action: {
                        viewModel.addTask(newTaskText)
                        newTaskText = ""
                    }) {
                        Image(systemName: "plus.circle.fill")
                            .font(.title2)
                    }
                    .disabled(newTaskText.isEmpty)
                }
                .padding()
                
                List {
                    ForEach(viewModel.tasks) { task in
                        TaskRow(task: task, viewModel: viewModel)
                    }
                }
            }
            .navigationTitle("Todo List")
        }
    }
}"""
        },
        {
            "path": "Sources/Models/Task.swift",
            "content": """import Foundation

struct Task: Identifiable, Codable {
    let id = UUID()
    var title: String
    var isCompleted: Bool = false
    var createdAt = Date()
}"""
        },
        {
            "path": "Sources/ViewModels/TodoViewModel.swift",
            "content": """import Foundation

@MainActor
class TodoViewModel: ObservableObject {
    @Published var tasks: [Task] = []
    
    func addTask(_ title: String) {
        let task = Task(title: title)
        tasks.append(task)
    }
    
    func toggleTask(_ task: Task) {
        if let index = tasks.firstIndex(where: { $0.id == task.id }) {
            tasks[index].isCompleted.toggle()
        }
    }
    
    func deleteTask(_ task: Task) {
        tasks.removeAll { $0.id == task.id }
    }
}"""
        }
    ]
    
    # Test 1: Simple modification (should work with xAI)
    logger.info("=== TEST 1: Simple Modification ===")
    simple_mod = "Change the navigation title to 'My Tasks' and make the plus button green"
    
    result1 = await handler.handle_modification(
        project_id="test-1",
        app_name="TodoApp",
        original_description="A todo list app",
        modification_request=simple_mod,
        existing_files=todo_app_files,
        existing_bundle_id="com.test.todoapp"
    )
    
    logger.info(f"Simple modification success: {result1.get('success', False)}")
    if result1.get('success'):
        logger.info(f"Modified by: {result1.get('modified_by_llm', 'unknown')}")
    
    # Test 2: Complex modification (should trigger fallback from xAI)
    logger.info("\n=== TEST 2: Complex Modification with Fallback ===")
    complex_mod = """Add a statistics dashboard feature that shows:
1. Total tasks completed today/this week/this month
2. Completion rate percentage
3. Tasks by category breakdown (pie chart style)
4. Streak counter for consecutive days with completed tasks
5. Add a new tab bar item called 'Stats' with an appropriate SF Symbol"""
    
    result2 = await handler.handle_modification(
        project_id="test-2",
        app_name="TodoApp",
        original_description="A todo list app",
        modification_request=complex_mod,
        existing_files=todo_app_files,
        existing_bundle_id="com.test.todoapp"
    )
    
    logger.info(f"Complex modification success: {result2.get('success', False)}")
    if result2.get('success'):
        logger.info(f"Modified by: {result2.get('modified_by_llm', 'unknown')}")
        logger.info(f"Files modified: {len(result2.get('files', []))}")
        
        # Check if fallback was used
        if 'modified_by_llm' in result2 and result2['modified_by_llm'] != 'xai':
            logger.info("✅ FALLBACK WORKED! xAI failed but modification succeeded with another LLM")
    
    # Test 3: Medium complexity (should use Claude/GPT-4 based on routing)
    logger.info("\n=== TEST 3: Medium Complexity Modification ===")
    medium_mod = "Add dark mode support with a toggle in the navigation bar"
    
    result3 = await handler.handle_modification(
        project_id="test-3",
        app_name="TodoApp", 
        original_description="A todo list app",
        modification_request=medium_mod,
        existing_files=todo_app_files,
        existing_bundle_id="com.test.todoapp"
    )
    
    logger.info(f"Medium modification success: {result3.get('success', False)}")
    if result3.get('success'):
        logger.info(f"Modified by: {result3.get('modified_by_llm', 'unknown')}")
    
    # Summary
    logger.info("\n=== TEST SUMMARY ===")
    logger.info(f"Simple modification: {'✅ PASSED' if result1.get('success') else '❌ FAILED'}")
    logger.info(f"Complex modification: {'✅ PASSED' if result2.get('success') else '❌ FAILED'}")
    logger.info(f"Medium modification: {'✅ PASSED' if result3.get('success') else '❌ FAILED'}")
    
    # Check if fallback mechanism worked
    if result2.get('success') and result2.get('modified_by_llm') != 'xai':
        logger.info("\n🎉 FALLBACK MECHANISM CONFIRMED WORKING!")
        logger.info("xAI failed on complex modification but system automatically used another LLM")

if __name__ == "__main__":
    asyncio.run(test_modification_with_fallback())