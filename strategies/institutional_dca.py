"""
Institutional DCA Strategy Engine (v2)
Designed for manual entry with automated averaging, exit, and meta-learning.
Assets: BTC, ETH only.
"""
import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger("InstitutionalDcaStrategy")


@dataclass
class DCAConfig:
    """Configuration for DCA operations."""
    MAX_SAFETY_ORDERS: int = 4
    BASE_ATR_MULT: float = 1.5
    STEP_EXPONENT: float = 1.2
    VOLUME_MULTIPLIER: float = 1.5
    TP1_MULT: float = 1.5
    TP2_MULT: float = 3.0
    TP3_MULT: float = 4.5
    SL_ATR_MULT: float = 4.0
    TRAILING_ATR_MULT: float = 1.0
    TP1_CLOSE_PCT: float = 0.35
    TP2_CLOSE_PCT: float = 0.35
    TP3_CLOSE_PCT: float = 0.30
    TAKER_FEE_PCT: float = 0.0006
    SLIPPAGE_PCT: float = 0.0003


@dataclass
class PositionState:
    """Mutable state for an active DCA position."""
    asset: str
    side: str
    size: float
    entry_price: float
    active_so_count: int
    last_order_price: float
    tp1_hit: bool = False
    tp2_hit: bool = False
    trailing_stop: float = 0.0
    bars_held: int = 0


class InstitutionalDcaStrategy:
    def __init__(self):
        self.name = "INSTITUTIONAL_DCA"
        self.config = DCAConfig()
        self.positions: Dict[str, PositionState] = {}

    def calculate_next_layer(self, pos: PositionState, layer: int, atr: float) -> Tuple[float, float]:
        """Calculate next safety order price and size."""
        base_anchor = pos.last_order_price
        step_distance = atr * self.config.BASE_ATR_MULT * (self.config.STEP_EXPONENT ** (layer - 1))
        target_price = base_anchor - step_distance if pos.side == "LONG" else base_anchor + step_distance
        next_size = pos.size * (self.config.VOLUME_MULTIPLIER ** layer) / (self.config.VOLUME_MULTIPLIER ** (pos.active_so_count))
        return float(target_price), float(next_size)

    def process_exits(self, pos: PositionState, current_price: float, atr: float) -> Tuple[bool, str, float]:
        """Check for exit conditions. Returns (should_exit, reason, close_pct)."""
        side = pos.side
        entry_avg = pos.entry_price

        tp1 = entry_avg + atr * self.config.TP1_MULT if side == "LONG" else entry_avg - atr * self.config.TP1_MULT
        tp2 = entry_avg + atr * self.config.TP2_MULT if side == "LONG" else entry_avg - atr * self.config.TP2_MULT
        tp3 = entry_avg + atr * self.config.TP3_MULT if side == "LONG" else entry_avg - atr * self.config.TP3_MULT
        sl = entry_avg - atr * self.config.SL_ATR_MULT if side == "LONG" else entry_avg + atr * self.config.SL_ATR_MULT

        # 1. Emergency Stop Loss
        if (side == "LONG" and current_price <= sl) or (side == "SHORT" and current_price >= sl):
            return True, "EMERGENCY_STOP", 1.0

        # 2. Trailing Stop (Active after TP1)
        if pos.tp1_hit and pos.trailing_stop > 0:
            if (side == "LONG" and current_price <= pos.trailing_stop) or (side == "SHORT" and current_price >= pos.trailing_stop):
                return True, "TRAILING_STOP", 1.0

        # 3. Take Profit 3 (Full Close)
        if pos.tp2_hit:
            if (side == "LONG" and current_price >= tp3) or (side == "SHORT" and current_price <= tp3):
                return True, "TAKE_PROFIT_3", 1.0

        # 4. Take Profit 2 (Partial)
        if pos.tp1_hit and not pos.tp2_hit:
            if (side == "LONG" and current_price >= tp2) or (side == "SHORT" and current_price <= tp2):
                return True, "TAKE_PROFIT_2", self.config.TP2_CLOSE_PCT

        # 5. Take Profit 1 (Partial)
        if not pos.tp1_hit:
            if (side == "LONG" and current_price >= tp1) or (side == "SHORT" and current_price <= tp1):
                return True, "TAKE_PROFIT_1", self.config.TP1_CLOSE_PCT

        return False, "HOLD", 0.0

    def update_trailing_stop(self, pos: PositionState, current_price: float, atr: float):
        """Update trailing stop if price moves in favor."""
        if not pos.tp1_hit:
            return
        candidate = current_price - atr * self.config.TRAILING_ATR_MULT if pos.side == "LONG" else current_price + atr * self.config.TRAILING_ATR_MULT
        if pos.side == "LONG":
            pos.trailing_stop = max(pos.trailing_stop, candidate)
        else:
            pos.trailing_stop = min(pos.trailing_stop, candidate)

    def record_meta_learning(self, asset: str, side: str, pnl: float, reason: str):
        """Record trade outcome to ChromaDB for meta-learning."""
        try:
            from core.signal_generator import save_meta_learning_data
            save_meta_learning_data(
                asset=asset,
                strategy=self.name,
                signal=side,
                confidence=100,
                pnl=pnl,
                reason=reason
            )
            logger.info(f"🧠 Meta-learning recorded for {asset}: {reason} ({pnl:.2f})")
        except Exception as e:
            logger.error(f"❌ Failed to record meta-learning: {e}")
