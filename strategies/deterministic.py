from .base import BaseStrategy

class DeterministicStrategy(BaseStrategy):
    """First-class citizen for deep oversold/overbought math."""
    def __init__(self):
        super().__init__("Deterministic")

    def calculate_signal(self, data: dict) -> tuple:
        rsi_1d = float(data.get("1d", {}).get("rsi", 50))
        rsi_1h = float(data.get("1h", {}).get("rsi", 50))
        
        if rsi_1d < 30 and rsi_1h < 55:
            return "BUY", 95
        if rsi_1d > 70 and rsi_1h > 65:
            return "SELL", 95
        return "HOLD", 0
