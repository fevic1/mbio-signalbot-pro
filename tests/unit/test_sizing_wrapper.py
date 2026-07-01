"""Test the sizing wrapper."""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.sizing_wrapper import calculate_safe_position_size

class TestSizingWrapper(unittest.TestCase):
    """Test the safe sizing wrapper."""
    
    def test_feature_disabled(self):
        """Test that wrapper returns None when feature is disabled."""
        result = calculate_safe_position_size(
            account_balance=1000,
            entry_price=50000,
            stop_loss_price=49000,
            feature_enabled=False,
        )
        self.assertIsNone(result)
        print("✅ Feature disabled - returns None (backward compatible)")
    
    def test_feature_enabled(self):
        """Test that wrapper works when feature is enabled."""
        result = calculate_safe_position_size(
            account_balance=1000,
            entry_price=50000,
            stop_loss_price=49000,
            strategy_name='TestStrategy',
            strategy_confidence=0.80,
            feature_enabled=True,
        )
        self.assertIsNotNone(result)
        self.assertIn('size_usd', result)
        self.assertGreater(result['size_usd'], 0)
        print(f"✅ Feature enabled - returns sizing: ${result['size_usd']}")
    
    def test_error_handling(self):
        """Test that wrapper handles errors gracefully."""
        result = calculate_safe_position_size(
            account_balance=-100,  # Invalid
            entry_price=50000,
            stop_loss_price=49000,
            feature_enabled=True,
        )
        self.assertIsNone(result)
        print("✅ Error handling - returns None on invalid input")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSizingWrapper)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
