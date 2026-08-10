from pathlib import Path

import core.state as state


def test_save_state_syncs_dca_positions_from_open_positions(tmp_path):
    original_state_file = state.STATE_FILE
    original_open_positions = state.OPEN_POSITIONS
    original_dca_positions = state.DCA_POSITIONS

    try:
        state.STATE_FILE = Path(tmp_path) / "state.json"
        state.OPEN_POSITIONS = {
            "BTC": {
                "side": "BUY",
                "entry": 100.0,
                "size": 0.01,
                "opened_at": "2026-08-08T17:00:00+00:00",
                "dca": {
                    "enabled": True,
                    "direction": "LONG",
                    "base_size": 0.01,
                    "avg_entry": 99.5,
                    "active_orders": [
                        {"level": 2, "order_id": 42, "price": 97.5, "status": "active"}
                    ],
                    "filled_levels": [1],
                    "last_fill_price": 98.0,
                    "is_waiting_for_fill": False,
                    "adaptive": {
                        "enabled": True,
                        "aggressive_enabled": True,
                        "last_monitor_price": 98.5,
                    },
                },
            }
        }
        state.DCA_POSITIONS = {}

        state.save_state()

        persisted = state.DCA_POSITIONS["BTC"]
        assert persisted["entry_price"] == 99.5
        assert persisted["base_size"] == 0.01
        assert persisted["direction"] == "LONG"
        assert persisted["levels"][0]["order_id"] == 42
        assert persisted["active_orders"][0]["order_id"] == 42
        assert persisted["filled_levels"] == [1]
        assert persisted["last_fill_price"] == 98.0
        assert persisted["adaptive"]["aggressive_enabled"] is True

        saved = state.STATE_FILE.read_text()
        assert '"dca_positions"' in saved
        assert '"order_id": 42' in saved
    finally:
        state.STATE_FILE = original_state_file
        state.OPEN_POSITIONS = original_open_positions
        state.DCA_POSITIONS = original_dca_positions
