"""
core/data_fetcher.py — Market data retrieval only.
Fetches OHLCV candles from Hyperliquid candle API (all coins).
yFinance removed — was returning empty responses from VPS IP.
Delegates indicator calculation to indicator_engine.
No AI calls. No trading decisions. No state mutations.
"""
import logging
import os
import time
import numpy as np
import pandas as pd
import requests
from core.indicator_engine import (
    apply_indicators,
    extract_timeframe_data,
    normalize_columns,
    resample_to_4h,
    _fallback,
)

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Ticker → HL coin name mapping
# ------------------------------------------------------------------
_TICKER_TO_COIN = {
    "BTC-USD": "BTC", "ETH-USD": "ETH", "SOL-USD": "SOL",
    "XRP-USD": "XRP", "DOGE-USD": "DOGE", "AVAX-USD": "AVAX",
    "LINK-USD": "LINK", "BNB-USD": "BNB", "HYPE-USD": "HYPE",
}

_TICKER_DEFAULTS = {
    "BTC-USD": 63000.0, "ETH-USD": 1700.0, "SOL-USD": 67.0,
    "XRP-USD": 1.17, "DOGE-USD": 0.087, "AVAX-USD": 15.0,
    "LINK-USD": 15.0, "BNB-USD": 600.0, "HYPE-USD": 60.0,
}


def _get_neutral_data(price: float = 100.0) -> dict:
    return {
        "price": price, "rsi": 50.0, "macd": 0.0,
        "bb_upper": price * 1.05, "bb_lower": price * 0.95,
        "atr": price * 0.02, "candles": [],
    }


def get_safe_fallback(price: float = 100.0) -> dict:
    neutral = _get_neutral_data(price)
    return {"1h": neutral.copy(), "4h": neutral.copy(), "1d": neutral.copy()}


# ------------------------------------------------------------------
# Hyperliquid helpers
# ------------------------------------------------------------------
def _hl_api_url() -> str:
    from hyperliquid.utils import constants
    network = os.getenv("HL_NETWORK", "MAINNET").upper()
    return constants.TESTNET_API_URL if network == "TESTNET" else constants.MAINNET_API_URL


def get_account_balance() -> float:
    """Fetch live account equity from Hyperliquid."""
    try:
        from hyperliquid.info import Info
        info = Info(_hl_api_url(), skip_ws=True)
        address = os.getenv("HL_ACCOUNT_ADDRESS", "")
        if not address:
            logger.warning("HL_ACCOUNT_ADDRESS not set — returning 0.0")
            return 0.0
        state = info.user_state(address)
        # Universal safe extraction: handle dict, SDK objects, and edge cases
        # Step 1: Extract margin_summary
        margin_summary = None
        if isinstance(state, dict):
            margin_summary = state.get("marginSummary")
        elif hasattr(state, "marginSummary"):
            margin_summary = getattr(state, "marginSummary", None)
        else:
            # Fallback: try dict-style get on any object (handles custom dict-like SDK responses)
            try:
                margin_summary = state.get("marginSummary") if hasattr(state, "get") else None
            except:
                margin_summary = None
        
        # Step 2: Extract account_value
        account_value = None
        if isinstance(margin_summary, dict):
            account_value = margin_summary.get("accountValue", 0)
        elif hasattr(margin_summary, "accountValue"):
            account_value = getattr(margin_summary, "accountValue", 0)
        else:
            # Fallback: try dict-style get
            try:
                account_value = margin_summary.get("accountValue") if hasattr(margin_summary, "get") else 0
            except:
                account_value = 0
        
        # UNCONDITIONAL FORCE LOG: Reveal account_value before condition
        # Step 3: Convert to float safely with diagnostic logging

        try:
            if account_value in (None, "", "0", 0, 0.0):
                balance = 0.0
                # Log diagnostic info only if balance is zero (avoid log spam)
                logger.info(f"🔍 DEBUG VISIBLE: state={type(state)}, margin_summary={margin_summary}, account_value={account_value}")
                # Also log specific checks
                if margin_summary:
                    logger.info(f"🔍 DEBUG VISIBLE: margin_summary keys={margin_summary.keys() if isinstance(margin_summary, dict) else dir(margin_summary)}")
            else:
                balance = float(account_value)
        except (ValueError, TypeError) as e:
            logger.warning(f"⚠️ Invalid accountValue: {account_value} (type: {type(account_value)}, error: {e})")
            balance = 0.0
        logger.info(f"💰 Account balance (Address: {address[:8]}...): ${balance:.2f}")
        return balance
    except Exception as e:
        logger.error(f"Balance fetch failed: {e}")
        return 0.0


