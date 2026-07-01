"""
core/state.py — Shared runtime state with disk persistence.
Saves state every 60s to prevent loss on crash.
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Live open positions keyed by asset name
OPEN_POSITIONS: dict = {}
SIGNAL_CACHE: dict = {}
TIER_TIMESTAMPS: dict = {"crypto": 0.0}
LIVE_SIGNALS: dict = {}

daily_pnl: float = 0.0
TRADE_HISTORY: list = []
daily_pnl_reset_date: str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

STATE_FILE = Path("state.json")

# Auto-DCA persistence variables (populated by dca_lifecycle module)
auto_dca_active: dict = {}
auto_dca_params: dict = {}
auto_dca_consec_losses: dict = {}

def save_state() -> None:
    """Persist state to disk."""
    try:
        data = {
            "open_positions": OPEN_POSITIONS,
            "signal_cache": SIGNAL_CACHE,
            "tier_timestamps": TIER_TIMESTAMPS,
            "daily_pnl": daily_pnl,
            "daily_pnl_reset_date": daily_pnl_reset_date,
            "trade_history": TRADE_HISTORY,
        }
        # Include Auto-DCA state for restart survival
        global auto_dca_active, auto_dca_params, auto_dca_consec_losses
        data["auto_dca_active"] = auto_dca_active
        data["auto_dca_params"] = auto_dca_params
        data["auto_dca_consec_losses"] = auto_dca_consec_losses
        
        STATE_FILE.write_text(json.dumps(data, indent=2, default=str))
        logger.debug("✅ State saved to disk")
    except Exception as e:
        logger.error(f"❌ Failed to save state: {e}")

def load_state() -> None:
    """Load state from disk on startup."""
    global OPEN_POSITIONS, SIGNAL_CACHE, TIER_TIMESTAMPS, daily_pnl, daily_pnl_reset_date, TRADE_HISTORY
    global auto_dca_active, auto_dca_params, auto_dca_consec_losses
    try:
        if STATE_FILE.exists():
            data = json.loads(STATE_FILE.read_text())
            OPEN_POSITIONS = data.get("open_positions", {})
            SIGNAL_CACHE = data.get("signal_cache", {})
            TIER_TIMESTAMPS = data.get("tier_timestamps", {"crypto": 0.0})
            daily_pnl = data.get("daily_pnl", 0.0)
            daily_pnl_reset_date = data.get("daily_pnl_reset_date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
            TRADE_HISTORY = data.get("trade_history", [])
            
            # Restore Auto-DCA state
            auto_dca_active = data.get("auto_dca_active", {})
            auto_dca_params = data.get("auto_dca_params", {})
            auto_dca_consec_losses = data.get("auto_dca_consec_losses", {})
            
            logger.info(f"✅ State loaded from disk: {len(OPEN_POSITIONS)} positions, {len(TRADE_HISTORY)} historical trades")
            if auto_dca_active:
                logger.info("🔄 Restored Auto-DCA state: %s", list(auto_dca_active.keys()))
    except Exception as e:
        logger.error(f"❌ Failed to load state: {e}")

def reset_daily_pnl_if_new_day() -> None:
    global daily_pnl, daily_pnl_reset_date
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if today != daily_pnl_reset_date:
        daily_pnl = 0.0
        daily_pnl_reset_date = today
        logger.info(f"🔄 Daily PnL reset for {today}")

def add_pnl(pnl_pct: float) -> float:
    global daily_pnl
    daily_pnl += pnl_pct
    return daily_pnl

def is_drawdown_halt(halt_threshold_pct: float) -> bool:
    return daily_pnl <= halt_threshold_pct

def record_closed_trade(asset: str, side: str, entry: float, exit_price: float, size: float, close_reason: str, strategy: str = "Ensemble", regime: str = "RANGING"):
    """Records trade outcome, updates Daily PnL, and feeds the Smart Learner."""
    global daily_pnl
    
    # Calculate PnL
    if side == "BUY":
        pnl_pct = ((exit_price - entry) / entry) * 100
        usd_pnl = (exit_price - entry) * size
    else:
        pnl_pct = ((entry - exit_price) / entry) * 100
        usd_pnl = (entry - exit_price) * size
        
    # Update Daily PnL
    daily_pnl += pnl_pct
    
    # Record in History
    trade_record = {
        "asset": asset, "side": side, "entry": entry, "exit": exit_price,
        "size": size, "pnl_pct": pnl_pct, "usd_pnl": usd_pnl,
        "reason": close_reason, "strategy": strategy, "regime": regime,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    TRADE_HISTORY.append(trade_record)
    
    # 🧠 Feed the Smart Learner (MetaLearner)
    try:
        from core.meta_learner import get_meta_learner
        meta = get_meta_learner()
        meta.update(regime, strategy, pnl_pct)
        print(f" Smart Learner updated: {strategy} in {regime} (PnL: {pnl_pct:+.2f}%)")
    except Exception as e:
        pass
        
    return pnl_pct


def get_live_performance_stats():
    """Calculate real-time performance statistics from TRADE_HISTORY."""
    global TRADE_HISTORY, daily_pnl
    
    if not TRADE_HISTORY:
        return {
            "daily_pnl": 0.0,
            "lifetime_pnl": 0.0,
            "total_trades": 0,
            "win_rate": 0.0,
            "best_strategy": "N/A",
            "avg_win": 0.0,
            "avg_loss": 0.0
        }
    
    # Calculate metrics
    total_trades = len(TRADE_HISTORY)
    winning_trades = [t for t in TRADE_HISTORY if t.get("pnl_pct", 0) > 0]
    losing_trades = [t for t in TRADE_HISTORY if t.get("pnl_pct", 0) <= 0]
    
    wins = len(winning_trades)
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0.0
    
    # Calculate lifetime PnL
    lifetime_pnl = sum(t.get("usd_pnl", 0) for t in TRADE_HISTORY)
    
    # Calculate average win/loss
    avg_win = sum(t.get("pnl_pct", 0) for t in winning_trades) / wins if wins > 0 else 0.0
    avg_loss = sum(t.get("pnl_pct", 0) for t in losing_trades) / len(losing_trades) if losing_trades else 0.0
    
    # Find best performing strategy
    strategy_stats = {}
    for trade in TRADE_HISTORY:
        strat = trade.get("strategy", "Unknown")
        if strat not in strategy_stats:
            strategy_stats[strat] = {"wins": 0, "total": 0, "pnl": 0.0}
        strategy_stats[strat]["total"] += 1
        strategy_stats[strat]["pnl"] += trade.get("usd_pnl", 0)
        if trade.get("pnl_pct", 0) > 0:
            strategy_stats[strat]["wins"] += 1
    
    best_strat = "N/A"
    best_win_rate = 0.0
    for strat, stats in strategy_stats.items():
        if stats["total"] >= 3:  # Minimum trades to be considered
            wr = (stats["wins"] / stats["total"] * 100) if stats["total"] > 0 else 0.0
            if wr > best_win_rate:
                best_win_rate = wr
                best_strat = f"{strat} ({wr:.0f}% WR, {stats['total']} trades)"
    
    return {
        "daily_pnl": daily_pnl,
        "lifetime_pnl": lifetime_pnl,
        "total_trades": total_trades,
        "win_rate": win_rate,
        "best_strategy": best_strat,
        "avg_win": avg_win,
        "avg_loss": avg_loss
    }

