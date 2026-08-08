"""
Institutional DCA Strategy Engine (v2.1)
"""

import logging
from dataclasses import dataclass
from typing import Dict, Tuple

logger = logging.getLogger("InstitutionalDcaStrategy")


@dataclass
class DCAConfig:
    """Profitable RR config: SL 2.5x ATR vs TP1 4.0x ATR = 1.6:1 minimum."""
    MAX_SAFETY_ORDERS: int = 4
    BASE_ATR_MULT: float = 1.5
    STEP_EXPONENT: float = 1.2
    VOLUME_MULTIPLIER: float = 1.5
    
    # FIXED: Was 1.5/3.0/4.5 vs SL=4.0 (toxic 0.375:1). 
    # Now 4.0/7.0/10.0 vs SL=2.5 = 1.6:1 → 4:1 scaling.
    TP1_MULT: float = 4.0
    TP2_MULT: float = 7.0
    TP3_MULT: float = 10.0
    SL_ATR_MULT: float = 2.5
    TRAILING_ATR_MULT: float = 1.5
    
    TP1_CLOSE_PCT: float = 0.35
    TP2_CLOSE_PCT: float = 0.35
    TP3_CLOSE_PCT: float = 0.30
    TAKER_FEE_PCT: float = 0.0006
    SLIPPAGE_PCT: float = 0.0003


@dataclass
class PositionState:
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

    def __post_init__(self):
        if self.trailing_stop == 0.0:
            self.trailing_stop = self.entry_price * 0.95 if self.side == "LONG" else self.entry_price * 1.05


class InstitutionalDcaStrategy:
    def __init__(self):
        self.name = "INSTITUTIONAL_DCA"
        self.config = DCAConfig()
        self.positions: Dict[str, PositionState] = {}

    def calculate_next_layer(self, pos: PositionState, layer: int, atr: float) -> Tuple[float, float]:
        """Anchor spacing from ORIGINAL entry_price to prevent compounding drift."""
        anchor = pos.entry_price
        step_distance = atr * self.config.BASE_ATR_MULT * (self.config.STEP_EXPONENT ** (layer - 1))
        target_price = anchor - step_distance if pos.side == "LONG" else anchor + step_distance
        next_size = pos.size * (self.config.VOLUME_MULTIPLIER ** layer)
        return float(target_price), float(next_size)

    def process_exits(self, pos: PositionState, current_price: float, atr: float) -> Tuple[bool, str, float]:
        side = pos.side
        entry_avg = pos.entry_price

        tp1 = entry_avg + atr * self.config.TP1_MULT if side == "LONG" else entry_avg - atr * self.config.TP1_MULT
        tp2 = entry_avg + atr * self.config.TP2_MULT if side == "LONG" else entry_avg - atr * self.config.TP2_MULT
        tp3 = entry_avg + atr * self.config.TP3_MULT if side == "LONG" else entry_avg - atr * self.config.TP3_MULT
        sl = entry_avg - atr * self.config.SL_ATR_MULT if side == "LONG" else entry_avg + atr * self.config.SL_ATR_MULT

        # 1. Emergency Stop Loss
        if (side == "LONG" and current_price <= sl) or (side == "SHORT" and current_price >= sl):
            return True, "EMERGENCY_STOP", 1.0

        # 2. Trailing Stop (after TP1)
        if pos.tp1_hit and pos.trailing_stop > 0:
            if (side == "LONG" and current_price <= pos.trailing_stop) or (side == "SHORT" and current_price >= pos.trailing_stop):
                return True, "TRAILING_STOP", 1.0

        # 3. TP3 (Full close) — requires TP2 hit first
        if pos.tp2_hit:
            if (side == "LONG" and current_price >= tp3) or (side == "SHORT" and current_price <= tp3):
                return True, "TAKE_PROFIT_3", self.config.TP3_CLOSE_PCT

        # 4. TP2 (Partial) — requires TP1 hit first
        if pos.tp1_hit and not pos.tp2_hit:
            if (side == "LONG" and current_price >= tp2) or (side == "SHORT" and current_price <= tp2):
                pos.tp2_hit = True  # FIX: set flag so TP3 unlocks
                logger.info(f"🎯 {pos.asset} TP2 hit @ ${current_price:.2f}")
                return True, "TAKE_PROFIT_2", self.config.TP2_CLOSE_PCT

        # 5. TP1 (Partial)
        if not pos.tp1_hit:
            if (side == "LONG" and current_price >= tp1) or (side == "SHORT" and current_price <= tp1):
                pos.tp1_hit = True  # FIX: set flag so trailing + TP2 unlock
                pos.trailing_stop = sl
                logger.info(f"🎯 {pos.asset} TP1 hit @ ${current_price:.2f} | Trailing armed @ ${pos.trailing_stop:.2f}")
                return True, "TAKE_PROFIT_1", self.config.TP1_CLOSE_PCT

        return False, "HOLD", 0.0

    def update_trailing_stop(self, pos: PositionState, current_price: float, atr: float):
        if not pos.tp1_hit:
            return
        if pos.side == "LONG":
            candidate = current_price - atr * self.config.TRAILING_ATR_MULT
            if candidate > pos.trailing_stop:
                pos.trailing_stop = candidate
                logger.info(f"📈 {pos.asset} Trailing stop raised to ${pos.trailing_stop:.2f}")
        else:
            candidate = current_price + atr * self.config.TRAILING_ATR_MULT
            if candidate < pos.trailing_stop:
                pos.trailing_stop = candidate
                logger.info(f"📉 {pos.asset} Trailing stop lowered to ${pos.trailing_stop:.2f}")

    def get_rr_ratio(self, atr: float) -> float:
        sl_dist = atr * self.config.SL_ATR_MULT
        tp1_dist = atr * self.config.TP1_MULT
        return round(tp1_dist / sl_dist, 2) if sl_dist > 0 else 0.0

    def record_meta_learning(self, asset: str, side: str, pnl: float, reason: str):
        try:
            from core.signal_generator import save_meta_learning_data
            save_meta_learning_data(asset=asset, strategy=self.name, signal=side, confidence=100, pnl=pnl, reason=reason)
            logger.info(f"🧠 Meta-learning recorded for {asset}: {reason} ({pnl:.2f})")
        except Exception as e:
            logger.error(f"❌ Failed to record meta-learning: {e}")
