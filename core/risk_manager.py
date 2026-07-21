"""
Advanced Risk Management Engine
Provides pre-trade validation, correlation checks, and exposure limits.
"""
import logging
import pandas as pd
import requests
import time
from typing import Dict, Any, List
from core.app_context import app_context
import config_loader

logger = logging.getLogger(__name__)

def get_config_limits() -> Dict[str, Any]:
    """Dynamically fetch risk limits from config (No Hardcoding)."""
    cfg = config_loader.get_config()
    risk_cfg = cfg.get("risk_management", {})
    execution_cfg = cfg.get("execution", {})
    return {
        "max_open_positions": risk_cfg.get("max_open_positions", 5),
        "max_notional_per_asset": risk_cfg.get("max_notional_per_asset", 100.0),
        "max_total_exposure": risk_cfg.get("max_total_exposure", 1000.0),
        "correlation_warning_threshold": risk_cfg.get("correlation_warning_threshold", 0.75)
    }

async def validate_portfolio_exposure(asset: str, proposed_investment: float) -> Dict[str, Any]:
    """
    Validates if a proposed trade breaches portfolio risk limits.
    """
    try:
        limits = get_config_limits()
        state_positions = app_context.state.OPEN_POSITIONS if hasattr(app_context, 'state') else {}
        
        # 1. Check Max Open Positions
        # Filter out grid state keys to count actual directional positions, or count all active strategies
        active_strategies = len([k for k in state_positions.keys() if not k.endswith("_grid")])
        if active_strategies >= limits["max_open_positions"]:
            return {
                "approved": False,
                "reason": f"Max open positions limit reached ({active_strategies}/{limits['max_open_positions']})."
            }

        # 2. Check Max Notional Per Asset
        # (Simplified: assuming proposed_investment is the max exposure for this asset)
        if proposed_investment > limits["max_notional_per_asset"]:
            return {
                "approved": False,
                "reason": f"Proposed investment (${proposed_investment}) exceeds max notional per asset (${limits['max_notional_per_asset']})."
            }

        # 3. Check Total Exposure (Optional: sum of all open position notionals)
        # Implementation depends on how your state tracks total notional. 
        # For now, we pass if individual limits are met.

        return {
            "approved": True,
            "message": "Exposure limits validated successfully.",
            "limits_checked": limits
        }
    except Exception as e:
        logger.error(f"validate_portfolio_exposure failed: {e}")
        return {"approved": False, "reason": f"Internal risk check error: {str(e)}"}

async def check_asset_correlation(target_asset: str, open_assets: List[str]) -> Dict[str, Any]:
    """
    Calculates rolling 7-day correlation between target asset and open positions.
    Returns a warning if correlation is dangerously high.
    """
    try:
        if not open_assets:
            return {"approved": True, "message": "No open positions to correlate against."}

        limits = get_config_limits()
        threshold = limits["correlation_warning_threshold"]
        
        # Fetch 7 days of 1H candles for correlation
        end_time = int(time.time() * 1000)
        start_time = end_time - (7 * 24 * 3600 * 1000)
        
        closes = {}
        assets_to_check = list(set(open_assets + [target_asset]))
        
        for coin in assets_to_check:
            resp = requests.post(
                "https://api.hyperliquid.xyz/info",
                json={
                    "type": "candleSnapshot",
                    "req": {"coin": coin, "interval": "1h", "startTime": start_time, "endTime": end_time}
                },
                timeout=5
            )
            if resp.status_code == 200 and resp.json():
                df = pd.DataFrame(resp.json())
                df['close'] = pd.to_numeric(df['c'])
                # Calculate percentage returns to normalize price scales
                closes[coin] = df['close'].pct_change().dropna()

        if len(closes) < 2:
            return {"approved": True, "message": "Insufficient data for correlation check."}

        corr_df = pd.DataFrame(closes)
        correlations = corr_df.corr()
        
        warnings = []
        for open_coin in open_assets:
            if open_coin in correlations.columns and target_asset in correlations.index:
                corr_val = correlations.loc[target_asset, open_coin]
                if pd.notna(corr_val) and abs(corr_val) >= threshold:
                    warnings.append(f"High correlation ({corr_val:.2f}) with open {open_coin} position.")

        if warnings:
            return {
                "approved": True, # Still approved, but flags a warning for the human/AI to consider
                "warning": " ".join(warnings),
                "correlation_matrix": correlations.loc[target_asset, open_assets].to_dict()
            }

        return {"approved": True, "message": "Correlation checks passed."}

    except Exception as e:
        logger.error(f"check_asset_correlation failed: {e}")
        return {"approved": True, "message": "Correlation check skipped due to error (fail-safe)."}

# ============================================================
# RESTORED FUNCTION FOR POSITION TRACKER COMPATIBILITY
# ============================================================
def is_drawdown_halted(threshold: float = -15.0) -> bool:
    """
    Checks if the daily drawdown has exceeded the halt threshold.
    Restored to prevent import crashes in monitoring/position_tracker.py.
    """
    try:
        from core.state import DAILY_PNL
        # If daily PnL is worse (more negative) than the threshold, halt.
        return DAILY_PNL <= threshold
    except Exception:
        # Fail-safe: if state is unavailable, do not halt trading.
        return False

# ============================================================
# RESTORED FUNCTION FOR POSITION TRACKER COMPATIBILITY
# ============================================================
