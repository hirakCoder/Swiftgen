"""
Patch for BuildService to ensure all errors reach the UI
This is a minimal, safe patch that adds error communication without changing architecture
"""
import asyncio


def patch_build_service(build_service_class):
    """Add error communication to BuildService"""
    
    # Store original methods
    original_build_project = build_service_class.build_project
    original_update_status = build_service_class._update_status
    
    # Enhanced update_status that always tries to send
    async def enhanced_update_status(self, message: str, is_error: bool = False):
        """Enhanced status update that ensures delivery"""
        try:
            # Determine if this is an error message
            if is_error or any(indicator in message.lower() for indicator in ['error', 'failed', 'timeout', 'not found', '❌']):
                # For errors, ensure it shows in the UI
                if self.status_callback:
                    # Only send string messages to status callback
                    await self.status_callback(message)
            else:
                # Normal status update
                if self.status_callback:
                    await self.status_callback(message)
        except Exception as e:
            # Don't let callback errors break the build
            print(f"Warning: Status callback error: {e}")
    
    # Enhanced build_project that ensures all errors are communicated
    async def enhanced_build_project(self, project_path, project_id, bundle_id, app_complexity=None, is_modification=False):
        """Build with enhanced error communication"""
        
        # Wrap the entire build in try-catch to ensure errors are communicated
        try:
            # Call original method
            result = await original_build_project(
                self, project_path, project_id, bundle_id, 
                app_complexity=app_complexity, 
                is_modification=is_modification
            )
            
            # If build failed, ensure error is communicated
            if not result.success and result.errors:
                error_summary = result.errors[0] if result.errors else "Build failed"
                await enhanced_update_status(self, f"❌ {error_summary}", is_error=True)
            
            return result
            
        except Exception as e:
            # Ensure any unexpected error is communicated
            error_msg = f"Build failed: {str(e)}"
            await enhanced_update_status(self, f"❌ {error_msg}", is_error=True)
            
            # Still return a proper BuildResult
            from models import BuildResult
            return BuildResult(
                success=False,
                errors=[error_msg],
                warnings=[],
                build_time=0
            )
    
    # Apply patches
    build_service_class._update_status = enhanced_update_status
    build_service_class.build_project = enhanced_build_project
    
    # Also patch specific error-prone methods
    if hasattr(build_service_class, '_validate_project_structure'):
        original_validate = build_service_class._validate_project_structure
        
        async def enhanced_validate(self, project_path):
            """Validate with error communication"""
            result = original_validate(self, project_path)
            
            # Check for specific error conditions that don't communicate
            import os
            sources_dir = os.path.join(project_path, "Sources")
            if not os.path.exists(sources_dir):
                await enhanced_update_status(self, "❌ Sources directory not found", is_error=True)
            
            swift_files = []
            if os.path.exists(sources_dir):
                for root, _, files in os.walk(sources_dir):
                    swift_files.extend([f for f in files if f.endswith('.swift')])
            
            if not swift_files:
                await enhanced_update_status(self, "❌ No Swift files found in Sources directory", is_error=True)
            
            return result
        
        build_service_class._validate_project_structure = enhanced_validate
    
    return build_service_class


def apply_build_service_patch():
    """Apply the patch to BuildService"""
    try:
        # Import BuildService
        from build_service import BuildService
        
        # Apply patch
        patch_build_service(BuildService)
        
        print("✓ BuildService patched for enhanced error communication")
        return True
        
    except Exception as e:
        print(f"Warning: Could not patch BuildService: {e}")
        return False