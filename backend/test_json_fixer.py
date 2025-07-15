#!/usr/bin/env python3
"""
Test the enhanced JSON fixer for xAI unterminated string errors
"""

import json
import sys
sys.path.append('backend')

from json_fixer import extract_and_fix_json

# Test cases based on actual xAI failures
test_cases = [
    {
        "name": "Unterminated string in file content",
        "input": '''{"files": [{"path": "ContentView.swift", "content": "import SwiftUI\\n\\nstruct ContentView: View {\\n    var body: some View {\\n        Text(\\"Hello, World!\\")\\n    }\\n}''',
        "should_fix": True
    },
    {
        "name": "Multiple unterminated strings",
        "input": '''{"files": [{"path": "File1.swift", "content": "import SwiftUI}, {"path": "File2.swift", "content": "struct View {''',
        "should_fix": True
    },
    {
        "name": "Valid JSON (should not change)",
        "input": '{"files": [{"path": "Test.swift", "content": "import Foundation"}]}',
        "should_fix": False
    },
    {
        "name": "Complex unterminated with nested quotes",
        "input": '''{"files": [{"path": "ComplexView.swift", "content": "struct ComplexView: View {\\n    @State private var text = \\"Hello\\n    var body: some View {\\n        Text(text)\\n    }\\n}''',
        "should_fix": True
    }
]

print("Testing Enhanced JSON Fixer")
print("=" * 50)

passed = 0
failed = 0

for test in test_cases:
    print(f"\nTest: {test['name']}")
    print(f"Input: {test['input'][:100]}...")
    
    try:
        result = extract_and_fix_json(test['input'])
        print(f"✅ Successfully parsed!")
        print(f"Result has {len(result.get('files', []))} files")
        
        # Verify it's valid JSON by re-encoding
        json.dumps(result)
        passed += 1
        
    except Exception as e:
        if test['should_fix']:
            print(f"❌ Failed to fix: {str(e)}")
            failed += 1
        else:
            print(f"✅ Correctly failed on invalid input")
            passed += 1

print(f"\n{'=' * 50}")
print(f"Results: {passed} passed, {failed} failed")
print(f"Success rate: {(passed / len(test_cases)) * 100:.1f}%")

# Test the specific error from logs
print("\n\nTesting actual xAI error case:")
print("=" * 50)

# This is similar to what xAI returns when it fails
xai_error_json = '''{"files": [
    {"path": "Sources/Views/StatsView.swift", "content": "import SwiftUI\\nimport Charts\\n\\nstruct StatsView: View {\\n    @StateObject private var viewModel = TodoViewModel()\\n    \\n    var body: some View {\\n        NavigationView {\\n            ScrollView {\\n                VStack(spacing: 20) {\\n                    // Summary Card\\n                    VStack(alignment: .leading, spacing: 12) {\\n                        Text(\\"Today's Progress\\")\\n                            .font(.headline)\\n                        \\n                        HStack {\\n                            StatItem(title: \\"Completed\\", value: \\"\\(viewModel.tasksCompletedToday)\\")\\n                            Spacer()\\n                            StatItem(title: \\"Remaining\\", value: \\"\\(viewModel.tasksRemainingToday)\\")\\n                        }\\n                    }\\n                    .padding()\\n                    .background(Color.gray.opacity(0.1))\\n                    .cornerRadius(12)\\n                    \\n                    // Completion Rate\\n                    VStack(alignment: .leading, spacing: 12) {\\n                        Text(\\"Completion Rate\\")\\n                            .font(.headline)\\n                        \\n                        ProgressView(value: viewModel.completionRate)\\n                            .progressViewStyle(LinearProgressViewStyle())\\n                        \\n                        Text(\\"\\(Int(viewModel.completionRate * 100))%\\")\\n                            .font(.caption)\\n                            .foregroundColor(.secondary)\\n                    }\\n                    .padding()\\n                    .background(Color.gray.opacity(0.1))\\n                    .cornerRadius(12)\\n                }\\n                .padding()\\n            }\\n            .navigationTitle(\\"Statistics\\")\\n        }\\n    }\\n}\\n\\nstruct StatItem: View {\\n    let title: String\\n    let value: String\\n    \\n    var body: some View {\\n        VStack(alignment: .leading) {\\n            Text(title)\\n                .font(.caption)\\n                .foregroundColor(.secondary)\\n            Text(value)\\n                .font(.title2)\\n                .fontWeight(.semibold)\\n        }\\n    }\\n}"},
    {"path": "Sources/Views/ContentView.swift", "content": "import SwiftUI\\n\\nstruct ContentView: View {\\n    @StateObject private var viewModel = TodoViewModel()\\n    @State private var newTaskText = \\"\\"\\n    @State private var selectedTab = 0\\n    \\n    var body: some View {\\n        TabView(selection: $selectedTab) {\\n            NavigationView {\\n                VStack {\\n                    HStack {\\n                        TextField(\\"New task\\", text: $newTaskText)\\n                            .textFieldStyle(RoundedBorderTextFieldStyle())\\n                        \\n                        Button(action: {\\n                            viewModel.addTask(newTaskText)\\n                            newTaskText = \\"\\"\\n                        }) {\\n                            Image(systemName: \\"plus.circle.fill\\")\\n                                .font(.title2)\\n                                .foregroundColor(.green)\\n                        }\\n                        .disabled(newTaskText.isEmpty)\\n                    }\\n                    .padding()\\n                    \\n                    List {\\n                        ForEach(viewModel.tasks) { task in\\n                            TaskRow(task: task, viewModel: viewModel)\\n                        }\\n                    }\\n                }\\n                .navigationTitle(\\"My Tasks\\")\\n            }\\n            .tabItem {\\n                Label(\\"Tasks\\", systemImage: \\"checklist\\")\\n            }\\n            .tag(0)\\n            \\n            StatsView()\\n                .tabItem {\\n                    Label(\\"Stats\\", systemImage: \\"chart.bar.fill\\")\\n                }\\n                .tag(1)\\n        }\\n    }\\n}"}
],
"bundle_id": "com.test.todoapp",
"modification_summary": "Added statistics dashboard with completion tracking and progress visualization",
"changes_made": [
    "Created new StatsView with statistics dashboard",
    "Added completion rate tracking with progress bar",
    "Implemented today's task summary cards",  
    "Added TabView to ContentView for navigation",
    "Created Stats tab with chart.bar.fill SF Symbol'''

try:
    result = extract_and_fix_json(xai_error_json)
    print("✅ Successfully fixed xAI error case!")
    print(f"Files in result: {len(result.get('files', []))}")
    for file in result.get('files', []):
        print(f"  - {file['path']}: {len(file['content'])} chars")
except Exception as e:
    print(f"❌ Failed to fix xAI case: {str(e)}")