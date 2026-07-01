"""
Sideways Grid Strategy Engine v1
Manual activation + automated grid matrix calculation + boundary protection.
Assets: Configurable (Ideal for XRP, DOGE, AVAX).
"""
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

logger = logging.getLogger("SidewaysGridStrategy")

@dataclass
class GridConfig:
    GRID_LEVELS: int = 8
    ATR_RANGE_MULT: float = 2.0       # Grid spans +/- 2 ATR from current price
    PROFIT_PCT: float = 0.003         # 0.3% take profit per grid cell
    CANCEL_BOUNDARY_ATR: float = 3.0  # Cancel all grids if price breaks 3 ATR from center

@dataclass
class GridState:
    asset: str
    center_price: float
    upper_bound: float
    lower_bound: float
    grid_levels: List[float] = field(default_factory=list)
    active_orders: Dict[float, str] = field(default_factory=dict)

class SidewaysGridStrategy:
    def __init__(self):
        self.name = "SIDEWAYS_GRID"
        self.config = GridConfig()
        self.grids: Dict[str, GridState] = {}

    def calculate_grid(self, current_price: float, atr: float) -> Tuple[float, float, List[float]]:
        """Calculate the upper/lower bounds and individual grid price levels."""
        upper = current_price + (atr * self.config.ATR_RANGE_MULT)
        lower = current_price - (atr * self.config.ATR_RANGE_MULT)
        step = (upper - lower) / self.config.GRID_LEVELS
        levels = [round(lower + (i * step), 6) for i in range(self.config.GRID_LEVELS + 1)]
        return upper, lower, levels

    def check_boundary_break(self, state: GridState, current_price: float, atr: float) -> bool:
        """Check if price has broken out of the ranging market, requiring grid cancellation."""
        boundary_limit = state.center_price + (atr * self.config.CANCEL_BOUNDARY_ATR)
        lower_limit = state.center_price - (atr * self.config.CANCEL_BOUNDARY_ATR)
        return current_price > boundary_limit or current_price < lower_limit
