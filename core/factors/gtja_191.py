"""
GTJA-191 Factor Library for Crypto Markets
Implements foundational time-series operators and the first 5 GTJA factors.
Optimized for vectorized pandas/numpy calculations.
"""
import pandas as pd
import numpy as np
from typing import Union

# --- WorldQuant Time-Series Operators ---

def delay(df: pd.Series, period: int) -> pd.Series:
    """Lag the series by `period` days."""
    return df.shift(period)

def delta(df: pd.Series, period: int) -> pd.Series:
    """Difference between current value and value `period` days ago."""
    return df - df.shift(period)

def ts_min(df: pd.Series, period: int) -> pd.Series:
    """Rolling minimum over `period` days."""
    return df.rolling(window=period, min_periods=1).min()

def ts_max(df: pd.Series, period: int) -> pd.Series:
    """Rolling maximum over `period` days."""
    return df.rolling(window=period, min_periods=1).max()

def ts_rank(df: pd.Series, period: int) -> pd.Series:
    """Rolling rank percentile over `period` days."""
    return df.rolling(window=period, min_periods=1).apply(
        lambda x: x.rank(pct=True).iloc[-1], raw=False
    )

def correlation(x: pd.Series, y: pd.Series, period: int) -> pd.Series:
    """Rolling correlation between x and y over `period` days."""
    return x.rolling(window=period, min_periods=1).corr(y)

def decay_linear(df: pd.Series, period: int) -> pd.Series:
    """Linearly weighted moving average over `period` days."""
    weights = np.array(range(1, period + 1), dtype=float)
    weights /= weights.sum()
    return df.rolling(window=period, min_periods=1).apply(
        lambda x: np.dot(x, weights), raw=True
    )

def rank(df: pd.Series) -> pd.Series:
    """Cross-sectional rank (percentile) of the series."""
    return df.rank(pct=True)


# --- GTJA-191 Factor Implementations ---

class GTJA191Factors:
    """Vectorized implementations of GTJA-191 factors for crypto OHLCV data."""

    @staticmethod
    def factor_001_returns(close: pd.Series) -> pd.Series:
        """
        Factor 001: Asset Returns (Momentum)
        Formula: (close / delay(close, 1)) - 1
        """
        return (close / delay(close, 1)) - 1

    @staticmethod
    def factor_006_volume_weighted(open: pd.Series, volume: pd.Series) -> pd.Series:
        """
        Factor 006: Volume Weighted Price
        Formula: -1 * correlation(open, volume, 10)
        """
        return -1 * correlation(open, volume, 10)

    @staticmethod
    def factor_012_volume_momentum(volume: pd.Series, close: pd.Series) -> pd.Series:
        """
        Factor 012: Volume Momentum
        Formula: sign(delta(volume, 1)) * (-delta(close, 1))
        """
        return np.sign(delta(volume, 1)) * (-delta(close, 1))

    @staticmethod
    def factor_020_realized_volatility(close: pd.Series) -> pd.Series:
        """
        Factor 020: Realized Volatility
        Formula: -1 * delta(log(close), 5)
        """
        return -1 * delta(np.log(close), 5)

    @staticmethod
    def factor_042_price_reversal(high: pd.Series, low: pd.Series) -> pd.Series:
        """
        Factor 042: Price Reversal (Mean Reversion)
        Formula: -1 * delta(high - low, 1) / (high - low)
        """
        hl_range = high - low
        # Avoid division by zero
        hl_range = hl_range.replace(0, np.nan)
        return -1 * delta(hl_range, 1) / hl_range

    @classmethod
    def calculate_all(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all implemented factors for a given OHLCV DataFrame."""
        factors = pd.DataFrame(index=df.index)
        
        factors['f001'] = cls.factor_001_returns(df['close'])
        factors['f006'] = cls.factor_006_volume_weighted(df['open'], df['volume'])
        factors['f012'] = cls.factor_012_volume_momentum(df['volume'], df['close'])
        factors['f020'] = cls.factor_020_realized_volatility(df['close'])
        factors['f042'] = cls.factor_042_price_reversal(df['high'], df['low'])
        
        return factors
