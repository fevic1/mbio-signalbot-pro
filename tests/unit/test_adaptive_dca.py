import pytest
import sys
from types import SimpleNamespace

from core.adaptive_dca import (
    AdaptiveDCAConfig,
    DCAAction,
    MarketSnapshot,
    evaluate_dca_order,
    parse_ai_advice,
)
from core.dca_manager import DCAManager
from monitoring.adaptive_dca_supervisor import _interval_seconds


def test_ai_advice_is_bounded_and_unknown_action_fails_closed():
    advice = parse_ai_advice(
        {
            "action": "DO_SOMETHING",
            "confidence": 999,
            "learner_score": -5,
            "size_multiplier": 99,
            "valid_for_seconds": 9999,
        }
    )
    assert advice.action == "WAIT"
    assert advice.confidence == 1.0
    assert advice.learner_score == 0.0
    assert advice.size_multiplier == 10.0
    assert advice.valid_for_seconds == 300.0


def test_stale_long_order_is_repriced_toward_market():
    decision = evaluate_dca_order(
        side="LONG",
        market=MarketSnapshot(price=96.0, momentum=-0.3),
        order={"price": 94.0, "placed_at_ts": 0.0, "order_id": 1},
        now_ts=60.0,
        config=AdaptiveDCAConfig(order_ttl_seconds=45.0),
    )
    assert decision.action is DCAAction.REPRICE
    assert decision.target_price == pytest.approx(95.856)


def test_ai_can_accelerate_only_when_all_gates_pass():
    decision = evaluate_dca_order(
        side="LONG",
        market=MarketSnapshot(
            price=96.0,
            momentum=-0.6,
            spread_pct=0.10,
            liquidity_score=0.95,
        ),
        order={"price": 94.0, "placed_at_ts": 55.0, "order_id": 1},
        now_ts=60.0,
        config=AdaptiveDCAConfig(),
        ai_advice={
            "action": "ACCELERATE",
            "confidence": 0.91,
            "learner_score": 0.82,
            "max_price": 96.0,
            "size_multiplier": 2.0,
            "valid_for_seconds": 30,
        },
    )
    assert decision.action is DCAAction.ACCELERATE
    assert decision.target_price == 96.0
    assert decision.size_multiplier == 1.25


def test_ai_acceleration_is_rejected_without_directional_momentum():
    decision = evaluate_dca_order(
        side="LONG",
        market=MarketSnapshot(
            price=96.0,
            momentum=0.2,
            spread_pct=0.10,
            liquidity_score=0.95,
        ),
        order={"price": 94.0, "placed_at_ts": 55.0, "order_id": 1},
        now_ts=60.0,
        config=AdaptiveDCAConfig(),
        ai_advice={
            "action": "ACCELERATE",
            "confidence": 0.95,
            "learner_score": 0.90,
            "max_price": 96.0,
        },
    )
    assert decision.action is DCAAction.WAIT


def test_risk_gate_always_wins():
    decision = evaluate_dca_order(
        side="LONG",
        market=MarketSnapshot(price=96.0, momentum=-0.7),
        order={"price": 94.0, "placed_at_ts": 0.0, "order_id": 1},
        now_ts=60.0,
        config=AdaptiveDCAConfig(),
        ai_advice={
            "action": "ACCELERATE",
            "confidence": 1.0,
            "learner_score": 1.0,
            "max_price": 96.0,
        },
        risk_allowed=False,
    )
    assert decision.action is DCAAction.PAUSE


def test_invalid_side_fails_closed():
    decision = evaluate_dca_order(
        side="SIDEWAYS",
        market=MarketSnapshot(price=100.0),
        order={"price": 99.0, "placed_at_ts": 0.0},
        now_ts=60.0,
    )
    assert decision.action is DCAAction.PAUSE


def test_manager_clamps_acceleration_multiplier():
    manager = DCAManager(None)
    config = {
        "adaptive": {
            "enabled": True,
            "aggressive_enabled": True,
            "acceleration_confidence": 5.0,
            "min_learner_score": -2.0,
            "max_acceleration_multiplier": 9.0,
        }
    }
    bounded = manager._adaptive_config(config)
    assert bounded.acceleration_confidence == 1.0
    assert bounded.min_learner_score == 0.0
    assert bounded.max_acceleration_multiplier == 1.25


def test_manager_builds_progressive_dca_levels():
    manager = DCAManager(None)
    config = {"levels": 3, "spacing_pct": 2.0, "multiplier": 1.5, "direction": "LONG"}
    levels = manager.calculate_dca_levels(100.0, 1.0, config)
    assert [level["price"] for level in levels] == [98.0, 96.0, 94.0]
    assert [level["size"] for level in levels] == [1.5, 2.25, 3.375]


