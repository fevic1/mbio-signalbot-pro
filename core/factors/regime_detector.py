"""
Factor-Based Market Regime Detection
Uses composite GTJA-191 factor scores to identify TRENDING, RANGING, or BREAKOUT regimes.
"""
import pandas as pd
import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class MarketRegime(Enum):
    TRENDING = "TRENDING"
    RANGING = "RANGING"
    BREAKOUT = "BREAKOUT"

@dataclass
class RegimeScore:
    regime: MarketRegime
    confidence: float
    momentum_score: float
    volatility_score: float
    mean_reversion_score: float

class FactorRegimeDetector:
    """
    Detects market regimes using a weighted composite of GTJA-191 factors.
    - High momentum + low volatility = TRENDING
    - Low momentum + high mean-reversion = RANGING
    - High volatility + shifting momentum = BREAKOUT
    """
    
    def __init__(self, lookback: int = 20):
        self.lookback = lookback
        # Weights for regime classification
        self.weights = {
            'momentum': 0.4,
            'volatility': 0.3,
            'mean_reversion': 0.3
        }
    
    def calculate_regime_score(self, factors: pd.DataFrame) -> Optional[RegimeScore]:
        """
        Calculate composite regime score from a DataFrame of calculated factors.
        """
        if factors.empty or len(factors) < self.lookback:
            return None

        # 1. Calculate rolling component scores
        momentum = factors['f001'].rolling(self.lookback).mean()
        volatility = factors['f020'].rolling(self.lookback).std()
        mean_reversion = factors['f042'].rolling(self.lookback).mean()

        # 2. Normalize scores to 0-1 range using rolling min/max
        def normalize(series: pd.Series) -> pd.Series:
            min_val = series.rolling(self.lookback).min()
            max_val = series.rolling(self.lookback).max()
            denom = max_val - min_val
            denom = denom.replace(0, 1) # Avoid division by zero
            return (series - min_val) / denom

        momentum_score = normalize(momentum)
        volatility_score = normalize(volatility)
        # Invert mean reversion for composite (high mean reversion = low trend)
        mean_reversion_score = 1 - normalize(mean_reversion)

        # 3. Calculate composite score
        composite = (
            self.weights['momentum'] * momentum_score +
            self.weights['volatility'] * volatility_score +
            self.weights['mean_reversion'] * mean_reversion_score
        )

        # 4. Determine regime based on thresholds
        latest_composite = composite.iloc[-1]
        latest_vol = volatility_score.iloc[-1]

        if latest_vol > 0.8 and abs(latest_composite - 0.5) < 0.2:
            regime = MarketRegime.BREAKOUT
        elif latest_composite > 0.65:
            regime = MarketRegime.TRENDING
        elif latest_composite < 0.35:
            regime = MarketRegime.RANGING
        else:
            regime = MarketRegime.BREAKOUT # Default to breakout for uncertain mid-range

        # 5. Calculate confidence (distance from the neutral 0.5 mark)
        confidence = abs(latest_composite - 0.5) * 2

        return RegimeScore(
            regime=regime,
            confidence=round(float(confidence), 4),
            momentum_score=round(float(momentum_score.iloc[-1]), 4),
            volatility_score=round(float(volatility_score.iloc[-1]), 4),
            mean_reversion_score=round(float(mean_reversion_score.iloc[-1]), 4)
        )
