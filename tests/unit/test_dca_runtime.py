import pytest

import core.state as state
from core.dca_runtime import DCARuntimeCoordinator


class FakeManager:
    def __init__(self, executor):
        self.executor = executor
        self.placed = []
        self.cancelled = []

    def should_pause_dca(self, asset, price):
        return False

    def calculate_dca_levels(self, entry_price, base_size, config):
        multiplier = float(config.get("size_multiplier", 1.5))
        spacing = float(config.get("spacing_pct", 2.0)) / 100.0
        direction = str(config.get("direction", "LONG")).upper()
        return [
            {
                "level": i,
                "price": round(
                    entry_price * (1 - spacing * i)
                    if direction == "LONG"
                    else entry_price * (1 + spacing * i),
                    2,
                ),
                "size": round(base_size * (multiplier ** i), 8),
                "status": "pending",
                "order_id": None,
            }
            for i in range(1, int(config.get("levels", 3)) + 1)
        ]

    async def _submit_limit(self, asset, side, size, price, label):
        oid = 100 + len(self.placed)
        self.placed.append((asset, side, size, price, label))
        return {"success": True, "order_id": oid}

    async def _cancel_order(self, asset, order_id):
        self.cancelled.append(order_id)
        return {"success": True}


class FakeExecutor:
    def __init__(self, open_orders, positions):
        self.open_orders = open_orders
        self.positions = positions

    def get_open_orders(self):
        return self.open_orders

    def get_open_positions(self):
        return self.positions


@pytest.fixture(autouse=True)
def reset_state():
    state.DCA_POSITIONS.clear()
    state.OPEN_POSITIONS.clear()
    yield
    state.DCA_POSITIONS.clear()
    state.OPEN_POSITIONS.clear()


@pytest.mark.asyncio
async def test_initial_runtime_rebuild_skips_filled_base():
    executor = FakeExecutor([], [{"coin": "BTC", "size": 1.0, "entry_price": 100.0}])
    manager = FakeManager(executor)
    runtime = DCARuntimeCoordinator(manager)
    position = {
        "side": "BUY",
        "entry": 100.0,
        "size": 1.0,
        "dca": {
            "enabled": True,
            "direction": "LONG",
            "levels": 3,
            "spacing_pct": 2.0,
            "size_multiplier": 1.5,
            "base_size": 1.0,
            "active_orders": [],
            "filled_levels": [1],
        },
    }

    result = await runtime.ensure("BTC", position)

    assert result["action"] == "INITIALIZE"
    assert [x[0] for x in manager.placed] == ["BTC", "BTC"]
    assert [x[3] for x in manager.placed] == [96.0, 94.0]
    assert len(position["dca"]["active_orders"]) == 2
    assert state.DCA_POSITIONS["BTC"]["filled_levels"] == [1]


@pytest.mark.asyncio
async def test_filled_order_is_detected_and_remaining_ladder_rebuilt():
    executor = FakeExecutor(
        [],
        [{"coin": "BTC", "size": 3.25, "entry_price": 98.0}],
    )
    manager = FakeManager(executor)
    runtime = DCARuntimeCoordinator(manager)
    position = {
        "side": "BUY",
        "entry": 100.0,
        "size": 1.0,
        "dca": {
            "enabled": True,
            "direction": "LONG",
            "levels": 3,
            "spacing_pct": 2.0,
            "size_multiplier": 1.5,
            "base_size": 1.0,
            "filled_levels": [1],
            "last_exchange_size": 1.0,
            "last_fill_price": 100.0,
            "active_orders": [
                {"level": 2, "price": 96.0, "size": 2.25, "order_id": 20, "status": "active"},
            ],
        },
    }

    result = await runtime.ensure("BTC", position)

    assert result["action"] == "REBUILD"
    assert position["dca"]["filled_levels"] == [1, 2]
    assert position["dca"]["last_fill_price"] == pytest.approx(98.0)
    assert [x[3] for x in manager.placed] == [94.08]
    assert manager.cancelled == [20]


@pytest.mark.asyncio
async def test_external_cancel_without_fill_is_replaced():
    executor = FakeExecutor(
        [],
        [{"coin": "BTC", "size": 1.0, "entry_price": 100.0}],
    )
    manager = FakeManager(executor)
    runtime = DCARuntimeCoordinator(manager)
    position = {
        "side": "BUY",
        "entry": 100.0,
        "size": 1.0,
        "dca": {
            "enabled": True,
            "direction": "LONG",
            "levels": 2,
            "spacing_pct": 2.0,
            "size_multiplier": 1.5,
            "base_size": 1.0,
            "filled_levels": [1],
            "last_exchange_size": 1.0,
            "active_orders": [
                {"level": 2, "price": 96.0, "size": 2.25, "order_id": 20, "status": "active"},
            ],
        },
    }

    result = await runtime.ensure("BTC", position)

    assert result["action"] == "REBUILD"
    assert manager.cancelled == []
    assert len(position["dca"]["active_orders"]) == 1
    assert position["dca"]["active_orders"][0]["order_id"] == 100
