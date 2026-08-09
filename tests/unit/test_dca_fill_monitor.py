from types import SimpleNamespace

import pytest

import core.state as state
from core import dca_fill_monitor as monitor


@pytest.mark.asyncio
async def test_missing_resting_order_requires_verified_fill(monkeypatch):
    position = {
        "size": 1.0,
        "entry": 100.0,
        "dca": {
            "enabled": True,
            "active_orders": [
                {"order_id": 101, "price": 98.0, "size": 1.0, "level": 1, "status": "OPEN"}
            ],
            "filled_levels": [],
            "processed_fills": [],
        },
    }

    executor = SimpleNamespace(address="0xabc", info=SimpleNamespace(user_fills=lambda _: []))
    monkeypatch.setattr(monitor.app_context, "executor", executor)
    monkeypatch.setattr(monitor.market_cache, "orders", lambda: [])
    monkeypatch.setattr(monitor.market_cache, "positions", lambda: [])
    monkeypatch.setattr(state, "save_state", lambda: None)

    await monitor.reconcile_dca_position("BTC", position)

    assert position["dca"]["active_orders"][0]["status"] == "OPEN"
    assert position["dca"]["filled_levels"] == []


@pytest.mark.asyncio
async def test_missing_resting_order_is_filled_only_when_oid_is_in_user_fills(monkeypatch):
    position = {
        "size": 1.0,
        "entry": 100.0,
        "dca": {
            "enabled": True,
            "active_orders": [
                {"order_id": 101, "price": 98.0, "size": 1.0, "level": 1, "status": "OPEN"}
            ],
            "filled_levels": [],
            "processed_fills": [],
        },
    }

    async def on_fill(asset, current_position):
        return None

    executor = SimpleNamespace(
        address="0xabc",
        info=SimpleNamespace(user_fills=lambda _: [{"coin": "BTC", "oid": 101, "sz": "1.0"}]),
    )
    monkeypatch.setattr(monitor.app_context, "executor", executor)
    monkeypatch.setattr(monitor.market_cache, "orders", lambda: [])
    monkeypatch.setattr(monitor.market_cache, "positions", lambda: [{"coin": "BTC", "entryPx": "98.0", "size": "2.0"}])
    monkeypatch.setattr(monitor.dca_execution_engine, "on_fill", on_fill)
    monkeypatch.setattr(state, "save_state", lambda: None)

    await monitor.reconcile_dca_position("BTC", position)

    assert position["dca"]["active_orders"] == []
    assert position["dca"]["filled_levels"] == [1]
    assert "101" in position["dca"]["processed_fills"]
    assert position["size"] == 2.0
    assert position["entry"] == 98.0


@pytest.mark.asyncio
async def test_recovery_does_not_promote_non_dca_position(monkeypatch):
    original = dict(state.OPEN_POSITIONS)
    try:
        state.OPEN_POSITIONS.clear()
        state.OPEN_POSITIONS["ETH"] = {
            "entry": 2000.0,
            "size": 0.1,
        }

        monkeypatch.setattr(
            monitor.market_cache,
            "positions",
            lambda: [{"coin": "ETH", "entryPx": "2000", "szi": "0.1"}],
        )
        monkeypatch.setattr(
            monitor.market_cache,
            "orders",
            lambda: [{"coin": "ETH", "oid": 77, "limitPx": "1950", "sz": "0.1"}],
        )
        monkeypatch.setattr(state, "save_state", lambda: None)

        await monitor.recover_dca_positions()

        assert "dca" not in state.OPEN_POSITIONS["ETH"]
    finally:
        state.OPEN_POSITIONS.clear()
        state.OPEN_POSITIONS.update(original)
