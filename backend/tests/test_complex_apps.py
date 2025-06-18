"""
Test suite for complex app generation
Tests food delivery, social media, and e-commerce apps
"""

import pytest
import asyncio
import os
import json
from pathlib import Path

# Import the services we need to test
try:
    from enhanced_claude_service import EnhancedClaudeService
    from build_service import BuildService
    from project_manager import ProjectManager
    from complex_app_architect import ComplexAppArchitect
    from file_structure_manager import FileStructureManager
except ImportError as e:
    print(f"Import error: {e}")

class TestComplexApps:
    """Test suite for complex app generation"""
    
    @pytest.fixture
    def setup_services(self):
        """Set up services for testing"""
        claude_service = EnhancedClaudeService()
        build_service = BuildService()
        project_manager = ProjectManager()
        architect = ComplexAppArchitect()
        file_manager = FileStructureManager()
        
        return {
            "claude": claude_service,
            "build": build_service,
            "project": project_manager,
            "architect": architect,
            "file_manager": file_manager
        }
    
    @pytest.mark.asyncio
    async def test_food_delivery_app_generation(self, setup_services):
        """Test generating a DoorDash-like food delivery app"""
        services = setup_services
        
        # Test app details
        app_name = "QuickBites"
        description = """Create a food delivery app like DoorDash with:
        - Restaurant browsing with categories
        - Menu viewing and item selection
        - Shopping cart functionality
        - User authentication
        - Order tracking
        - Search and filtering
        - User profile and order history
        """
        
        # Step 1: Analyze complexity
        complexity = services["architect"].analyze_complexity(description)
        assert complexity == "high", f"Expected high complexity, got {complexity}"
        
        # Step 2: Generate architecture plan
        plan = services["architect"].create_architecture_plan(description, app_name)
        assert plan["app_type"] == "food_delivery"
        assert len(plan["file_structure"]) > 20, "Complex app should have many files"
        
        # Step 3: Generate the app
        result = await services["claude"].generate_ios_app(description, app_name)
        
        # Verify generation result
        assert result is not None
        assert "files" in result
        assert len(result["files"]) > 20, f"Expected 20+ files, got {len(result['files'])}"
        
        # Step 4: Verify file structure
        files = result["files"]
        
        # Check for required models
        model_files = [f for f in files if "Models/" in f["path"]]
        assert len(model_files) >= 5, "Should have at least 5 model files"
        
        required_models = ["Restaurant", "MenuItem", "Cart", "Order", "User"]
        for model in required_models:
            assert any(f"{model}.swift" in f["path"] for f in files), f"Missing {model} model"
        
        # Check for required views
        view_files = [f for f in files if "Views/" in f["path"]]
        assert len(view_files) >= 8, "Should have at least 8 view files"
        
        required_views = ["RestaurantListView", "RestaurantDetailView", "CartView", "CheckoutView"]
        for view in required_views:
            assert any(f"{view}.swift" in f["path"] for f in files), f"Missing {view}"
        
        # Check for services
        service_files = [f for f in files if "Services/" in f["path"]]
        assert len(service_files) >= 3, "Should have at least 3 service files"
        
        # Step 5: Create project and verify structure
        project_id = "test_food_delivery"
        project_path = services["project"].create_project(project_id, app_name, result)
        
        # Verify directory structure
        validation = services["file_manager"].validate_project_structure(project_path)
        assert validation["valid"], f"Invalid project structure: {validation['errors']}"
        
        # Step 6: Attempt to build (this will likely fail in test environment)
        try:
            build_result = await services["build"].build_project(
                project_path, 
                project_id, 
                result.get("bundle_id", "com.test.app")
            )
            
            # If build succeeds, great!
            if build_result.success:
                print("Build succeeded!")
            else:
                # Check that error recovery was attempted
                assert len(build_result.warnings) > 0 or len(build_result.errors) > 0
                
                # Verify missing file detection works
                missing_files = services["file_manager"].find_missing_files(
                    build_result.errors, 
                    files
                )
                print(f"Detected {len(missing_files)} missing files")
                
        except Exception as e:
            # Build might fail in test environment, that's OK
            print(f"Build failed (expected in test): {e}")
        
        # Clean up
        services["project"].cleanup_project(project_id)
    
    @pytest.mark.asyncio
    async def test_social_media_app_generation(self, setup_services):
        """Test generating an Instagram-like social media app"""
        services = setup_services
        
        app_name = "PhotoShare"
        description = """Create a social media app like Instagram with:
        - User profiles and authentication
        - Photo feed with infinite scrolling
        - Like and comment functionality
        - User following system
        - Direct messaging
        - Search and discovery
        - Notifications
        """
        
        # Generate the app
        result = await services["claude"].generate_ios_app(description, app_name)
        
        # Verify core components
        assert "files" in result
        files = result["files"]
        
        # Check for social media specific models
        required_models = ["User", "Post", "Comment", "Like", "Follow"]
        for model in required_models:
            assert any(f"{model}.swift" in f["path"] for f in files), f"Missing {model} model"
        
        # Check for feed and profile views
        required_views = ["FeedView", "ProfileView", "PostDetailView"]
        for view in required_views:
            assert any(f"{view}.swift" in f["path"] for f in files), f"Missing {view}"
    
    @pytest.mark.asyncio
    async def test_file_organization(self, setup_services):
        """Test that files are properly organized"""
        services = setup_services
        
        # Create mock files with mixed organization
        mock_files = [
            {"path": "Sources/ContentView.swift", "content": "struct ContentView: View { }"},
            {"path": "Sources/RestaurantModel.swift", "content": "struct Restaurant: Codable { }"},
            {"path": "Sources/CartViewModel.swift", "content": "class CartViewModel: ObservableObject { }"},
            {"path": "Sources/NetworkService.swift", "content": "class NetworkService { }"},
            {"path": "Sources/OrderView.swift", "content": "struct OrderView: View { }"}
        ]
        
        # Organize files
        organized_files, mapping = services["file_manager"].organize_files(mock_files, "/test/path")
        
        # Verify organization
        assert any("Views/ContentView.swift" in f["path"] for f in organized_files)
        assert any("Models/RestaurantModel.swift" in f["path"] for f in organized_files)
        assert any("ViewModels/CartViewModel.swift" in f["path"] for f in organized_files)
        assert any("Services/NetworkService.swift" in f["path"] for f in organized_files)
        assert any("Views/OrderView.swift" in f["path"] for f in organized_files)
    
    @pytest.mark.asyncio
    async def test_missing_file_detection(self, setup_services):
        """Test detection of missing files from errors"""
        services = setup_services
        
        # Mock build errors
        errors = [
            "Sources/Views/ContentView.swift:25:8: error: cannot find 'CartView' in scope",
            "Sources/Models/Restaurant.swift:15:20: error: 'MenuItem' must conform to 'Hashable'",
            "Sources/Views/RestaurantListView.swift:45:12: error: cannot find 'RestaurantDetailView' in scope"
        ]
        
        # Mock existing files
        existing_files = [
            {"path": "Sources/Views/ContentView.swift", "content": "..."},
            {"path": "Sources/Models/Restaurant.swift", "content": "..."}
        ]
        
        # Detect missing files
        missing = services["file_manager"].find_missing_files(errors, existing_files)
        
        # Verify detection
        assert len(missing) >= 2
        assert any(m["type"] == "CartView" for m in missing)
        assert any(m["type"] == "RestaurantDetailView" for m in missing)
        
        # Verify suggested paths
        cart_view = next(m for m in missing if m["type"] == "CartView")
        assert cart_view["suggested_path"] == "Sources/Views/CartView.swift"
    
    def test_complexity_detection(self, setup_services):
        """Test app complexity detection"""
        services = setup_services
        architect = services["architect"]
        
        # Test various descriptions
        assert architect.analyze_complexity("simple calculator app") == "low"
        assert architect.analyze_complexity("todo list with persistence") == "medium"
        assert architect.analyze_complexity("food delivery app like doordash") == "high"
        assert architect.analyze_complexity("social media platform like instagram") == "high"
        assert architect.analyze_complexity("e-commerce marketplace") == "high"
    
    def test_app_type_identification(self, setup_services):
        """Test app type identification"""
        services = setup_services
        architect = services["architect"]
        
        assert architect.identify_app_type("food delivery like doordash") == "food_delivery"
        assert architect.identify_app_type("social media like instagram") == "social_media"
        assert architect.identify_app_type("online shopping marketplace") == "ecommerce"
        assert architect.identify_app_type("task management app") == "general"

# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])