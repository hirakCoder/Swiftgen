#!/usr/bin/env python3
"""Test UI Quality Validator directly"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from ui_quality_validator import UIQualityValidator

# Sample good code (following guidelines)
good_code = """
import SwiftUI

struct ContentView: View {
    @State private var count = 0
    
    var body: some View {
        VStack(spacing: 16) {
            Text("Counter: \\(count)")
                .font(.largeTitle)
                .foregroundColor(.primary)
            
            HStack(spacing: 24) {
                Button(action: { count -= 1 }) {
                    Text("Decrement")
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(minWidth: 100, minHeight: 44)
                        .background(Color.accentColor)
                        .cornerRadius(10)
                }
                
                Button(action: { count += 1 }) {
                    Text("Increment") 
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(minWidth: 100, minHeight: 44)
                        .background(Color.accentColor)
                        .cornerRadius(10)
                }
            }
        }
        .padding()
    }
}
"""

# Sample bad code (violating guidelines)
bad_code = """
import SwiftUI

struct ContentView: View {
    @State private var count = 0
    
    var body: some View {
        VStack {
            Text("Counter: \\(count)")
                .font(.largeTitle)
                .foregroundStyle(LinearGradient(colors: [.red, .blue], startPoint: .leading, endPoint: .trailing))
                .background(
                    LinearGradient(colors: [.purple, .pink], startPoint: .top, endPoint: .bottom)
                )
                .background(
                    RadialGradient(colors: [.yellow, .orange], center: .center, startRadius: 10, endRadius: 100)
                )
            
            HStack {
                Button(action: { 
                    withAnimation(.spring()) {
                        count -= 1
                    }
                }) {
                    Text("−")
                        .foregroundColor(.gray)
                        .background(Color.gray.opacity(0.3))
                }
                .frame(width: 30, height: 30)
                .transition(.scale)
                .animation(.bounce)
                
                Button(action: { count += 1 }) {
                    Text("+")
                        .frame(width: 30, height: 30)
                        .background(Color(red: 0.2, green: 0.8, blue: 0.4))
                }
                .animation(.easeInOut)
            }
        }
        .background(
            ZStack {
                LinearGradient(colors: [.blue, .purple], startPoint: .topLeading, endPoint: .bottomTrailing)
                Circle().fill(.yellow.opacity(0.3)).scaleEffect(2)
            }
        )
    }
}
"""

def test_validator():
    validator = UIQualityValidator()
    
    print("Testing UI Quality Validator")
    print("="*60)
    
    # Test good code
    print("\n1. Testing GOOD code (following guidelines):")
    print("-"*40)
    good_files = [{"path": "ContentView.swift", "content": good_code}]
    is_valid, issues, score = validator.validate_ui_quality(good_files)
    print(f"Valid: {is_valid}")
    print(f"Score: {score}/100")
    print(f"Issues: {len(issues)}")
    for issue in issues:
        print(f"  - {issue}")
    
    # Test bad code
    print("\n2. Testing BAD code (violating guidelines):")
    print("-"*40)
    bad_files = [{"path": "ContentView.swift", "content": bad_code}]
    is_valid, issues, score = validator.validate_ui_quality(bad_files)
    print(f"Valid: {is_valid}")
    print(f"Score: {score}/100") 
    print(f"Issues: {len(issues)}")
    for issue in issues:
        print(f"  - {issue}")
    
    # Test async validate method
    print("\n3. Testing async validate method:")
    print("-"*40)
    import asyncio
    
    async def test_async():
        result = await validator.validate({"files": bad_files})
        print(f"Success: {result.success}")
        print(f"Errors: {len(result.errors)}")
        for error in result.errors:
            print(f"  ERROR: {error}")
        print(f"Warnings: {len(result.warnings)}")
        for warning in result.warnings:
            print(f"  WARN: {warning}")
    
    asyncio.run(test_async())

if __name__ == "__main__":
    test_validator()