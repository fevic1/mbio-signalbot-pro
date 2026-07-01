"""Unit tests for dynamic position sizing."""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.dynamic_sizing import DynamicPositionSizer

class TestDynamicPositionSizer(unittest.TestCase):
    """Test dynamic position sizing calculations."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Disable max position cap for unit testing the core logic
        config = {'max_position_size_pct': 1.0} 
        self.sizer = DynamicPositionSizer(config)
        self.balance = 10000
        self.entry = 100
        self.stop_loss = 90  # 10% stop loss distance
        
    def test_basic_sizing(self):
        """Test basic position sizing."""
        result = self.sizer.calculate_position_size(
            account_balance=self.balance,
            entry_price=self.entry,
            stop_loss_price=self.stop_loss,
            strategy_confidence=1.0, # Neutralize confidence
            current_drawdown=0.0,    # Neutralize drawdown
            current_volatility=0.02, # Neutralize volatility
        )
        
        self.assertGreater(result['size_usd'], 0)
        self.assertGreater(result['size_units'], 0)
        self.assertIn('method', result)
        print(f"✅ Basic sizing: {result}")
    
    def test_zero_balance(self):
        """Test with zero balance."""
        result = self.sizer.calculate_position_size(
            account_balance=0,
            entry_price=self.entry,
            stop_loss_price=self.stop_loss,
        )
        self.assertEqual(result['size_usd'], 0)
        print("✅ Zero balance handled correctly")
    
    def test_invalid_stop_loss(self):
        """Test with invalid stop loss."""
        result = self.sizer.calculate_position_size(
            account_balance=self.balance,
            entry_price=self.entry,
            stop_loss_price=self.entry,
        )
        self.assertEqual(result['size_usd'], 0)
        print("✅ Invalid stop loss handled correctly")
    
    def test_high_volatility(self):
        """Test sizing with high volatility."""
        # BASELINE: Neutralize other factors
        normal_result = self.sizer.calculate_position_size(
            account_balance=self.balance,
            entry_price=self.entry,
            stop_loss_price=self.stop_loss,
            current_volatility=0.02,
            strategy_confidence=1.0,
            current_drawdown=0.0,
        )
        
        # TEST: Only change volatility
        high_vol_result = self.sizer.calculate_position_size(
            account_balance=self.balance,
            entry_price=self.entry,
            stop_loss_price=self.stop_loss,
            current_volatility=0.08,  # 4x normal
            strategy_confidence=1.0,
            current_drawdown=0.0,
        )
        
        self.assertLess(high_vol_result['size_usd'], normal_result['size_usd'])
        print(f"✅ High volatility reduces size: {normal_result['size_usd']} → {high_vol_result['size_usd']}")
    
    def test_drawdown_reduction(self):
        """Test size reduction during drawdown."""
        # BASELINE: Neutralize other factors
        normal_result = self.sizer.calculate_position_size(
            account_balance=self.balance,
            entry_price=self.entry,
            stop_loss_price=self.stop_loss,
            current_drawdown=0.0,
            strategy_confidence=1.0,
            current_volatility=0.02,
        )
        
        # TEST: Only change drawdown
        drawdown_result = self.sizer.calculate_position_size(
            account_balance=self.balance,
            entry_price=self.entry,
            stop_loss_price=self.stop_loss,
            current_drawdown=0.20,  # 20% drawdown
            strategy_confidence=1.0,
            current_volatility=0.02,
        )
        
        self.assertLess(drawdown_result['size_usd'], normal_result['size_usd'])
        print(f"✅ Drawdown reduces size: {normal_result['size_usd']} → {drawdown_result['size_usd']}")
    
    def test_low_confidence(self):
        """Test size reduction with low confidence."""
        # BASELINE: Neutralize other factors
        high_conf_result = self.sizer.calculate_position_size(
            account_balance=self.balance,
            entry_price=self.entry,
            stop_loss_price=self.stop_loss,
            strategy_confidence=0.90,
            current_drawdown=0.0,
            current_volatility=0.02,
        )
        
        # TEST: Only change confidence
        low_conf_result = self.sizer.calculate_position_size(
            account_balance=self.balance,
            entry_price=self.entry,
            stop_loss_price=self.stop_loss,
            strategy_confidence=0.50,
            current_drawdown=0.0,
            current_volatility=0.02,
        )
        
        self.assertLess(low_conf_result['size_usd'], high_conf_result['size_usd'])
        print(f"✅ Low confidence reduces size: {high_conf_result['size_usd']} → {low_conf_result['size_usd']}")
    
    def test_kelly_criterion_low_win_rate(self):
        """Test Kelly Criterion with low win rate."""
        result = self.sizer.calculate_position_size(
            account_balance=self.balance,
            entry_price=self.entry,
            stop_loss_price=self.stop_loss,
            win_rate=0.30,  # Below minimum
            avg_win_loss_ratio=1.5,
            strategy_confidence=1.0,
        )
        
        kelly_size = result['all_methods'].get('kelly', 0)
        self.assertEqual(kelly_size, 0)
        print("✅ Kelly Criterion rejects low win rate")
    
    def test_max_position_limit(self):
        """Test maximum position size limit."""
        # Use a sizer with a strict limit for this specific test
        sizer = DynamicPositionSizer({'max_position_size_pct': 0.10}) # 10% limit
        result = sizer.calculate_position_size(
            account_balance=1000000,  # $1M
            entry_price=100,
            stop_loss_price=90,
            strategy_confidence=1.0,
        )
        
        max_allowed = 1000000 * 0.10
        self.assertLessEqual(result['size_usd'], max_allowed)
        print(f"✅ Max position limit enforced: {result['size_usd']} <= {max_allowed}")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDynamicPositionSizer)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
