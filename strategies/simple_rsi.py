import logging
from .base import BaseStrategy

logger = logging.getLogger(__name__)

class SimpleRSIStrategy(BaseStrategy):
    def __init__(self, oversold=35, overbought=65):
        super().__init__("SimpleRSI")
        self.oversold = oversold
        self.overbought = overbought

    def calculate_signal(self, data: dict) -> tuple:
        rsi = data.get("1h", {}).get("rsi", 50)
        if rsi < self.oversold:
            confidence = int(60 + (self.oversold - rsi) * 2)
            return "BUY", min(90, confidence)
        elif rsi > self.overbought:
            confidence = int(60 + (rsi - self.overbought) * 2)
            return "SELL", min(90, confidence)
        return "HOLD", 0
