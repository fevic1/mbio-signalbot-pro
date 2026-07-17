"""
Dashboard State Manager
Centralized state for SSE streaming.
"""
import threading
from typing import Dict, Any

_state_lock = threading.Lock()
_dashboard_state: Dict[str, Any] = {
    "balance": 0.0,
    "equity": 0.0,
    "deployed_pct": 0.0,
    "daily_pnl_pct": 0.0,
    "realized_pnl_usd": 0.0,
    "unrealized_pnl_usd": 0.0,
    "win_rate": "N/A",
    "positions": [],
    "grids": [],
}

def get_dashboard_state() -> Dict[str, Any]:
    """Get current dashboard state (thread-safe)."""
    with _state_lock:
        return _dashboard_state.copy()

def update_dashboard_state(updates: Dict[str, Any]) -> None:
    """Update dashboard state (thread-safe)."""
    with _state_lock:
        _dashboard_state.update(updates)

def reset_dashboard_state() -> None:
    """Reset dashboard state to defaults."""
    with _state_lock:
        _dashboard_state.clear()
        _dashboard_state.update({
            "balance": 0.0,
            "equity": 0.0,
            "deployed_pct": 0.0,
            "daily_pnl_pct": 0.0,
            "realized_pnl_usd": 0.0,
            "unrealized_pnl_usd": 0.0,
            "win_rate": "N/A",
            "positions": [],
            "grids": [],
        })
