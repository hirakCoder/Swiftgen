"""
Test script to verify modification degradation is fixed
Tests 10 consecutive modifications on a simple app
"""
import asyncio
import json
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_modification_degradation():
    """Test that we can make 10+ consecutive modifications without degradation"""
    
    try:
        # Import necessary modules
        from enhanced_claude_service import EnhancedClaudeService
        from modification_handler import ModificationHandler
        from project_manager import ProjectManager
        
        print("\n" + "="*60)
        print("🧪 Testing Modification Degradation Fix")
        print("="*60)
        
        # Initialize services
        service = EnhancedClaudeService()
        mod_handler = ModificationHandler(service)
        project_manager = ProjectManager()
        
        # Create a simple test app
        print("\n1️⃣ Creating test app...")
        app_description = "A simple counter app with increment and decrement buttons"
        app_name = "TestCounter"
        
        # Generate the app
        result = await service.generate_ios_app(app_description, app_name)
        
        if not result or 'files' not in result:
            print("❌ Failed to generate test app")
            return False
        
        print(f"✅ Test app created with {len(result['files'])} files")
        
        # Set up test project context
        project_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        test_context = {
            'generated_files': result['files'],
            'app_name': app_name,
            'project_id': project_id
        }
        
        # List of modifications to test
        modifications = [
            "Change the background color to blue",
            "Add a reset button that sets the counter to 0",
            "Make the increment button green",
            "Make the decrement button red",
            "Add a label showing 'Current count:' above the counter",
            "Change the font size of the counter to 48",
            "Add padding around all buttons",
            "Change the app title to 'Super Counter'",
            "Add a border around the counter label",
            "Make all buttons have rounded corners"
        ]
        
        # Track success rate
        successful_mods = 0
        failed_mods = 0
        
        print(f"\n2️⃣ Testing {len(modifications)} consecutive modifications...")
        print("-" * 60)
        
        for i, mod_request in enumerate(modifications, 1):
            print(f"\n🔄 Modification {i}/{len(modifications)}: {mod_request}")
            
            try:
                # Apply modification
                mod_result = await mod_handler.apply_modification(
                    mod_request,
                    test_context,
                    project_id
                )
                
                if mod_result and mod_result.get('files'):
                    # Check if files actually changed
                    original_files = {f['path']: f['content'] for f in test_context['generated_files']}
                    modified_files = {f['path']: f['content'] for f in mod_result['files']}
                    
                    changes_found = False
                    for path, new_content in modified_files.items():
                        if path in original_files and original_files[path] != new_content:
                            changes_found = True
                            break
                    
                    if changes_found:
                        print(f"  ✅ Modification successful - files changed")
                        successful_mods += 1
                        # Update context for next modification
                        test_context['generated_files'] = mod_result['files']
                    else:
                        print(f"  ❌ Modification failed - no files changed")
                        failed_mods += 1
                else:
                    print(f"  ❌ Modification failed - no result returned")
                    failed_mods += 1
                    
            except Exception as e:
                print(f"  ❌ Modification error: {str(e)}")
                failed_mods += 1
            
            # Small delay between modifications
            await asyncio.sleep(1)
        
        # Print results
        print("\n" + "="*60)
        print("📊 Test Results:")
        print(f"  ✅ Successful modifications: {successful_mods}/{len(modifications)}")
        print(f"  ❌ Failed modifications: {failed_mods}/{len(modifications)}")
        print(f"  📈 Success rate: {(successful_mods/len(modifications)*100):.1f}%")
        
        # Determine if test passed
        if successful_mods >= 8:  # 80% success rate
            print("\n🎉 TEST PASSED - Modification degradation appears to be fixed!")
            return True
        else:
            print("\n❌ TEST FAILED - Modification degradation still present")
            return False
            
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_modification_degradation())
    exit(0 if success else 1)