#!/usr/bin/env python3
"""Test JSON parsing fix for unterminated strings"""

import sys
sys.path.append('backend')

from json_fixer import extract_and_fix_json

def test_json_fixes():
    # Test case 1: Unterminated string
    malformed_json1 = '''
    {
        "files": [
            {
                "name": "test.swift",
                "content": "This is a long string that goes on and on
    '''
    
    print("Test 1: Unterminated string in content")
    print("-" * 40)
    try:
        result = extract_and_fix_json(malformed_json1)
        print("✅ PASS - Fixed JSON:", result)
    except Exception as e:
        print("❌ FAIL -", str(e))
    print()
    
    # Test case 2: Missing closing quote at line 25 (simulating xAI error)
    malformed_json2 = '''
    {
        "files": [
            {
                "name": "ContentView.swift",
                "content": "import SwiftUI\\n\\nstruct ContentView: View {\\n    var body: some View {\\n        Text(\\"Hello
            },
            {
                "name": "App.swift",
                "content": "import SwiftUI\\n\\n@main\\nstruct App: App {\\n    var body: some Scene {\\n        WindowGroup {\\n            ContentView()\\n        }\\n    }\\n}"
            }
        ]
    }
    '''
    
    print("Test 2: Missing quote in first file content")
    print("-" * 40)
    try:
        result = extract_and_fix_json(malformed_json2)
        print("✅ PASS - Fixed JSON with", len(result['files']), "files")
    except Exception as e:
        print("❌ FAIL -", str(e))
    print()
    
    # Test case 3: Complex nested unterminated string
    malformed_json3 = '''
    {
        "files": [
            {
                "name": "StatsView.swift",
                "path": "Sources/Views/StatsView.swift",
                "content": "import SwiftUI\\nimport Charts\\n\\nstruct StatsView: View {\\n    @ObservedObject var appState: AppStateManager\\n    \\n    var body: some View {\\n        NavigationStack {\\n            ScrollView {\\n                VStack(spacing: 20) {\\n                    // Summary Card\\n                    VStack(alignment: .leading, spacing: 12) {\\n                        Text(\\"Overview\\")\\n                            .font(.headline)\\n                        \\n                        HStack {\\n                            StatItem(title: \\"Today\\", value: \\"\\\\(todayCompleted)\\")\\n                            Spacer()\\n                            StatItem(title: \\"This Week\\", value: \\"\\\\(weekCompleted)\\")\\n                            Spacer()\\n                            StatItem(title: \\"This Month\\", value: \\"\\\\(monthCompleted)\\")\\n                        }\\n                        \\n                        HStack {\\n                            Text(\\"Completion Rate\\")\\n                            Spacer()\\n                            Text(\\"\\\\(Int(completionRate * 100))%\\")\\n                                .font(.title2)\\n                                .fontWeight(.bold)\\n                        }\\n                    }\\n                    .padding()\\n                    .background(Color.purple.opacity(0.1))\\n                    .cornerRadius(12)\\n                    \\n                    // Category Breakdown\\n                    VStack(alignment: .leading, spacing: 12) {\\n                        Text(\\"Tasks by Category\\")\\n                            .font(.headline)\\n                        \\n                        ForEach(categoryBreakdown.sorted(by: { $0.value > $1.value }), id: \\\\.key) { category, count in\\n                            HStack {\\n                                Circle()\\n                                    .fill(colorForCategory(category))\\n                                    .frame(width: 12, height: 12)\\n                                Text(category.rawValue)\\n                                Spacer()\\n                                Text(\\"\\\\(count)\\")\\n                                    .fontWeight(.medium)\\n                            }\\n                        }\\n                    }\\n                    .padding()\\n                    .background(Color.purple.opacity(0.1))\\n                    .cornerRadius(12)\\n                    \\n                    // Streak Counter\\n                    VStack(spacing: 8) {\\n                        Image(systemName: \\"flame.fill\\")\\n                            .font(.system(size: 40))\\n                            .foregroundColor(.orange)\\n                        Text(\\"\\\\(currentStreak) Day Streak!\\")\\n                            .font(.title2)\\n                            .fontWeight(.bold)\\n                        Text(\\"Keep it going!\\")\\n                            .font(.caption)\\n                            .foregroundColor(.secondary)\\n                    }\\n                    .frame(maxWidth: .infinity)\\n                    .padding()\\n                    .background(Color.orange.opacity(0.1))\\n                    .cornerRadius(12)\\n                }\\n                .padding()\\n            }\\n            .navigationTitle(\\"Statistics\\")\\n            .navigationBarTitleDisplayMode(.large)\\n        }\\n    }\\n    \\n    // Computed properties for statistics\\n    private var todayCompleted: Int {\\n        let calendar = Calendar.current\\n        let today = calendar.startOfDay(for: Date())\\n        return appState.items.filter { item in\\n            item.isCompleted && calendar.isDate(item.completedDate ?? Date(), inSameDayAs: today)\\n        }.count\\n    }\\n    \\n    private var weekCompleted: Int {\\n        let calendar = Calendar.current\\n        let weekAgo = calendar.date(byAdding: .day, value: -7, to: Date()) ?? Date()\\n        return appState.items.filter { item in\\n            item.isCompleted && (item.completedDate ?? Date()) >= weekAgo\\n        }.count\\n    }\\n    \\n    private var monthCompleted: Int {\\n        let calendar = Calendar.current\\n        let monthAgo = calendar.date(byAdding: .month, value: -1, to: Date()) ?? Date()\\n        return appState.items.filter { item in\\n            item.isCompleted && (item.completedDate ?? Date()) >= monthAgo\\n        }.count\\n    }\\n    \\n    private var completionRate: Double {\\n        let total = appState.items.count\\n        guard total > 0 else { return 0 }\\n        let completed = appState.items.filter { $0.isCompleted }.count\\n        return Double(completed) / Double(total)\\n    }\\n    \\n    private var categoryBreakdown: [AppCategory: Int] {\\n        Dictionary(grouping: appState.items, by: { $0.category })\\n            .mapValues { $0.count }\\n    }\\n    \\n    private var currentStreak: Int {\\n        // Simple streak calculation\\n        var streak = 0\\n        let calendar = Calendar.current\\n        var currentDate = Date()\\n        \\n        while true {\\n            let dayStart = calendar.startOfDay(for: currentDate)\\n            let hasCompletedTask = appState.items.contains { item in\\n                item.isCompleted && calendar.isDate(item.completedDate ?? Date(), inSameDayAs: dayStart)\\n            }\\n            \\n            if hasCompletedTask {\\n                streak += 1\\n                currentDate = calendar.date(byAdding: .day, value: -1, to: currentDate) ?? Date()\\n            } else {\\n                break\\n            }\\n        }\\n        \\n        return streak\\n    }\\n    \\n    private func colorForCategory(_ category: AppCategory) -> Color {\\n        switch category {\\n        case .personal: return .blue\\n        case .work: return .green\\n        case .shopping: return .orange\\n        case .health: return .red\\n        case .other: return .gray\\n        }\\n    }\\n}\\n\\nstruct StatItem: View {\\n    let title: String\\n    let value: String\\n    \\n    var body: some View {\\n        VStack(alignment: .center, spacing: 4) {\\n            Text(title)\\n                .font(.caption)\\n                .foregroundColor(.secondary)\\n            Text(value)\\n                .font(.title2)\\n                .fontWeight(.semibold)\\n        }\\n    }\\n}
            }
        ]
    }
    '''
    
    print("Test 3: Complex unterminated string (like xAI error)")
    print("-" * 40)
    try:
        result = extract_and_fix_json(malformed_json3)
        print("✅ PASS - Fixed complex JSON")
    except Exception as e:
        print("❌ FAIL -", str(e))

if __name__ == "__main__":
    print("🧪 Testing JSON Parsing Fixes")
    print("="*60)
    test_json_fixes()