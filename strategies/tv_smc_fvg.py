"""
Strategy 2: SMC + FVG + EMA Matrix (v6 Fixed)
Candle format: [timestamp, open, high, low, close, volume]
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

    def calculate_signal(self, data: dict) -> tuple:
        try:
            candles = self._extract_candles(data, "1h")
            min_len = max(self.ema_len, self.sweep_lookback, self.atr_len) + 5

            if not candles or len(candles) < min_len:
                return "HOLD", 0

            opens, highs, lows, closes = [], [], [], []
            for c in candles:
                o, h, l, cl = self._get_ohlc(c)
                opens.append(o)
                highs.append(h)
                lows.append(l)
                closes.append(cl)

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
