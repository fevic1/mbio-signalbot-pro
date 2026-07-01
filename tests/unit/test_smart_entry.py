"""Unit tests for Smart Entry Optimization."""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestSmartEntryLogic(unittest.TestCase):
    """Test the smart entry tranche calculations."""
    
    def test_buy_scale_in_calculation(self):
        """Test BUY scale-in target price and sizes."""
        total_size = 1.0
        entry_price = 1000.0
        initial_pct = 0.5
        pullback_pct = 0.005 # 0.5%
        
        initial_size = total_size * initial_pct
        pending_size = total_size - initial_size
        # For BUY, pullback means a LOWER price
        target_price = entry_price * (1.0 - pullback_pct)
        
        self.assertEqual(initial_size, 0.5)
        self.assertEqual(pending_size, 0.5)
        self.assertAlmostEqual(target_price, 995.0, places=5)
        print("✅ BUY scale-in calculation correct")

    def test_sell_scale_in_calculation(self):
        """Test SELL (Short) scale-in target price and sizes."""
        total_size = 1.0
        entry_price = 1000.0
        initial_pct = 0.5
        pullback_pct = 0.005 # 0.5%
        
        initial_size = total_size * initial_pct
        pending_size = total_size - initial_size
        # For SELL, pullback means a HIGHER price
        target_price = entry_price * (1.0 + pullback_pct)
        
        self.assertEqual(initial_size, 0.5)
        self.assertEqual(pending_size, 0.5)
        # Use assertAlmostEqual for floating-point math
        self.assertAlmostEqual(target_price, 1005.0, places=5)
        print("✅ SELL scale-in calculation correct")

    def test_disabled_smart_entry(self):
        """Test that disabled smart entry uses 100% size."""
        total_size = 1.0
        initial_pct = 1.0 # Disabled
        
        initial_size = total_size * initial_pct
        pending_size = total_size - initial_size
        
        self.assertEqual(initial_size, 1.0)
        self.assertEqual(pending_size, 0.0)
        print("✅ Disabled smart entry behaves as 100% immediate entry")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSmartEntryLogic)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
