"""
Unit tests for AI signal parsing
"""
import pytest
from ai.groq_client import GroqClient

@pytest.fixture
def groq_client():
    """Create a GroqClient instance for testing"""
    return GroqClient(api_key="test_key")

class TestSignalParsing:
    """Test signal parsing from AI responses"""
    
    def test_parse_pipe_format(self, groq_client):
        """Test parsing standard pipe-delimited format"""
        content = "BUY|85|RSI oversold with bullish divergence"
        
        result = groq_client._parse_response(content)
        
        assert result['signal'] == 'BUY'
        assert result['confidence'] == 85
        assert 'RSI oversold' in result['reasoning']
    
    def test_parse_strong_buy(self, groq_client):
        """Test parsing STRONG BUY signal"""
        content = "STRONG BUY|92|Multiple bullish indicators aligned"
        
        result = groq_client._parse_response(content)
        
        assert result['signal'] == 'STRONG BUY'
        assert result['confidence'] == 92
    
    def test_parse_natural_language(self, groq_client):
        """Test parsing natural language response"""
        content = "Based on the analysis, I recommend a BUY position with 78% confidence due to oversold RSI."
        
        result = groq_client._parse_response(content)
        
        assert result['signal'] == 'BUY'
        assert result['confidence'] == 78
    
    def test_parse_hold_signal(self, groq_client):
        """Test parsing HOLD signal"""
        content = "HOLD|60|Market conditions unclear"
        
        result = groq_client._parse_response(content)
        
        assert result['signal'] == 'HOLD'
        assert result['confidence'] == 60
    
    def test_parse_sell_signal(self, groq_client):
        """Test parsing SELL signal"""
        content = "SELL|75|Overbought conditions with bearish divergence"
        
        result = groq_client._parse_response(content)
        
        assert result['signal'] == 'SELL'
        assert result['confidence'] == 75
    
    def test_parse_invalid_format(self, groq_client):
        """Test parsing invalid format returns HOLD"""
        content = "This is just random text without any signal"
        
        result = groq_client._parse_response(content)
        
        assert result['signal'] == 'HOLD'
        assert result['confidence'] == 50  # Default
    
    def test_parse_case_insensitive(self, groq_client):
        """Test that parsing is case-insensitive"""
        content = "buy|80|test"
        
        result = groq_client._parse_response(content)
        
        assert result['signal'] == 'BUY'
