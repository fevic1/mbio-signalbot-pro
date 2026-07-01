"""Unit tests for LLM Trade Reasoning Engine."""
import unittest
import asyncio
import sys
import os
from unittest.mock import AsyncMock, patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.llm_reasoning import LLMReasoningEngine, FALLBACK_REASONING

class TestLLMReasoningEngine(unittest.TestCase):
    """Test the LLM reasoning engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize with dummy key (won't actually connect)
        self.engine = LLMReasoningEngine(api_key="dummy_key", model="test-model")
        self.market_data = {'rsi': 65, 'adx': 25, 'volume_ratio': 1.5}
        
    def run_async(self, coro):
        """Helper to run async functions in tests."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    def test_skip_hold_signal(self):
        """Test that HOLD signals skip LLM analysis to save tokens."""
        result = self.run_async(self.engine.analyze_trade(
            'BTC', 'HOLD', 0, self.market_data
        ))
        self.assertEqual(result, FALLBACK_REASONING)
        print("✅ HOLD signals correctly skip LLM analysis")

    def test_skip_low_confidence(self):
        """Test that low confidence signals skip LLM analysis."""
        result = self.run_async(self.engine.analyze_trade(
            'BTC', 'BUY', 40, self.market_data
        ))
        self.assertEqual(result, FALLBACK_REASONING)
        print("✅ Low confidence signals correctly skip LLM analysis")

    @patch('core.llm_reasoning.ChatGroq.ainvoke', new_callable=AsyncMock)
    def test_valid_json_parsing(self, mock_ainvoke):
        """Test parsing perfect JSON from LLM."""
        mock_response = MagicMock()
        mock_response.content = '{"reasoning": "Good setup", "risk_factors": "None", "timeframe_alignment": "Bullish"}'
        mock_ainvoke.return_value = mock_response
        
        result = self.run_async(self.engine.analyze_trade(
            'BTC', 'BUY', 80, self.market_data
        ))
        
        self.assertEqual(result['reasoning'], "Good setup")
        print("✅ Perfect JSON parsed successfully")

    @patch('core.llm_reasoning.ChatGroq.ainvoke', new_callable=AsyncMock)
    def test_messy_json_extraction(self, mock_ainvoke):
        """Test parsing JSON when LLM adds conversational filler."""
        mock_response = MagicMock()
        # LLM often adds text before/after JSON
        mock_response.content = "Here is the analysis:\n```json\n{\"reasoning\": \"Messy setup\", \"risk_factors\": \"High vol\", \"timeframe_alignment\": \"Mixed\"}\n```"
        mock_ainvoke.return_value = mock_response
        
        result = self.run_async(self.engine.analyze_trade(
            'BTC', 'SELL', 75, self.market_data
        ))
        
        self.assertEqual(result['reasoning'], "Messy setup")
        self.assertEqual(result['risk_factors'], "High vol")
        print("✅ Messy JSON (with markdown) extracted successfully via regex")

    @patch('core.llm_reasoning.ChatGroq.ainvoke', new_callable=AsyncMock)
    def test_llm_crash_fallback(self, mock_ainvoke):
        """Test graceful fallback when LLM API throws an error."""
        mock_ainvoke.side_effect = Exception("API Timeout")
        
        result = self.run_async(self.engine.analyze_trade(
            'BTC', 'BUY', 80, self.market_data
        ))
        
        self.assertEqual(result, FALLBACK_REASONING)
        print("✅ LLM crash handled gracefully (fallback returned)")

    @patch('core.llm_reasoning.ChatGroq.ainvoke', new_callable=AsyncMock)
    def test_invalid_json_fallback(self, mock_ainvoke):
        """Test fallback when LLM returns complete garbage."""
        mock_response = MagicMock()
        mock_response.content = "I am a teapot and I don't know JSON."
        mock_ainvoke.return_value = mock_response
        
        result = self.run_async(self.engine.analyze_trade(
            'BTC', 'BUY', 80, self.market_data
        ))
        
        self.assertEqual(result, FALLBACK_REASONING)
        print("✅ Garbage response handled gracefully (fallback returned)")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLLMReasoningEngine)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
