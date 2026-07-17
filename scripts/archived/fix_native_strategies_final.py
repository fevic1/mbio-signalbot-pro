import os

# ============================================================
# REWRITE tv_bos_v6.py WITH CORRECT DATA EXTRACTION
# ============================================================
bos_code = '''"""
Strategy 1: Multi-Timeframe Structure + BOS (v6 Fixed)
Ported from Pine Script to Python. All 4 audit fixes applied.
Data format compatible with get_mtf_data() nested dict structure.
"""
import logging

logger = logging.getLogger(__name__)


class TVBOSV6Strategy:
    def __init__(self):
        self.name = "TV_BOS_V6"
        self.swing_left = 5
        self.swing_right = 5
        self.atr_length = 14
        self.atr_sl_mult = 2.0
        self.atr_tp_mult = 4.0
        self.last_swing_high = None
        self.last_swing_low = None
        self.market_bullish = None
        self.clear_swing_high = False
        self.clear_swing_low = False
        self.initialized = False

    def _extract_candles(self, data, timeframe):
        """Safely extract candle list from nested data structure."""
        tf_data = data.get(timeframe, {})
        if isinstance(tf_data, dict):
            candles = tf_data.get("candles", [])
        elif isinstance(tf_data, list):
            candles = tf_data
        else:
            candles = []
        # Validate: must be list of dicts with OHLC keys
        if candles and isinstance(candles[0], dict) and "high" in candles[0]:
            return candles
        return []

    def _detect_pivot(self, series, idx, left, right, mode="high"):
        if idx < left or idx >= len(series) - right:
            return None
        val = series[idx]
        for i in range(1, left + 1):
            if mode == "high" and series[idx - i] >= val:
                return None
            if mode == "low" and series[idx - i] <= val:
                return None
        for i in range(1, right + 1):
            if mode == "high" and series[idx + i] >= val:
                return None
            if mode == "low" and series[idx + i] <= val:
                return None
        return val

    def calculate_signal(self, data: dict) -> tuple:
        try:
            candles_1h = self._extract_candles(data, "1h")
            candles_4h = self._extract_candles(data, "4h")

            if not candles_1h or len(candles_1h) < 30:
                return "HOLD", 0

            highs = [float(c["high"]) for c in candles_1h]
            lows = [float(c["low"]) for c in candles_1h]
            closes = [float(c["close"]) for c in candles_1h]
            opens = [float(c["open"]) for c in candles_1h]

            # [F1] Seed market_bullish from actual price
            if not self.initialized:
                self.market_bullish = closes[-1] >= opens[-1]
                self.initialized = True

            # [F2] Deferred clear
            if self.clear_swing_high:
                self.last_swing_high = None
                self.clear_swing_high = False
            if self.clear_swing_low:
                self.last_swing_low = None
                self.clear_swing_low = False

            check_idx = len(closes) - self.swing_right - 1
            ph = self._detect_pivot(highs, check_idx, self.swing_left, self.swing_right, "high")
            pl = self._detect_pivot(lows, check_idx, self.swing_left, self.swing_right, "low")
            if ph is not None:
                self.last_swing_high = ph
            if pl is not None:
                self.last_swing_low = pl

            # HTF trend filter
            htf_closes = [float(c["close"]) for c in candles_4h] if candles_4h else closes
            if len(htf_closes) >= 50:
                htf_ema = sum(htf_closes[-50:]) / 50
                htf_bullish = closes[-1] > htf_ema
            else:
                htf_bullish = self.market_bullish

            bos_bull = choch_bull = bos_bear = choch_bear = False
            curr_close = closes[-1]
            prev_close = closes[-2] if len(closes) > 1 else curr_close

            if self.last_swing_high and curr_close > self.last_swing_high and prev_close <= self.last_swing_high:
                if self.market_bullish:
                    bos_bull = True
                else:
                    choch_bull = True
                self.market_bullish = True
                self.clear_swing_high = True

            if self.last_swing_low and curr_close < self.last_swing_low and prev_close >= self.last_swing_low:
                if not self.market_bullish:
                    bos_bear = True
                else:
                    choch_bear = True
                self.market_bullish = False
                self.clear_swing_low = True

            # ATR
            atr_vals = []
            for i in range(1, min(len(closes), self.atr_length + 1)):
                tr = max(highs[-i] - lows[-i],
                         abs(highs[-i] - closes[-i - 1]),
                         abs(lows[-i] - closes[-i - 1]))
                atr_vals.append(tr)
            atr = sum(atr_vals) / len(atr_vals) if atr_vals else 0

            long_cond = (bos_bull or choch_bull) and htf_bullish
            short_cond = (bos_bear or choch_bear) and not htf_bullish

            if long_cond and atr > 0:
                logger.info(f"📐 TV_BOS_V6 LONG | BOS={bos_bull} CHoCH={choch_bull}")
                return "BUY", 90
            if short_cond and atr > 0:
                logger.info(f"📐 TV_BOS_V6 SHORT | BOS={bos_bear} CHoCH={choch_bear}")
                return "SELL", 90

            return "HOLD", 0

        except Exception as e:
            logger.error(f"❌ TV_BOS_V6 internal error: {e}")
            return "HOLD", 0
'''

with open('strategies/tv_bos_v6.py', 'w') as f:
    f.write(bos_code)
print("✅ Rewrote strategies/tv_bos_v6.py with safe data extraction")

