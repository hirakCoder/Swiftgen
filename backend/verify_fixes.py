"""
Verify that all critical fixes are in place
"""
import os
import re


def verify_json_parsing_fix():
    """Check that JSON parsing has retry limits"""
    print("\n1️⃣ Checking JSON Parsing Fix...")
    
    # Check enhanced_claude_service.py for MAX_RETRIES
    with open('enhanced_claude_service.py', 'r') as f:
        content = f.read()
        
    checks = {
        "MAX_RETRIES defined": "MAX_RETRIES = 3" in content,
        "Retry limit check": "if retry_count >= MAX_RETRIES:" in content,
        "JSON fixer imported": "from json_fixer import extract_and_fix_json" in content,
        "JSON fixer used": "extract_and_fix_json" in content and "except json.JSONDecodeError" in content
    }
    
    all_passed = all(checks.values())
    for check, passed in checks.items():
        print(f"  {'✅' if passed else '❌'} {check}")
    
    return all_passed


def verify_ssl_fixer_integration():
    """Check that SSL fixer is safely integrated"""
    print("\n2️⃣ Checking SSL Fixer Integration...")
    
    # Check main.py for safe integration
    with open('main.py', 'r') as f:
        content = f.read()
    
    checks = {
        "Safe SSL integration imported": "from safe_ssl_integration import safe_integrate_ssl_fixer" in content,
        "SSL fixer safely integrated": "safe_integrate_ssl_fixer(auto_ssl_fixer" in content,
        "Old unsafe integration removed": "# if auto_ssl_fixer:" in content or "# TEMPORARILY DISABLED" in content
    }
    
    # Check safe_ssl_integration.py exists and has validation
    if os.path.exists('safe_ssl_integration.py'):
        with open('safe_ssl_integration.py', 'r') as f:
            safe_content = f.read()
        checks["JSON validation in SSL wrapper"] = "validate_files_json" in safe_content
        checks["Safe apply fixes wrapper"] = "safe_apply_fixes" in safe_content
    else:
        checks["Safe SSL integration file exists"] = False
    
    all_passed = all(checks.values())
    for check, passed in checks.items():
        print(f"  {'✅' if passed else '❌'} {check}")
    
    return all_passed


def verify_error_communication():
    """Check that error communication is enhanced"""
    print("\n3️⃣ Checking Error Communication...")
    
    # Check main.py for user communication service
    with open('main.py', 'r') as f:
        content = f.read()
    
    checks = {
        "User Communication Service imported": "from user_communication_service import user_comm_service" in content,
        "User Comm Service initialized": "User Communication Service initialized" in content,
        "BuildService patch imported": "from build_service_patch import apply_build_service_patch" in content,
        "BuildService patch applied": "apply_build_service_patch()" in content,
        "Callback connected in startup": "user_comm_service.set_notify_callback(notify_clients)" in content
    }
    
    # Check files exist
    checks["user_communication_service.py exists"] = os.path.exists('user_communication_service.py')
    checks["build_service_patch.py exists"] = os.path.exists('build_service_patch.py')
    
    all_passed = all(checks.values())
    for check, passed in checks.items():
        print(f"  {'✅' if passed else '❌'} {check}")
    
    return all_passed


def verify_modification_fix():
    """Check that modification degradation fix is in place"""
    print("\n4️⃣ Checking Modification Degradation Fix...")
    
    # Check main.py for the critical fix
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Look for the fix mentioned in MASTER_ISSUES_AND_FIXES.md
    checks = {
        "Fresh file reads implemented": "read_project_files" in content or "Read files from disk" in content
    }
    
    # Check project_manager.py if it exists
    if os.path.exists('project_manager.py'):
        with open('project_manager.py', 'r') as f:
            pm_content = f.read()
        checks["read_project_files method exists"] = "def read_project_files" in pm_content
    
    # Check modification_handler.py for retry logic
    if os.path.exists('modification_handler.py'):
        with open('modification_handler.py', 'r') as f:
            mh_content = f.read()
        checks["Modification retry logic exists"] = "retry" in mh_content.lower() or "attempt" in mh_content.lower()
    
    all_passed = all(checks.values()) if checks else False
    for check, passed in checks.items():
        print(f"  {'✅' if passed else '❌'} {check}")
    
    return all_passed


def main():
    """Run all verification checks"""
    print("="*60)
    print("🔍 Verifying Critical Fixes")
    print("="*60)
    
    results = {
        "JSON Parsing": verify_json_parsing_fix(),
        "SSL Fixer": verify_ssl_fixer_integration(),
        "Error Communication": verify_error_communication(),
        "Modification Degradation": verify_modification_fix()
    }
    
    print("\n" + "="*60)
    print("📊 Summary:")
    print("="*60)
    
    all_passed = True
    for fix, passed in results.items():
        print(f"  {'✅' if passed else '❌'} {fix}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ All critical fixes are in place!")
    else:
        print("\n⚠️  Some fixes may need attention")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)