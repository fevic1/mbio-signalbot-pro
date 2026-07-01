"""Integration test for LLM reasoning in trade flow."""
import unittest
import sys
import os
from unittest.mock import AsyncMock, patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestLLMReasoningIntegration(unittest.TestCase):
    """Test LLM reasoning integration."""
    
    def test_reasoning_engine_imports(self):
        """Test that reasoning engine can be imported."""
        try:
            from core.llm_reasoning import LLMReasoningEngine
            print("✅ LLMReasoningEngine imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import LLMReasoningEngine: {e}")
    
    def test_reasoning_in_main_imports(self):
        """Test that main.py has reasoning imports."""
        with open('main.py', 'r') as f:
            content = f.read()
        
        self.assertIn('from core.llm_reasoning import LLMReasoningEngine', content)
        self.assertIn('llm_reasoning', content)
        print("✅ main.py has LLM reasoning imports")
    
    def test_reasoning_in_position_state(self):
        """Test that reasoning is stored in position state."""
        with open('main.py', 'r') as f:
            content = f.read()
        
        self.assertIn('position_data["llm_reasoning"]', content)
        self.assertIn('position_data["risk_factors"]', content)
        print("✅ Reasoning stored in position state")
    
    def test_telegram_shows_reasoning(self):
        """Test that /positions command shows reasoning."""
        with open('main.py', 'r') as f:
            content = f.read()
        
        self.assertIn('pos.get(\'llm_reasoning\'', content)
        self.assertIn('🧠 *Reasoning:*', content)
        print("✅ Telegram /positions shows reasoning")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLLMReasoningIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