# ============================================================
# REWRITE tv_smc_fvg.py WITH CORRECT DATA EXTRACTION
# ============================================================
smc_code = '''"""
Strategy 2: SMC + FVG + EMA Matrix (v6 Fixed)
Ported from Pine Script to Python. All 6 audit fixes applied.
Data format compatible with get_mtf_data() nested dict structure.
"""
import logging

logger = logging.getLogger(__name__)


class TVSMCFVGStrategy:
    def __init__(self):
        self.name = "TV_SMC_FVG"
        self.ema_len = 200
        self.sweep_lookback = 20
        self.atr_len = 14
        self.atr_sl_mult = 1.5
        self.atr_tp_mult = 3.5
        self.bull_fvg_top = None
        self.bull_fvg_bottom = None
        self.bear_fvg_top = None
        self.bear_fvg_bottom = None
        self.ob_long_level = None
        self.ob_short_level = None

    def _extract_candles(self, data, timeframe):
        """Safely extract candle list from nested data structure."""
        tf_data = data.get(timeframe, {})
        if isinstance(tf_data, dict):
            candles = tf_data.get("candles", [])
        elif isinstance(tf_data, list):
            candles = tf_data
        else:
            candles = []
        if candles and isinstance(candles[0], dict) and "high" in candles[0]:
            return candles
        return []

    def calculate_signal(self, data: dict) -> tuple:
        try:
            candles = self._extract_candles(data, "1h")
            min_len = max(self.ema_len, self.sweep_lookback, self.atr_len) + 5

            if not candles or len(candles) < min_len:
                return "HOLD", 0

            highs = [float(c["high"]) for c in candles]
            lows = [float(c["low"]) for c in candles]
            closes = [float(c["close"]) for c in candles]
            opens = [float(c["open"]) for c in candles]

            ema = sum(closes[-self.ema_len:]) / self.ema_len
            macro_bull = closes[-1] > ema
            macro_bear = closes[-1] < ema

            atr_vals = []
            for i in range(1, self.atr_len + 1):
                tr = max(highs[-i] - lows[-i],
                         abs(highs[-i] - closes[-i - 1]),
                         abs(lows[-i] - closes[-i - 1]))
                atr_vals.append(tr)
            atr = sum(atr_vals) / len(atr_vals) if atr_vals else 0

            # [F3] Liquidity sweep (corrected direction)
            hh_bound = max(highs[-self.sweep_lookback - 1:-1])
            ll_bound = min(lows[-self.sweep_lookback - 1:-1])
            bull_sweep = (lows[-1] < ll_bound) and (closes[-1] > ll_bound)
            bear_sweep = (highs[-1] > hh_bound) and (closes[-1] < hh_bound)

            # [F1] FVG detection (corrected)
            fvg_bull = lows[-1] > highs[-3] if len(highs) >= 3 else False
            fvg_bear = highs[-1] < lows[-3] if len(lows) >= 3 else False

            # [F2] Track FVG zones
            if fvg_bull:
                self.bull_fvg_bottom = highs[-3]
                self.bull_fvg_top = lows[-1]
            if fvg_bear:
                self.bear_fvg_top = lows[-3]
                self.bear_fvg_bottom = highs[-1]

            if self.bull_fvg_bottom is not None and lows[-1] <= self.bull_fvg_top:
                self.bull_fvg_bottom = None
                self.bull_fvg_top = None
            if self.bear_fvg_top is not None and highs[-1] >= self.bear_fvg_bottom:
                self.bear_fvg_top = None
                self.bear_fvg_bottom = None

            near_bull_fvg = (self.bull_fvg_bottom is not None and
                             lows[-1] <= self.bull_fvg_top + atr * 0.25)
            near_bear_fvg = (self.bear_fvg_top is not None and
                             highs[-1] >= self.bear_fvg_bottom - atr * 0.25)

            # [F4] Order blocks with half-ATR tolerance
            if fvg_bull and len(closes) >= 2 and closes[-2] > opens[-2]:
                self.ob_long_level = opens[-2]
            if fvg_bear and len(closes) >= 2 and closes[-2] < opens[-2]:
                self.ob_short_level = opens[-2]

            at_ob_long = (self.ob_long_level is not None and
                          lows[-1] <= self.ob_long_level + atr * 0.5)
            at_ob_short = (self.ob_short_level is not None and
                           highs[-1] >= self.ob_short_level - atr * 0.5)

            enter_long = macro_bull and bull_sweep and (near_bull_fvg or at_ob_long)
            enter_short = macro_bear and bear_sweep and (near_bear_fvg or at_ob_short)

            if enter_long and atr > 0:
                logger.info(f"📐 TV_SMC_FVG LONG | Sweep=Y FVG={near_bull_fvg} OB={at_ob_long}")
                return "BUY", 90
            if enter_short and atr > 0:
                logger.info(f"📐 TV_SMC_FVG SHORT | Sweep=Y FVG={near_bear_fvg} OB={at_ob_short}")
                return "SELL", 90

            return "HOLD", 0

        except Exception as e:
            logger.error(f"❌ TV_SMC_FVG internal error: {e}")
            return "HOLD", 0
'''

with open('strategies/tv_smc_fvg.py', 'w') as f:
    f.write(smc_code)
print("✅ Rewrote strategies/tv_smc_fvg.py with safe data extraction")

print("\n🎉 Both strategies rewritten with defensive data extraction.")
