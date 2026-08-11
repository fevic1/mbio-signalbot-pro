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

MIN_VOTES_TO_PASS = 4
TOTAL_COMMITTEE_VOTERS = 6
MIN_CONSENSUS_CONFIDENCE = 70


class StrategyManager:
    """Six-strategy trading committee.

    The committee is limited to the six strategies represented by MetaLearner
    weights: Momentum, MeanReversion, Breakout, Carry, SimpleRSI and LLM.
    DeterministicStrategy remains available for other callers but is not a
    committee voter.

    A trade decision requires a true 4-of-6 directional majority and a
    weighted confidence of at least 70%. Individual high-confidence strategies
    cannot bypass the committee.
    """

    COMMITTEE = (
        "Momentum",
        "MeanReversion",
        "Breakout",
        "Carry",
        "SimpleRSI",
        "LLM",
    )

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

    async def get_trade_signal(
        self,
        asset_data: Dict[str, Any],
        llm_signal: str | None = None,
        llm_confidence: int = 0,
    ) -> Tuple[str, int, str]:
        """Evaluate the six-strategy committee and return its final decision.

        ``llm_signal``/``llm_confidence`` let the canonical MBIO intelligence
        result serve as the LLM committee vote without making a second API
        request. When omitted, the LLM strategy remains a HOLD voter.
        """
        if "4h" in asset_data and asset_data["4h"].get("candles"):
            self.current_regime = detect_regime(asset_data["4h"])
        else:
            self.current_regime = "RANGING"

        weights = self.meta.get_weights(self.current_regime)
        committee_weights = {
            name: float(weights.get(name, 0.0))
            for name in self.COMMITTEE
        }

        if sum(committee_weights.values()) <= 0:
            committee_weights = {name: 1.0 for name in self.COMMITTEE}

        tasks = []
        for name in self.COMMITTEE:
            if name == "LLM" and llm_signal is not None:
                tasks.append(self._provided_llm_vote(llm_signal, llm_confidence))
            else:
                tasks.append(
                    self._get_strategy_signal(
                        self.strategies[name],
                        asset_data,
                        name,
                    )
                )

        results = await asyncio.gather(*tasks, return_exceptions=True)

        votes = []
        for res in results:
            if isinstance(res, Exception):
                logger.error("Strategy error: %s", res)
                continue

            name, signal, conf = res
            signal = str(signal or "HOLD").upper().strip()
            if signal not in {"BUY", "SELL", "HOLD"}:
                signal = "HOLD"

            try:
                conf = max(0, min(100, int(conf)))
            except (TypeError, ValueError):
                conf = 0

            votes.append({
                "strategy": name,
                "signal": signal,
                "confidence": conf,
                "weight": committee_weights.get(name, 0.0),
            })

        buy_votes = [v for v in votes if v["signal"] == "BUY"]
        sell_votes = [v for v in votes if v["signal"] == "SELL"]

        if len(buy_votes) >= len(sell_votes):
            winner_signal = "BUY"
            winning_votes = buy_votes
        else:
            winner_signal = "SELL"
            winning_votes = sell_votes

        vote_count = len(winning_votes)
        total_weight = sum(v["weight"] for v in winning_votes)
        weighted_confidence = (
            sum(v["confidence"] * v["weight"] for v in winning_votes) / total_weight
            if total_weight > 0
            else 0.0
        )

        passed = (
            vote_count >= MIN_VOTES_TO_PASS
            and weighted_confidence >= MIN_CONSENSUS_CONFIDENCE
        )

        final_signal = winner_signal if passed else "HOLD"
        final_confidence = int(round(weighted_confidence)) if passed else 0

        if final_signal != "HOLD":
            if self.current_regime == "TRENDING_UP" and final_signal == "SELL":
                logger.info(
                    "🚫 REGIME GATE: Blocked committee SELL in TRENDING_UP regime."
                )
                final_signal, final_confidence = "HOLD", 0
            elif self.current_regime == "TRENDING_DOWN" and final_signal == "BUY":
                logger.info(
                    "🚫 REGIME GATE: Blocked committee BUY in TRENDING_DOWN regime."
                )
                final_signal, final_confidence = "HOLD", 0

        logger.info(
            "🏆 Ensemble Vote: %s | Votes: %d/%d | Confidence: %d%% | Regime: %s | Committee=%s",
            final_signal,
            vote_count,
            TOTAL_COMMITTEE_VOTERS,
            final_confidence,
            self.current_regime,
            ",".join(
                f"{v['strategy']}={v['signal']}:{v['confidence']}"
                for v in votes
            ),
        )
        return final_signal, final_confidence, "ENSEMBLE"

    async def _provided_llm_vote(self, signal: str, confidence: int):
        return "LLM", signal, confidence

    async def _get_strategy_signal(self, strat, data, name):
        if asyncio.iscoroutinefunction(strat.calculate_signal):
            sig, conf = await strat.calculate_signal(data)
        else:
            loop = asyncio.get_event_loop()
            sig, conf = await loop.run_in_executor(
                None,
                strat.calculate_signal,
                data,
            )
        return name, sig, conf
