"""Unit tests for Sentiment Analysis."""
import unittest
import asyncio
import sys
import os
from unittest.mock import AsyncMock, patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.sentiment_analysis import SentimentAnalyzer

class TestSentimentAnalyzer(unittest.TestCase):
    """Test the sentiment analyzer."""
    
    def run_async(self, coro):
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(coro)

    @patch('core.sentiment_analysis.LLMReasoningEngine')
    def test_bullish_sentiment(self, mock_engine_class):
        """Test parsing a bullish response."""
        # Mock the instance creation
        mock_instance = MagicMock()
        mock_engine_class.return_value = mock_instance
        
        # Mock the LLM response content
        mock_response = MagicMock()
        mock_response.content = '{"score": 0.9, "summary": "Very bullish news."}'
        mock_instance.client = AsyncMock()
        mock_instance.client.ainvoke.return_value = mock_response
        
        analyzer = SentimentAnalyzer(api_key="dummy")
        # Inject the mocked client instance
        analyzer.engine = mock_instance
        
        result = self.run_async(analyzer.analyze(
            asset="BTC",
            headlines=["BTC breaks all time high!", "ETF inflows surge."]
        ))
        
        self.assertEqual(result["score"], 0.9)
        self.assertIn("bullish", result["summary"].lower())
        print("✅ Bullish sentiment parsed correctly")

    @patch('core.sentiment_analysis.LLMReasoningEngine')
    def test_bearish_sentiment(self, mock_engine_class):
        """Test parsing a bearish response."""
        mock_instance = MagicMock()
        mock_engine_class.return_value = mock_instance
        
        mock_response = MagicMock()
        mock_response.content = '{"score": -0.5, "summary": "Bearish due to exchange hack."}'
        mock_instance.client = AsyncMock()
        mock_instance.client.ainvoke.return_value = mock_response
        
        analyzer = SentimentAnalyzer(api_key="dummy")
        analyzer.engine = mock_instance
        
        result = self.run_async(analyzer.analyze(
            asset="ETH",
            headlines=["Major exchange hacked", "Regulators crack down on ETH."]
        ))
        
        self.assertEqual(result["score"], -0.5)
        self.assertIn("bearish", result["summary"].lower())
        print("✅ Bearish sentiment parsed correctly")

    def test_no_headlines(self):
        """Test handling of empty input."""
        analyzer = SentimentAnalyzer(api_key="dummy")
        result = self.run_async(analyzer.analyze("BTC", []))
        
        self.assertEqual(result["score"], 0.0)
        print("✅ Empty headlines handled correctly")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSentimentAnalyzer)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
