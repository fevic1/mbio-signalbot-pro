# core/regime.py
import logging
import numpy as np
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# Simple cache to avoid recomputing regime for identical data
_cache = {}
_cache_size = 50

def _hash_data(data: Dict) -> int:
    """Create a hash from the last 10 candles to detect changes."""
    candles = data.get("candles", [])
    if not candles:
        return 0
    # use last 10 closes and timestamps
    key = tuple((c[0], c[4]) for c in candles[-10:])  # timestamp, close
    return hash(key)

def compute_adx(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> float:
    """Compute Average Directional Index (ADX)."""
    if len(high) < period + 1:
        return 0.0
    
    # True Range
    tr1 = high[1:] - low[1:]
    tr2 = np.abs(high[1:] - close[:-1])
    tr3 = np.abs(low[1:] - close[:-1])
    tr = np.maximum(tr1, np.maximum(tr2, tr3))
    atr = np.convolve(tr, np.ones(period)/period, mode='valid')[-1]
    
    # +DM and -DM
    up_move = high[1:] - high[:-1]
    down_move = low[:-1] - low[1:]
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    
    # Smoothed DM and TR
    plus_di = 100 * np.convolve(plus_dm, np.ones(period)/period, mode='valid')[-1] / atr
    minus_di = 100 * np.convolve(minus_dm, np.ones(period)/period, mode='valid')[-1] / atr
    dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di + 1e-8)
    adx = np.convolve(dx, np.ones(period)/period, mode='valid')[-1]
    return float(adx)

def compute_atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> float:
    """Compute Average True Range as a ratio of current close."""
    if len(high) < period:
        return 0.0
    tr1 = high[1:] - low[1:]
    tr2 = np.abs(high[1:] - close[:-1])
    tr3 = np.abs(low[1:] - close[:-1])
    tr = np.maximum(tr1, np.maximum(tr2, tr3))
    atr = np.convolve(tr, np.ones(period)/period, mode='valid')[-1]
    return float(atr / close[-1])  # as percentage of price


def detect_regime(df_4h):
    """
    Institutional Regime Detection using standard 0-100 ADX and ATR%.
    """
    try:
        import pandas_ta as ta
        if df_4h is None or len(df_4h) < 20:
            return "RANGING"
            
        adx_df = ta.adx(df_4h["high"], df_4h["low"], df_4h["close"], length=14)
        if adx_df is None or "ADX_14" not in adx_df.columns:
            return "RANGING"
            
        adx = float(adx_df["ADX_14"].iloc[-1])
        atr = float(ta.atr(df_4h["high"], df_4h["low"], df_4h["close"], length=14).iloc[-1])
        atr_pct = atr / float(df_4h["close"].iloc[-1])
        
        if adx > 25:
            return "TRENDING"
        if atr_pct > 0.03:
            return "VOLATILE"
        return "RANGING"
    except Exception as e:
        return "RANGING"

