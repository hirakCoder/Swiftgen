"""
Simplified Next Steps Generator
Provides 2-3 relevant next actions for users
"""

def generate_simplified_next_steps(app_type: str, is_modification: bool = False) -> str:
    """Generate 2-3 simple, actionable next steps"""
    
    if is_modification:
        return """
💡 **What would you like to do next?**
• Test the changes in the iOS Simulator
• Make another modification to your app
• Add a new feature or screen"""
    
    # App type specific suggestions
    next_steps_map = {
        "food_delivery": """
💡 **What would you like to do next?**
• Test your food delivery app in the iOS Simulator
• Add restaurant search or filtering features
• Customize the app's colors and branding""",
        
        "ecommerce": """
💡 **What would you like to do next?**
• Test your shopping app in the iOS Simulator
• Add product categories or search functionality
• Customize the product display layout""",
        
        "social_media": """
💡 **What would you like to do next?**
• Test your social app in the iOS Simulator
• Add user profiles or messaging features
• Customize the post layout and styling""",
        
        "ride_sharing": """
💡 **What would you like to do next?**
• Test your ride app in the iOS Simulator
• Add driver tracking or route display
• Customize the booking interface""",
        
        "fitness": """
💡 **What would you like to do next?**
• Test your fitness app in the iOS Simulator
• Add workout tracking or progress charts
• Customize the exercise categories""",
        
        "default": """
💡 **What would you like to do next?**
• Test your app in the iOS Simulator
• Add a new feature or screen
• Customize the app's appearance"""
    }
    
    return next_steps_map.get(app_type, next_steps_map["default"])