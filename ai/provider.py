"""
AI Provider Interface
Abstract base for AI providers
"""
from abc import ABC, abstractmethod
from typing import Dict

class AIProvider(ABC):
    """Base class for AI providers"""
    
    def __init__(self, name: str, api_key: str, model: str, timeout: int = 30):
        self.name = name
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
    
    @abstractmethod
    async def analyze(self, asset: str, data: Dict) -> Dict:
        """
        Analyze market data and return signal
        Returns: {signal, confidence, reasoning}
        """
        pass
    
    def _build_prompt(self, asset: str, data: Dict) -> str:
        """Build analysis prompt"""
        return f"""Analyze {asset} for trading:
1H: Price={data['1h']['price']}, RSI={data['1h']['rsi']}, ATR={data['1h']['atr']}
4H: RSI={data['4h']['rsi']}
1D: RSI={data['1d']['rsi']}

Provide: signal (STRONG BUY/BUY/HOLD/SELL/STRONG SELL), confidence (0-100), reasoning (1 sentence of professional institutional analysis)
Format: SIGNAL|CONFIDENCE|REASONING"""
