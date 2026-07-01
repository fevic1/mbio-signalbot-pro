"""
core/trade_ledger.py — Persistent Trade History Ledger
Append-only JSON log of every open/close/PnL event.
Survives restarts, position closures, and state resets.
"""
import json
import os
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

LEDGER_PATH = "data/trade_history.json"


def _ensure_dir():
    os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)


def record_trade(event_type: str, asset: str, strategy: str, side: str,
                 size: float, price: float, pnl: float = 0.0,
                 order_id: str = None, metadata: Dict = None) -> Dict:
    """Append a trade record to the persistent ledger."""
    _ensure_dir()

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,  # "open", "close", "partial_close", "grid_fill", "grid_tp"
        "asset": asset,
        "strategy": strategy,      # "DCA", "GRID", "SIGNAL", "MANUAL"
        "side": side,              # "BUY", "SELL"
        "size": size,
        "price": price,
        "pnl": round(pnl, 6),
        "order_id": order_id,
        "metadata": metadata or {},
    }

    try:
        history = load_history()
        history.append(record)
        with open(LEDGER_PATH, "w") as f:
            json.dump(history, f, indent=2)
        logger.info(f"📝 Trade recorded: {event_type} {asset} {side} {size} @ ${price} | PnL: ${pnl:+.4f}")
    except Exception as e:
        logger.error(f"❌ Failed to record trade: {e}")

    return record


def load_history() -> List[Dict]:
    """Load full trade history from disk."""
    if not os.path.exists(LEDGER_PATH):
        return []
    try:
        with open(LEDGER_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        logger.warning("⚠️ Trade history corrupted — returning empty list")
        return []


def get_trades_for_asset(asset: str, limit: int = 20) -> List[Dict]:
    """Get recent trades for a specific asset."""
    history = load_history()
    asset_trades = [t for t in history if t.get("asset") == asset]
    return asset_trades[-limit:]


def get_summary() -> Dict:
    """Get aggregate trade statistics."""
    history = load_history()
    if not history:
        return {"total_trades": 0, "total_pnl": 0.0, "by_strategy": {}, "by_asset": {}}

    total_pnl = sum(t.get("pnl", 0) for t in history)
    by_strategy = {}
    by_asset = {}

    for t in history:
        strat = t.get("strategy", "UNKNOWN")
        asset = t.get("asset", "UNKNOWN")

        if strat not in by_strategy:
            by_strategy[strat] = {"count": 0, "pnl": 0.0}
        by_strategy[strat]["count"] += 1
        by_strategy[strat]["pnl"] += t.get("pnl", 0)

        if asset not in by_asset:
            by_asset[asset] = {"count": 0, "pnl": 0.0}
        by_asset[asset]["count"] += 1
        by_asset[asset]["pnl"] += t.get("pnl", 0)

    return {
        "total_trades": len(history),
        "total_pnl": round(total_pnl, 4),
        "by_strategy": by_strategy,
        "by_asset": by_asset,
    }
