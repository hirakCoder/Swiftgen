"""
Integration test for SSL fix functionality
Tests the full flow of detecting and fixing SSL errors in iOS apps
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modification_handler import ModificationHandler
from robust_ssl_handler import RobustSSLHandler


@pytest.mark.integration
class TestSSLFixIntegration:
    """Test SSL fix integration"""
    
    @pytest.fixture
    def modification_handler(self):
        """Create modification handler instance"""
        return ModificationHandler()
    
    @pytest.fixture
    def robust_ssl_handler(self):
        """Create robust SSL handler instance"""
        return RobustSSLHandler()
    
    @pytest.fixture
    def sample_files(self):
        """Sample iOS project files"""
        return [
            {
                "path": "Info.plist",
                "content": """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>QuoteApp</string>
    <key>CFBundleIdentifier</key>
    <string>com.example.quoteapp</string>
</dict>
</plist>"""
            },
            {
                "path": "Sources/ViewModels/QuotesViewModel.swift",
                "content": """import SwiftUI
import Combine

@MainActor
class QuotesViewModel: ObservableObject {
    @Published var currentQuote: QuoteModel = QuoteModel.sample
    @Published var isLoading: Bool = false
    @Published var errorMessage: String = ""
    
    private let apiURL = "https://api.quotable.io/random"
    
    func fetchNewQuote() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            guard let url = URL(string: apiURL) else {
                errorMessage = "Invalid URL"
                return
            }
            
            let (data, _) = try await URLSession.shared.data(from: url)
            let quote = try JSONDecoder().decode(QuoteModel.self, from: data)
            currentQuote = quote
        } catch {
            errorMessage = "Failed to fetch quote: \\(error.localizedDescription)"
        }
    }
}"""
            }
        ]
    
    def test_detect_ssl_issue(self, modification_handler):
        """Test SSL issue detection"""
        # Test various SSL error messages
        test_cases = [
            "Failed to load quote. SSL certificate error",
            "App crashes with transport security error",
            "Cannot connect to api.quotable.io - SSL error",
            "Failed to fetch data from external API"
        ]
        
        for request in test_cases:
            issue_type, details = modification_handler.detect_issue_type(request)
            assert issue_type in ["ssl_error", "api_error"], f"Failed to detect SSL issue in: {request}"
    
    def test_apply_ssl_fix_to_info_plist(self, modification_handler, sample_files):
        """Test applying SSL fix to Info.plist"""
        # Apply SSL fix
        result = modification_handler.apply_ssl_fix(
            sample_files,
            "add_ats_exception",
            domain="api.quotable.io"
        )
        
        # Check results
        assert len(result["files_modified"]) > 0
        assert "Info.plist" in result["files_modified"]
        
        # Verify Info.plist was updated
        info_plist = next(f for f in result["files"] if f["path"] == "Info.plist")
        assert "NSAppTransportSecurity" in info_plist["content"]
        assert "api.quotable.io" in info_plist["content"]
        assert "NSTemporaryExceptionAllowsInsecureHTTPLoads" in info_plist["content"]
    
    def test_comprehensive_ssl_fix(self, robust_ssl_handler, sample_files):
        """Test comprehensive SSL fix"""
        # Apply comprehensive fix
        result = robust_ssl_handler.apply_comprehensive_ssl_fix(
            sample_files,
            "api.quotable.io"
        )
        
        # Check results
        assert len(result["files_modified"]) >= 3  # Info.plist + NetworkConfiguration + APIClient
        assert result["ssl_fixes_applied"]["info_plist"]
        assert result["ssl_fixes_applied"]["network_configuration"]
        assert result["ssl_fixes_applied"]["api_client_ssl"]
        
        # Verify NetworkConfiguration was created
        network_config = next(
            (f for f in result["files"] if "NetworkConfiguration" in f["path"]),
            None
        )
        assert network_config is not None
        assert "SSLPinningDelegate" in network_config["content"]
        assert "DevelopmentSSLDelegate" in network_config["content"]
    
    def test_ssl_fix_idempotency(self, modification_handler, sample_files):
        """Test that SSL fix doesn't duplicate entries"""
        # Apply fix twice
        result1 = modification_handler.apply_ssl_fix(
            sample_files,
            "add_ats_exception",
            domain="api.quotable.io"
        )
        
        result2 = modification_handler.apply_ssl_fix(
            result1["files"],
            "add_ats_exception",
            domain="api.quotable.io"
        )
        
        # Second application should not modify Info.plist again
        info_plist = next(f for f in result2["files"] if f["path"] == "Info.plist")
        # Count occurrences of NSAppTransportSecurity
        count = info_plist["content"].count("NSAppTransportSecurity")
        assert count == 1, "NSAppTransportSecurity should appear only once"
    
    def test_missing_info_plist_creation(self, modification_handler):
        """Test creating Info.plist when it doesn't exist"""
        files_without_plist = [
            {
                "path": "Sources/App.swift",
                "content": "import SwiftUI\n@main struct App {}"
            }
        ]
        
        result = modification_handler.apply_ssl_fix(
            files_without_plist,
            "add_ats_exception",
            domain="api.example.com"
        )
        
        # Check that Info.plist was created
        assert "Info.plist" in result["files_modified"]
        info_plist = next(
            (f for f in result["files"] if f["path"] == "Info.plist"),
            None
        )
        assert info_plist is not None
        assert "NSAppTransportSecurity" in info_plist["content"]
        assert "api.example.com" in info_plist["content"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])