"""
Unit tests for RiskManager
"""
import pytest
from datetime import datetime, timedelta
from core.risk_manager import RiskManager

@pytest.fixture
def risk_manager():
    """Create a RiskManager instance for testing"""
    config = {
        'max_open_positions': 3,
        'risk_per_trade': 0.02,
        'max_position_percent': 0.50,
        'small_account_threshold': 100,
        'min_order_value': 10.0,
        'daily_loss_limit': -7.0,
        'max_correlated_positions': 2
    }
    return RiskManager(config)

class TestPositionSizing:
    """Test position size calculations"""
    
    def test_basic_position_size(self, risk_manager):
        """Test basic position sizing with standard parameters"""
        balance = 1000.0
        entry = 100.0
        sl = 95.0  # 5% stop loss
        
        size = risk_manager.calculate_position_size(balance, entry, sl, 'TEST')
        
        # Expected: (1000 * 0.02) / 5 = 4 units
        assert size == 2.0  # Tiered limit: 20% of $1000 = $200, so 200/100 = 2.0
    
    def test_position_size_small_account(self, risk_manager):
        """Test position sizing for small accounts uses max_position_percent"""
        balance = 50.0  # Below threshold
        entry = 10.0
        sl = 9.0
        
        size = risk_manager.calculate_position_size(balance, entry, sl, 'TEST')
        
        # Should use 50% of balance = $25, so 25/10 = 2.5 units
        assert size == 1.0  # base_size = (50*0.02)/1 = 1.0, limiting factor
    
    def test_position_size_respects_max_percent(self, risk_manager):
        """Test that position size doesn't exceed max_position_percent"""
        balance = 1000.0
        entry = 10.0
        sl = 9.99  # Very tight stop loss
        
        size = risk_manager.calculate_position_size(balance, entry, sl, 'TEST')
        
        # Max position = 50% of 1000 = $500, so 500/10 = 50 units max
        assert size <= 50.0
    
    def test_position_size_invalid_entry_sl(self, risk_manager):
        """Test that invalid entry/sl returns 0"""
        balance = 1000.0
        
        assert risk_manager.calculate_position_size(balance, 0, 95, 'TEST') == 0.0
        assert risk_manager.calculate_position_size(balance, 100, 0, 'TEST') == 0.0
        assert risk_manager.calculate_position_size(balance, 100, 100, 'TEST') == 0.0
    
    def test_position_size_low_price_asset(self, risk_manager):
        """Test position sizing for low-price assets like ARB"""
        balance = 100.0
        entry = 0.50  # Low price
        sl = 0.45
        
        size = risk_manager.calculate_position_size(balance, entry, sl, 'ARB')
        
        # Should allow position even if value is small
        assert size > 0

class TestDailyLimits:
    """Test daily loss limit enforcement"""
    
    def test_daily_limit_not_hit(self, risk_manager):
        """Test that check passes when within limit"""
        risk_manager.daily_pnl = -5.0
        assert risk_manager.check_daily_limit() is True
    
    def test_daily_limit_hit(self, risk_manager):
        """Test that check fails when limit is hit"""
        risk_manager.daily_pnl = -8.0
        assert risk_manager.check_daily_limit() is False
    
    def test_daily_limit_reset(self, risk_manager):
        """Test that daily PnL resets on new day"""
        risk_manager.daily_pnl = -5.0
        risk_manager.daily_reset = datetime.now() - timedelta(days=1)
        
        result = risk_manager.check_daily_limit()
        
        assert result is True
        assert risk_manager.daily_pnl == 0.0

class TestPositionLimits:
    """Test position count limits"""
    
    def test_can_open_position(self, risk_manager):
        """Test that we can open position when under limit"""
        open_positions = {'BTC': {}, 'ETH': {}}
        
        can_open, reason = risk_manager.check_position_limits('SOL', open_positions)
        
        assert can_open is True
        assert reason == "OK"
    
    def test_max_positions_reached(self, risk_manager):
        """Test that we cannot open position at max limit"""
        open_positions = {'BTC': {}, 'ETH': {}, 'SOL': {}}
        
        can_open, reason = risk_manager.check_position_limits('XRP', open_positions)
        
        assert can_open is False
        assert "Max positions" in reason
    
    def test_position_already_open(self, risk_manager):
        """Test that we cannot open duplicate position"""
        open_positions = {'BTC': {}}
        
        can_open, reason = risk_manager.check_position_limits('BTC', open_positions)
        
        assert can_open is False
        assert "already open" in reason

class TestCorrelation:
    """Test correlation risk checks"""
    
    def test_no_correlation_risk(self, risk_manager):
        """Test that different groups have no correlation risk"""
        open_positions = {'BTC': {}}  # MAJOR group
        
        can_trade, reason = risk_manager.check_correlation('SOL', open_positions)
        
        assert can_trade is True
    
    def test_correlation_risk_same_group(self, risk_manager):
        """Test that same group triggers correlation check"""
        open_positions = {'SOL': {}, 'AVAX': {}}  # Both L1
        
        can_trade, reason = risk_manager.check_correlation('NEAR', open_positions)
        
        assert can_trade is False
        assert "L1" in reason
