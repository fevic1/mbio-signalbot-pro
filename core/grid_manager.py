"""
core/grid_manager.py — Reversal Grid Trading Engine
Mean-reversion grid that flips filled nodes to opposite side ±1 step.
Capital-efficient: recycles funds per completed cycle.
Fully isolated via GRID:: namespace. Sync HLExecutor API.
"""
import logging
import math
from typing import Dict, List, Optional
from core.grid_persistence import save_grid_state
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

GRID_PREFIX = "GRID::"


def grid_state_key(asset: str) -> str:
    return f"{GRID_PREFIX}{asset.upper()}"


def is_grid_position(key: str) -> bool:
    return key.startswith(GRID_PREFIX)


def grid_asset_from_key(key: str) -> str:
    return key.replace(GRID_PREFIX, "")


class GridManager:
    """Reversal Grid Engine. Stateless — all persistence via caller."""

    def __init__(self, executor):
        self.executor = executor

    def create_grid(self, asset: str, lower_price: float, upper_price: float,
                    grid_quantity: int, investment_amount: float,
                    profit_per_grid_pct: float = 0.5,
                    exchange: str = "hyperliquid") -> Dict:
        """Create reversal grid configuration with arithmetic node map."""
        price_range = upper_price - lower_price
        step_size = price_range / (grid_quantity - 1) if grid_quantity > 1 else price_range
        import config_loader as _cfg_mod
        _grid_cfg = _cfg_mod.get_config().get("grid", {})
        order_value_usd = investment_amount / min(grid_quantity, int(_grid_cfg.get("capital_recycle_divisor", 4)))

        mid_price = (lower_price + upper_price) / 2

        nodes = []
        for i in range(grid_quantity):
            price = round(lower_price + (step_size * i), 2)
            if price < mid_price:
                side = "BUY"
            elif price > mid_price:
                side = "SELL"
            else:
                continue  # Skip exact mid to prevent instant fill

            raw_size = order_value_usd / price if price > 0 else 0
            # Enforce $10 minimum notional with margin for rounding loss
            import config_loader as _cfg_mod
            _dca_cfg = _cfg_mod.get_config().get("dca", {})
            min_notional = float(_dca_cfg.get("min_notional", 10.0)) * float(_dca_cfg.get("min_notional_buffer", 1.15))
            min_size = min_notional / price if price > 0 else 0
            size = math.ceil(max(raw_size, min_size) * 100000) / 100000

            nodes.append({
                "level_index": i,
                "price": price,
                "side": side,
                "size": size,
                "order_id": None,
                "status": "PENDING",
                "filled_count": 0,
                "realized_pnl": 0.0,
            })

        config = {
            "enabled": True,
            "asset": asset,
            "exchange": exchange,
            "strategy_type": "GRID_REVERSAL",
            "lower_price": lower_price,
            "upper_price": upper_price,
            "grid_quantity": grid_quantity,
            "step_size": round(step_size, 2),
            "investment_amount": investment_amount,
            "profit_per_grid_pct": profit_per_grid_pct,
            "nodes": nodes,
            "completed_cycles": 0,
            "total_realized_pnl": 0.0,
            "origin": "GRID",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_update": None,
        }

        avg_size = sum(n["size"] for n in nodes) / len(nodes) if nodes else 0
        logger.info(f"🔲 REVERSAL GRID CREATED: {asset} | Range: ${lower_price}-${upper_price} | "
                     f"Levels: {grid_quantity} | Step: ${step_size:.2f} | Investment: ${investment_amount}")
        logger.info(f"🔲 Avg node size: {avg_size:.8f} {asset} (~${avg_size * mid_price:.2f} notional)")

        return config

    def place_grid_orders(self, asset: str, config: Dict, current_price: float,
                          max_concurrent: int = 4) -> Dict:
        """Deploy only the nearest N orders to market. Reversal grids don't seed all levels."""
        from execution.hl_executor import execute_hl_order

        results = {"placed": 0, "failed": 0, "errors": [], "skipped": 0}
        nodes = config.get("nodes", [])

        # Sort by distance to current price, deploy closest N
        pending = [n for n in nodes if n["status"] == "PENDING"]
        pending.sort(key=lambda n: abs(n["price"] - current_price))

        for node in pending[:max_concurrent]:
            order_size = node["size"]
            order_price = node["price"]

            # Enforce $10 minimum after rounding
            actual_notional = order_size * order_price
            if actual_notional < 10.0 and order_price > 0:
                order_size = math.ceil((float(config.get("dca", {}).get("min_notional", 10.0)) / order_price) * 100000) / 100000

            # Skip BUY orders at/above market and SELL orders at/below market
            # These would fill instantly as takers, defeating the grid purpose
            if node["side"] == "BUY" and order_price >= current_price * 1.001:
                node["status"] = "SKIPPED_ABOVE_MARKET"
                results["skipped"] += 1
                logger.debug(f"🔲 Skipped L{node['level_index']}: BUY @ ${order_price} >= market ${current_price:.2f}")
                continue
            if node["side"] == "SELL" and order_price <= current_price * 0.999:
                node["status"] = "SKIPPED_BELOW_MARKET"
                results["skipped"] += 1
                logger.debug(f"🔲 Skipped L{node['level_index']}: SELL @ ${order_price} <= market ${current_price:.2f}")
                continue

            try:
                result = execute_hl_order(
                    coin=asset, side=node["side"], size=order_size,
                    limit_px=order_price, order_type="Limit",
                    reduce_only=False, strategy="GRID", regime="SIDEWAYS",
                )
                if result.get("success"):
                    node["order_id"] = result.get("order_id")
                    node["status"] = "OPEN"
                    results["placed"] += 1
                    logger.info(f"🔲 Node L{node['level_index']:02d}: {node['side']} {asset} "
                                f"{order_size} @ ${order_price}")
                else:
                    node["status"] = "FAILED"
                    results["failed"] += 1
                    results["errors"].append(f"L{node['level_index']}: {result.get('error')}")
            except Exception as e:
                node["status"] = "ERROR"
                results["failed"] += 1
                results["errors"].append(f"L{node['level_index']}: {str(e)}")
                logger.error(f"❌ Grid order failed {asset} L{node['level_index']}: {e}")

        results["skipped"] = len(pending) - results["placed"] - results["failed"]
        config["last_update"] = datetime.now(timezone.utc).isoformat()
        return results

    def handle_fill_event(self, asset: str, config: Dict, filled_node: Dict,
                          fill_price: float) -> Optional[Dict]:
        """Core reversal logic: flip filled node to opposite side ±1 step."""
        step_size = config.get("step_size", 0)
        upper = config["upper_price"]
        lower = config["lower_price"]
        p_prec = 2

        new_node = None

        if filled_node["side"] == "BUY":
            next_price = round(filled_node["price"] + step_size, p_prec)
            if next_price <= upper:
                filled_node["side"] = "SELL"
                filled_node["price"] = next_price
                filled_node["status"] = "PENDING"
                filled_node["order_id"] = None
                filled_node["filled_count"] += 1
                new_node = filled_node
                logger.info(f"🔄 REVERSAL: L{filled_node['level_index']} BUY filled @ ${fill_price} → "
                            f"SELL @ ${next_price}")
        elif filled_node["side"] == "SELL":
            next_price = round(filled_node["price"] - step_size, p_prec)
            if next_price >= lower:
                filled_node["side"] = "BUY"
                filled_node["price"] = next_price
                filled_node["status"] = "PENDING"
                filled_node["order_id"] = None
                filled_node["filled_count"] += 1
                new_node = filled_node
                logger.info(f"🔄 REVERSAL: L{filled_node['level_index']} SELL filled @ ${fill_price} → "
                            f"BUY @ ${next_price}")

        if new_node:
            config["completed_cycles"] += 1
            cycle_pnl = step_size * filled_node["size"]
            filled_node["realized_pnl"] += cycle_pnl
            config["total_realized_pnl"] += cycle_pnl

            from core.trade_ledger import record_trade
            record_trade("grid_cycle", asset, "GRID_REVERSAL", new_node["side"],
                         filled_node["size"], fill_price, pnl=cycle_pnl,
                         metadata={"level": filled_node["level_index"],
                                   "cycle": filled_node["filled_count"],
                                   "next_price": new_node["price"]})

        # Persist updated grid state after reversal flip
        import core.state as _state
        save_grid_state(_state.OPEN_POSITIONS)

        return new_node

    def monitor_grid_fills(self, asset: str, config: Dict) -> Dict:
        """Detect fills via pending order sync + position check. Triggers reversal flips."""
        from execution.hl_executor import execute_hl_order

        results = {"fills_detected": 0, "flips_executed": 0, "orders_placed": 0, "tp_orders_placed": 0, "errors": []}
        
        # NEW: Direct order-existence verification to prevent zombie cancellation loops
        try:
            open_orders = self.executor.info.open_orders(self.executor.address)
            live_order_ids = {str(o.get("oid")) for o in open_orders if o.get("coin") == asset}
            
            for node in config.get("nodes", []):
                if node["status"] == "OPEN" and node.get("order_id"):
                    if str(node["order_id"]) not in live_order_ids:
                        logger.warning(f"🔲 Node L{node['level_index']} order {node['order_id']} vanished from exchange. Marking CANCELLED.")
                        node["status"] = "CANCELLED"
                        node["order_id"] = None
        except Exception as e:
            logger.error(f"❌ Order existence check failed for {asset}: {e}")
            results["errors"].append(f"Order check failed: {str(e)}")

        # PRIMARY: Sync against exchange open_orders (most reliable fill detection)
        sync_result = self.sync_pending_orders(asset, config)
        results["fills_detected"] += sync_result.get("fills_detected", 0)
        results["errors"].extend(sync_result.get("errors", []))
        nodes = config.get("nodes", [])

        try:
            positions = self.executor.get_open_positions() or []
            asset_positions = [p for p in positions if isinstance(p, dict) and p.get("coin") == asset]

            for pos in asset_positions:
                entry_price = float(pos.get("entry_price", pos.get("entryPx", 0)))
                pos_size = abs(float(pos.get("size", pos.get("szi", 0))))

                for node in nodes:
                    if node["status"] != "OPEN":
                        continue
                    if abs(node["price"] - entry_price) < 1.0:
                        # Fill detected — trigger reversal
                        results["fills_detected"] += 1
                        node["status"] = "FILLED"

                        flipped = self.handle_fill_event(asset, config, node, entry_price)
                        if flipped:
                            results["flips_executed"] += 1
                            # Deploy the flipped order
                            order_size = flipped["size"]
                            order_price = flipped["price"]
                            actual_notional = order_size * order_price
                            if actual_notional < 10.0 and order_price > 0:
                                order_size = math.ceil((float(config.get("dca", {}).get("min_notional", 10.0)) / order_price) * 100000) / 100000

                            try:
                                res = execute_hl_order(
                                    coin=asset, side=flipped["side"], size=order_size,
                                    limit_px=order_price, order_type="Limit",
                                    reduce_only=False, strategy="GRID", regime="SIDEWAYS",
                                )
                                if res.get("success"):
                                    flipped["order_id"] = res.get("order_id")
                                    flipped["status"] = "OPEN"
                                    results["orders_placed"] += 1
                            except Exception as e:
                                results["errors"].append(f"Flip order failed: {str(e)}")

        except Exception as e:
            results["errors"].append(f"Fill monitoring error: {str(e)}")
            logger.error(f"❌ Reversal grid fill monitor failed for {asset}: {e}")

        config["last_update"] = datetime.now(timezone.utc).isoformat()
        return results

    def close_grid(self, asset: str, config: Dict) -> Dict:
        """Cancel all open nodes + close any residual positions."""
        from execution.hl_executor import execute_hl_order

        results = {"orders_cancelled": 0, "positions_closed": 0,
                    "total_pnl": config.get("total_realized_pnl", 0.0), "errors": []}

        for node in config.get("nodes", []):
            if node["status"] == "OPEN" and node.get("order_id"):
                try:
                    cancel = self.executor.cancel_order(coin=asset, order_id=int(node["order_id"]))
                    # Mark as CANCELLED even if exchange says "already canceled" to prevent loop
                    cancel_result = cancel.get("result", {})
                    statuses = cancel_result.get("response", {}).get("data", {}).get("statuses", [])
                    has_already_canceled = any("already canceled" in str(s.get("error", "")).lower() for s in statuses)
                    if cancel.get("success") or has_already_canceled:
                        results["orders_cancelled"] += 1
                        node["status"] = "CANCELLED"
                except Exception as e:
                    results["errors"].append(f"Cancel L{node['level_index']}: {str(e)}")

        try:
            positions = self.executor.get_open_positions() or []
            asset_positions = [p for p in positions if isinstance(p, dict) and p.get("coin") == asset]
            for pos in asset_positions:
                size = abs(float(pos.get("size", pos.get("szi", 0))))
                if size <= 0:
                    continue
                side_str = str(pos.get("side", "")).lower()
                close_side = "SELL" if side_str in ("long", "buy") else "BUY"
                entry = float(pos.get("entry_price", pos.get("entryPx", 0)))

                close_result = execute_hl_order(
                    coin=asset, side=close_side, size=size,
                    reduce_only=True, strategy="GRID", regime="SIDEWAYS",
                )
                if close_result.get("success"):
                    results["positions_closed"] += 1
                    exit_px = float(close_result.get("avg_price", entry))
                    pnl = (exit_px - entry) * size if close_side == "SELL" else (entry - exit_px) * size
                    results["total_pnl"] += pnl
        except Exception as e:
            results["errors"].append(f"Position close error: {str(e)}")

        config["enabled"] = False
        config["closed_at"] = datetime.now(timezone.utc).isoformat()
        return results


    def sync_pending_orders(self, asset: str, config: Dict) -> Dict:
        """Detect grid fills via user_state position snapshot comparison.
        More reliable than open_orders() which returns empty on this SDK version."""
        results = {"synced": 0, "fills_detected": 0, "errors": []}
        
        try:
            # Get current position state
            user_state = self.executor.info.user_state(self.executor.address)
            positions = user_state.get("assetPositions", [])
            asset_pos = None
            for p in positions:
                pos_data = p.get("position", {})
                if pos_data.get("coin") == asset and float(pos_data.get("szi", 0)) != 0:
                    asset_pos = pos_data
                    break
            
            current_size = abs(float(asset_pos.get("szi", 0))) if asset_pos else 0
            current_entry = float(asset_pos.get("entryPx", 0)) if asset_pos else 0
            
            # Compare against last known snapshot stored in config
            prev_size = config.get("_last_known_size", 0)
            prev_entry = config.get("_last_known_entry", 0)
            
            # Detect size change = fill occurred
            if current_size != prev_size and current_size > 0:
                size_delta = current_size - prev_size
                if abs(size_delta) > 0.00001:  # Meaningful change
                    results["fills_detected"] += 1
                    
                    # Find which node likely filled based on entry price proximity
                    best_node = None
                    best_dist = float("inf")
                    for node in config.get("nodes", []):
                        if node["status"] == "OPEN":
                            dist = abs(node["price"] - current_entry)
                            if dist < best_dist:
                                best_dist = dist
                                best_node = node
                    
                    if best_node and best_dist < config.get("step_size", 500):
                        best_node["status"] = "FILLED"
                        flipped = self.handle_fill_event(asset, config, best_node, current_entry)
                        if flipped:
                            logger.info(f"🔄 REVERSAL TRIGGERED: L{best_node['level_index']} "
                                        f"{best_node['side']} filled @ ${current_entry} "
                                        f"(size delta: {size_delta:+.6f})")
            
            # Update snapshot for next comparison
            config["_last_known_size"] = current_size
            config["_last_known_entry"] = current_entry
            
            # Also check for nodes that should be OPEN but have no corresponding order
            # (Handles case where open_orders API is unreliable)
            for node in config.get("nodes", []):
                if node["status"] == "OPEN":
                    results["synced"] += 1
            
            config["last_update"] = datetime.now(timezone.utc).isoformat()
            
        except Exception as e:
            results["errors"].append(f"Position sync failed: {str(e)}")
            logger.error(f"❌ Grid position sync failed for {asset}: {e}")
        
        return results

    def check_exit_conditions(self, asset: str, config: Dict, current_price: float) -> Optional[str]:
        sl_pct = config.get("stop_loss_pct")
        if sl_pct and current_price <= config["lower_price"] * (1 - sl_pct / 100):
            return f"Stop-loss: ${current_price} <= ${config['lower_price'] * (1 - sl_pct / 100):.2f}"
        tp_pct = config.get("take_profit_pct")
        if tp_pct and config.get("total_realized_pnl", 0) >= config["investment_amount"] * (tp_pct / 100):
            return f"Take-profit: ${config['total_realized_pnl']:+.2f} >= target"
        if current_price < config["lower_price"] * 0.95 or current_price > config["upper_price"] * 1.05:
            return f"Out of range: ${current_price} outside ${config['lower_price'] * 0.95:.2f}-${config['upper_price'] * 1.05:.2f}"
        return None

    def get_grid_status(self, asset: str, state_positions: Dict) -> Optional[Dict]:
        key = grid_state_key(asset)
        config = state_positions.get(key)
        if not config or not config.get("enabled"):
            return None
        nodes = config.get("nodes", [])
        open_count = len([n for n in nodes if n["status"] == "OPEN"])
        total_fills = sum(n.get("filled_count", 0) for n in nodes)
        return {
            "enabled": config["enabled"],
            "strategy": config.get("strategy_type", "GRID"),
            "range": f"${config['lower_price']}-${config['upper_price']}",
            "levels": config["grid_quantity"],
            "step_size": f"${config['step_size']}",
            "open_orders": open_count,
            "completed_cycles": config.get("completed_cycles", 0),
            "total_fills": total_fills,
            "investment": f"${config['investment_amount']:.2f}",
            "realized_pnl": f"${config.get('total_realized_pnl', 0):+.4f}",
        }
