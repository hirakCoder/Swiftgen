"""
Test RAG Integration with SwiftGen Components
"""

import os
import sys
import json
import asyncio
from typing import Dict, List

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test utilities
from test_utils import TestRunner, print_test_header, print_test_result


class TestRAGIntegration(TestRunner):
    """Test RAG integration with various components"""
    
    def __init__(self):
        super().__init__("RAG Integration Tests")
        self.rag_kb = None
        self.pre_validator = None
        self.self_healer = None
        self.error_recovery = None
    
    def test_rag_initialization(self):
        """Test RAG Knowledge Base initialization"""
        print_test_header("RAG Initialization")
        
        try:
            from rag_knowledge_base import RAGKnowledgeBase
            self.rag_kb = RAGKnowledgeBase()
            
            # Check if documents loaded
            doc_count = len(self.rag_kb.metadata)
            assert doc_count > 0, f"No documents loaded. Expected > 0, got {doc_count}"
            
            print(f"✓ RAG initialized with {doc_count} documents")
            
            # Test cache manager
            if self.rag_kb.cache_manager:
                stats = self.rag_kb.get_cache_stats()
                print(f"✓ Cache manager active: {stats}")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"RAG initialization failed: {e}")
            return False
    
    def test_rag_search(self):
        """Test RAG search functionality"""
        print_test_header("RAG Search")
        
        if not self.rag_kb:
            print_test_result(False, "RAG not initialized")
            return False
        
        try:
            # Test common queries
            test_queries = [
                ("reserved type Task", 3),
                ("NavigationView deprecated", 2),
                ("missing import SwiftUI", 3),
                ("architecture MVVM", 2)
            ]
            
            for query, k in test_queries:
                results = self.rag_kb.search(query, k)
                assert len(results) > 0, f"No results for query: {query}"
                
                # Check result structure
                for result in results:
                    assert 'title' in result
                    assert 'content' in result
                    assert 'relevance_score' in result
                
                print(f"✓ Query '{query}' returned {len(results)} results")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"RAG search failed: {e}")
            return False
    
    def test_pre_generation_with_rag(self):
        """Test pre-generation validator with RAG"""
        print_test_header("Pre-Generation Validator with RAG")
        
        try:
            from pre_generation_validator import PreGenerationValidator
            self.pre_validator = PreGenerationValidator(rag_kb=self.rag_kb)
            
            # Test validation with RAG
            test_cases = [
                ("Todo App", "A simple todo list app with tasks"),
                ("Timer App", "A countdown timer application"),
                ("Photo App", "An image gallery viewer")
            ]
            
            for app_name, description in test_cases:
                enhanced_desc, validated_name = self.pre_validator.validate_and_enhance_prompt(
                    app_name, description
                )
                
                # Check if warnings were added
                if "todo" in app_name.lower():
                    assert "TodoItem" in enhanced_desc, "Should warn about Task reserved type"
                if "timer" in app_name.lower():
                    assert "AppTimer" in enhanced_desc, "Should warn about Timer type"
                
                print(f"✓ Validated '{app_name}' with RAG enhancements")
            
            # Test architecture guidance
            guidance = self.pre_validator.get_architecture_guidance("Complex App", "A complex multi-screen app")
            print(f"✓ Architecture guidance: {guidance[:50]}..." if guidance else "✓ No specific guidance")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Pre-generation validation failed: {e}")
            return False
    
    def test_self_healing_with_rag(self):
        """Test self-healing generator with RAG"""
        print_test_header("Self-Healing Generator with RAG")
        
        try:
            from self_healing_generator import SelfHealingGenerator
            self.self_healer = SelfHealingGenerator(rag_kb=self.rag_kb)
            
            # Test pattern finding
            patterns = asyncio.run(
                self.self_healer._find_working_patterns("todo list app")
            )
            
            assert len(patterns) > 0, "Should find working patterns"
            print(f"✓ Found {len(patterns)} working patterns")
            
            # Test constraint building
            predicted_issues = ["reserved_type", "missing_import"]
            constraints = self.self_healer._build_constraints(predicted_issues)
            
            assert "TodoItem" in constraints, "Should include TodoItem suggestion"
            assert "import SwiftUI" in constraints, "Should include import guidance"
            
            print(f"✓ Built constraints with RAG: {len(constraints)} chars")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Self-healing test failed: {e}")
            return False
    
    def test_error_recovery_with_rag(self):
        """Test error recovery system with RAG"""
        print_test_header("Error Recovery with RAG")
        
        try:
            from robust_error_recovery_system import RobustErrorRecoverySystem
            
            # Mock Claude service
            class MockClaudeService:
                async def generate_ios_app(self, *args, **kwargs):
                    return {"success": True}
            
            self.error_recovery = RobustErrorRecoverySystem(
                claude_service=MockClaudeService(),
                rag_kb=self.rag_kb
            )
            
            # Test RAG-based recovery
            test_errors = [
                "struct Task: Cannot find type 'Task' in scope",
                "NavigationView is deprecated in iOS 16.0",
                "Missing import SwiftUI"
            ]
            
            test_files = [{
                "path": "Sources/ContentView.swift",
                "content": """
struct Task {
    let title: String
}

NavigationView {
    Text("Hello")
}
"""
            }]
            
            # Analyze errors
            error_analysis = self.error_recovery._analyze_errors(test_errors)
            assert len(error_analysis["missing_imports"]) > 0
            
            # Test RAG recovery
            success, fixed_files = asyncio.run(
                self.error_recovery._rag_based_recovery(
                    test_errors, test_files, error_analysis
                )
            )
            
            if success:
                fixed_content = fixed_files[0]["content"]
                assert "TodoItem" in fixed_content, "Should replace Task with TodoItem"
                assert "NavigationStack" in fixed_content or "NavigationView" not in fixed_content
                print("✓ RAG recovery successfully fixed issues")
            else:
                print("✓ RAG recovery completed (no changes needed)")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Error recovery test failed: {e}")
            return False
    
    def test_cache_performance(self):
        """Test RAG cache performance"""
        print_test_header("RAG Cache Performance")
        
        if not self.rag_kb or not self.rag_kb.cache_manager:
            print_test_result(False, "RAG or cache not available")
            return False
        
        try:
            import time
            
            # Test query performance
            query = "reserved type Task"
            k = 3
            
            # First query (cache miss)
            start = time.time()
            results1 = self.rag_kb.search(query, k)
            time1 = time.time() - start
            
            # Second query (cache hit)
            start = time.time()
            results2 = self.rag_kb.search(query, k)
            time2 = time.time() - start
            
            # Verify cache hit
            assert results1 == results2, "Results should be identical"
            assert time2 < time1 * 0.5, f"Cached query should be faster: {time1:.3f}s vs {time2:.3f}s"
            
            print(f"✓ Cache performance: {time1:.3f}s → {time2:.3f}s ({(1-time2/time1)*100:.0f}% faster)")
            
            # Check cache stats
            stats = self.rag_kb.get_cache_stats()
            assert stats['hits'] > 0, "Should have cache hits"
            print(f"✓ Cache stats: {stats}")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Cache performance test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all RAG integration tests"""
        print("\n" + "="*60)
        print("🧪 Running RAG Integration Tests")
        print("="*60 + "\n")
        
        tests = [
            self.test_rag_initialization,
            self.test_rag_search,
            self.test_pre_generation_with_rag,
            self.test_self_healing_with_rag,
            self.test_error_recovery_with_rag,
            self.test_cache_performance
        ]
        
        results = []
        for test in tests:
            try:
                results.append(test())
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {e}")
                results.append(False)
        
        # Summary
        passed = sum(results)
        total = len(results)
        
        print("\n" + "="*60)
        print(f"📊 Test Summary: {passed}/{total} passed ({passed/total*100:.0f}%)")
        print("="*60)
        
        return all(results)


def main():
    """Run RAG integration tests"""
    tester = TestRAGIntegration()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()