def get_hype_price_from_hyperliquid() -> float:
    try:
        from hyperliquid.info import Info
        info = Info(_hl_api_url(), skip_ws=True)
        all_mids = info.all_mids()
        return float(all_mids.get("HYPE", 60.0))
    except Exception:
        return 60.0


def get_current_price(ticker_symbol: str) -> float:
    """Fetch the latest price for a ticker via HL allMids."""
    try:
        coin = _TICKER_TO_COIN.get(ticker_symbol, ticker_symbol.replace("-USD", ""))
        r = requests.post(
            "https://api.hyperliquid.xyz/info",
            json={"type": "allMids"}, timeout=10
        )
        if r.status_code == 200:
            return float(r.json().get(coin, 0))
        return 0.0
    except Exception:
        return 0.0


def get_all_live_prices(coins: list) -> dict:
    """Batch-fetch live mid prices for a list of HL coin names."""
    prices = {}
    try:
        r = requests.post(
            "https://api.hyperliquid.xyz/info",
            json={"type": "allMids"}, timeout=10
        )
        if r.status_code == 200:
            all_mids = r.json()
            for coin in coins:
                price = float(all_mids.get(coin, 0))
                if price > 0:
                    prices[coin] = price
        else:
            logger.error(f"Price fetch HTTP {r.status_code}")
    except Exception as e:
        logger.error(f"Failed to fetch live prices: {e}")
    return prices


# ------------------------------------------------------------------
# Core HL candle fetcher
# ------------------------------------------------------------------
def _fetch_hl_candles(coin: str, interval: str, lookback_days: int) -> list:
    """Fetch raw candles from Hyperliquid candleSnapshot endpoint."""
    now = int(time.time() * 1000)
    start = now - (lookback_days * 24 * 60 * 60 * 1000)
    payload = {
        "type": "candleSnapshot",
        "req": {
            "coin": coin,
            "interval": interval,
            "startTime": start,
            "endTime": now,
        },
    }
    try:
        r = requests.post(
            "https://api.hyperliquid.xyz/info",
            json=payload, timeout=15
        )
        if r.status_code == 200:
            candles = r.json()
            if isinstance(candles, list) and candles:
                logger.info(f"✅ {coin}-USD: Got {len(candles)} {interval} candles")
                return candles
            else:
                logger.warning(f"⚠️ {coin} {interval}: empty response")
                return []
        else:
            logger.error(f"❌ HL candle API {r.status_code} for {coin} {interval}")
            return []
    except Exception as e:
        logger.error(f"❌ {coin} {interval} candle fetch failed: {e}")
        return []


def _parse_hl_candles(candles: list) -> pd.DataFrame:
    """Convert raw HL candle list to OHLCV DataFrame with normalized columns."""
    rows = []
    for c in candles:
        try:
            rows.append({
                "time":   pd.to_datetime(int(c.get("t", 0)), unit="ms", utc=True),
                "open":   float(c.get("o", 0)),
                "high":   float(c.get("h", 0)),
                "low":    float(c.get("l", 0)),
                "close":  float(c.get("c", 0)),
                "volume": float(c.get("v", 0)),
            })
        except Exception:
            continue
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows).set_index("time").sort_index()
    return df[df["close"] > 0]


