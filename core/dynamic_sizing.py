"""
Dynamic position sizing based on volatility, account equity, and risk parameters.
Implements Kelly Criterion and volatility-adjusted sizing.
"""
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class DynamicPositionSizer:
    """Calculate optimal position sizes based on market conditions."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # Risk parameters
        self.max_risk_per_trade = self.config.get('max_risk_per_trade_pct', 0.02)  # 2%
        self.max_portfolio_risk = self.config.get('max_portfolio_risk_pct', 0.10)  # 10%
        self.max_position_size = self.config.get('max_position_size_pct', 0.20)  # 20% of account
        
        # Kelly Criterion parameters
        self.kelly_fraction = self.config.get('kelly_fraction', 0.5)  # Half-Kelly for safety
        self.min_win_rate = self.config.get('min_win_rate', 0.40)  # Minimum 40% win rate
        
        # Volatility adjustments
        self.volatility_scalar = self.config.get('volatility_scalar', 1.0)
        self.min_volatility = self.config.get('min_volatility', 0.01)  # 1%
        self.max_volatility = self.config.get('max_volatility', 0.10)  # 10%
        
    def calculate_position_size(
        self,
        account_balance: float,
        entry_price: float,
        stop_loss_price: float,
        win_rate: float = 0.50,
        avg_win_loss_ratio: float = 1.5,
        current_volatility: float = 0.02,
        current_drawdown: float = 0.0,
        strategy_confidence: float = 0.75,
    ) -> Dict:
        """
        Calculate optimal position size using multiple methods.
        """
        if account_balance <= 0 or entry_price <= 0:
            return {'size_usd': 0, 'size_units': 0, 'reason': 'Invalid inputs'}
        
        # Calculate risk per unit (absolute dollar amount)
        risk_per_unit = abs(entry_price - stop_loss_price)
        if risk_per_unit <= 0:
            return {'size_usd': 0, 'size_units': 0, 'reason': 'Invalid stop loss'}
        
        # Method 1: Fixed Risk Percentage
        fixed_risk_size = self._fixed_risk_sizing(account_balance, risk_per_unit, entry_price)
        
        # Method 2: Kelly Criterion
        kelly_size = self._kelly_criterion_sizing(
            account_balance, risk_per_unit, entry_price, win_rate, avg_win_loss_ratio
        )
        
        # Method 3: Volatility-Adjusted
        vol_size = self._volatility_adjusted_sizing(
            account_balance, risk_per_unit, entry_price, current_volatility
        )
        
        # Method 4: Confidence-Adjusted
        confidence_size = self._confidence_adjusted_sizing(
            account_balance, risk_per_unit, entry_price, strategy_confidence
        )
        
        # Method 5: Drawdown-Adjusted
        drawdown_size = self._drawdown_adjusted_sizing(
            account_balance, risk_per_unit, entry_price, current_drawdown
        )
        
        # Take the most conservative size
        sizes = [
            ('fixed_risk', fixed_risk_size),
            ('kelly', kelly_size),
            ('volatility', vol_size),
            ('confidence', confidence_size),
            ('drawdown', drawdown_size),
        ]
        
        # Filter out invalid sizes
        valid_sizes = [(name, size) for name, size in sizes if size > 0]
        
        if not valid_sizes:
            return {'size_usd': 0, 'size_units': 0, 'reason': 'All sizing methods returned 0'}
        
        # Use the smallest (most conservative) size
        method_used, size_usd = min(valid_sizes, key=lambda x: x[1])
        
        # Apply maximum position size limit
        max_size_usd = account_balance * self.max_position_size
        size_usd = min(size_usd, max_size_usd)
        
        # Calculate units
        size_units = size_usd / entry_price
        
        return {
            'size_usd': round(size_usd, 2),
            'size_units': round(size_units, 6),
            'method': method_used,
            'risk_usd': round(size_units * risk_per_unit, 2),
            'risk_pct': round((size_units * risk_per_unit / account_balance) * 100, 2),
            'all_methods': {name: round(size, 2) for name, size in sizes},
        }
    
    def _fixed_risk_sizing(self, balance: float, risk_per_unit: float, entry_price: float) -> float:
        """Size based on fixed risk percentage."""
        risk_amount = balance * self.max_risk_per_trade
        size_units = risk_amount / risk_per_unit
        return size_units * entry_price
    
    def _kelly_criterion_sizing(
        self, balance: float, risk_per_unit: float, entry_price: float, 
        win_rate: float, win_loss_ratio: float
    ) -> float:
        """Size using Kelly Criterion."""
        if win_rate < self.min_win_rate:
            return 0  # Don't trade if win rate too low
        
        # Kelly formula: f = (bp - q) / b
        b = win_loss_ratio
        p = win_rate
        q = 1 - p
        
        kelly_pct = (b * p - q) / b
        kelly_pct = max(0, kelly_pct * self.kelly_fraction)
        
        risk_amount = balance * kelly_pct
        size_units = risk_amount / risk_per_unit
        return size_units * entry_price
    
    def _volatility_adjusted_sizing(
        self, balance: float, risk_per_unit: float, entry_price: float, volatility: float
    ) -> float:
        """Reduce size in high volatility, increase in low volatility."""
        vol = max(self.min_volatility, min(volatility, self.max_volatility))
        vol_scalar = self.volatility_scalar * (0.02 / vol)
        
        risk_amount = balance * self.max_risk_per_trade * vol_scalar
        size_units = risk_amount / risk_per_unit
        return size_units * entry_price
    
    def _confidence_adjusted_sizing(
        self, balance: float, risk_per_unit: float, entry_price: float, confidence: float
    ) -> float:
        """Scale size by strategy confidence."""
        conf = max(0, min(1, confidence))
        risk_amount = balance * self.max_risk_per_trade * conf
        size_units = risk_amount / risk_per_unit
        return size_units * entry_price
    
    def _drawdown_adjusted_sizing(
        self, balance: float, risk_per_unit: float, entry_price: float, drawdown: float
    ) -> float:
        """Reduce size during drawdowns."""
        dd = max(0, min(1, drawdown))
        dd_scalar = 1 - dd
        
        risk_amount = balance * self.max_risk_per_trade * dd_scalar
        size_units = risk_amount / risk_per_unit
        return size_units * entry_price

# Multi-user safe factory (Stateless instantiation)
# We return a fresh instance every time to prevent state leakage 
# between different users or concurrent threads.
def get_position_sizer(config: Dict = None) -> DynamicPositionSizer:
    return DynamicPositionSizer(config or {})
