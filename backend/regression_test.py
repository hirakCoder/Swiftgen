"""
Basic regression test to ensure core functionality still works
"""
import os
import sys
import subprocess


def test_syntax_check():
    """Check all Python files for syntax errors"""
    print("\n1️⃣ Checking Python syntax...")
    
    python_files = [
        'main.py',
        'enhanced_claude_service.py',
        'build_service.py',
        'modification_handler.py',
        'user_communication_service.py',
        'safe_ssl_integration.py',
        'build_service_patch.py',
        'json_fixer.py'
    ]
    
    all_good = True
    for file in python_files:
        if os.path.exists(file):
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', file],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"  ✅ {file}")
            else:
                print(f"  ❌ {file}: {result.stderr}")
                all_good = False
        else:
            print(f"  ⚠️  {file} not found")
    
    return all_good


def test_imports():
    """Test that key imports work"""
    print("\n2️⃣ Testing critical imports...")
    
    test_imports = [
        ("json_fixer", "extract_and_fix_json"),
        ("user_communication_service", "UserCommunicationService"),
        ("safe_ssl_integration", "safe_integrate_ssl_fixer"),
        ("build_service_patch", "apply_build_service_patch")
    ]
    
    all_good = True
    for module, item in test_imports:
        try:
            exec(f"from {module} import {item}")
            print(f"  ✅ {module}.{item}")
        except Exception as e:
            print(f"  ❌ {module}.{item}: {str(e)}")
            all_good = False
    
    return all_good


def test_file_structure():
    """Check that critical files exist"""
    print("\n3️⃣ Checking file structure...")
    
    critical_files = [
        'main.py',
        'enhanced_claude_service.py',
        'build_service.py',
        'modification_handler.py',
        'project_manager.py',
        'models.py'
    ]
    
    all_good = True
    for file in critical_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} missing")
            all_good = False
    
    return all_good


def test_no_breaking_changes():
    """Check for common breaking changes"""
    print("\n4️⃣ Checking for breaking changes...")
    
    checks = []
    
    # Check main.py still has key endpoints
    if os.path.exists('main.py'):
        with open('main.py', 'r') as f:
            main_content = f.read()
        
        checks.append(('@app.post("/api/generate")' in main_content, "Generate app endpoint exists"))
        checks.append(('@app.post("/api/modify")' in main_content, "Modify app endpoint exists"))
        checks.append(('@app.websocket("/ws/{project_id}")' in main_content, "WebSocket endpoint exists"))
        checks.append(('async def notify_clients' in main_content, "notify_clients function exists"))
    
    # Check build_service.py still has BuildService class
    if os.path.exists('build_service.py'):
        with open('build_service.py', 'r') as f:
            build_content = f.read()
        
        checks.append(('class BuildService:' in build_content, "BuildService class exists"))
        checks.append(('async def build_project' in build_content, "build_project method exists"))
    
    all_good = True
    for passed, check in checks:
        print(f"  {'✅' if passed else '❌'} {check}")
        if not passed:
            all_good = False
    
    return all_good


def main():
    """Run all regression tests"""
    print("="*60)
    print("🧪 Running Regression Tests")
    print("="*60)
    
    results = {
        "Syntax Check": test_syntax_check(),
        "Import Test": test_imports(),
        "File Structure": test_file_structure(),
        "Breaking Changes": test_no_breaking_changes()
    }
    
    print("\n" + "="*60)
    print("📊 Regression Test Results:")
    print("="*60)
    
    all_passed = True
    for test, passed in results.items():
        print(f"  {'✅' if passed else '❌'} {test}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ All regression tests passed! No functionality broken.")
    else:
        print("\n❌ Some regression tests failed. Please review.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)