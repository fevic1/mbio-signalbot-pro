# core/exit_analytics.py
"""
Phase 2: MetaLearner Exit Analytics - Data Collection Only
Records every closed trade with regime, strategy, exit method, profit, and hold time.
"""
import json
import os
from datetime import datetime, timezone
from typing import Dict, Any

ANALYTICS_FILE = "data/exit_analytics.json"

def record_exit_analytics(
    asset: str,
    regime: str,
    entry_strategy: str,
    exit_method: str,
    profit_pct: float,
    hold_time_hours: float,
    entry_price: float,
    exit_price: float
) -> None:
    """Record trade exit data for future MetaLearner analysis."""
    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Load existing analytics
        if os.path.exists(ANALYTICS_FILE):
            with open(ANALYTICS_FILE, 'r') as f:
                analytics = json.load(f)
        else:
            analytics = []
        
        # Add new record
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "asset": asset,
            "market_regime": regime,
            "entry_strategy": entry_strategy,
            "exit_method": exit_method,
            "profit_pct": profit_pct,
            "hold_time_hours": round(hold_time_hours, 2),
            "entry_price": entry_price,
            "exit_price": exit_price
        }
        
        analytics.append(record)
        
        # Save back to file
        with open(ANALYTICS_FILE, 'w') as f:
            json.dump(analytics, f, indent=2)
            
    except Exception as e:
        import logging
        logging.getLogger(__name__).exception("Failed to record exit analytics")

def get_exit_analytics_summary() -> Dict[str, Any]:
    """Get summary of exit performance by regime and method."""
    try:
        if not os.path.exists(ANALYTICS_FILE):
            return {"total_trades": 0}
        
        with open(ANALYTICS_FILE, 'r') as f:
            analytics = json.load(f)
        
        if not analytics:
            return {"total_trades": 0}
        
        # Group by regime and exit method
        summary = {}
        for record in analytics:
            regime = record["market_regime"]
            method = record["exit_method"]
            profit = record["profit_pct"]
            
            key = f"{regime}_{method}"
            if key not in summary:
                summary[key] = {"count": 0, "total_profit": 0, "avg_profit": 0}
            
            summary[key]["count"] += 1
            summary[key]["total_profit"] += profit
            summary[key]["avg_profit"] = summary[key]["total_profit"] / summary[key]["count"]
        
        return {
            "total_trades": len(analytics),
            "by_regime_method": summary
        }
    except Exception as e:
        return {"error": str(e)}

def get_live_performance_stats():
    """Live stats from persisted exit analytics."""
    try:
        import json
        import os
        from datetime import datetime, timezone

        if not os.path.exists(ANALYTICS_FILE):
            return {
                "total_trades": 0,
                "win_rate": 0.0,
                "total_pnl": 0.0,
                "daily_pnl": 0.0,
                "best_strategy": "N/A"
            }

        with open(ANALYTICS_FILE, "r") as f:
            trades = json.load(f)

        if not trades:
            return {
                "total_trades": 0,
                "win_rate": 0.0,
                "total_pnl": 0.0,
                "daily_pnl": 0.0,
                "best_strategy": "N/A"
            }

        total_trades = len(trades)

        wins = sum(
            1 for t in trades
            if float(t.get("profit_pct", 0)) > 0
        )

        win_rate = (wins / total_trades) * 100

        total_pnl = sum(
            float(t.get("profit_pct", 0))
            for t in trades
        )

        today = datetime.now(timezone.utc).date()

        daily_pnl = 0.0

        for t in trades:
            try:
                ts = datetime.fromisoformat(
                    t["timestamp"]
                ).date()

                if ts == today:
                    daily_pnl += float(
                        t.get("profit_pct", 0)
                    )
            except Exception:
                pass

        strategy_stats = {}

        for t in trades:
            strat = t.get(
                "entry_strategy",
                "Unknown"
            )

            strategy_stats.setdefault(
                strat,
                []
            ).append(
                float(t.get("profit_pct", 0))
            )

        best_strategy = "N/A"

        if strategy_stats:
            best_strategy = max(
                strategy_stats,
                key=lambda s:
                sum(strategy_stats[s]) /
                len(strategy_stats[s])
            )

        return {
            "total_trades": total_trades,
            "win_rate": round(win_rate, 1),
            "total_pnl": round(total_pnl, 2),
            "daily_pnl": round(daily_pnl, 2),
            "best_strategy": best_strategy
        }

    except Exception as e:
        return {
            "total_trades": 0,
            "win_rate": 0.0,
            "total_pnl": 0.0,
            "daily_pnl": 0.0,
            "best_strategy": f"ERR:{e}"
        }

