import logging
import numpy as np
from .base import BaseStrategy

logger = logging.getLogger(__name__)

class MomentumStrategy(BaseStrategy):
    def __init__(self, fast_period: int = 20, slow_period: int = 50, filter_period: int = 50):
        super().__init__("Momentum")
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.filter_period = filter_period

    def calculate_signal(self, data: dict) -> tuple:
        candles = data.get("1h", {}).get("candles")
        if not candles or len(candles) < self.filter_period:
            logger.warning(f"{self.name}: insufficient candle data")
            return "HOLD", 0

        closes = np.array([c[4] for c in candles])
        fast_ema = self._ema(closes, self.fast_period)
        slow_ema = self._ema(closes, self.slow_period)
        sma_filter = np.mean(closes[-self.filter_period:])

        if len(fast_ema) < 2 or len(slow_ema) < 2:
            return "HOLD", 0

        fast_curr, fast_prev = fast_ema[-1], fast_ema[-2]
        slow_curr, slow_prev = slow_ema[-1], slow_ema[-2]
        price = closes[-1]

        was_below = fast_prev <= slow_prev
        now_above = fast_curr > slow_curr
        was_above = fast_prev >= slow_prev
        now_below = fast_curr < slow_curr

        if was_below and now_above and price > sma_filter:
            confidence = min(100, 60 + (fast_curr - slow_curr) / slow_curr * 100)
            return "BUY", int(confidence)
        elif was_above and now_below and price < sma_filter:
            confidence = min(100, 60 + (slow_curr - fast_curr) / slow_curr * 100)
            return "SELL", int(confidence)
        return "HOLD", 0

    @staticmethod
    def _ema(values, period):
        alpha = 2 / (period + 1)
        ema = [values[0]]
        for v in values[1:]:
            ema.append(alpha * v + (1 - alpha) * ema[-1])
        return np.array(ema)
