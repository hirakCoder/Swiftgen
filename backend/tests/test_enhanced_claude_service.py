"""
Unit tests for enhanced_claude_service.py
Tests the core LLM service functionality including multi-LLM routing and modifications
"""
import pytest
import json
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, List
import asyncio

from enhanced_claude_service import EnhancedClaudeService
from conftest import TEST_FILES, TEST_APP_NAME, TEST_DESCRIPTION
from utils import create_mock_llm_response, create_mock_modification_response


@pytest.mark.unit
class TestEnhancedClaudeService:
    """Test suite for EnhancedClaudeService"""
    
    @pytest.fixture
    def service(self, mock_env_vars):
        """Create service instance with mocked dependencies"""
        with patch('enhanced_claude_service.Anthropic'), \
             patch('enhanced_claude_service.OpenAI'), \
             patch('enhanced_claude_service.httpx.AsyncClient'), \
             patch('enhanced_claude_service.RAGKnowledgeBase'), \
             patch('enhanced_claude_service.IntelligentLLMRouter'), \
             patch('enhanced_claude_service.ModificationHandler'), \
             patch('enhanced_claude_service.UIEnhancementHandler'):
            
            service = EnhancedClaudeService()
            # Mock the router to return predictable results
            service.router.analyze_request = Mock(return_value="simple_ui")
            return service
    
    @pytest.mark.asyncio
    async def test_generate_ios_app_simple(self, service, mock_llm_response):
        """Test simple app generation"""
        # Mock Claude response
        service.claude_client.messages.create = AsyncMock(
            return_value=Mock(content=[Mock(text=json.dumps(mock_llm_response))])
        )
        
        result = await service.generate_ios_app(TEST_APP_NAME, TEST_DESCRIPTION)
        
        assert result["app_name"] == TEST_APP_NAME
        assert "files" in result
        assert len(result["files"]) > 0
        assert service.claude_client.messages.create.called
    
    @pytest.mark.asyncio
    async def test_generate_ios_app_with_retry(self, service):
        """Test app generation with retry on failure"""
        # First call fails, second succeeds
        service.claude_client.messages.create = AsyncMock(
            side_effect=[
                Exception("Connection error"),
                Mock(content=[Mock(text=create_mock_llm_response())])
            ]
        )
        
        result = await service.generate_ios_app(TEST_APP_NAME, TEST_DESCRIPTION)
        
        assert result["app_name"] == TEST_APP_NAME
        assert service.claude_client.messages.create.call_count == 2
    
    @pytest.mark.asyncio
    async def test_generate_ios_app_max_retries(self, service):
        """Test app generation fails after max retries"""
        service.claude_client.messages.create = AsyncMock(
            side_effect=Exception("Connection error")
        )
        
        result = await service.generate_ios_app(
            TEST_APP_NAME, 
            TEST_DESCRIPTION,
            retry_count=3  # Already at max
        )
        
        assert result is None
        assert service.claude_client.messages.create.call_count == 1
    
    @pytest.mark.asyncio
    async def test_routing_to_gpt4(self, service):
        """Test routing to GPT-4 for complex apps"""
        service.router.analyze_request = Mock(return_value="complex_architecture")
        service.openai_client.chat.completions.create = AsyncMock(
            return_value=Mock(choices=[Mock(message=Mock(content=create_mock_llm_response()))])
        )
        
        result = await service.generate_ios_app(TEST_APP_NAME, "Complex app with architecture")
        
        assert result["app_name"] == TEST_APP_NAME
        assert service.openai_client.chat.completions.create.called
        assert not service.claude_client.messages.create.called
    
    @pytest.mark.asyncio
    async def test_routing_to_xai(self, service):
        """Test routing to xAI for UI-heavy apps"""
        service.router.analyze_request = Mock(return_value="ui_heavy")
        
        # Mock xAI client response
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={
            "choices": [{
                "message": {"content": create_mock_llm_response()}
            }]
        })
        mock_response.raise_for_status = AsyncMock()
        
        service.xai_client.post = AsyncMock(return_value=mock_response)
        
        result = await service.generate_ios_app(TEST_APP_NAME, "Beautiful UI app")
        
        assert result["app_name"] == TEST_APP_NAME
        assert service.xai_client.post.called
    
    @pytest.mark.asyncio
    async def test_apply_modification_simple(self, service):
        """Test simple modification application"""
        service.modification_handler.apply_modification = AsyncMock(
            return_value={
                "modified_files": TEST_FILES,
                "explanation": "Modified successfully"
            }
        )
        
        result = await service.apply_modification(
            "Add a button",
            TEST_FILES,
            project_id="test_123"
        )
        
        assert "modified_files" in result
        assert result["explanation"] == "Modified successfully"
        assert service.modification_handler.apply_modification.called
    
    @pytest.mark.asyncio
    async def test_apply_modification_with_issue_detection(self, service):
        """Test modification with issue detection"""
        # Mock issue detection
        service.modification_handler.detect_issue_type = Mock(
            return_value=("ssl_error", {"domain": "api.example.com"})
        )
        service.modification_handler.apply_ssl_fix = AsyncMock(
            return_value={"fix_applied": True}
        )
        
        result = await service.apply_modification(
            "App crashes with SSL error",
            TEST_FILES,
            project_id="test_123"
        )
        
        assert service.modification_handler.detect_issue_type.called
        assert service.modification_handler.apply_ssl_fix.called
    
    @pytest.mark.asyncio
    async def test_json_parsing_fallback(self, service):
        """Test JSON parsing with fallback on error"""
        # Invalid JSON response
        service.claude_client.messages.create = AsyncMock(
            return_value=Mock(content=[Mock(text="Invalid JSON {{")])
        )
        
        # Fallback should use modification handler
        service.modification_handler.apply_modification = AsyncMock(
            return_value={"modified_files": TEST_FILES}
        )
        
        result = await service.apply_modification(
            "Add feature",
            TEST_FILES,
            project_id="test_123"
        )
        
        assert service.modification_handler.apply_modification.called
    
    @pytest.mark.asyncio
    async def test_ui_enhancement_application(self, service):
        """Test UI enhancement handler integration"""
        # Mock UI enhancement
        service.ui_handler.enhance_ui_code = Mock(
            return_value="enhanced code"
        )
        
        service.claude_client.messages.create = AsyncMock(
            return_value=Mock(content=[Mock(text=json.dumps({
                "files": [{
                    "path": "ContentView.swift",
                    "content": "struct ContentView: View { }"
                }]
            }))])
        )
        
        result = await service.generate_ios_app(TEST_APP_NAME, TEST_DESCRIPTION)
        
        # UI handler should be called for SwiftUI files
        assert service.ui_handler.enhance_ui_code.called
    
    @pytest.mark.asyncio
    async def test_rag_integration(self, service):
        """Test RAG knowledge base integration"""
        # Mock RAG search
        service.rag.search = AsyncMock(
            return_value=["Use @Observable for iOS 17+"]
        )
        
        service.claude_client.messages.create = AsyncMock(
            return_value=Mock(content=[Mock(text=create_mock_llm_response())])
        )
        
        result = await service.generate_ios_app(
            TEST_APP_NAME, 
            TEST_DESCRIPTION,
            use_ios17_features=True
        )
        
        assert service.rag.search.called
        # Verify RAG context was included in prompt
        call_args = service.claude_client.messages.create.call_args
        assert "@Observable" in str(call_args)
    
    @pytest.mark.asyncio 
    async def test_modification_history_tracking(self, service):
        """Test modification history is properly tracked"""
        modification_history = [
            {"type": "ui_change", "description": "Added dark mode"}
        ]
        
        service.modification_handler.apply_modification = AsyncMock(
            return_value={"modified_files": TEST_FILES}
        )
        
        result = await service.apply_modification(
            "Add button",
            TEST_FILES,
            modification_history=modification_history
        )
        
        # Verify history was passed to handler
        call_args = service.modification_handler.apply_modification.call_args
        assert call_args[1]["modification_history"] == modification_history
    
    @pytest.mark.asyncio
    async def test_error_recovery_integration(self, service):
        """Test error recovery system integration"""
        # Simulate build error that needs recovery
        error_context = {
            "errors": [{
                "type": "type_not_found",
                "message": "Cannot find 'CustomView' in scope"
            }]
        }
        
        service.modification_handler.apply_modification = AsyncMock(
            return_value={
                "modified_files": TEST_FILES,
                "needs_recovery": True,
                "error_context": error_context
            }
        )
        
        result = await service.apply_modification(
            "Fix errors",
            TEST_FILES,
            error_context=error_context
        )
        
        assert "error_context" in result
        assert result["needs_recovery"] is True
    
    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self, service):
        """Test handling multiple concurrent requests"""
        service.claude_client.messages.create = AsyncMock(
            return_value=Mock(content=[Mock(text=create_mock_llm_response())])
        )
        
        # Create multiple concurrent requests
        tasks = [
            service.generate_ios_app(f"App{i}", f"Description {i}")
            for i in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        assert all(r is not None for r in results)
        assert service.claude_client.messages.create.call_count == 5
    
    def test_parse_llm_response_valid_json(self, service):
        """Test parsing valid JSON response"""
        response = json.dumps({
            "files": TEST_FILES,
            "app_name": TEST_APP_NAME
        })
        
        result = service._parse_llm_response(response, "generate")
        
        assert result["files"] == TEST_FILES
        assert result["app_name"] == TEST_APP_NAME
    
    def test_parse_llm_response_with_code_blocks(self, service):
        """Test parsing JSON from code blocks"""
        response = """
        Here's the app:
        ```json
        {"files": [], "app_name": "Test"}
        ```
        """
        
        result = service._parse_llm_response(response, "generate")
        
        assert result["app_name"] == "Test"
    
    def test_parse_llm_response_invalid_json(self, service):
        """Test parsing invalid JSON returns None"""
        response = "Invalid JSON {{"
        
        result = service._parse_llm_response(response, "generate")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, service):
        """Test proper timeout handling"""
        # Mock a timeout
        async def slow_response():
            await asyncio.sleep(35)  # Longer than 30s timeout
            return Mock(content=[Mock(text="{}")])
        
        service.claude_client.messages.create = AsyncMock(side_effect=slow_response)
        
        with pytest.raises(asyncio.TimeoutError):
            # This should timeout
            await asyncio.wait_for(
                service.generate_ios_app(TEST_APP_NAME, TEST_DESCRIPTION),
                timeout=1.0
            )