def test_supervisor_interval_has_safe_bounds(monkeypatch):
    monkeypatch.setattr(
        "monitoring.adaptive_dca_supervisor.get_config",
        lambda: {"dca": {"adaptive": {"monitor_interval_sec": 0.1}}},
    )
    assert _interval_seconds() == 2.0

    monkeypatch.setattr(
        "monitoring.adaptive_dca_supervisor.get_config",
        lambda: {"dca": {"adaptive": {"monitor_interval_sec": 120}}},
    )
    assert _interval_seconds() == 60.0


@pytest.mark.asyncio
async def test_manager_reprices_stale_order_without_exchange_access(monkeypatch):
    manager = DCAManager(None)
    config = {
        "enabled": True,
        "direction": "LONG",
        "base_size": 1.0,
        "levels": 3,
        "spacing_pct": 2.0,
        "multiplier": 1.5,
        "active_orders": [
            {
                "level": 1,
                "price": 94.0,
                "size": 1.5,
                "order_id": 10,
                "status": "active",
                "placed_at_ts": 0.0,
            }
        ],
        "adaptive": {
            "enabled": True,
            "monitor_interval_sec": 2.0,
            "order_ttl_seconds": 45.0,
            "last_ai_review_ts": 100.0,
        },
    }
    monkeypatch.setattr("core.dca_manager.time.time", lambda: 100.0)
    monkeypatch.setattr("core.dca_manager.state.save_state", lambda: None)
    fake_data_fetcher = SimpleNamespace(
        get_mtf_data=lambda _: {"1h": {"price": 96.0, "atr": 1.0, "rsi": 50.0}}
    )
    monkeypatch.setitem(sys.modules, "core.data_fetcher", fake_data_fetcher)
    monkeypatch.setattr(manager, "_cancel_order", lambda *args: _ok())
    monkeypatch.setattr(manager, "_submit_limit", lambda *args: _ok(order_id=11))

    result = await manager.monitor_adaptive_dca("BTC", config, 96.0)

    assert result["action"] == "REPRICE"
    assert config["active_orders"][0]["order_id"] == 11
    assert config["active_orders"][0]["price"] == pytest.approx(95.856)


@pytest.mark.asyncio
async def test_manager_acceleration_cancels_resting_orders_and_rebuilds(monkeypatch):
    manager = DCAManager(None)
    config = {
        "enabled": True,
        "direction": "LONG",
        "base_size": 1.0,
        "levels": 3,
        "spacing_pct": 2.0,
        "multiplier": 1.5,
        "filled_levels": [],
        "active_orders": [
            {
                "level": 1,
                "price": 94.0,
                "size": 1.5,
                "order_id": 10,
                "status": "active",
                "placed_at_ts": 0.0,
            },
            {
                "level": 2,
                "price": 92.0,
                "size": 2.25,
                "order_id": 20,
                "status": "active",
                "placed_at_ts": 0.0,
            },
        ],
        "adaptive": {
            "enabled": True,
            "aggressive_enabled": True,
            "monitor_interval_sec": 2.0,
            "order_ttl_seconds": 45.0,
            "last_ai_review_ts": 100.0,
        },
    }
    monkeypatch.setattr("core.dca_manager.time.time", lambda: 100.0)
    monkeypatch.setattr("core.dca_manager.state.save_state", lambda: None)
    fake_data_fetcher = SimpleNamespace(
        get_mtf_data=lambda _: {"1h": {"price": 96.0, "atr": 2.0, "rsi": 30.0}}
    )
    monkeypatch.setitem(sys.modules, "core.data_fetcher", fake_data_fetcher)
    monkeypatch.setattr(
        manager,
        "_ai_advice",
        lambda *args: {
            "action": "ACCELERATE",
            "confidence": 0.95,
            "learner_score": 0.90,
            "max_price": 96.0,
            "size_multiplier": 1.25,
            "valid_for_seconds": 30,
        },
    )
    monkeypatch.setattr(manager, "_risk_budget_allows_acceleration", lambda *args: _true())
    cancelled = []

    async def cancel(asset, order_id):
        cancelled.append(order_id)
        return _ok()

    submitted = []

    async def submit_limit(asset, side, size, price, label):
        submitted.append((label, size, price))
        return _ok(order_id=100 + len(submitted))

    async def submit_aggressive(asset, side, size, label):
        submitted.append((label, size, 96.0))
        return _ok(avg_price=95.9)

    monkeypatch.setattr(manager, "_cancel_order", cancel)
    monkeypatch.setattr(manager, "_submit_limit", submit_limit)
    monkeypatch.setattr(manager, "_submit_aggressive", submit_aggressive)

    result = await manager.monitor_adaptive_dca("BTC", config, 96.0)

    assert result["action"] == "ACCELERATE"
    assert cancelled == [10, 20]
    assert config["filled_levels"] == [1]
    assert len(config["active_orders"]) == 2
    assert all(order["status"] == "active" for order in config["active_orders"])


def _ok(**extra):
    return {"success": True, **extra}


def _true():
    return True
