import logging
import asyncio
from typing import Dict, Any, Tuple
from strategies.momentum import MomentumStrategy
from strategies.meanreversion import MeanReversionStrategy
from strategies.breakout import BreakoutStrategy
from strategies.carry import CarryStrategy
from strategies.simple_rsi import SimpleRSIStrategy
from strategies.llm import LLMStrategy
from strategies.deterministic import DeterministicStrategy
from core.meta_learner import get_meta_learner
from core.regime import detect_regime

logger = logging.getLogger(__name__)

class StrategyManager:
    def __init__(self):
        self.strategies = {
            "Momentum": MomentumStrategy(),
            "MeanReversion": MeanReversionStrategy(),
            "Breakout": BreakoutStrategy(),
            "Carry": CarryStrategy(),
            "SimpleRSI": SimpleRSIStrategy(),
            "LLM": LLMStrategy(),
            "Deterministic": DeterministicStrategy(),
        }
        self.meta = get_meta_learner()
        self.current_regime = "RANGING"
        self.last_signal_cache = {}

    async def get_trade_signal(self, asset_data: Dict[str, Any]) -> Tuple[str, int, str]:
        final_signal = "HOLD"  # 🛡️ Prevent UnboundLocalError
        final_confidence = 0
        used_strategy = "ENSEMBLE"
        # Detect regime
        if "4h" in asset_data and asset_data["4h"].get("candles"):
            self.current_regime = detect_regime(asset_data["4h"])
        else:
            self.current_regime = "RANGING"

        weights = self.meta.get_weights(self.current_regime)

        # 🛡️ ARCHITECTURAL FIX: Prevent Meta-Learner Weight Collapse
        if not weights or sum(weights.values()) < 0.5:
            weights = {name: 1.0 for name in self.strategies.keys()}
            logger.warning("⚠️ Meta-Learner weights collapsed. Forcing uniform committee distribution.")


        tasks = []
        for name, strat in self.strategies.items():
            if name not in weights or weights[name] <= 0:
                continue
            tasks.append(self._get_strategy_signal(strat, asset_data, name))
        results = await asyncio.gather(*tasks, return_exceptions=True)

        weighted_sum = 0.0
        total_weight = 0.0
        best_signal = None
        best_confidence = 0
        used_strategy = None

        sniper_signal = None
        sniper_conf = 0
        
        for res in results:
            if isinstance(res, Exception):
                logger.error(f"Strategy error: {res}")
                continue
            name, signal, conf = res
            
            # SNIPER OVERRIDE: If any strategy is > 85% confident, force it
            if conf >= 85 and signal != "HOLD":
                if conf > sniper_conf:
                    sniper_conf = conf
                    sniper_signal = signal
                    sniper_name = name
                    
            weight = weights.get(name, 0.1)
            numeric = 1 if signal == "BUY" else -1 if signal == "SELL" else 0
            weighted_sum += numeric * conf * weight
            total_weight += weight
            if conf > best_confidence and signal != "HOLD":
                best_confidence = conf
                best_signal = signal
                used_strategy = name

        # Return Sniper Override if triggered
        if sniper_signal:
            logger.info(f"🎯 SNIPER OVERRIDE: {sniper_name} triggered with {sniper_conf}% confidence! (Bypassing Ensemble)")
            return sniper_signal, sniper_conf, sniper_name

        if total_weight == 0:
            return best_signal or "HOLD", best_confidence, used_strategy or "LLM"

        norm = weighted_sum / (total_weight * 100)
        if norm > 0.2:
            final_signal = "BUY"
            conf = int(min(100, norm * 100))
        elif norm < -0.3:
            final_signal = "SELL"
            conf = int(min(100, -norm * 100))
        else:
            # WEAK ENSEMBLE: Use best individual strategy instead of blocking
            if best_signal and best_confidence > 0:
                final_signal = best_signal
                conf = best_confidence
                # 🛡️ PHASE 4: BLIND SPOT OVERRIDE (Deterministic Math Fallback)
                _rsi_1d = float(asset_data.get("1d", {}).get("rsi", 50))
                _rsi_1h = float(asset_data.get("1h", {}).get("rsi", 50))
                
                if _rsi_1d < 30 and _rsi_1h < 45:
                    logger.info(f"🚀 BLIND SPOT OVERRIDE: 1D RSI={_rsi_1d:.1f} < 30 & 1H RSI={_rsi_1h:.1f} < 45. Deterministic BUY.")
                    return "BUY", 85, "DETERMINISTIC_MATH"
                elif _rsi_1d > 70 and _rsi_1h > 65:
                    logger.info(f"🚀 BLIND SPOT OVERRIDE: 1D RSI={_rsi_1d:.1f} > 70 & 1H RSI={_rsi_1h:.1f} > 65. Deterministic SELL.")
                    return "SELL", 85, "DETERMINISTIC_MATH"
                else:
                    pass  # 🛡️ Auto-fixed empty block
        winner = locals().get("winner", "ENSEMBLE")
        logger.info(f"🏆 Ensemble Vote: {final_signal} | Winning Strategy: {winner} | Consensus Score: {conf}%")
        return final_signal, conf, winner

    async def _get_strategy_signal(self, strat, data, name):
        if asyncio.iscoroutinefunction(strat.calculate_signal):
            sig, conf = await strat.calculate_signal(data)
        else:
            loop = asyncio.get_event_loop()
            sig, conf = await loop.run_in_executor(None, strat.calculate_signal, data)
        return name, sig, conf
