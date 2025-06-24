"""
Unit tests for api_error_handler.py
Tests API error detection and fixing capabilities
"""
import pytest
from api_error_handler import APIErrorHandler


@pytest.mark.unit
class TestAPIErrorHandler:
    """Test suite for APIErrorHandler"""
    
    @pytest.fixture
    def handler(self):
        """Create handler instance"""
        return APIErrorHandler()
    
    def test_detect_api_issue_positive(self, handler):
        """Test detection of API-related issues"""
        test_cases = [
            ("Failed to load quote. Please try again!", True),
            ("App crashes with SSL certificate error", True),
            ("Network timeout when fetching data", True),
            ("Cannot connect to api.example.com", True),
            ("App Transport Security blocked the request", True),
            ("No internet connection available", True),
            ("Server returned error 500", True)
        ]
        
        for error_msg, expected in test_cases:
            is_api, analysis = handler.detect_api_issue(error_msg)
            assert is_api == expected
            if expected:
                assert analysis['is_api_issue'] is True
                assert 'error_type' in analysis
    
    def test_detect_api_issue_negative(self, handler):
        """Test non-API issues are not detected"""
        test_cases = [
            "Button color should be blue",
            "Add dark mode toggle",
            "Change font size",
            "App crashes when clicking button"
        ]
        
        for error_msg in test_cases:
            is_api, _ = handler.detect_api_issue(error_msg)
            assert is_api is False
    
    def test_categorize_error_types(self, handler):
        """Test error categorization"""
        test_cases = [
            ("SSL certificate is invalid", "ssl_error"),
            ("Request timed out", "timeout_error"),
            ("No internet connection", "connectivity_error"),
            ("Failed to load data", "fetch_error"),
            ("Server error 500", "server_error"),
            ("Unknown API problem", "generic_api_error")
        ]
        
        for error_msg, expected_type in test_cases:
            _, analysis = handler.detect_api_issue(error_msg)
            assert analysis['error_type'] == expected_type
    
    def test_detect_apis_in_use(self, handler):
        """Test API detection from error messages"""
        error = "Failed to fetch from api.quotable.io"
        _, analysis = handler.detect_api_issue(error)
        
        assert 'api.quotable.io' in analysis['detected_apis']
    
    def test_add_retry_logic(self, handler):
        """Test retry logic addition"""
        original_code = '''
class QuoteService {
    func fetchQuote() async throws -> Quote {
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode(Quote.self, from: data)
    }
}'''
        
        modified = handler._add_retry_logic(original_code)
        
        assert 'fetchWithRetry' in modified
        assert 'maxRetries' in modified
        assert 'Task.sleep' in modified
    
    def test_improve_error_handling(self, handler):
        """Test error handling improvements"""
        original_code = '''
} catch {
    self.errorMessage = "Failed to load quote. Please try again."
}'''
        
        modified = handler._improve_error_handling(original_code)
        
        assert 'URLError' in modified
        assert 'notConnectedToInternet' in modified
        assert 'timedOut' in modified
        assert 'print("API Error:' in modified
    
    def test_generate_api_fix_ssl(self, handler):
        """Test SSL error fix generation"""
        files = [{'path': 'Service.swift', 'content': 'API code'}]
        analysis = {'error_type': 'ssl_error'}
        
        result = handler.generate_api_fix(files, analysis)
        
        assert result['fix_applied'] is True
        assert result['fix_type'] == 'ssl_ats'
        assert 'ATS exceptions' in result['changes'][0]
    
    def test_generate_api_fix_timeout(self, handler):
        """Test timeout error fix generation"""
        files = [{'path': 'QuoteService.swift', 'content': 'async func fetch()'}]
        analysis = {'error_type': 'timeout_error'}
        
        result = handler.generate_api_fix(files, analysis)
        
        assert result['fix_applied'] is True
        assert result['fix_type'] == 'timeout_retry'
        assert any('retry logic' in change for change in result['changes'])
    
    def test_suggest_improvements(self, handler):
        """Test API improvement suggestions"""
        files = [{
            'path': 'APIService.swift',
            'content': '''
class APIService {
    func fetch() async throws {
        let (data, _) = try await URLSession.shared.data(from: url)
    }
}'''
        }]
        
        suggestions = handler.suggest_api_improvements(files)
        
        assert any('timeout' in s for s in suggestions)
        assert any('retry' in s for s in suggestions)