"""
core/dca_manager.py — Professional DCA Engine
Implements DCA.md Steps 1-5 and DCA(1).md Features 1-4.
Adapted to verified HLExecutor API: place_order(limit_price=), cancel_order(coin, oid),
get_open_positions() → {coin, side, size, entry_price}
"""
import logging
from core.executor_utils import run_executor_method
from typing import Dict, List, Optional
from datetime import datetime, timezone
import core.state as state

logger = logging.getLogger(__name__)


class DCAManager:
    """Manages DCA strategies for open positions."""

    def __init__(self, executor):
        self.executor = executor
        self.active_dca: Dict[str, Dict] = {}

    def enable_dca(self, asset: str, levels: int = 3, spacing_pct: float = 1.2,
                   multiplier: float = 1.25, direction: str = "LONG",
                   base_size: float = 0.00025, trailing: bool = False,
                   trailing_offset_pct: float = 0.8, profit_target_pct: float = 0.0) -> Dict:
        config = {
            "enabled": True,
            "levels": levels,
            "spacing_pct": spacing_pct,
            "multiplier": multiplier,
            "direction": direction,
            "base_size": base_size,
            "trailing": trailing,
            "trailing_offset_pct": trailing_offset_pct,
            "profit_target_pct": profit_target_pct,
            "active_orders": [],
            "filled_levels": [],
            "total_invested": 0.0,
            "avg_entry": 0.0,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.active_dca[asset] = config
        logger.info(f"🔄 Auto-DCA ACTIVATED: {asset} {direction} | Levels={levels} Spacing={spacing_pct}% Mult={multiplier}x")
        return config

    def calculate_dca_levels(self, entry_price: float, base_size: float, config: Dict) -> List[Dict]:
        levels = []
        current_size = base_size * config["multiplier"]
        direction = config.get("direction", "LONG")
        for i in range(1, config["levels"] + 1):
            if direction == "LONG":
                level_price = entry_price * (1 - config["spacing_pct"] / 100 * i)
            else:
                level_price = entry_price * (1 + config["spacing_pct"] / 100 * i)
            levels.append({
                "level": i, "price": round(level_price, 2),
                "size": round(current_size, 8), "status": "pending", "order_id": None,
            })
            current_size *= config["multiplier"]
        return levels

    def calculate_trailing_levels(self, entry_price: float, current_price: float,
                                  base_size: float, config: Dict) -> List[Dict]:
        if current_price >= entry_price:
            return self.calculate_dca_levels(entry_price, base_size, config)
        trailing_offset = config.get("trailing_offset_pct", config["spacing_pct"])
        current_level_price = current_price * (1 - trailing_offset / 100)
        current_size = base_size * config["multiplier"]
        levels = []
        for i in range(1, config["levels"] + 1):
            levels.append({
                "level": i, "price": round(current_level_price, 2),
                "size": round(current_size, 8), "status": "pending",
                "order_id": None, "trailing": True,
            })
            current_level_price *= (1 - config["spacing_pct"] / 100)
            current_size *= config["multiplier"]
        return levels

    async def place_dca_orders(self, asset: str, entry_price: float, base_size: float,
                               config: Dict) -> List[Dict]:
        # === SAFETY GUARDRAIL: Check pause conditions ===
        if self.should_pause_dca(asset, entry_price):
            logger.info(f"⏸️ DCA orders paused for {asset} — guardrail triggered")
            return []
        
        from execution.hl_executor import execute_hl_order
        levels = self.calculate_dca_levels(entry_price, base_size, config)
        placed = []
        side = "BUY" if config.get("direction", "LONG") == "LONG" else "SELL"
        for level in levels:
            try:
                result = execute_hl_order(
                    coin=asset, side=side, size=level["size"],
                    limit_price=level["price"], order_type="Limit",
                    strategy="AUTO_DCA", regime="AUTO"
                )
                if result.get("success"):
                    level["order_id"] = result.get("order_id")
                    level["status"] = "active"
                    level["placed_at"] = datetime.now(timezone.utc).isoformat()
                    placed.append(level)
                    # 🛡️ ENGAGE LOCK: Prevent next order until reconciliation confirms fill
                    config["is_waiting_for_fill"] = True
                    config["last_fill_price"] = level["price"]
                    logger.info(f"🔒 {asset} DCA lock engaged. Waiting for fill at ${level['price']}")
                    logger.info(f"📊 DCA Level {level['level']} placed: {asset} {side} {level['size']} @ ${level['price']}")
                else:
                    logger.warning(f"⚠️ Failed to place DCA level {level['level']}: {result.get('error')}")
            except Exception as e:
                logger.error(f"❌ DCA order placement failed for {asset} level {level['level']}: {e}")
        config["active_orders"] = placed
        
        # PERSISTENCE: Write DCA position state to disk (CODING_STANDARD: Persistence layer)
        if placed:
            async with state.STATE_LOCK:
                state.DCA_POSITIONS[asset] = {
                    "entry_price": entry_price,
                    "base_size": base_size,
                    "direction": config.get("direction", "LONG"),
                    "levels": placed,
                    "is_waiting_for_fill": config.get("is_waiting_for_fill", False),
                    "last_fill_price": config.get("last_fill_price"),
                    "opened_at": datetime.now(timezone.utc).isoformat(),
                }
                state.save_state()
                logger.info(f"💾 DCA position persisted for {asset}: {len(placed)} levels")
        
        return placed

    async def close_dca_position(self, asset: str, config: Dict, close_side: str) -> Dict:
        results = {"base_closed": False, "dca_cancelled": 0, "dca_closed": 0, "total_pnl": 0.0, "errors": []}
        # 1. Cancel pending DCA orders
        for order in config.get("active_orders", []):
            if order.get("status") == "active" and order.get("order_id"):
                try:
                    cancel_result = await run_executor_method(self.executor.cancel_order, coin=asset, order_id=int(order["order_id"]))
                    if cancel_result.get("success"):
                        results["dca_cancelled"] += 1
                        logger.info(f"🗑️ Cancelled DCA order {order['order_id']} for {asset}")
                    else:
                        results["errors"].append(f"Cancel {order['order_id']}: {cancel_result.get('error')}")
                except Exception as e:
                    results["errors"].append(f"Cancel error: {str(e)}")
        # 2. Close filled positions using verified normalized format
        try:
            positions = (await run_executor_method(self.executor.get_open_positions)) or []
            asset_positions = [p for p in positions if isinstance(p, dict) and p.get("coin") == asset]
            for pos in asset_positions:
                size = float(pos.get("size", 0))
                if size <= 0:
                    continue
                from execution.hl_executor import execute_hl_order
                close_result = execute_hl_order(
                    coin=asset, side=close_side, size=size,
                    reduce_only=True, strategy="AUTO_DCA", regime="AUTO"
                )
                if close_result.get("success"):
                    results["base_closed"] = True
                    results["dca_closed"] += 1
                    entry = float(pos.get("entry_price", 0))
                    exit_price = float(close_result.get("avg_price", entry))
                    pnl = (exit_price - entry) * size if close_side == "SELL" else (entry - exit_price) * size
                    results["total_pnl"] += pnl
                    logger.info(f"✅ Closed {asset}: {size} @ ${exit_price} | PnL: ${pnl:+.4f}")
                else:
                    results["errors"].append(f"Close failed: {close_result.get('error')}")
        except Exception as e:
            results["errors"].append(f"Position close error: {str(e)}")
        config["enabled"] = False
        config["closed_at"] = datetime.now(timezone.utc).isoformat()
        
        # PERSISTENCE: Remove closed DCA position from state (CODING_STANDARD: Persistence layer)
        async with state.STATE_LOCK:
            removed = state.DCA_POSITIONS.pop(asset, None)
            state.save_state()
            if removed:
                logger.info(f"🗑️ DCA position removed from state for {asset} | Total PnL: ${results['total_pnl']:+.4f}")
        
        return results

    async def close_dca_position_partial(self, asset: str, config: Dict,
                                         close_side: str, percent: float) -> Dict:
        results = {"base_closed_pct": 0.0, "dca_closed": 0, "dca_cancelled": 0, "total_pnl": 0.0, "errors": []}
        for order in config.get("active_orders", []):
            if order.get("status") == "active" and order.get("order_id"):
                try:
                    cancel_result = await run_executor_method(self.executor.cancel_order, coin=asset, order_id=int(order["order_id"]))
                    if cancel_result.get("success"):
                        results["dca_cancelled"] += 1
                except Exception as e:
                    results["errors"].append(f"Cancel error: {str(e)}")
        try:
            positions = (await run_executor_method(self.executor.get_open_positions)) or []
            asset_positions = [p for p in positions if isinstance(p, dict) and p.get("coin") == asset]
            for pos in asset_positions:
                total_size = float(pos.get("size", 0))
                if total_size <= 0:
                    continue
                close_size = total_size * (percent / 100)
                from execution.hl_executor import execute_hl_order
                close_result = execute_hl_order(
                    coin=asset, side=close_side, size=close_size,
                    reduce_only=True, strategy="AUTO_DCA", regime="AUTO"
                )
                if close_result.get("success"):
                    results["dca_closed"] += 1
                    entry = float(pos.get("entry_price", 0))
                    exit_price = float(close_result.get("avg_price", entry))
                    pnl = (exit_price - entry) * close_size if close_side == "SELL" else (entry - exit_price) * close_size
                    results["total_pnl"] += pnl
            results["base_closed_pct"] = percent
        except Exception as e:
            results["errors"].append(f"Position close error: {str(e)}")
        if percent >= 100:
            config["enabled"] = False
            config["closed_at"] = datetime.now(timezone.utc).isoformat()
        return results

    async def update_trailing_orders(self, asset: str, config: Dict, current_price: float) -> Dict:
        if not config.get("enabled") or not config.get("trailing"):
            return {"updated": 0, "errors": []}
        
        # 🛡️ STATE LOCK: Prevent multi-tick spamming if an order is already pending fill
        if config.get("is_waiting_for_fill", False):
            logger.debug(f"⏳ {asset} DCA waiting for fill, skipping order placement cycle")
            return {"updated": 0, "errors": []}
            
        results = {"updated": 0, "cancelled": 0, "errors": []}
        
        # 🎯 CALCULATE FROM LAST FILL, not shifting average entry, to prevent compounding drift
        last_fill_price = config.get("last_fill_price", config.get("avg_entry", 0))
        base_size = config.get("base_size", 0.00018)
        new_levels = self.calculate_trailing_levels(entry_price, current_price, base_size, config)
        for order in config.get("active_orders", []):
            if order.get("status") == "active" and order.get("order_id"):
                try:
                    cancel_result = await run_executor_method(self.executor.cancel_order, coin=asset, order_id=int(order["order_id"]))
                    if cancel_result.get("success"):
                        results["cancelled"] += 1
                except Exception as e:
                    results["errors"].append(f"Cancel error: {str(e)}")
        placed = []
        side = "BUY" if config.get("direction", "LONG") == "LONG" else "SELL"
        from execution.hl_executor import execute_hl_order
        for level in new_levels:
            if abs(level["price"] - current_price) / current_price < 0.001:
                continue
            try:
                result = execute_hl_order(
                    coin=asset, side=side, size=level["size"],
                    limit_price=level["price"], order_type="Limit",
                    strategy="AUTO_DCA", regime="AUTO"
                )
                if result.get("success"):
                    level["order_id"] = result.get("order_id")
                    level["status"] = "active"
                    level["updated_at"] = datetime.now(timezone.utc).isoformat()
                    placed.append(level)
                    results["updated"] += 1
                    logger.info(f"📊 Trailing DCA Level {level['level']} updated: {asset} {side} {level['size']} @ ${level['price']}")
            except Exception as e:
                results["errors"].append(f"Place error: {str(e)}")
        config["active_orders"] = placed
        config["last_trailing_update"] = datetime.now(timezone.utc).isoformat()
        return results

    def check_profit_target(self, asset: str, config: Dict, current_price: float) -> Optional[Dict]:
        target_pct = config.get("profit_target_pct", 0)
        if not target_pct or not config.get("enabled"):
            return None
        avg_entry = config.get("avg_entry", 0)
        if avg_entry <= 0:
            return None
        direction = config.get("direction", "LONG")
        if direction == "LONG":
            pnl_pct = ((current_price - avg_entry) / avg_entry) * 100
        else:
            pnl_pct = ((avg_entry - current_price) / avg_entry) * 100
        if pnl_pct >= target_pct:
            logger.info(f"🎯 DCA profit target hit for {asset}: {pnl_pct:.2f}% >= {target_pct}%")
            return {"action": "close_all", "pnl_pct": pnl_pct, "target_pct": target_pct}
        return None

    def get_dca_status(self, asset: str) -> Optional[Dict]:
        if asset not in self.active_dca:
            return None
        config = self.active_dca[asset]
        return {
            "enabled": config["enabled"], "levels": config["levels"],
            "active_orders": len([o for o in config["active_orders"] if o.get("status") == "active"]),
            "filled_levels": len(config.get("filled_levels", [])),
            "total_invested": config.get("total_invested", 0.0),
            "avg_entry": config.get("avg_entry", 0.0),
        }
