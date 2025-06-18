"""
Regression tests to ensure simple app creation and modification still work
"""

import pytest
import asyncio
import os
import json
from pathlib import Path

# Import the services we need to test
try:
    from enhanced_claude_service import EnhancedClaudeService
    from complex_app_architect import ComplexAppArchitect
    from file_structure_manager import FileStructureManager
except ImportError as e:
    print(f"Import error: {e}")

class TestSimpleAppRegression:
    """Test that simple app functionality isn't broken"""
    
    @pytest.fixture
    def services(self):
        """Set up services"""
        return {
            "claude": EnhancedClaudeService(),
            "architect": ComplexAppArchitect(),
            "file_manager": FileStructureManager()
        }
    
    @pytest.mark.asyncio
    async def test_simple_calculator_app(self, services):
        """Test that simple calculator app still generates correctly"""
        
        # Simple app description
        description = "Create a basic calculator app with add, subtract, multiply, divide"
        app_name = "SimpleCalc"
        
        # Verify this is detected as low complexity
        complexity = services["architect"].analyze_complexity(description)
        assert complexity == "low", f"Simple calculator should be low complexity, got {complexity}"
        
        # Generate the app - this should NOT trigger complex architect
        result = await services["claude"].generate_ios_app(description, app_name)
        
        # Verify result
        assert result is not None
        assert "files" in result
        
        # Simple apps should have fewer files
        files = result["files"]
        assert len(files) < 10, f"Simple app has too many files: {len(files)}"
        
        # Should have basic structure
        assert any("App.swift" in f["path"] for f in files), "Missing App.swift"
        assert any("ContentView.swift" in f["path"] for f in files), "Missing ContentView.swift"
        
        # Should NOT have complex structure
        assert not any("Services/" in f["path"] for f in files), "Simple app shouldn't have Services"
        assert not any("ViewModels/" in f["path"] for f in files), "Simple calculator shouldn't need ViewModels"
        
        print(f"✅ Simple calculator app generation works! Generated {len(files)} files")
    
    @pytest.mark.asyncio
    async def test_simple_todo_app(self, services):
        """Test that medium complexity todo app works"""
        
        description = "Create a todo list app with add, delete, and mark complete"
        app_name = "TodoList"
        
        # Should be medium complexity
        complexity = services["architect"].analyze_complexity(description)
        assert complexity == "medium", f"Todo app should be medium complexity, got {complexity}"
        
        # Generate the app
        result = await services["claude"].generate_ios_app(description, app_name)
        
        assert result is not None
        assert "files" in result
        
        files = result["files"]
        # Medium apps have more files than simple
        assert 5 <= len(files) <= 15, f"Medium app unexpected file count: {len(files)}"
        
        print(f"✅ Todo app generation works! Generated {len(files)} files")
    
    @pytest.mark.asyncio
    async def test_simple_app_modification(self, services):
        """Test that modifications still work for simple apps"""
        
        # Create a minimal app first
        mock_files = [
            {
                "path": "Sources/App.swift",
                "content": """import SwiftUI

@main
struct SimpleApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}"""
            },
            {
                "path": "Sources/ContentView.swift", 
                "content": """import SwiftUI

struct ContentView: View {
    var body: some View {
        Text("Hello World")
            .padding()
    }
}"""
            }
        ]
        
        # Test modification
        modification = "Change the text to say Welcome and make it blue"
        
        result = await services["claude"].modify_ios_app(
            app_name="SimpleApp",
            description="Simple hello world app",
            modification=modification,
            files=mock_files
        )
        
        # Verify modification worked
        assert result is not None
        assert "files" in result
        assert len(result["files"]) == len(mock_files), "Should return same number of files"
        
        # Check that the modification was applied
        content_view = next((f for f in result["files"] if "ContentView" in f["path"]), None)
        assert content_view is not None
        
        content = content_view["content"]
        assert "Welcome" in content, "Text should be changed to Welcome"
        assert ".foregroundStyle(.blue)" in content or ".foregroundColor(.blue)" in content, "Color should be blue"
        
        print("✅ Simple app modification works!")
    
    def test_complexity_detection_accuracy(self, services):
        """Test that complexity detection is accurate"""
        architect = services["architect"]
        
        # Test various app descriptions
        test_cases = [
            ("calculator", "low"),
            ("timer app", "low"),
            ("unit converter", "low"),
            ("note taking app", "medium"),
            ("weather app with API", "medium"),
            ("recipe manager", "medium"),
            ("uber clone", "high"),
            ("amazon shopping", "high"),
            ("instagram social media", "high"),
            ("doordash delivery", "high")
        ]
        
        for description, expected in test_cases:
            actual = architect.analyze_complexity(description)
            assert actual == expected, f"'{description}' should be {expected} complexity, got {actual}"
        
        print("✅ Complexity detection is accurate!")

