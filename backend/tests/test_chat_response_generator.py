"""
Unit tests for chat_response_generator.py
Tests the contextual response generation system
"""
import pytest
from chat_response_generator import ChatResponseGenerator


@pytest.mark.unit
class TestChatResponseGenerator:
    """Test suite for ChatResponseGenerator"""
    
    @pytest.fixture
    def generator(self):
        """Create generator instance"""
        return ChatResponseGenerator()
    
    def test_modification_response_dark_mode(self, generator):
        """Test dark mode modification response"""
        response = generator.generate_modification_response(
            "Add dark mode toggle", 
            "MyApp"
        )
        
        assert "dark mode" in response.lower() or "dark theme" in response.lower()
        assert "MyApp" in response
        assert "Perfect!" not in response  # Should not use the old response
        assert "progress" in response.lower()
    
    def test_modification_response_button(self, generator):
        """Test button modification response"""
        response = generator.generate_modification_response(
            "Add a blue button to the main screen",
            "TodoApp"
        )
        
        assert "button" in response.lower()
        assert "TodoApp" in response
        assert any(word in response.lower() for word in ["add", "implement", "include"])
    
    def test_modification_response_fix_issue(self, generator):
        """Test fix/bug response"""
        response = generator.generate_modification_response(
            "Fix the crash when loading data",
            "DataApp"
        )
        
        assert any(word in response.lower() for word in ["fix", "resolve", "investigate"])
        assert "DataApp" in response
        assert "crash" in response.lower() or "issue" in response.lower()
    
    def test_modification_response_ssl_error(self, generator):
        """Test SSL error response"""
        response = generator.generate_modification_response(
            "App crashes with SSL certificate error",
            "NetworkApp"
        )
        
        assert any(word in response.lower() for word in ["ssl", "security", "certificate"])
        assert "NetworkApp" in response
    
    def test_creation_response_game(self, generator):
        """Test game app creation response"""
        response = generator.generate_creation_response(
            "Create a puzzle game app",
            "PuzzleGame"
        )
        
        assert "🎮" in response
        assert "PuzzleGame" in response
        assert "progress" in response.lower()
    
    def test_creation_response_food(self, generator):
        """Test food app creation response"""
        response = generator.generate_creation_response(
            "Build a food delivery app",
            "FoodDelivery"
        )
        
        assert "🍕" in response
        assert "FoodDelivery" in response
    
    def test_creation_response_generic(self, generator):
        """Test generic app creation response"""
        response = generator.generate_creation_response(
            "Create a simple utility app",
            "UtilityApp"
        )
        
        assert any(emoji in response for emoji in ["✨", "🚀", "💡", "⭐"])
        assert "UtilityApp" in response
    
    def test_response_variation(self, generator):
        """Test that responses vary and don't repeat"""
        responses = []
        
        # Generate multiple responses for the same type
        for _ in range(5):
            response = generator.generate_modification_response(
                "Add a button",
                "TestApp"
            )
            responses.append(response)
        
        # Check that we have some variation
        unique_responses = set(responses)
        assert len(unique_responses) > 1  # Should have at least 2 different responses
    
    def test_feature_extraction(self, generator):
        """Test feature extraction from messages"""
        test_cases = [
            ("Add a red button", "button"),
            ("Change the color scheme", "color"),
            ("Update the UI", "interface"),
            ("Fix the bug", "issue"),
        ]
        
        for message, expected_keyword in test_cases:
            feature = generator._extract_feature(message)
            assert expected_keyword in feature.lower()
    
    def test_error_response_generation(self, generator):
        """Test error-specific responses"""
        response = generator.generate_error_response("ssl", "MyApp")
        assert "SSL" in response or "certificate" in response
        assert "MyApp" in response
        
        response = generator.generate_error_response("build", "MyApp")
        assert "build" in response.lower()
        
        response = generator.generate_error_response("syntax", "MyApp")
        assert "syntax" in response.lower()
    
    def test_response_history_tracking(self, generator):
        """Test that recent responses are tracked"""
        # Generate a response
        first_response = generator.generate_modification_response(
            "Add feature",
            "App"
        )
        
        # Check it's in history
        assert len(generator.recent_responses) > 0
        
        # Generate many more to test history limit
        for i in range(15):
            generator.generate_modification_response(
                f"Add feature {i}",
                "App"
            )
        
        # History should be capped at max_history
        assert len(generator.recent_responses) <= generator.max_history
    
    def test_contextual_details_extraction(self, generator):
        """Test extraction of specific details from messages"""
        # Button color extraction
        details = generator._extract_button_details("Add a blue button")
        assert "blue" in details
        
        # Color scheme extraction
        details = generator._extract_color_details("Change colors to dark theme")
        assert "dark" in details
        
        # Issue type extraction
        details = generator._extract_issue_type("App crashes on startup")
        assert "crash" in details