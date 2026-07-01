import logging
from datetime import datetime, timezone
from typing import Dict, List

logger = logging.getLogger(__name__)

class PerformanceTracker:
    """Tracks all trades with real-time PnL calculation."""
    
    def __init__(self):
        self.trades: List[Dict] = []
        self._load_from_state()
    
    def _load_from_state(self):
        """Load trade history from state."""
        import core.state as state
        if hasattr(state, 'TRADE_HISTORY') and state.TRADE_HISTORY:
            self.trades = state.TRADE_HISTORY.copy()
            logger.info(f"📊 Loaded {len(self.trades)} trades from state")
    
    def record_open_trade(self, asset: str, side: str, entry: float, size: float, 
                         strategy: str = "LLM", regime: str = "RANGING"):
        trade = {
            "asset": asset, "side": side, "entry": entry, "size": size,
            "strategy": strategy, "regime": regime,
            "opened_at": datetime.now(timezone.utc).isoformat(),
            "closed_at": None, "exit": None, "pnl_pct": None, "usd_pnl": None,
            "status": "OPEN"
        }
        self.trades.append(trade)
        self._save_to_state()
        logger.info(f"📈 Trade opened: {asset} {side} @ ${entry:.4f}")
    
    def record_close_trade(self, asset: str, exit_price: float, close_reason: str = "Manual"):
        for trade in reversed(self.trades):
            if trade["asset"] == asset and trade["status"] == "OPEN":
                trade["closed_at"] = datetime.now(timezone.utc).isoformat()
                trade["exit"] = exit_price
                trade["close_reason"] = close_reason
                trade["status"] = "CLOSED"
                
                if trade["side"] == "BUY":
                    trade["pnl_pct"] = ((exit_price - trade["entry"]) / trade["entry"]) * 100
                    trade["usd_pnl"] = (exit_price - trade["entry"]) * trade["size"]
                else:
                    trade["pnl_pct"] = ((trade["entry"] - exit_price) / trade["entry"]) * 100
                    trade["usd_pnl"] = (trade["entry"] - exit_price) * trade["size"]
                
                self._save_to_state()
                logger.info(f"📉 Trade closed: {asset} | PnL: ${trade['usd_pnl']:+.2f}")
                return trade
        return None
    
    def get_performance_stats(self, current_prices: Dict[str, float] = None) -> Dict:
        closed_trades = [t for t in self.trades if t["status"] == "CLOSED"]
        open_trades = [t for t in self.trades if t["status"] == "OPEN"]
        
        realized_pnl_usd = sum(t.get("usd_pnl", 0) for t in closed_trades)
        winning_trades = [t for t in closed_trades if t.get("pnl_pct", 0) > 0]
        win_rate = (len(winning_trades) / len(closed_trades) * 100) if closed_trades else 0
        
        unrealized_pnl_usd = 0.0
        if current_prices:
            for trade in open_trades:
                if trade["asset"] in current_prices:
                    price = current_prices[trade["asset"]]
                    if trade["side"] == "BUY":
                        unrealized_pnl_usd += (price - trade["entry"]) * trade["size"]
                    else:
                        unrealized_pnl_usd += (trade["entry"] - price) * trade["size"]
        
        strategy_stats = {}
        for trade in closed_trades:
            strat = trade.get("strategy", "Unknown")
            if strat not in strategy_stats:
                strategy_stats[strat] = {"wins": 0, "total": 0, "pnl": 0}
            strategy_stats[strat]["total"] += 1
            strategy_stats[strat]["pnl"] += trade.get("usd_pnl", 0)
            if trade.get("pnl_pct", 0) > 0:
                strategy_stats[strat]["wins"] += 1
        
        best_strategy = "N/A"
        if strategy_stats:
            best = max(strategy_stats.items(), key=lambda x: x[1]["pnl"])
            best_strategy = f"{best[0]} (${best[1]['pnl']:+.2f})"
        
        # Calculate percentages
        realized_pnl_pct = 0.0
        if closed_trades:
            realized_pnl_pct = sum(t.get("pnl_pct", 0) for t in closed_trades)
        
        unrealized_pnl_pct = 0.0
        if current_prices and open_trades:
            for trade in open_trades:
                if trade["asset"] in current_prices:
                    price = current_prices[trade["asset"]]
                    if trade["side"] == "BUY":
                        pnl_pct = ((price - trade["entry"]) / trade["entry"]) * 100
                    else:
                        pnl_pct = ((trade["entry"] - price) / trade["entry"]) * 100
                    unrealized_pnl_pct += pnl_pct
        
        return {
            "total_trades": len(self.trades),
            "closed_trades": len(closed_trades),
            "open_trades": len(open_trades),
            "realized_pnl_usd": realized_pnl_usd,
            "realized_pnl_pct": realized_pnl_pct,
            "unrealized_pnl_usd": unrealized_pnl_usd,
            "unrealized_pnl_pct": unrealized_pnl_pct,
            "win_rate": win_rate,
            "best_strategy": best_strategy
        }
    
    def _save_to_state(self):
        """Save trades to state."""
        import core.state as state
        state.TRADE_HISTORY = self.trades.copy()
        try:
            state.save_state()
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

_tracker = None
def get_performance_tracker() -> PerformanceTracker:
    global _tracker
    if _tracker is None:
        _tracker = PerformanceTracker()
    return _tracker
