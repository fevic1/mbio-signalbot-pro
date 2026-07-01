"""Integration test for dynamic sizing with existing code."""
import unittest
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.dynamic_sizing import get_position_sizer

class TestSizingIntegration(unittest.TestCase):
    """Test integration with existing bot code."""
    
    def test_sizer_initialization(self):
        """Test that sizer can be initialized."""
        sizer = get_position_sizer()
        self.assertIsNotNone(sizer)
        print("✅ Sizer initialized successfully")
    
    def test_sizing_with_real_data(self):
        """Test sizing with realistic market data."""
        sizer = get_position_sizer()
        
        # Simulate a BTC trade
        result = sizer.calculate_position_size(
            account_balance=85.0,  # Current balance
            entry_price=65000,
            stop_loss_price=64000,  # ~1.5% stop
            win_rate=0.55,
            avg_win_loss_ratio=1.8,
            current_volatility=0.025,
            current_drawdown=0.05,
            strategy_confidence=0.75,
        )
        
        print(f"\n📊 BTC Trade Sizing:")
        print(f"   Size USD: ${result['size_usd']}")
        print(f"   Size Units: {result['size_units']} BTC")
        print(f"   Method: {result['method']}")
        print(f"   Risk: ${result['risk_usd']} ({result['risk_pct']}%)")
        
        # Validate results
        self.assertGreater(result['size_usd'], 0)
        self.assertLessEqual(result['risk_pct'], 2.0)  # Should be <= 2%
        
        print("✅ Integration test passed")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSizingIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
