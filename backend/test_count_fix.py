#!/usr/bin/env python3
"""
Test the count bug fix
"""

from modification_handler import ModificationHandler

# Test files from the Brew Counter app
test_files = [
    {
        "path": "Sources/ViewModels/BrewViewModel.swift",
        "content": """import SwiftUI
import Combine
import Foundation

@MainActor
class BrewViewModel: ObservableObject {
    @Published var beverages: [BeverageItem] = []
    @AppStorage("savedBeverages") private var savedBeveragesData: Data?
    
    init() {
        loadBeverages()
    }
    
    func addBeverage(name: String, emoji: String) {
        let newBeverage = BeverageItem(name: name, count: 0, emoji: emoji)
        beverages.append(newBeverage)
        saveBeverages()
    }
    
    func incrementCount(for beverage: BeverageItem) {
        if let index = beverages.firstIndex(where: { $0.id == beverage.id }) {
            beverages[index].count += 1
            saveBeverages()
        }
    }
}"""
    },
    {
        "path": "Sources/Views/ContentView.swift",
        "content": "// ContentView code"
    }
]

handler = ModificationHandler()

# Test the count bug fix
print("Testing count bug fix...")
print("=" * 50)

request = "I cant add more than one count, you need to fix this"
result = handler.create_minimal_modification(test_files, request)

print(f"Modification summary: {result['modification_summary']}")
print(f"Changes made: {result['changes_made']}")
print(f"Files modified: {result['files_modified']}")

# Check if the fix was applied
for file in result['files']:
    if 'BrewViewModel' in file['path']:
        if 'count: 1' in file['content']:
            print("\n✅ Fix applied successfully! Initial count changed from 0 to 1")
        else:
            print("\n❌ Fix not applied")
        
        # Show the relevant line
        lines = file['content'].split('\n')
        for i, line in enumerate(lines):
            if 'BeverageItem(name: name' in line:
                print(f"\nLine {i+1}: {line.strip()}")

print("\n✅ Test complete!")