class TestComplexAppCapabilities:
    """Test that we can handle Uber and Amazon style apps"""
    
    @pytest.fixture
    def architect(self):
        return ComplexAppArchitect()
    
    def test_uber_app_detection(self, architect):
        """Test Uber-style ride sharing app detection"""
        
        descriptions = [
            "Create a ride sharing app like Uber",
            "Build an app for booking rides with drivers",
            "Make a taxi booking application"
        ]
        
        for desc in descriptions:
            complexity = architect.analyze_complexity(desc)
            assert complexity == "high", f"Uber-style app should be high complexity"
            
            # Check if we need to add ride-sharing template
            app_type = architect.identify_app_type(desc)
            print(f"Detected app type for '{desc}': {app_type}")
    
    def test_amazon_app_detection(self, architect):
        """Test Amazon-style e-commerce detection"""
        
        descriptions = [
            "Create an e-commerce app like Amazon",
            "Build a shopping marketplace",
            "Make an online store with products"
        ]
        
        for desc in descriptions:
            complexity = architect.analyze_complexity(desc)
            assert complexity == "high", f"Amazon-style app should be high complexity"
            
            app_type = architect.identify_app_type(desc)
            assert app_type == "ecommerce", f"Should detect e-commerce type"
    
    def test_uber_architecture_plan(self, architect):
        """Test that Uber-style apps get proper architecture"""
        
        description = "Create a ride sharing app like Uber with driver and rider modes"
        app_name = "RideShare"
        
        # Since we don't have a specific ride_sharing template yet,
        # it should fall back to general complex app
        plan = architect.create_architecture_plan(description, app_name)
        
        assert plan["complexity"] == "high"
        assert len(plan["file_structure"]) > 15, "Complex app needs many files"
        
        # Should have proper technical requirements
        assert any("location" in req.lower() for req in plan["technical_requirements"])
        
        print("✅ Uber-style app architecture planning works!")
    
    def test_amazon_architecture_plan(self, architect):
        """Test Amazon-style e-commerce architecture"""
        
        description = "Create an e-commerce marketplace like Amazon"
        app_name = "MegaStore"
        
        plan = architect.create_architecture_plan(description, app_name)
        
        assert plan["complexity"] == "high"
        assert plan["app_type"] == "ecommerce"
        
        # Check for e-commerce specific files
        file_structure = plan["file_structure"]
        
        # Should have product-related files
        assert any("Product" in path for path in file_structure)
        assert any("Cart" in path for path in file_structure)
        assert any("Order" in path for path in file_structure)
        
        # Should have proper services
        assert any("ProductService" in path for path in file_structure)
        assert any("CartService" in path for path in file_structure)
        
        print("✅ Amazon-style app architecture planning works!")

# Run tests
if __name__ == "__main__":
    # Run regression tests
    print("\n=== Running Simple App Regression Tests ===")
    pytest.main([__file__, "-v", "-k", "TestSimpleAppRegression", "-s"])
    
    print("\n=== Running Complex App Capability Tests ===")
    pytest.main([__file__, "-v", "-k", "TestComplexAppCapabilities", "-s"])