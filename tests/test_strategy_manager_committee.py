import pytest

from core.strategy_manager import StrategyManager


class StubStrategy:
    def __init__(self, signal, confidence):
        self.signal = signal
        self.confidence = confidence

    def calculate_signal(self, data):
        return self.signal, self.confidence


class StubMeta:
    def get_weights(self, regime):
        return {
            "Momentum": 1.0,
            "MeanReversion": 1.0,
            "Breakout": 1.0,
            "Carry": 1.0,
            "SimpleRSI": 1.0,
            "LLM": 1.0,
        }


def make_manager(signals):
    manager = object.__new__(StrategyManager)
    manager.meta = StubMeta()
    manager.current_regime = "RANGING"
    manager.last_signal_cache = {}
    manager.strategies = {
        name: StubStrategy(signal, confidence)
        for name, (signal, confidence) in signals.items()
    }
    return manager


@pytest.mark.asyncio
async def test_requires_true_four_of_six_majority():
    manager = make_manager({
        "Momentum": ("BUY", 90),
        "MeanReversion": ("BUY", 80),
        "Breakout": ("BUY", 80),
        "Carry": ("BUY", 75),
        "SimpleRSI": ("HOLD", 0),
        "LLM": ("SELL", 95),
    })

    signal, confidence, winner = await manager.get_trade_signal(
        {}, llm_signal="SELL", llm_confidence=95
    )

    assert signal == "BUY"
    assert confidence >= 70
    assert winner == "ENSEMBLE"


@pytest.mark.asyncio
async def test_three_three_split_is_hold():
    manager = make_manager({
        "Momentum": ("BUY", 95),
        "MeanReversion": ("BUY", 95),
        "Breakout": ("BUY", 95),
        "Carry": ("SELL", 95),
        "SimpleRSI": ("SELL", 95),
        "LLM": ("SELL", 95),
    })

    signal, confidence, winner = await manager.get_trade_signal(
        {}, llm_signal="SELL", llm_confidence=95
    )

    assert signal == "HOLD"
    assert confidence >= 0
    assert winner == "ENSEMBLE"


@pytest.mark.asyncio
async def test_single_high_confidence_strategy_cannot_bypass_committee():
    manager = make_manager({
        "Momentum": ("BUY", 99),
        "MeanReversion": ("HOLD", 0),
        "Breakout": ("HOLD", 0),
        "Carry": ("HOLD", 0),
        "SimpleRSI": ("HOLD", 0),
        "LLM": ("HOLD", 0),
    })

    signal, confidence, winner = await manager.get_trade_signal(
        {}, llm_signal="HOLD", llm_confidence=0
    )

    assert signal == "HOLD"
    assert confidence == 99
    assert winner == "ENSEMBLE"


@pytest.mark.asyncio
async def test_mbio_llm_vote_can_complete_four_of_six():
    manager = make_manager({
        "Momentum": ("BUY", 80),
        "MeanReversion": ("BUY", 80),
        "Breakout": ("BUY", 80),
        "Carry": ("HOLD", 0),
        "SimpleRSI": ("HOLD", 0),
        "LLM": ("HOLD", 0),
    })

    signal, confidence, winner = await manager.get_trade_signal(
        {}, llm_signal="BUY", llm_confidence=80
    )

    assert signal == "BUY"
    assert confidence == 80
    assert winner == "ENSEMBLE"
