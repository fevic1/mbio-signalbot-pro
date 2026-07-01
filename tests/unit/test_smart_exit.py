"""Unit tests for Smart Exit Strategies."""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.smart_exit import SmartExitManager

class TestSmartExitManager(unittest.TestCase):
    """Test the smart exit manager."""
    
    def setUp(self):
        self.manager = SmartExitManager()

    def test_calculate_partial_sizes(self):
        """Test splitting a position into partials."""
        total = 100.0
        partials = [0.3, 0.3, 0.4]
        
        sizes = self.manager.calculate_partial_sizes(total, partials)
        
        self.assertEqual(len(sizes), 3)
        self.assertAlmostEqual(sizes[0], 30.0)
        self.assertAlmostEqual(sizes[1], 30.0)
        self.assertAlmostEqual(sizes[2], 40.0)
        self.assertAlmostEqual(sum(sizes), total)
        print("✅ Partial sizes calculated correctly")

    def test_normalize_partials(self):
        """Test normalization when partials don't sum to 1.0."""
        total = 100.0
        partials = [0.2, 0.2, 0.2] # Sums to 0.6
        
        sizes = self.manager.calculate_partial_sizes(total, partials)
        
        # Should sum to 100.0 exactly
        self.assertAlmostEqual(sum(sizes), total)
        # Each should be roughly 33.33
        self.assertAlmostEqual(sizes[0], 33.3333, places=2)
        print("✅ Partials normalized correctly")

    def test_volatility_multiplier_ranging(self):
        """Test multiplier for ranging regime."""
        mult = self.manager.get_volatility_multiplier("RANGING", 20.0)
        self.assertEqual(mult, 0.8)
        print("✅ Ranging multiplier correct")

    def test_volatility_multiplier_trending(self):
        """Test multiplier for trending regime."""
        mult = self.manager.get_volatility_multiplier("TRENDING", 40.0)
        # Strength factor = 40/50 = 0.8. Multiplier = 1.0 + (0.8 * 0.4) = 1.32
        self.assertAlmostEqual(mult, 1.32)
        print("✅ Trending multiplier correct")

    def test_adjust_tps(self):
        """Test TP adjustment logic."""
        entry = 1000.0
        base_distances = {"tp1": 100.0, "tp2": 200.0}
        
        # Ranging (0.8)
        adj = self.manager.adjust_tps_for_volatility(entry, base_distances, "RANGING")
        self.assertAlmostEqual(adj["tp1"], 80.0)
        
        # Neutral (1.0)
        adj = self.manager.adjust_tps_for_volatility(entry, base_distances, "NEUTRAL")
        self.assertAlmostEqual(adj["tp1"], 100.0)
        print("✅ TP adjustments correct")

    def test_time_based_exit(self):
        """Test time-based exit logic."""
        self.assertTrue(self.manager.calculate_time_based_exit(25.0, 24.0))
        self.assertFalse(self.manager.calculate_time_based_exit(10.0, 24.0))
        print("✅ Time-based exit logic correct")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSmartExitManager)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
