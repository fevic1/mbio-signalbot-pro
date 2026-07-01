"""
Real-time position analytics and pattern recognition.
Monitors open positions and learns from their behavior.
"""
import logging
import numpy as np
from datetime import datetime, timezone
from typing import Dict, List, Optional
import core.state as state

logger = logging.getLogger(__name__)

class PositionAnalytics:
    """Analyzes open positions in real-time and identifies patterns."""
    
    def __init__(self):
        self.pattern_history = []  # Store patterns for learning
        self.strategy_scores = {}  # Track strategy performance per regime
        
    def analyze_position(self, symbol: str, pos: Dict, current_price: float, current_atr: float) -> Dict:
        """Analyze a single open position and return insights."""
        entry = pos.get('entry', 0)
        side = pos.get('side', 'BUY')
        opened_at = pos.get('opened_at')
        
        if entry <= 0:
            return {}
        
        # Calculate metrics
        if side == 'BUY':
            pnl_pct = ((current_price - entry) / entry) * 100
            distance_to_tp1 = ((pos.get('tp1', 0) - current_price) / current_price) * 100
            distance_to_sl = ((current_price - pos.get('sl', 0)) / current_price) * 100
        else:
            pnl_pct = ((entry - current_price) / entry) * 100
            distance_to_tp1 = ((current_price - pos.get('tp1', 0)) / current_price) * 100
            distance_to_sl = ((pos.get('sl', 0) - current_price) / current_price) * 100
        
        # Time in trade
        if opened_at:
            try:
                open_time = datetime.fromisoformat(opened_at.replace('Z', '+00:00'))
                time_in_trade_hours = (datetime.now(timezone.utc) - open_time).total_seconds() / 3600
            except:
                time_in_trade_hours = 0
        else:
            time_in_trade_hours = 0
        
        # Volatility ratio (current ATR vs entry ATR approximation)
        entry_atr_approx = entry * 0.02  # Rough approximation
        volatility_ratio = current_atr / entry_atr_approx if entry_atr_approx > 0 else 1.0
        
        # Pattern classification
        pattern = self._classify_pattern(
            pnl_pct, time_in_trade_hours, distance_to_tp1, distance_to_sl, volatility_ratio
        )
        
        # Decision: Should we adjust TP/SL or exit early?
        action = self._determine_action(pattern, pnl_pct, time_in_trade_hours)
        
        return {
            'symbol': symbol,
            'pnl_pct': pnl_pct,
            'time_hours': time_in_trade_hours,
            'distance_to_tp1_pct': distance_to_tp1,
            'distance_to_sl_pct': distance_to_sl,
            'volatility_ratio': volatility_ratio,
            'pattern': pattern,
            'action': action
        }
    
    def _classify_pattern(self, pnl_pct: float, time_hours: float, 
                         dist_tp1: float, dist_sl: float, vol_ratio: float) -> str:
        """Classify the current position behavior pattern."""
        
        # Quick winner: High profit, short time
        if pnl_pct > 1.0 and time_hours < 2:
            return "QUICK_WINNER"
        
        # Slow winner: Moderate profit, longer time
        if pnl_pct > 0.5 and time_hours > 4:
            return "SLOW_WINNER"
        
        # Struggling: Small loss, but not hitting SL
        if -1.0 < pnl_pct < 0 and dist_sl > 1.0:
            return "STRUGGLING"
        
        # Loser pattern: Approaching SL
        if pnl_pct < -1.0 or dist_sl < 0.5:
            return "LIKELY_LOSER"
        
        # Choppy: High volatility, small PnL
        if vol_ratio > 1.5 and abs(pnl_pct) < 0.5:
            return "CHOPPY"
        
        return "NEUTRAL"
    
    def _determine_action(self, pattern: str, pnl_pct: float, time_hours: float) -> str:
        """Determine what action to take based on pattern."""
        
        if pattern == "QUICK_WINNER":
            return "TIGHTEN_STOP"  # Lock in profits
        
        if pattern == "LIKELY_LOSER":
            return "EARLY_EXIT"  # Cut losses early
        
        if pattern == "CHOPPY" and time_hours > 6:
            return "REDUCE_SIZE"  # Market is choppy, reduce exposure
        
        if pattern == "SLOW_WINNER":
            return "TRAIL_STOP"  # Let it run but protect profits
        
        return "HOLD"  # Normal behavior
    
    def record_pattern_outcome(self, symbol: str, pattern: str, strategy: str, 
                              regime: str, pnl_pct: float):
        """Record how a pattern performed for future learning."""
        self.pattern_history.append({
            'symbol': symbol,
            'pattern': pattern,
            'strategy': strategy,
            'regime': regime,
            'pnl_pct': pnl_pct,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
        # Update strategy scores
        key = f"{strategy}_{regime}"
        if key not in self.strategy_scores:
            self.strategy_scores[key] = {'wins': 0, 'losses': 0, 'total_pnl': 0}
        
        if pnl_pct > 0:
            self.strategy_scores[key]['wins'] += 1
        else:
            self.strategy_scores[key]['losses'] += 1
        self.strategy_scores[key]['total_pnl'] += pnl_pct
        
        logger.info(f"📊 Pattern recorded: {pattern} | {strategy} in {regime} | PnL: {pnl_pct:+.2f}%")
    
    def get_strategy_performance(self, strategy: str, regime: str) -> Dict:
        """Get performance metrics for a strategy in a specific regime."""
        key = f"{strategy}_{regime}"
        return self.strategy_scores.get(key, {'wins': 0, 'losses': 0, 'total_pnl': 0})

# Singleton instance
_analytics_instance = None

def get_position_analytics() -> PositionAnalytics:
    global _analytics_instance
    if _analytics_instance is None:
        _analytics_instance = PositionAnalytics()
    return _analytics_instance
