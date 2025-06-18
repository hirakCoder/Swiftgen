#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

from robust_error_recovery_system import RobustErrorRecoverySystem

# Test the specific string literal issue
test_content = '''
import SwiftUI

struct RestaurantDetailView: View {
    let restaurant: Restaurant
    
    var body: some View {
        VStack {
            Text("Minimum order: String(format: "%.2f", restaurant.minimumOrder)")
                .font(.subheadline)
                .foregroundStyle(.gray)
            
            Text("Another test: String(format: "%.1f", value)")
            
            Text(String(format: "%.2f", directCall))
        }
    }
}
'''

print("🧪 Testing String Literal Fix")
print("=" * 50)

recovery_system = RobustErrorRecoverySystem(None)
fixed_content = recovery_system._fix_string_literals(test_content)

print("ORIGINAL:")
print(test_content)
print("\nFIXED:")
print(fixed_content)

# Check if the fix worked
if 'Text("Minimum order: \\(String(format: "%.2f", restaurant.minimumOrder))")' in fixed_content:
    print("\n✅ String literal fix SUCCESSFUL!")
else:
    print("\n❌ String literal fix FAILED!")
    print("Expected: Text(\"Minimum order: \\(String(format: \"%.2f\", restaurant.minimumOrder))\")")