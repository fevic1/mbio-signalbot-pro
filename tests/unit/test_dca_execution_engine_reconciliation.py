from types import SimpleNamespace

import pytest

from core.dca_execution_engine import DCAExecutionEngine, DCAOrder


@pytest.fixture
def engine(monkeypatch):
    instance = DCAExecutionEngine.__new__(DCAExecutionEngine)
    instance.active = {}
    monkeypatch.setattr("core.dca_execution_engine.state.save_state", lambda: None)
    return instance


@pytest.mark.asyncio
async def test_same_price_same_size_zero_cancel_zero_submit(engine, monkeypatch):
    cancelled = []
    submitted = []

    async def cancel(asset, order_id):
        cancelled.append((asset, order_id))
        return {"success": True}

    async def submit(asset, order):
        submitted.append((asset, order))
        return SimpleNamespace(success=True, payload={"order_id": 999})

    async def exchange(asset):
        return []

    monkeypatch.setattr(engine, "_cancel", cancel)
    monkeypatch.setattr(engine, "_submit_limit", submit)
    monkeypatch.setattr(engine, "_exchange_open_orders", exchange)

    dca = {"active_orders": [
        {"order_id": 101, "price": 100.0, "size": 1.0, "level": 1, "status": "OPEN"},
        {"order_id": 102, "price": 98.0, "size": 1.25, "level": 2, "status": "OPEN"},
    ]}
    ladder = [DCAOrder(1, 100.0, 1.0, "BUY"), DCAOrder(2, 98.0, 1.25, "BUY")]

    await engine.replace_ladder("AVAX", ladder, dca)

    assert cancelled == []
    assert submitted == []
    assert [order["order_id"] for order in dca["active_orders"]] == [101, 102]


@pytest.mark.asyncio
async def test_equivalent_exchange_order_with_different_oid_is_retained(engine, monkeypatch):
    cancelled = []
    submitted = []

    async def cancel(asset, order_id):
        cancelled.append((asset, order_id))
        return {"success": True}

    async def submit(asset, order):
        submitted.append((asset, order))
        return SimpleNamespace(success=True, payload={"order_id": 999})

    async def exchange(asset):
        return [{"oid": 777, "coin": asset, "limitPx": 100.0, "sz": 1.0, "side": "BUY"}]

    monkeypatch.setattr(engine, "_cancel", cancel)
    monkeypatch.setattr(engine, "_submit_limit", submit)
    monkeypatch.setattr(engine, "_exchange_open_orders", exchange)

    dca = {"active_orders": [{"order_id": 101, "price": 99.0, "size": 1.0, "level": 1, "status": "OPEN"}]}
    await engine.replace_ladder("BTC", [DCAOrder(1, 100.0, 1.0, "BUY")], dca)

    assert cancelled == []
    assert submitted == []
    assert dca["active_orders"][0]["order_id"] == 777


@pytest.mark.asyncio
async def test_duplicate_ladder_levels_are_collapsed_before_submission(engine, monkeypatch):
    submitted = []

    async def submit(asset, order):
        submitted.append((asset, order))
        return SimpleNamespace(success=True, payload={"order_id": 303})

    async def exchange(asset):
        return []

    monkeypatch.setattr(engine, "_submit_limit", submit)
    monkeypatch.setattr(engine, "_exchange_open_orders", exchange)

    dca = {"active_orders": []}
    ladder = [DCAOrder(1, 100.0, 1.0, "BUY"), DCAOrder(2, 100.0, 1.0, "BUY")]
    await engine.replace_ladder("SOL", ladder, dca)

    assert len(submitted) == 1
    assert submitted[0][1].price == 100.0


@pytest.mark.asyncio
async def test_below_threshold_price_change_is_kept(engine, monkeypatch):
    cancelled = []
    submitted = []

    async def cancel(asset, order_id):
        cancelled.append((asset, order_id))
        return {"success": True}

    async def submit(asset, order):
        submitted.append((asset, order))
        return SimpleNamespace(success=True, payload={"order_id": 999})

    async def exchange(asset):
        return []

    monkeypatch.setattr(engine, "_cancel", cancel)
    monkeypatch.setattr(engine, "_submit_limit", submit)
    monkeypatch.setattr(engine, "_exchange_open_orders", exchange)

    dca = {"minimum_reprice_pct": 0.15, "active_orders": [
        {"order_id": 101, "price": 100.0, "size": 1.0, "level": 1, "status": "OPEN"}
    ]}
    await engine.replace_ladder("ETH", [DCAOrder(1, 100.10, 1.0, "BUY")], dca)

    assert cancelled == []
    assert submitted == []
    assert dca["active_orders"][0]["order_id"] == 101


@pytest.mark.asyncio
async def test_genuine_reprice_cancels_verifies_then_submits(engine, monkeypatch):
    events = []
    exchange_orders = [{"oid": 101, "coin": "BTC", "limitPx": 100.0, "sz": 1.0, "side": "BUY"}]

    async def cancel(asset, order_id):
        events.append("cancel")
        exchange_orders.clear()
        return {"success": True}

    async def submit(asset, order):
        events.append("submit")
        return SimpleNamespace(success=True, payload={"order_id": 202})

    async def exchange(asset):
        events.append("exchange")
        return list(exchange_orders)

    monkeypatch.setattr(engine, "_cancel", cancel)
    monkeypatch.setattr(engine, "_submit_limit", submit)
    monkeypatch.setattr(engine, "_exchange_open_orders", exchange)

    dca = {"minimum_reprice_pct": 0.15, "active_orders": [
        {"order_id": 101, "price": 100.0, "size": 1.0, "level": 1, "status": "OPEN"}
    ]}
    await engine.replace_ladder("BTC", [DCAOrder(1, 101.0, 1.0, "BUY")], dca)

    assert events[:3] == ["exchange", "cancel", "exchange"]
    assert events[3:] == ["submit"]
    assert dca["active_orders"][0]["order_id"] == 202


@pytest.mark.asyncio
async def test_unverified_cancel_withholds_replacement(engine, monkeypatch):
    submitted = []
    exchange_orders = [{"oid": 101, "coin": "BTC", "limitPx": 100.0, "sz": 1.0, "side": "BUY"}]

    async def cancel(asset, order_id):
        return {"success": True}

    async def submit(asset, order):
        submitted.append(order)
        return SimpleNamespace(success=True, payload={"order_id": 202})

    async def exchange(asset):
        return list(exchange_orders)

    monkeypatch.setattr(engine, "_cancel", cancel)
    monkeypatch.setattr(engine, "_submit_limit", submit)
    monkeypatch.setattr(engine, "_exchange_open_orders", exchange)

    dca = {"minimum_reprice_pct": 0.15, "active_orders": [
        {"order_id": 101, "price": 100.0, "size": 1.0, "level": 1, "status": "OPEN"}
    ]}
    await engine.replace_ladder("BTC", [DCAOrder(1, 101.0, 1.0, "BUY")], dca)

    assert submitted == []


def test_orders_equivalent_accepts_legacy_missing_side(engine):
    desired = DCAOrder(1, 100.0, 1.0, "BUY")
    legacy = {"order_id": 1, "price": 100.0, "size": 1.0, "status": "OPEN"}
    assert engine._orders_equivalent(legacy, desired)
