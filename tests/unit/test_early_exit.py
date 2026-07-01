"""Unit tests for automatic early exit logic."""
import unittest
import sys
import os
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestEarlyExitLogic(unittest.TestCase):
    """Test the early exit decision logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'early_exit': {
                'enabled': True,
                'pattern_threshold': 'LIKELY_LOSER',
                'pnl_threshold': -2.0,
                'consecutive_checks': 3,
                'cooldown_minutes': 30
            }
        }
    
    def should_trigger_early_exit(self, pos: dict, config: dict) -> bool:
        """
        Pure decision function - easy to test.
        Returns True if early exit should be triggered.
        """
        early_cfg = config.get('early_exit', {})
        
        if not early_cfg.get('enabled', False):
            return False
        
        pattern = pos.get('last_pattern', 'UNKNOWN')
        pnl_pct = pos.get('pnl_pct', 0)
        consecutive_count = pos.get('likely_loser_count', 0)
        last_attempt = pos.get('last_early_exit_attempt')
        
        # Check pattern threshold
        if pattern != early_cfg.get('pattern_threshold'):
            return False
        
        # Check PnL threshold
        if pnl_pct >= early_cfg.get('pnl_threshold', -2.0):
            return False
        
        # Check consecutive count
        if consecutive_count < early_cfg.get('consecutive_checks', 3):
            return False
        
        # Check cooldown
        if last_attempt:
            try:
                if isinstance(last_attempt, str):
                    last_attempt = datetime.fromisoformat(last_attempt.replace('Z', '+00:00'))
                cooldown = timedelta(minutes=early_cfg.get('cooldown_minutes', 30))
                if datetime.now(timezone.utc) - last_attempt < cooldown:
                    return False
            except Exception:
                pass
        
        return True
    
    def test_disabled_feature(self):
        """Test that disabled feature never triggers."""
        config = {'early_exit': {'enabled': False}}
        pos = {
            'last_pattern': 'LIKELY_LOSER',
            'pnl_pct': -5.0,
            'likely_loser_count': 10
        }
        self.assertFalse(self.should_trigger_early_exit(pos, config))
        print("✅ Disabled feature correctly returns False")
    
    def test_wrong_pattern(self):
        """Test that non-LIKELY_LOSER pattern doesn't trigger."""
        pos = {
            'last_pattern': 'NEUTRAL',
            'pnl_pct': -5.0,
            'likely_loser_count': 10
        }
        self.assertFalse(self.should_trigger_early_exit(pos, self.config))
        print("✅ Wrong pattern correctly returns False")
    
    def test_pnl_above_threshold(self):
        """Test that PnL above threshold doesn't trigger."""
        pos = {
            'last_pattern': 'LIKELY_LOSER',
            'pnl_pct': -1.5,  # Above -2.0
            'likely_loser_count': 10
        }
        self.assertFalse(self.should_trigger_early_exit(pos, self.config))
        print("✅ PnL above threshold correctly returns False")
    
    def test_insufficient_consecutive_checks(self):
        """Test that insufficient consecutive checks don't trigger."""
        pos = {
            'last_pattern': 'LIKELY_LOSER',
            'pnl_pct': -5.0,
            'likely_loser_count': 2  # Need 3
        }
        self.assertFalse(self.should_trigger_early_exit(pos, self.config))
        print("✅ Insufficient consecutive checks correctly returns False")
    
    def test_cooldown_active(self):
        """Test that cooldown prevents re-trigger."""
        pos = {
            'last_pattern': 'LIKELY_LOSER',
            'pnl_pct': -5.0,
            'likely_loser_count': 10,
            'last_early_exit_attempt': datetime.now(timezone.utc).isoformat()  # Just now
        }
        self.assertFalse(self.should_trigger_early_exit(pos, self.config))
        print("✅ Active cooldown correctly returns False")
    
    def test_cooldown_expired(self):
        """Test that expired cooldown allows trigger."""
        pos = {
            'last_pattern': 'LIKELY_LOSER',
            'pnl_pct': -5.0,
            'likely_loser_count': 10,
            'last_early_exit_attempt': (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        }
        self.assertTrue(self.should_trigger_early_exit(pos, self.config))
        print("✅ Expired cooldown correctly allows trigger")
    
    def test_all_conditions_met(self):
        """Test that all conditions met triggers early exit."""
        pos = {
            'last_pattern': 'LIKELY_LOSER',
            'pnl_pct': -3.5,
            'likely_loser_count': 5
        }
        self.assertTrue(self.should_trigger_early_exit(pos, self.config))
        print("✅ All conditions met correctly returns True")
    
    def test_boundary_pnl(self):
        """Test boundary PnL values."""
        # Exactly at threshold should NOT trigger (must be worse than)
        pos = {
            'last_pattern': 'LIKELY_LOSER',
            'pnl_pct': -2.0,  # Exactly at threshold
            'likely_loser_count': 10
        }
        self.assertFalse(self.should_trigger_early_exit(pos, self.config))
        
        # Just below threshold should trigger
        pos['pnl_pct'] = -2.01
        self.assertTrue(self.should_trigger_early_exit(pos, self.config))
        print("✅ Boundary PnL values handled correctly")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEarlyExitLogic)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
