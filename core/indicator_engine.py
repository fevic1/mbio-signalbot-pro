"""
core/indicator_engine.py — Technical indicator calculation.
Pure functions only. No API calls, no state, no side effects.
"""
import logging
import pandas as pd

import numpy as np
import pandas as pd

def _native_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def _native_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    prev_close = close.shift(1)
    tr = np.maximum(high - low, np.maximum(abs(high - prev_close), abs(low - prev_close)))
    return tr.rolling(window=period, min_periods=period).mean()

def _native_bbands(series: pd.Series, period: int = 20, std_dev: float = 2.0):
    sma = series.rolling(window=period, min_periods=period).mean()
    std = series.rolling(window=period, min_periods=period).std()
    upper = sma + std_dev * std
    lower = sma - std_dev * std
    return upper, sma, lower

def _native_ema(series: pd.Series, period: int = 20) -> pd.Series:
    return series.ewm(span=period, adjust=False, min_periods=period).mean()

def _native_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = _native_ema(series, fast)
    ema_slow = _native_ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = _native_ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram



logger = logging.getLogger(__name__)

def safe_get_col(df: pd.DataFrame, prefix: str) -> str | None:
    """Find a column name that starts with the given prefix (case-insensitive)."""
    if df is None or df.empty:
        return None
    for col in df.columns:
        if col.lower().startswith(prefix.lower()):
            return col
    return None

def apply_indicators(
    df: pd.DataFrame,
    include_bb: bool = False,
    include_atr: bool = False,
) -> pd.DataFrame:
    """
    Apply RSI, MACD, and optionally BB + ATR to a DataFrame.
    Uses pure native pandas/numpy calculations — no pandas-ta dependency.
    Returns the DataFrame with indicator columns appended.
    Requires at least 14 rows.
    """
    if df is None or df.empty or len(df) < 14:
        return df

    try:
        close_col = safe_get_col(df, "close")
        high_col = safe_get_col(df, "high")
        low_col = safe_get_col(df, "low")

        if not close_col:
            logger.warning("⚠️ No close column found in DataFrame")
            return df

        # RSI (always applied)
        df["rsi_14"] = _native_rsi(df[close_col], period=14)

        # MACD (always applied)
        macd_line, signal_line, histogram = _native_macd(df[close_col])
        df["macd_12_26_9"] = macd_line
        df["macds_12_26_9"] = signal_line
        df["macdh_12_26_9"] = histogram

        # Bollinger Bands (optional)
        if include_bb:
            bb_upper, bb_mid, bb_lower = _native_bbands(df[close_col], period=20)
            df["bbu_20_2.0"] = bb_upper
            df["bbm_20_2.0"] = bb_mid
            df["bbl_20_2.0"] = bb_lower

        # ATR (optional)
        if include_atr and high_col and low_col:
            df["atr_14"] = _native_atr(df[high_col], df[low_col], df[close_col], period=14)

    except Exception as e:
        logger.warning(f"Indicator calculation failed: {e}")

    return df

def extract_timeframe_data(df: pd.DataFrame, fallback_price: float = 100.0) -> dict:
    """
    Extract the latest indicator values from a prepared DataFrame.
    Returns a dict with: price, rsi, macd, bb_upper, bb_lower, atr.
    Falls back to neutral defaults if data is missing.
    """
    if df is None or df.empty:
        return _fallback(fallback_price)
    
    latest = df.iloc[-1]
    close_val = float(latest.get("close", fallback_price))
    if close_val == 0:
        return _fallback(fallback_price)

    return {
        "price":    round(close_val, 4),
        "rsi":      _safe_float(latest, safe_get_col(df, "rsi_"), 50.0),
        "macd":     _safe_float(latest, safe_get_col(df, "macd_"), 0.0, decimals=4),
        "bb_upper": _safe_float(latest, safe_get_col(df, "bbu_"), round(close_val * 1.05, 4)),
        "bb_lower": _safe_float(latest, safe_get_col(df, "bbl_"), round(close_val * 0.95, 4)),
        "atr":      _safe_float(latest, safe_get_col(df, "atr_"), round(close_val * 0.02, 4)),
    }

def _safe_float(row, col: str | None, default: float, decimals: int = 2) -> float:
    if col is None:
        return round(default, decimals)
    try:
        return round(float(row.get(col, default)), decimals)
    except (TypeError, ValueError):
        return round(default, decimals)

def _fallback(price: float) -> dict:
    return {
        "price":    price,
        "rsi":      50.0,
        "macd":     0.0,
        "bb_upper": round(price * 1.05, 4),
        "bb_lower": round(price * 0.95, 4),
        "atr":      round(price * 0.02, 4),
    }

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Flatten MultiIndex columns and lowercase all column names."""
    if df is None or df.empty:
        return df
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [col.lower() for col in df.columns]
    return df

def resample_to_4h(df_1h: pd.DataFrame) -> pd.DataFrame:
    """Resample a 1H DataFrame to 4H OHLCV candles."""
    if df_1h is None or df_1h.empty:
        return pd.DataFrame()
    try:
        df_4h = df_1h.resample("4h").agg(
            {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
        ).dropna()
        return df_4h[df_4h["close"] > 0]
    except Exception as e:
        logger.warning(f"4H resample failed: {e}")
        return pd.DataFrame()
