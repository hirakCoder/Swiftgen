#!/usr/bin/env python3
"""
Test script to verify UI enhancement handler fixes
"""

from ui_enhancement_handler import UIEnhancementHandler

def test_ui_fixes():
    handler = UIEnhancementHandler()
    
    # Test case 1: Fix transition on closing brace
    test_content_1 = """
struct TestView: View {
    var body: some View {
        VStack {
            Text("Hello")
        }
        .transition(.scale.combined(with: .opacity))
        .animation(.spring(response: 0.5, dampingFraction: 0.8), value: UUID())
    }
}
"""
    
    # Test case 2: Fix .fill() on shadow modifier
    test_content_2 = """
struct CardView: View {
    var body: some View {
        RoundedRectangle(cornerRadius: 10)
            .shadow(color: .black.opacity(0.1), radius: 10, x: 0, y: 5)
            .fill(.gray.opacity(0.1))
    }
}
"""
    
    # Test case 3: Fix color reference without Color prefix
    test_content_3 = """
struct ColorView: View {
    var body: some View {
        Rectangle()
            .fill(.gray)
            .foregroundStyle(.gray)
    }
}
"""
    
    files = [
        {"path": "TestView.swift", "content": test_content_1},
        {"path": "CardView.swift", "content": test_content_2},
        {"path": "ColorView.swift", "content": test_content_3}
    ]
    
    print("Testing UI Enhancement Handler Fixes...")
    print("=" * 50)
    
    enhanced_files = handler.enhance_ui_in_files(files, "improve UI")
    
    for i, file in enumerate(enhanced_files):
        print(f"\nTest Case {i+1}: {file['path']}")
        print("-" * 30)
        if file['modified']:
            print("✅ Modified")
            # Check for specific fixes
            content = file['content']
            
            # Check transition fix
            if '.transition(' in content and '}.transition(' not in content:
                print("✅ Transition syntax fixed")
            
            # Check fill order
            if '.fill(' in content and '.shadow(' in content:
                fill_pos = content.find('.fill(')
                shadow_pos = content.find('.shadow(')
                if fill_pos < shadow_pos or shadow_pos == -1:
                    print("✅ Fill/shadow order correct")
            
            # Check color references
            if 'Color.gray' in content and '.gray)' not in content:
                print("✅ Color references fixed")
                
            print("\nFixed content preview:")
            print(content[:200] + "...")
        else:
            print("❌ Not modified")
    
    print("\n✅ Test complete!")

if __name__ == "__main__":
    test_ui_fixes()