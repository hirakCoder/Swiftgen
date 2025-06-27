#!/usr/bin/env python3
"""
Test Apple Design Agent - Demonstrates UI/UX capabilities
"""

import asyncio
import json
from apple_design_agent import AppleDesignAgent


async def test_apple_design_agent():
    """Test the Apple Design Agent capabilities"""
    print("=" * 70)
    print("Apple Design Agent Test Suite")
    print("=" * 70)
    
    # Initialize agent
    agent = AppleDesignAgent()
    
    # Test 1: Create new beautiful UI
    print("\n1. Testing new UI creation...")
    new_ui_request = {
        "description": "Create a beautiful task management app with modern UI",
        "app_name": "TaskFlow"
    }
    
    confidence = await agent.can_handle(new_ui_request)
    print(f"   Confidence: {confidence:.2f}")
    
    if confidence > 0.5:
        result = await agent.process(new_ui_request)
        print(f"   Success: {result['success']}")
        print(f"   Files generated: {len(result.get('files', []))}")
        print(f"   Design patterns: {result.get('design_patterns', [])}")
        
        # Show a snippet of generated UI
        if result.get('files'):
            content_view = next((f for f in result['files'] if 'ContentView' in f['path']), None)
            if content_view:
                print("\n   Generated UI Preview:")
                print("   " + "-" * 60)
                lines = content_view['content'].split('\n')[:20]
                for line in lines:
                    print(f"   {line}")
                print("   ...")
    
    # Test 2: Enhance existing UI
    print("\n\n2. Testing UI enhancement...")
    enhance_request = {
        "modification": "Enhance the UI with beautiful animations and modern design",
        "files": [
            {
                "path": "ContentView.swift",
                "content": """import SwiftUI

struct ContentView: View {
    @State private var items = ["Item 1", "Item 2", "Item 3"]
    
    var body: some View {
        VStack {
            Text("My List")
                .font(.system(size: 24))
            
            List(items, id: \\.self) { item in
                Text(item)
                    .padding(10)
            }
            
            Button(action: {
                items.append("New Item")
            }) {
                Text("Add Item")
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
            }
        }
    }
}"""
            }
        ]
    }
    
    confidence = await agent.can_handle(enhance_request)
    print(f"   Confidence: {confidence:.2f}")
    
    if confidence > 0.5:
        result = await agent.process(enhance_request)
        print(f"   Success: {result['success']}")
        print(f"   Changes made: {result.get('changes_made', [])}")
        
        # Show enhanced code snippet
        if result.get('files'):
            enhanced_file = result['files'][0]
            print("\n   Enhanced UI Preview:")
            print("   " + "-" * 60)
            lines = enhanced_file['content'].split('\n')[:30]
            for line in lines:
                print(f"   {line}")
            print("   ...")
    
    # Test 3: UI Pattern Examples
    print("\n\n3. Demonstrating UI patterns...")
    patterns = [
        "navigation_patterns",
        "animations",
        "form_components",
        "modal_presentations"
    ]
    
    for pattern in patterns[:2]:  # Show first 2 patterns
        print(f"\n   Pattern: {pattern}")
        request = {
            "description": f"Create a {pattern.replace('_', ' ')} example",
            "pattern_type": pattern
        }
        
        result = await agent.process(request)
        if result['success'] and result.get('files'):
            print(f"   ✓ Generated {pattern} successfully")
    
    # Test 4: Apple HIG Principles
    print("\n\n4. Apple HIG Principles Applied:")
    for principle, description in agent.design_principles.items():
        print(f"   • {principle.title()}: {description}")
    
    print("\n" + "=" * 70)
    print("Apple Design Agent Test Complete!")
    print("=" * 70)


def show_ui_capabilities():
    """Show what the Apple Design Agent can do"""
    print("\nApple Design Agent Capabilities:")
    print("-" * 50)
    
    capabilities = {
        "UI Creation": [
            "Modern SwiftUI interfaces",
            "Apple HIG compliant designs",
            "Beautiful animations",
            "Responsive layouts",
            "Dark mode support"
        ],
        "Design Patterns": [
            "Navigation (tabs, stacks, split views)",
            "Lists and grids with proper spacing",
            "Forms with validation",
            "Modal presentations",
            "Search interfaces"
        ],
        "Enhancements": [
            "Add smooth animations",
            "Improve typography",
            "Apply system colors",
            "Add accessibility",
            "Implement haptic feedback"
        ],
        "Best Practices": [
            "SF Symbols usage",
            "Proper spacing (8pt grid)",
            "Consistent design language",
            "Performance optimization",
            "VoiceOver support"
        ]
    }
    
    for category, items in capabilities.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  ✓ {item}")
    
    print("\n" + "-" * 50)


if __name__ == "__main__":
    # Show capabilities
    show_ui_capabilities()
    
    # Run tests
    asyncio.run(test_apple_design_agent())