import logging
from .base import BaseStrategy

logger = logging.getLogger(__name__)

class CarryStrategy(BaseStrategy):
    """
    Momentum-based strategy with RSI guards to prevent selling the bottom 
    or buying the top during volatile mean-reversion setups.
    """
    def __init__(self, momentum_period: int = 20, threshold: float = 0.03):
        super().__init__("Carry")
        self.momentum_period = momentum_period
        self.threshold = threshold

    def calculate_signal(self, data: dict) -> tuple:
        candles = data.get("1h", {}).get("candles")
        if not candles or len(candles) < self.momentum_period + 1:
            return "HOLD", 0

        # 🛡️ RSI FILTER: Prevent momentum from fighting mean-reversion
        rsi_1h = float(data.get("1h", {}).get("rsi", 50.0))
        rsi_1d = float(data.get("1d", {}).get("rsi", 50.0))

        closes = [c[4] for c in candles]
        current_price = closes[-1]
        past_price = closes[-self.momentum_period - 1]
        
        momentum = (current_price - past_price) / past_price
        
        if momentum > self.threshold:
            # Block BUY if already overbought
            if rsi_1h > 65 or rsi_1d > 70:
                return "HOLD", 0
            confidence = int(50 + (momentum / self.threshold) * 20)
            return "BUY", min(85, confidence)
            
        elif momentum < -self.threshold:
            # Block SELL if already oversold (FIXES THE INVERSION BUG)
            if rsi_1h < 40 or rsi_1d < 40:
                return "HOLD", 0
            confidence = int(50 + (abs(momentum) / self.threshold) * 20)
            return "SELL", min(85, confidence)
        
        return "HOLD", 0
