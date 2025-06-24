"""
Unit tests for modification_handler.py
Tests the modification system including issue detection, fixes, and special handlers
"""
import pytest
import json
from unittest.mock import Mock, patch, AsyncMock, MagicMock, call
from typing import Dict, List
import os

from modification_handler import ModificationHandler
from conftest import TEST_FILES


@pytest.mark.unit
class TestModificationHandler:
    """Test suite for ModificationHandler"""
    
    @pytest.fixture
    def handler(self):
        """Create handler instance"""
        with patch('modification_handler.OpenAI'), \
             patch('modification_handler.Anthropic'), \
             patch('modification_handler.httpx.AsyncClient'), \
             patch('modification_handler.IntelligentLLMRouter'), \
             patch('modification_handler.SSLErrorHandler'), \
             patch('modification_handler.IOSSpecificFixes'), \
             patch('modification_handler.RobustSSLHandler'):
            
            handler = ModificationHandler()
            # Mock router to return predictable results
            handler.router.analyze_request = Mock(return_value="ui_change")
            return handler
    
    def test_detect_issue_type_ssl_error(self, handler):
        """Test SSL error detection"""
        modification = "App crashes with 'App Transport Security has blocked a cleartext HTTP'"
        
        issue_type, details = handler.detect_issue_type(modification)
        
        assert issue_type == "ssl_error"
        assert details is not None
    
    def test_detect_issue_type_dark_theme(self, handler):
        """Test dark theme request detection"""
        modification = "Add dark theme toggle to the app"
        
        issue_type, details = handler.detect_issue_type(modification)
        
        assert issue_type == "dark_theme"
        assert details is not None
    
    def test_detect_issue_type_general(self, handler):
        """Test general modification detection"""
        modification = "Add a new button to the screen"
        
        issue_type, details = handler.detect_issue_type(modification)
        
        assert issue_type is None
        assert details is None
    
    @pytest.mark.asyncio
    async def test_apply_modification_basic(self, handler):
        """Test basic modification application"""
        handler.openai_client.chat.completions.create = AsyncMock(
            return_value=Mock(choices=[Mock(message=Mock(content=json.dumps({
                "modified_files": TEST_FILES,
                "explanation": "Added button"
            })))])
        )
        
        result = await handler.apply_modification(
            "Add a button",
            TEST_FILES
        )
        
        assert "modified_files" in result
        assert result["explanation"] == "Added button"
        assert handler.openai_client.chat.completions.create.called
    
    @pytest.mark.asyncio
    async def test_apply_modification_with_ssl_fix(self, handler):
        """Test modification with SSL fix"""
        handler.ssl_handler.analyze_error = Mock(return_value={
            "is_ssl_error": True,
            "domain": "api.example.com",
            "error_type": "cleartext_http"
        })
        
        handler.ssl_handler.generate_fix_code = Mock(return_value={
            "type": "info_plist",
            "code": "<key>NSAppTransportSecurity</key>"
        })
        
        result = await handler.apply_ssl_fix(
            TEST_FILES,
            "SSL error occurred",
            {"domain": "api.example.com"}
        )
        
        assert "fix_applied" in result
        assert handler.ssl_handler.analyze_error.called
        assert handler.ssl_handler.generate_fix_code.called
    
    @pytest.mark.asyncio
    async def test_apply_modification_dark_theme(self, handler):
        """Test dark theme implementation"""
        result = await handler._implement_dark_theme(TEST_FILES)
        
        assert "modified_files" in result
        # Check that ContentView was modified
        content_view = next((f for f in result["modified_files"] 
                           if f["path"] == "Sources/ContentView.swift"), None)
        assert content_view is not None
        assert "@AppStorage" in content_view["content"]
        assert "isDarkMode" in content_view["content"]
    
    def test_fix_count_bug(self, handler):
        """Test count bug fix"""
        files = [{
            "path": "Sources/ContentView.swift",
            "content": 'let newBeverage = BeverageItem(name: name, count: 0, emoji: emoji)'
        }]
        
        result = handler._fix_count_bug(files)
        
        assert result["fix_applied"] is True
        modified_file = result["modified_files"][0]
        assert "count: 1" in modified_file["content"]
        assert "count: 0" not in modified_file["content"]
    
    def test_track_repeated_issues(self, handler):
        """Test repeated issue tracking"""
        # First occurrence
        handler._track_issue("ssl_error", "api.example.com")
        assert handler.issue_history["ssl_error"]["api.example.com"]["count"] == 1
        
        # Second occurrence
        handler._track_issue("ssl_error", "api.example.com")
        assert handler.issue_history["ssl_error"]["api.example.com"]["count"] == 2
    
    def test_get_alternative_fix_first_attempt(self, handler):
        """Test getting fix for first attempt"""
        fix = handler._get_alternative_fix("ssl_error", 1)
        
        assert "basic" in fix.lower() or "standard" in fix.lower()
    
    def test_get_alternative_fix_multiple_attempts(self, handler):
        """Test getting alternative fixes for multiple attempts"""
        fix1 = handler._get_alternative_fix("ssl_error", 1)
        fix2 = handler._get_alternative_fix("ssl_error", 2)
        fix3 = handler._get_alternative_fix("ssl_error", 3)
        
        # Fixes should be different
        assert fix1 != fix2
        assert fix2 != fix3
    
    @pytest.mark.asyncio
    async def test_json_parsing_error_handling(self, handler):
        """Test handling of JSON parsing errors"""
        # Return invalid JSON
        handler.openai_client.chat.completions.create = AsyncMock(
            return_value=Mock(choices=[Mock(message=Mock(content="Invalid JSON {{"))])
        )
        
        # Should fall back to returning original files
        result = await handler.apply_modification(
            "Add feature",
            TEST_FILES
        )
        
        assert "modified_files" in result
        assert result["modified_files"] == TEST_FILES
    
    @pytest.mark.asyncio
    async def test_llm_routing(self, handler):
        """Test proper LLM routing based on modification type"""
        # Test UI modification routes to OpenAI
        handler.router.analyze_request = Mock(return_value="ui_change")
        handler.openai_client.chat.completions.create = AsyncMock(
            return_value=Mock(choices=[Mock(message=Mock(content=json.dumps({
                "modified_files": TEST_FILES
            })))])
        )
        
        await handler.apply_modification("Change UI", TEST_FILES)
        assert handler.openai_client.chat.completions.create.called
        
        # Test complex modification routes to Claude
        handler.router.analyze_request = Mock(return_value="complex_modification")
        handler.claude_client.messages.create = AsyncMock(
            return_value=Mock(content=[Mock(text=json.dumps({
                "modified_files": TEST_FILES
            }))])
        )
        
        await handler.apply_modification("Complex change", TEST_FILES)
        assert handler.claude_client.messages.create.called
    
    @pytest.mark.asyncio
    async def test_comprehensive_ssl_fix(self, handler):
        """Test comprehensive SSL fix with robust handler"""
        files = [
            {"path": "Info.plist", "content": "<dict></dict>"},
            {"path": "Sources/NetworkManager.swift", "content": "URLSession.shared"}
        ]
        
        handler.robust_ssl_handler.apply_comprehensive_fix = Mock(
            return_value={
                "files": files,
                "fixes_applied": ["info_plist", "url_session"]
            }
        )
        
        result = await handler.apply_ssl_fix(
            files,
            "SSL error",
            {"comprehensive": True}
        )
        
        assert handler.robust_ssl_handler.apply_comprehensive_fix.called
        assert "fixes_applied" in result
    
    def test_implement_dark_theme_adds_all_components(self, handler):
        """Test dark theme implementation adds all necessary components"""
        files = [
            {
                "path": "Sources/App.swift",
                "content": '@main\nstruct MyApp: App {\n    var body: some Scene {\n        WindowGroup {\n            ContentView()\n        }\n    }\n}'
            },
            {
                "path": "Sources/ContentView.swift",
                "content": 'struct ContentView: View {\n    var body: some View {\n        Text("Hello")\n    }\n}'
            }
        ]
        
        result = handler._implement_dark_theme(files)
        
        # Check App.swift has preferredColorScheme
        app_file = next(f for f in result["modified_files"] if f["path"] == "Sources/App.swift")
        assert ".preferredColorScheme" in app_file["content"]
        assert "isDarkMode" in app_file["content"]
        
        # Check ContentView has toggle
        content_file = next(f for f in result["modified_files"] if f["path"] == "Sources/ContentView.swift")
        assert "@AppStorage" in content_file["content"]
        assert "Toggle" in content_file["content"]
        assert "Dark Mode" in content_file["content"]
    
    @pytest.mark.asyncio
    async def test_modification_with_history(self, handler):
        """Test modification considering previous history"""
        modification_history = [
            {"type": "ui_change", "description": "Added button"},
            {"type": "dark_theme", "description": "Added dark mode"}
        ]
        
        handler.openai_client.chat.completions.create = AsyncMock(
            return_value=Mock(choices=[Mock(message=Mock(content=json.dumps({
                "modified_files": TEST_FILES
            })))])
        )
        
        await handler.apply_modification(
            "Change button color",
            TEST_FILES,
            modification_history=modification_history
        )
        
        # Verify history was included in prompt
        call_args = handler.openai_client.chat.completions.create.call_args
        prompt = str(call_args)
        assert "Added button" in prompt
        assert "Added dark mode" in prompt
    
    def test_specific_bug_fixes(self, handler):
        """Test specific bug fix implementations"""
        # Test each specific fix method exists and works
        assert hasattr(handler, '_fix_count_bug')
        assert hasattr(handler, '_implement_dark_theme')
        
        # Test they return expected structure
        result = handler._fix_count_bug([{
            "path": "test.swift",
            "content": "count: 0"
        }])
        assert "fix_applied" in result
        assert "modified_files" in result