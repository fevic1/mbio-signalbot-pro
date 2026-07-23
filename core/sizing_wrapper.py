"""
Production-safe wrapper for dynamic position sizing.
Integrates seamlessly with main.py and falls back to legacy logic if anything fails.
"""
import logging
from typing import Dict, Optional
from core.exchange_limits import get_exchange_limits

logger = logging.getLogger(__name__)

# FEATURE FLAG: Set to True to enable dynamic sizing, False to use legacy logic
ENABLE_DYNAMIC_SIZING = True 

def calculate_safe_position_size(
    account_balance: float,
    entry_price: float,
    stop_loss_price: float,
    strategy_name: str = "Unknown",
    feature_enabled: bool = True,
    strategy_confidence: float = 0.75,
    current_volatility: float = 0.02,
    current_drawdown: float = 0.0,
    win_rate: float = 0.55,
    avg_win_loss_ratio: float = 1.5,
) -> Optional[Dict]:
    """
    Calculate position size. Returns None if feature is disabled or an error occurs.
    """
    if not feature_enabled or not ENABLE_DYNAMIC_SIZING:
        return None
        
    try:
        from core.dynamic_sizing import get_position_sizer
        
        sizer = get_position_sizer()
        
        result = sizer.calculate_position_size(
            account_balance=account_balance,
            entry_price=entry_price,
            stop_loss_price=stop_loss_price,
            win_rate=win_rate,
            avg_win_loss_ratio=avg_win_loss_ratio,
            current_volatility=current_volatility,
            current_drawdown=current_drawdown,
            strategy_confidence=strategy_confidence,
        )
        
        if not result or result.get("size_usd", 0) <= 0:
            return None

        # Only log if we actually got a valid size
        if result and result.get('size_usd', 0) > 0:
            logger.info(
                f"📏 [DynamicSizer] {strategy_name}: "
                f"${result['size_usd']} ({result['size_units']:.6f} units) "
                f"via {result['method']} | Risk: {result['risk_pct']}%"
            )
            
        # EXCHANGE FLOOR ENFORCEMENT (CODING_STANDARD: No magic numbers)
        # Ensure calculated position meets exchange minimum notional
        _limits = get_exchange_limits()
        _effective_min = _limits["min_notional_usd"] * _limits["min_notional_buffer"]
        _size_usd = result.get('size_usd', 0)
        if _size_usd > 0 and _size_usd < _effective_min:
            logger.warning(
                f"⚠️ [DynamicSizer] Calculated ${_size_usd:.2f} below effective "
                f"min ${_effective_min:.2f}. Skipping trade."
            )
            return None

        return result
        
    except Exception as e:
        # CRITICAL: Never let a sizing error crash the bot.
        logger.error(f"Dynamic sizing failed for {strategy_name}: {e}. Falling back to legacy.")
        return None
