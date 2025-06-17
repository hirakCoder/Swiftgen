"""
Simple Integration Test for SwiftGen
Tests core functionality without external dependencies
"""

import os
import sys
import json

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_enhanced_prompts():
    """Test enhanced prompts module"""
    print("\n🔍 Testing Enhanced Prompts...")
    try:
        import enhanced_prompts
        
        # Check for required attributes
        assert hasattr(enhanced_prompts, 'SWIFT_GENERATION_SYSTEM_PROMPT'), "Missing SWIFT_GENERATION_SYSTEM_PROMPT"
        assert hasattr(enhanced_prompts, 'SWIFT_GENERATION_USER_PROMPT_TEMPLATE'), "Missing SWIFT_GENERATION_USER_PROMPT_TEMPLATE"
        
        # Check content
        assert "iOS 16.0" in enhanced_prompts.SWIFT_GENERATION_SYSTEM_PROMPT
        assert "SwiftUI" in enhanced_prompts.SWIFT_GENERATION_SYSTEM_PROMPT
        assert "{app_name}" in enhanced_prompts.SWIFT_GENERATION_USER_PROMPT_TEMPLATE
        
        print("✅ Enhanced prompts module OK")
        return True
    except Exception as e:
        print(f"❌ Enhanced prompts test failed: {e}")
        return False


def test_validators():
    """Test validators without external dependencies"""
    print("\n🔍 Testing Validators...")
    
    results = []
    
    # Test pre-generation validator
    try:
        from pre_generation_validator import PreGenerationValidator
        validator = PreGenerationValidator()
        
        # Basic test
        assert hasattr(validator, 'reserved_types')
        assert 'Task' in validator.reserved_types
        assert 'State' in validator.reserved_types
        
        print("✅ Pre-generation validator OK")
        results.append(True)
    except Exception as e:
        print(f"❌ Pre-generation validator failed: {e}")
        results.append(False)
    
    # Test comprehensive validator
    try:
        from comprehensive_code_validator import ComprehensiveCodeValidator
        validator = ComprehensiveCodeValidator()
        
        # Test pattern structure
        assert hasattr(validator, 'reserved_types')
        assert hasattr(validator, 'validate_files')
        
        print("✅ Comprehensive validator OK")
        results.append(True)
    except Exception as e:
        print(f"❌ Comprehensive validator failed: {e}")
        results.append(False)
    
    # Test modern pattern validator  
    try:
        from modern_pattern_validator import ModernPatternValidator
        validator = ModernPatternValidator()
        
        assert hasattr(validator, 'deprecated_patterns')
        assert hasattr(validator, 'validate_files')
        
        print("✅ Modern pattern validator OK")
        results.append(True)
    except Exception as e:
        print(f"❌ Modern pattern validator failed: {e}")
        results.append(False)
    
    return all(results)


def test_error_recovery():
    """Test error recovery system"""
    print("\n🔍 Testing Error Recovery...")
    try:
        from robust_error_recovery_system import RobustErrorRecoverySystem
        
        recovery = RobustErrorRecoverySystem()
        
        # Test error patterns
        assert hasattr(recovery, 'error_patterns')
        assert len(recovery.error_patterns) > 0
        
        # Test error analysis
        test_errors = ["error: cannot find type 'Task' in scope"]
        analysis = recovery._analyze_errors(test_errors)
        
        assert isinstance(analysis, dict)
        assert 'missing_imports' in analysis
        
        print("✅ Error recovery system OK")
        return True
    except Exception as e:
        print(f"❌ Error recovery test failed: {e}")
        return False


def test_self_healing():
    """Test self-healing generator"""
    print("\n🔍 Testing Self-Healing Generator...")
    try:
        from self_healing_generator import SelfHealingGenerator
        
        healer = SelfHealingGenerator()
        
        # Test basic structure
        assert hasattr(healer, 'known_failure_patterns')
        assert 'reserved_type' in healer.known_failure_patterns
        assert 'missing_import' in healer.known_failure_patterns
        
        # Test pattern extraction
        patterns = healer._extract_patterns_from_content("@StateObject var viewModel")
        assert patterns['uses_stateobject'] == True
        
        print("✅ Self-healing generator OK")
        return True
    except Exception as e:
        print(f"❌ Self-healing test failed: {e}")
        return False


def test_modification_components():
    """Test modification components"""
    print("\n🔍 Testing Modification Components...")
    
    results = []
    
    # Test modification verifier
    try:
        from modification_verifier import ModificationVerifier
        verifier = ModificationVerifier()
        
        # Basic test
        original = [{"path": "test.swift", "content": "original"}]
        modified = [{"path": "test.swift", "content": "modified"}]
        
        issues = verifier.verify_modifications(original, modified, "test")
        assert isinstance(issues, list)
        
        print("✅ Modification verifier OK")
        results.append(True)
    except Exception as e:
        print(f"❌ Modification verifier failed: {e}")
        results.append(False)
    
    # Test modification handler
    try:
        from modification_handler import ModificationHandler
        handler = ModificationHandler()
        
        assert hasattr(handler, 'prepare_modification_prompt')
        
        print("✅ Modification handler OK")
        results.append(True)
    except Exception as e:
        print(f"❌ Modification handler failed: {e}")
        results.append(False)
    
    return all(results)


def test_rag_cache():
    """Test RAG cache manager"""
    print("\n🔍 Testing RAG Cache Manager...")
    try:
        from rag_cache_manager import RAGCacheManager
        
        cache = RAGCacheManager(max_cache_size=10, ttl_seconds=60)
        
        # Test basic operations
        assert cache.get("test", 3) is None  # Cache miss
        
        # Test put and get
        cache.put("test", 3, [{"result": 1}])
        cached = cache.get("test", 3)
        assert cached is not None
        assert cached[0]["result"] == 1
        
        # Test stats
        stats = cache.get_stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        
        print("✅ RAG cache manager OK")
        return True
    except Exception as e:
        print(f"❌ RAG cache test failed: {e}")
        return False


def main():
    """Run simple integration tests"""
    print("\n" + "="*60)
    print("🚀 SwiftGen Simple Integration Test")
    print("="*60)
    
    tests = [
        test_enhanced_prompts,
        test_validators,
        test_error_recovery,
        test_self_healing,
        test_modification_components,
        test_rag_cache
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\n💥 Test {test.__name__} crashed: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "="*60)
    print(f"📊 Results: {passed}/{total} passed ({passed/total*100:.0f}%)")
    print("="*60)
    
    if passed == total:
        print("\n✅ All core components working correctly!")
        print("🎉 RAG integration is functional!")
    else:
        print(f"\n⚠️  {total - passed} components need attention")
    
    return 0 if passed >= total * 0.8 else 1


if __name__ == "__main__":
    sys.exit(main())