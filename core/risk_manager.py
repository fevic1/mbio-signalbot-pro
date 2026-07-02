"""
core/risk_manager.py — Institutional-grade risk controls for MBIO SignalBot
"""

import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class RiskManager:
    """
    Manages position sizing, exposure limits, and correlation blocking.
    """

    def __init__(
        self,
        max_risk_per_trade_pct: float = 0.02,
        max_total_risk_pct: float = 0.20,
        max_total_exposure_pct: float = 5.0,  # 500% notional exposure
    ):
        self.max_risk_per_trade_pct = max_risk_per_trade_pct
        self.max_total_risk_pct = max_total_risk_pct
        self.max_total_exposure_pct = max_total_exposure_pct

        self.correlated_groups: Dict[str, List[str]] = {}

        logger.info(
            "✅ RiskManager initialized: "
            f"risk/trade={self.max_risk_per_trade_pct*100:.1f}% "
            f"total_risk={self.max_total_risk_pct*100:.1f}% "
            f"max_exposure={self.max_total_exposure_pct*100:.0f}%"
        )

    # ============================================================
    # Correlation Controls
    # ============================================================

    def set_correlated_groups(self, groups: List[List[str]]) -> None:
        self.correlated_groups = {}

        for group in groups:
            for asset in group:
                self.correlated_groups[asset.upper()] = [
                    a.upper() for a in group
                ]

        logger.info(
            f"🔗 Correlation groups loaded: {len(self.correlated_groups)} assets"
        )

    def check_correlation_block(
        self,
        asset: str,
        open_positions: Dict,
    ) -> bool:
        asset = asset.upper()

        if asset not in self.correlated_groups:
            return False

        group = self.correlated_groups[asset]

        for held in open_positions.keys():
            if held.upper() in group and held.upper() != asset:
                logger.warning(
                    f"🚫 Correlation block: {asset} conflicts with {held}"
                )
                return True

        return False

    # ============================================================
    # Position Sizing
    # ============================================================

    def calculate_position_size(
        self,
        balance: float,
        entry_price: float,
        stop_loss: float,
        side: str = "BUY",
    ) -> float:
        if balance <= 0:
            return 0.0

        if entry_price <= 0 or stop_loss <= 0:
            return 0.0

        risk_distance = abs(entry_price - stop_loss)

        if risk_distance <= 0:
            return 0.0

        risk_amount = balance * self.max_risk_per_trade_pct

        size = risk_amount / risk_distance

        # Hard safety cap: max 50% account value per position
        max_size = (balance * float(config.get("risk_guard", {}).get("max_position_pct", 0.5))) / entry_price

        return max(0.0, min(size, max_size))

    # ============================================================
    # Exposure Controls
    # ============================================================

    def check_capital_usage(
        self,
        balance: float,
        new_size: float,
        new_entry: float,
        open_positions: Dict,
    ) -> Tuple[bool, str]:
        """
        Checks whether a new position would exceed
        the configured exposure limit.
        """

        if balance <= 0:
            return False, "Zero/negative balance"

        current_exposure = 0.0

        for pos in open_positions.values():
            size = float(pos.get("size", 0))
            entry = float(pos.get("entry", 0))

            current_exposure += size * entry

        new_exposure = float(new_size) * float(new_entry)

        total_exposure = current_exposure + new_exposure

        max_allowed = balance * self.max_total_exposure_pct

        if total_exposure > max_allowed:
            total_pct = (total_exposure / balance) * 100

            msg = (
                f"Capital limit: {total_pct:.1f}% would exceed "
                f"{self.max_total_exposure_pct*100:.0f}% max "
                f"(current=${current_exposure:.2f} + "
                f"new=${new_exposure:.2f})"
            )

            logger.warning(f"💸 {msg}")

            return False, msg

        return True, "OK"

    # ============================================================
    # Drawdown Protection
    # ============================================================

    def check_drawdown_halt(
        self,
        current_pnl_pct: float,
        halt_threshold: float = -15.0,
    ) -> bool:
        if current_pnl_pct <= halt_threshold:
            logger.error(
                f"🛑 Drawdown halt triggered "
                f"({current_pnl_pct:.2f}% <= {halt_threshold:.2f}%)"
            )
            return True

        return False

    # ============================================================
    # Helpers
    # ============================================================

    def get_max_position_value(self, balance: float) -> float:
        """
        Maximum total exposure allowed.
        """

        if balance <= 0:
            return 0.0

        return balance * self.max_total_exposure_pct

# ============================================================
# LEGACY WRAPPERS (main.py compatibility)
# ============================================================

_default_rm = RiskManager()


def calculate_position_size(
    account_balance: float,
    entry: float,
    sl: float,
    risk_pct: float = 0.02,
    **kwargs,
) -> float:
    rm = RiskManager(max_risk_per_trade_pct=risk_pct)
    return rm.calculate_position_size(
        balance=account_balance,
        entry_price=entry,
        stop_loss=sl,
    )


def calculate_trade_plan(
    price: float,
    atr: float,
    signal: str,
    sl_mult: float = 1.5,
    tp1_mult: float = 1.0,
    tp2_mult: float = 2.0,
    tp3_mult: float = 3.0,
    min_atr_pct: float = 0.02,
):
    if atr < price * min_atr_pct:
        atr = price * min_atr_pct

    side = 1 if "BUY" in signal.upper() else -1

    sl = price - (side * atr * sl_mult)
    tp1 = price + (side * atr * tp1_mult)
    tp2 = price + (side * atr * tp2_mult)
    tp3 = price + (side * atr * tp3_mult)

    return price, sl, tp1, tp2, tp3


def is_correlation_blocked(
    asset: str,
    correlated_groups: list,
) -> bool:
    import core.state as state

    asset = asset.upper()

    open_assets = {
        k.upper()
        for k in state.OPEN_POSITIONS.keys()
    }

    if asset in open_assets:
        return True

    for group in correlated_groups:
        group_set = {a.upper() for a in group}

        if asset in group_set and open_assets & group_set:
            return True

    return False


def is_drawdown_halted(
    threshold: float,
) -> bool:
    import core.state as state

    daily_pnl = getattr(state, "daily_pnl", 0.0)

    return _default_rm.check_drawdown_halt(
        current_pnl_pct=daily_pnl,
        halt_threshold=threshold,
    )
