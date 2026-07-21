"""
Dynamic Regime Analyzer
Integrates GTJA-191 factors to provide real-time, non-hardcoded market regime detection.
"""
import pandas as pd
import logging
from typing import Optional, Dict, Any
from core.factors.gtja_191 import GTJA191Factors
from core.factors.regime_detector import FactorRegimeDetector, MarketRegime

logger = logging.getLogger(__name__)

class RegimeAnalyzer:
    """
    Analyzes market regime dynamically based on configurable lookback periods.
    No hardcoded asset limits or rigid thresholds.
    """
    def __init__(self, lookback: int = 20):
        self.lookback = lookback
        self.factor_calc = GTJA191Factors()
        self.detector = FactorRegimeDetector(lookback=lookback)

    def analyze(self, candles: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Analyzes a DataFrame of OHLCV candles and returns the current regime score.
        
        Args:
            candles: DataFrame with columns ['open', 'high', 'low', 'close', 'volume']
            
        Returns:
            Dict containing regime, confidence, and component scores, or None if insufficient data.
        """
        if candles is None or len(candles) < self.lookback:
            logger.debug("Insufficient data for regime analysis.")
            return None

        try:
            # 1. Calculate factors (vectorized, O(N) performance)
            factors = self.factor_calc.calculate_all(candles)
            
            # 2. Detect regime
            score = self.detector.calculate_regime_score(factors)
            
            if score is None:
                return None

            return {
                "regime": score.regime.value,
                "confidence": score.confidence,
                "momentum": score.momentum_score,
                "volatility": score.volatility_score,
                "mean_reversion": score.mean_reversion_score
            }
        except Exception as e:
            logger.error(f"Regime analysis failed: {e}", exc_info=True)
            return None
