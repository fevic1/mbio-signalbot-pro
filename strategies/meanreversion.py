import logging
import numpy as np
from .base import BaseStrategy

logger = logging.getLogger(__name__)

class MeanReversionStrategy(BaseStrategy):
    def __init__(self, bb_period: int = 20, bb_std: float = 2.0, rsi_period: int = 14):
        super().__init__("MeanReversion")
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.rsi_period = rsi_period

    def calculate_signal(self, data: dict) -> tuple:
        candles = data.get("1h", {}).get("candles")
        if not candles or len(candles) < self.bb_period + self.rsi_period:
            return "HOLD", 0

        closes = np.array([c[4] for c in candles])
        current_price = closes[-1]

        sma = np.mean(closes[-self.bb_period:])
        std = np.std(closes[-self.bb_period:])
        upper_band = sma + self.bb_std * std
        lower_band = sma - self.bb_std * std

        rsi = self._compute_rsi(closes, self.rsi_period)
        if rsi is None:
            return "HOLD", 0

        band_width = upper_band - lower_band
        if band_width == 0:
            return "HOLD", 0

        dist_to_lower = (current_price - lower_band) / band_width
        dist_to_upper = (upper_band - current_price) / band_width

        # Conservative: only trigger on extreme conditions
        if current_price <= lower_band and rsi < 30:
            conf = int(60 + (30 - rsi) * 1.5 + (1 - dist_to_lower) * 20)
            return "BUY", min(85, conf)  # Cap at 85% to avoid sniper override
        elif current_price >= upper_band and rsi > 70:
            conf = int(60 + (rsi - 70) * 1.5 + (1 - dist_to_upper) * 20)
            return "SELL", min(85, conf)  # Cap at 85%
        
        return "HOLD", 0

    @staticmethod
    def _compute_rsi(closes, period=14):
        if len(closes) < period + 1:
            return None
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
