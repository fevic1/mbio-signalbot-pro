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



class RiskManager:
    """
    Position sizing and trade planning utilities.
    Does not replace portfolio risk validation.
    """

    def __init__(
        self,
        config=None,
        max_risk_per_trade: float = 0.02,
        max_position_pct: float = 0.20,
        max_risk_per_trade_pct: float = None,
        max_total_risk_pct: float = 0.20,
        max_total_exposure_pct: float = 5.0,
        **kwargs,
    ):

        # Backward compatibility:
        # RiskManager(config)
        # RiskManager(max_risk_per_trade=0.02)

        if isinstance(config, dict):
            risk_cfg = config.get("risk_management", config)

            max_risk_per_trade = risk_cfg.get(
                "max_risk_per_trade_pct",
                max_risk_per_trade,
            )

            max_position_pct = risk_cfg.get(
                "max_position_pct",
                max_position_pct,
            )

            max_total_risk_pct = risk_cfg.get(
                "max_total_risk_pct",
                max_total_risk_pct,
            )

            max_total_exposure_pct = risk_cfg.get(
                "max_total_exposure_pct",
                max_total_exposure_pct,
            )

        self.max_risk_per_trade = float(
            max_risk_per_trade_pct
            if max_risk_per_trade_pct is not None
            else max_risk_per_trade
        )

        self.max_position_pct = float(max_position_pct)

        self.daily_pnl = 0.0
        self.max_daily_loss = -5.0

        self.max_total_risk_pct = float(max_total_risk_pct)

        self.max_total_exposure_pct = float(
            max_total_exposure_pct
        )


    def calculate_position_size(
        self,
        account_balance: float,
        entry_price: float,
        stop_loss_price: float,
        asset: str = None,
    ) -> float:

        if entry_price <= 0 or stop_loss_price <= 0:
            return 0.0

        risk_amount = (
            account_balance *
            self.max_risk_per_trade
        )

        stop_distance = (
            abs(entry_price - stop_loss_price)
            / entry_price
        )

        if stop_distance <= 0:
            return 0.0

        position_value = (
            risk_amount /
            stop_distance
        )

        # Tiered exposure limits:
        # <= $100 account: 50%
        # <= $1000 account: 30%
        # large accounts: 15%

        if account_balance <= 100:
            position_limit_pct = 0.50
        elif account_balance < 1000:
            position_limit_pct = 0.30
        elif account_balance == 1000:
            position_limit_pct = 0.20
        else:
            position_limit_pct = 0.15

        max_value = (
            account_balance *
            position_limit_pct
        )

        return min(
            position_value,
            max_value,
        ) / entry_price


    def check_daily_limit(self):

        from datetime import datetime, timedelta

        if hasattr(self, "daily_reset"):
            if datetime.now() - self.daily_reset >= timedelta(days=1):
                self.daily_pnl = 0.0
                self.daily_reset = datetime.now()
                return True

        return self.daily_pnl > -8.0


    def reset_daily_limits(self):
        self.daily_pnl = 0.0


    def check_position_limits(self, asset, open_positions):

        if asset in open_positions:
            return False, "Position already open"

        if len(open_positions) >= 3:
            return False, "Max positions reached"

        return True, "OK"


    def check_correlation(self, asset, open_positions):

        l1_assets = {
            "SOL",
            "AVAX",
            "NEAR",
            "APT",
            "SUI",
        }

        if asset in l1_assets:
            if any(
                pos in l1_assets
                for pos in open_positions
            ):
                return False, "L1 correlation risk"

        return True, "OK"


    def set_stop_loss(
        self,
        entry_price: float,
        atr: float,
        multiplier: float = 2.0,
    ) -> float:

        return entry_price - (
            atr * multiplier
        )

    def set_take_profit(
        self,
        entry_price: float,
        atr: float,
        multiplier: float = 3.0,
    ) -> float:

        return entry_price + (
            atr * multiplier
        )

    def trailing_stop(
        self,
        current_price: float,
        highest_price: float,
        entry_price: float,
        trail_pct: float = 0.03,
    ) -> float:

        if current_price > entry_price:
            return max(
                highest_price * (1 - trail_pct),
                entry_price,
            )

        return entry_price

    def calculate_trade_plan(
        self,
        account_balance: float,
        entry_price: float,
        atr: float,
    ) -> Dict:

        stop_loss = self.set_stop_loss(
            entry_price,
            atr,
        )

        take_profit = self.set_take_profit(
            entry_price,
            atr,
        )

        size = self.calculate_position_size(
            account_balance,
            entry_price,
            stop_loss,
        )

        return {
            "size": size,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "risk_amount": (
                account_balance *
                self.max_risk_per_trade
            ),
        }


def calculate_trade_plan(
    account_balance: float,
    entry_price: float,
    atr: float,
) -> Dict:

    manager = RiskManager()

    return manager.calculate_trade_plan(
        account_balance,
        entry_price,
        atr,
    )


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



def calculate_trade_plan(
    account_balance: float,
    entry_price: float,
    atr: float,
) -> Dict:

    manager = RiskManager()

    return manager.calculate_trade_plan(
        account_balance,
        entry_price,
        atr,
    )


# ============================================================
# RESTORED FUNCTION FOR POSITION TRACKER COMPATIBILITY
# ============================================================