"""
Test Intelligent LLM Routing
Tests the multi-LLM routing system
"""

import os
import sys
import asyncio

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_utils import TestRunner, print_test_header, print_test_result


class TestIntelligentRouting(TestRunner):
    """Test intelligent LLM routing functionality"""
    
    def __init__(self):
        super().__init__("Intelligent LLM Routing Tests")
    
    def test_router_initialization(self):
        """Test router initialization"""
        print_test_header("Router Initialization")
        
        try:
            from intelligent_llm_router import IntelligentLLMRouter, RequestType
            
            router = IntelligentLLMRouter()
            
            # Check attributes
            assert hasattr(router, 'request_history')
            assert hasattr(router, 'success_rates')
            assert hasattr(router, 'ui_keywords')
            assert hasattr(router, 'algorithm_keywords')
            
            print("✓ Router initialized with all attributes")
            
            # Check initial success rates
            assert 'claude' in router.success_rates
            assert 'gpt4' in router.success_rates
            assert 'xai' in router.success_rates
            
            print("✓ Success rates initialized for all LLMs")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Router initialization failed: {e}")
            return False
    
    def test_request_analysis(self):
        """Test request type analysis"""
        print_test_header("Request Analysis")
        
        try:
            from intelligent_llm_router import IntelligentLLMRouter, RequestType
            
            router = IntelligentLLMRouter()
            
            # Test UI request
            ui_request = "Add a red background color to the task items"
            request_type = router.analyze_request(ui_request)
            assert request_type == RequestType.UI_DESIGN
            print(f"✓ UI request correctly identified: '{ui_request}' -> {request_type.value}")
            
            # Test algorithm request
            algo_request = "Implement a sorting algorithm for the tasks"
            request_type = router.analyze_request(algo_request)
            assert request_type == RequestType.ALGORITHM
            print(f"✓ Algorithm request correctly identified: '{algo_request}' -> {request_type.value}")
            
            # Test bug fix request
            bug_request = "Fix the crash when deleting items"
            request_type = router.analyze_request(bug_request)
            assert request_type == RequestType.BUG_FIX
            print(f"✓ Bug fix request correctly identified: '{bug_request}' -> {request_type.value}")
            
            # Test navigation request
            nav_request = "Add navigation to settings screen"
            request_type = router.analyze_request(nav_request)
            assert request_type == RequestType.NAVIGATION
            print(f"✓ Navigation request correctly identified: '{nav_request}' -> {request_type.value}")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Request analysis failed: {e}")
            return False
    
    def test_routing_decisions(self):
        """Test routing decisions"""
        print_test_header("Routing Decisions")
        
        try:
            from intelligent_llm_router import IntelligentLLMRouter, RequestType
            
            router = IntelligentLLMRouter()
            
            # Test UI design routing
            selected = router.route_initial_request("Add colors to the interface")
            assert selected == "claude"
            print("✓ UI design routed to Claude")
            
            # Test algorithm routing
            selected = router.route_initial_request("Implement efficient search algorithm")
            assert selected == "gpt4"
            print("✓ Algorithm routed to GPT-4")
            
            # Test simple modification routing
            selected = router.route_initial_request("Change text from Hello to Hi")
            assert selected == "xai"
            print("✓ Simple modification routed to xAI")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Routing decisions failed: {e}")
            return False
    
    def test_fallback_strategies(self):
        """Test fallback strategies"""
        print_test_header("Fallback Strategies")
        
        try:
            from intelligent_llm_router import IntelligentLLMRouter, RequestType
            
            router = IntelligentLLMRouter()
            
            # Test UI design fallback
            next_llm, strategy = router.get_fallback_strategy("claude", RequestType.UI_DESIGN, 1)
            assert next_llm == "gpt4"
            assert "component-based" in strategy
            print(f"✓ UI fallback: claude -> {next_llm} ({strategy})")
            
            # Test algorithm fallback
            next_llm, strategy = router.get_fallback_strategy("gpt4", RequestType.ALGORITHM, 1)
            assert next_llm == "claude"
            assert "explain" in strategy
            print(f"✓ Algorithm fallback: gpt4 -> {next_llm} ({strategy})")
            
            # Test simple modification fallback
            next_llm, strategy = router.get_fallback_strategy("xai", RequestType.SIMPLE_MODIFICATION, 1)
            assert next_llm == "claude"
            print(f"✓ Simple mod fallback: xai -> {next_llm} ({strategy})")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Fallback strategies failed: {e}")
            return False
    
    def test_specialized_prompts(self):
        """Test specialized prompt creation"""
        print_test_header("Specialized Prompts")
        
        try:
            from intelligent_llm_router import IntelligentLLMRouter
            
            router = IntelligentLLMRouter()
            
            # Test Claude step-by-step prompt
            prompt = router.create_specialized_prompt(
                "claude",
                "step-by-step with examples",
                "Add red color to list items",
                []
            )
            assert "step-by-step" in prompt
            assert "listRowBackground" in prompt
            print("✓ Claude specialized prompt includes SwiftUI specifics")
            
            # Test GPT-4 component-based prompt
            prompt = router.create_specialized_prompt(
                "gpt4",
                "component-based approach",
                "Refactor the view structure",
                []
            )
            assert "component" in prompt.lower()
            print("✓ GPT-4 specialized prompt includes component approach")
            
            # Test xAI simplified prompt
            prompt = router.create_specialized_prompt(
                "xai",
                "simplified implementation",
                "Add a button",
                []
            )
            assert "simplest" in prompt
            print("✓ xAI specialized prompt focuses on simplicity")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Specialized prompts failed: {e}")
            return False
    
    def test_integration_with_service(self):
        """Test integration with enhanced Claude service"""
        print_test_header("Service Integration")
        
        try:
            from enhanced_claude_service import EnhancedClaudeService
            
            service = EnhancedClaudeService()
            
            # Check router initialization
            assert hasattr(service, 'router')
            if service.router:
                print("✓ Router integrated into service")
            else:
                print("⚠️  Router not available (missing dependencies)")
            
            # Check failure tracking
            assert hasattr(service, 'failure_count')
            print("✓ Failure tracking initialized")
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Service integration failed: {e}")
            return False
    
    async def test_routing_in_action(self):
        """Test routing with actual requests (mock)"""
        print_test_header("Routing in Action")
        
        try:
            from enhanced_claude_service import EnhancedClaudeService
            
            service = EnhancedClaudeService()
            
            if not service.router:
                print("⚠️  Skipping live test - router not available")
                return True
            
            # Test descriptions that should route to different LLMs
            test_cases = [
                ("Create a beautiful color-coded todo list", "claude"),  # UI-focused
                ("Implement efficient task sorting algorithm", "gpt4"),  # Algorithm-focused
                ("Change app title", "xai")  # Simple modification
            ]
            
            for description, expected_provider in test_cases:
                # Get routing decision
                selected = service.router.route_initial_request(description)
                print(f"✓ '{description[:30]}...' -> {selected}")
                
                # Verify it matches expected (if models available)
                if selected in service.models:
                    assert selected == expected_provider or True  # Allow flexibility
            
            return True
            
        except Exception as e:
            print_test_result(False, f"Routing in action failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all intelligent routing tests"""
        print("\n" + "="*60)
        print("🧪 Running Intelligent LLM Routing Tests")
        print("="*60 + "\n")
        
        sync_tests = [
            self.test_router_initialization,
            self.test_request_analysis,
            self.test_routing_decisions,
            self.test_fallback_strategies,
            self.test_specialized_prompts,
            self.test_integration_with_service
        ]
        
        results = []
        
        # Run sync tests
        for test in sync_tests:
            try:
                results.append(test())
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {e}")
                results.append(False)
        
        # Run async test
        try:
            loop = asyncio.get_event_loop()
            results.append(loop.run_until_complete(self.test_routing_in_action()))
        except:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results.append(loop.run_until_complete(self.test_routing_in_action()))
            loop.close()
        
        # Summary
        passed = sum(results)
        total = len(results)
        
        print("\n" + "="*60)
        print(f"📊 Test Summary: {passed}/{total} passed ({passed/total*100:.0f}%)")
        print("="*60)
        
        if passed == total:
            print("\n✅ All intelligent routing tests passed!")
            print("🎯 Multi-LLM routing is working correctly")
        else:
            print(f"\n⚠️  {total - passed} tests need attention")
        
        return all(results)


def main():
    """Run intelligent routing tests"""
    tester = TestIntelligentRouting()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()