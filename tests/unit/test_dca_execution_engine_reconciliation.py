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
async def test_replace_ladder_keeps_same_price_and_size(engine, monkeypatch):
    cancelled = []
    submitted = []

    async def cancel(asset, order_id):
        cancelled.append((asset, order_id))
        return {"success": True}

    async def submit(asset, order):
        submitted.append((asset, order))
        return SimpleNamespace(success=True, payload={"order_id": 999})

    monkeypatch.setattr(engine, "_cancel", cancel)
    monkeypatch.setattr(engine, "_submit_limit", submit)

    dca = {
        "active_orders": [
            {"order_id": 101, "price": 100.0, "size": 1.0, "level": 1, "status": "OPEN"},
            {"order_id": 102, "price": 98.0, "size": 1.25, "level": 2, "status": "OPEN"},
        ]
    }
    ladder = [
        DCAOrder(1, 100.0, 1.0, "BUY"),
        DCAOrder(2, 98.0, 1.25, "BUY"),
    ]

    await engine.replace_ladder("AVAX", ladder, dca)

    assert cancelled == []
    assert submitted == []
    assert [order["order_id"] for order in dca["active_orders"]] == [101, 102]


@pytest.mark.asyncio
async def test_replace_ladder_only_replaces_changed_level(engine, monkeypatch):
    cancelled = []
    submitted = []

    async def cancel(asset, order_id):
        cancelled.append((asset, order_id))
        return {"success": True}

    async def submit(asset, order):
        submitted.append((asset, order))
        return SimpleNamespace(success=True, payload={"order_id": 202})

    monkeypatch.setattr(engine, "_cancel", cancel)
    monkeypatch.setattr(engine, "_submit_limit", submit)

    dca = {
        "active_orders": [
            {"order_id": 101, "price": 100.0, "size": 1.0, "level": 1, "status": "OPEN"},
            {"order_id": 102, "price": 98.0, "size": 1.25, "level": 2, "status": "OPEN"},
        ]
    }
    ladder = [
        DCAOrder(1, 100.0, 1.0, "BUY"),
        DCAOrder(2, 97.5, 1.25, "BUY"),
    ]

    await engine.replace_ladder("AVAX", ladder, dca)

    assert cancelled == [("AVAX", 102)]
    assert len(submitted) == 1
    assert submitted[0][1].price == 97.5
    assert submitted[0][1].size == 1.25
    assert [order["order_id"] for order in dca["active_orders"]] == [101, 202]


@pytest.mark.asyncio
async def test_replace_ladder_removes_duplicate_resting_order(engine, monkeypatch):
    cancelled = []
    submitted = []

    async def cancel(asset, order_id):
        cancelled.append((asset, order_id))
        return {"success": True}

    async def submit(asset, order):
        submitted.append((asset, order))
        return SimpleNamespace(success=True, payload={"order_id": 303})

    monkeypatch.setattr(engine, "_cancel", cancel)
    monkeypatch.setattr(engine, "_submit_limit", submit)

    dca = {
        "active_orders": [
            {"order_id": 201, "price": 100.0, "size": 1.0, "level": 1, "status": "OPEN"},
            {"order_id": 202, "price": 100.0, "size": 1.0, "level": 1, "status": "OPEN"},
        ]
    }
    ladder = [DCAOrder(1, 100.0, 1.0, "BUY")]

    await engine.replace_ladder("SOL", ladder, dca)

    assert cancelled == [("SOL", 202)]
    assert submitted == []
    assert [order["order_id"] for order in dca["active_orders"]] == [201]


def test_orders_equivalent_accepts_legacy_missing_side(engine):
    desired = DCAOrder(1, 100.0, 1.0, "BUY")
    legacy = {"order_id": 1, "price": 100.0, "size": 1.0, "status": "OPEN"}

    assert engine._orders_equivalent(legacy, desired)