# ------------------------------------------------------------------
# Helper: convert DataFrame to list of candles (for strategies)
# ------------------------------------------------------------------
def df_to_candles(df: pd.DataFrame) -> list:
    """Convert OHLCV DataFrame to list of [timestamp, open, high, low, close, volume]."""
    if df.empty:
        return []
    candles = []
    for idx, row in df.iterrows():
        ts = int(idx.timestamp()) if hasattr(idx, "timestamp") else 0
        try:
            candles.append([
                ts,
                float(row["open"]),
                float(row["high"]),
                float(row["low"]),
                float(row["close"]),
                float(row.get("volume", 0))
            ])
        except Exception:
            continue
    return candles


# ------------------------------------------------------------------
# Multi-timeframe data builder — HL candles for ALL coins
# ------------------------------------------------------------------
def get_mtf_data(ticker_symbol: str) -> dict:
    """
    Build 1H / 4H / 1D indicator data using Hyperliquid candle API.
    Returns safe fallback (RSI=50) on failure — NEVER returns None.
    """
    coin = _TICKER_TO_COIN.get(ticker_symbol, ticker_symbol.replace("-USD", ""))
    default_p = _TICKER_DEFAULTS.get(ticker_symbol, 100.0)

    try:
        # 1H data — 7 days
        logger.info(f" Fetching {ticker_symbol} 1H data...")
        raw_1h = _fetch_hl_candles(coin, "1h", 7)
        df_1h = _parse_hl_candles(raw_1h)

        # FIX #1: Fetch 4H candles NATIVELY instead of resampling 60d of 1H
        # HL supports "4h" interval directly — faster, fewer candles, less bandwidth
        logger.info(f"📥 Fetching {ticker_symbol} 4H data...")
        raw_4h = _fetch_hl_candles(coin, "4h", 60)
        df_4h = _parse_hl_candles(raw_4h)

        # 1D data — 180 days
        logger.info(f"📥 Fetching {ticker_symbol} 1D data...")
        raw_1d = _fetch_hl_candles(coin, "1d", 180)
        df_1d = _parse_hl_candles(raw_1d)

        # Guard: if 1h fetch completely failed, return fallback
        if df_1h.empty:
            logger.error(f"❌ {ticker_symbol}: No 1H candles — using fallback")
            return get_safe_fallback(default_p)

        # Apply indicators
        df_1h = apply_indicators(df_1h, include_bb=True, include_atr=True)
        df_4h = apply_indicators(df_4h) if not df_4h.empty else df_4h
        df_1d = apply_indicators(df_1d) if not df_1d.empty else df_1d

        data_1h = extract_timeframe_data(df_1h, default_p)
        data_4h = extract_timeframe_data(df_4h, default_p) if not df_4h.empty else _get_neutral_data(default_p)
        data_1d = extract_timeframe_data(df_1d, default_p) if not df_1d.empty else _get_neutral_data(default_p)

        # Attach raw candle lists (used by strategy modules)
        data_1h["candles"] = df_to_candles(df_1h)
        data_4h["candles"] = df_to_candles(df_4h) if not df_4h.empty else []
        data_1d["candles"] = df_to_candles(df_1d) if not df_1d.empty else []

        logger.info(f"✅ {ticker_symbol}: Data extraction complete - 1H RSI: {data_1h['rsi']}")

        return {"1h": data_1h, "4h": data_4h, "1d": data_1d}

    except Exception as e:
        logger.error(f"❌ MTF data failed for {ticker_symbol}: {e}")
        return get_safe_fallback(default_p)


# Alias for any callers that reference the old HYPE-specific function
def _get_hype_mtf_data() -> dict:
    return get_mtf_data("HYPE-USD")


# FIX #2: Use top-level numpy import instead of __import__()
def calculate_atr(df, period=14):
    """Native ATR calculation using pandas/numpy."""
    high = df["high"]
    low = df["low"]
    close = df["close"]
    prev_close = close.shift(1)
    tr = pd.Series(
        data=np.maximum(
            high - low,
            np.maximum(abs(high - prev_close), abs(low - prev_close))
        ),
        index=df.index
    )
    return tr.rolling(window=period).mean()
