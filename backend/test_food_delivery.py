#!/usr/bin/env python3
"""
Simple test script for food delivery app generation
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_claude_service import EnhancedClaudeService
from build_service import BuildService
from project_manager import ProjectManager
from debug_logger import DebugLogger
import json

async def test_food_delivery_app():
    """Test generating a DoorDash-like food delivery app"""
    print("Testing food delivery app generation...")
    
    # Initialize services
    claude_service = EnhancedClaudeService()
    build_service = BuildService()
    project_manager = ProjectManager()
    
    # Test app details
    app_name = "QuickBites"
    description = """Create a food delivery app like DoorDash with:
    - Restaurant browsing with categories (Italian, Asian, Mexican, etc.)
    - Restaurant detail view with menu items
    - Cart functionality with add/remove items
    - User profile and order history
    - Search and filter restaurants
    - Order tracking
    """
    
    print(f"\n1. Creating app: {app_name}")
    print(f"Description: {description[:100]}...")
    
    try:
        # Generate code first
        print("\n2. Generating code...")
        result = await claude_service.generate_ios_app(
            description=description,
            app_name=app_name
        )
        
        # Check results
        files = result.get("files", [])
        print(f"✓ Generated {len(files)} files")
        
        # List generated files
        print("\n3. Generated files:")
        for file in files[:10]:  # Show first 10 files
            print(f"   - {file['path']}")
        if len(files) > 10:
            print(f"   ... and {len(files) - 10} more files")
        
        # Create project with generated code
        print("\n4. Creating project...")
        project_id = project_manager.create_project(app_name, result)
        print(f"✓ Project created: {project_id}")
        
        # Save files to project
        print("\n5. Saving files to project...")
        project_path = project_manager.get_project_path(project_id)
        
        # Use file structure manager if available
        try:
            from file_structure_manager import FileStructureManager
            file_manager = FileStructureManager()
            success, written, missing = file_manager.verify_and_write_files(files, project_path)
            print(f"✓ Written {len(written)} files")
            if missing:
                print(f"⚠️  Missing {len(missing)} files: {missing[:5]}")
        except ImportError:
            # Fallback to direct write
            for file_data in files:
                file_path = os.path.join(project_path, file_data["path"])
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "w") as f:
                    f.write(file_data["content"])
            print(f"✓ Saved {len(files)} files")
        
        # Check architecture
        print("\n6. Architecture analysis:")
        has_models = any("Models/" in f["path"] for f in files)
        has_views = any("Views/" in f["path"] for f in files)
        has_viewmodels = any("ViewModels/" in f["path"] for f in files)
        has_services = any("Services/" in f["path"] for f in files)
        
        print(f"   - Models: {'✓' if has_models else '✗'}")
        print(f"   - Views: {'✓' if has_views else '✗'}")
        print(f"   - ViewModels: {'✓' if has_viewmodels else '✗'}")
        print(f"   - Services: {'✓' if has_services else '✗'}")
        
        # Check for key views
        key_views = ["RestaurantListView", "RestaurantDetailView", "CartView", "ContentView"]
        for view in key_views:
            has_view = any(view in f["path"] for f in files)
            print(f"   - {view}: {'✓' if has_view else '✗'}")
        
        # Summary
        print(f"\n✅ Test completed successfully!")
        print(f"   Total files: {len(files)}")
        print(f"   Architecture: {'MVVM' if has_viewmodels else 'Basic'}")
        print(f"   Complexity: {'High' if len(files) > 20 else 'Medium' if len(files) > 10 else 'Low'}")
        
        # Check debug logs if available
        debug_log_path = os.path.join(project_path, "..", "debug_logs", f"debug_{project_id}.log")
        if os.path.exists(debug_log_path):
            print(f"\n📋 Debug log available at: {debug_log_path}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_food_delivery_app())
    sys.exit(0 if success else 1)