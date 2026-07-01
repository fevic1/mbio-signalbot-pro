"""Integration test for early exit with real position data."""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config_loader import get_config

class TestEarlyExitIntegration(unittest.TestCase):
    """Test early exit with actual config."""
    
    def test_config_loaded(self):
        """Test that early exit config is loaded correctly."""
        config = get_config()
        early_cfg = config.get('early_exit', {})
        
        self.assertTrue(early_cfg.get('enabled', False))
        self.assertEqual(early_cfg.get('pattern_threshold'), 'LIKELY_LOSER')
        self.assertEqual(early_cfg.get('pnl_threshold'), -2.0)
        self.assertEqual(early_cfg.get('consecutive_checks'), 3)
        self.assertEqual(early_cfg.get('cooldown_minutes'), 30)
        
        print(f"✅ Config loaded: {early_cfg}")
    
    def test_eth_position_would_trigger(self):
        """Test with current ETH position data."""
        config = get_config()
        early_cfg = config.get('early_exit', {})
        
        # Simulate current ETH position (from logs)
        pos = {
            'last_pattern': 'LIKELY_LOSER',
            'pnl_pct': -2.52,  # Current PnL
            'likely_loser_count': 5,  # Has been losing for 5 checks
            'side': 'SELL',
            'entry': 1720.2
        }
        
        # Check conditions
        pattern_match = pos['last_pattern'] == early_cfg['pattern_threshold']
        pnl_match = pos['pnl_pct'] < early_cfg['pnl_threshold']
        count_match = pos['likely_loser_count'] >= early_cfg['consecutive_checks']
        
        would_trigger = pattern_match and pnl_match and count_match
        
        print(f"\n📊 ETH Position Analysis:")
        print(f"   Pattern: {pos['last_pattern']} (need {early_cfg['pattern_threshold']}) → {'✅' if pattern_match else '❌'}")
        print(f"   PnL: {pos['pnl_pct']:.2f}% (need < {early_cfg['pnl_threshold']}) → {'✅' if pnl_match else '❌'}")
        print(f"   Count: {pos['likely_loser_count']} (need >= {early_cfg['consecutive_checks']}) → {'✅' if count_match else '❌'}")
        print(f"   Would trigger early exit: {'🚨 YES' if would_trigger else 'NO'}")
        
        self.assertTrue(would_trigger, "ETH should trigger early exit based on current data")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEarlyExitIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
