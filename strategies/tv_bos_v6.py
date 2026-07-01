"""
Strategy 1: Multi-Timeframe Structure + BOS (v6 Fixed)
Candle format: [timestamp, open, high, low, close, volume]
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
        """Extract candle list from nested data. Handles both list-of-lists and list-of-dicts."""
        tf_data = data.get(timeframe, {})
        if isinstance(tf_data, dict):
            candles = tf_data.get("candles", [])
        elif isinstance(tf_data, list):
            candles = tf_data
        else:
            candles = []
        if not candles:
            return []
        # Validate first element
        first = candles[0]
        if isinstance(first, (list, tuple)) and len(first) >= 5:
            return candles
        if isinstance(first, dict) and "high" in first:
            return candles
        return []

    def _get_ohlc(self, candle):
        """Return (open, high, low, close) from either list or dict format."""
        if isinstance(candle, (list, tuple)):
            return float(candle[1]), float(candle[2]), float(candle[3]), float(candle[4])
        return float(candle["open"]), float(candle["high"]), float(candle["low"]), float(candle["close"])

    def _detect_pivot(self, highs, idx, left, right, mode="high"):
        if idx < left or idx >= len(highs) - right:
            return None
        val = highs[idx]
        for i in range(1, left + 1):
            if highs[idx - i] >= val:
                return None
        for i in range(1, right + 1):
            if highs[idx + i] >= val:
                return None
        return val

    def calculate_signal(self, data: dict) -> tuple:
        try:
            candles_1h = self._extract_candles(data, "1h")
            candles_4h = self._extract_candles(data, "4h")

            if not candles_1h or len(candles_1h) < 30:
                return "HOLD", 0

            opens, highs, lows, closes = [], [], [], []
            for c in candles_1h:
                o, h, l, cl = self._get_ohlc(c)
                opens.append(o)
                highs.append(h)
                lows.append(l)
                closes.append(cl)

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

            # HTF trend filter (4H EMA50)
            if candles_4h and len(candles_4h) >= 50:
                htf_closes = [self._get_ohlc(c)[3] for c in candles_4h]
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
