from core.app_context import app_context
"""
MBIO Grid Monitor
"""

import asyncio
import logging
from config_loader import get_config
import core.state as state

logger = logging.getLogger(__name__)

async def monitor_grid_bots():
    _cfg = get_config()
    if not _cfg.get("grid", {}).get("enabled", True):
        logger.info("🔲 Grid strategy disabled via config. Grid monitor idle.")
        while True:
            await asyncio.sleep(300)
        return
    
    while True:
        await asyncio.sleep(120)
        try:
            from core.state import OPEN_POSITIONS
            from core.grid_manager import GridManager, is_grid_position, grid_asset_from_key
            executor = app_context.executor
            grid = GridManager(executor)

            for key in list(OPEN_POSITIONS.keys()):
                if not is_grid_position(key):
                    continue
                asset = grid_asset_from_key(key)
                config = OPEN_POSITIONS[key]
                if not config.get("enabled"):
                    continue

                mids = executor.info.all_mids()
                current_price = float(mids.get(asset, 0))
                if current_price <= 0:
                    continue

                exit_reason = await grid.check_exit_conditions(asset, config, current_price)
                if exit_reason:
                    logger.info(f"🔲 GRID exit for {asset}: {exit_reason}")
                    await grid.close_grid(asset, config)
                    OPEN_POSITIONS.pop(key, None)
                    import core.state as _st
                    _st.save_state()
                    continue

                nodes = config.get("nodes", [])
                active_nodes = [n for n in nodes if n.get("status") == "OPEN"]
                pending_nodes = [n for n in nodes if n.get("status") in ("PENDING", "CANCELLED")]
                
                for node in pending_nodes:
                    if node.get("status") == "CANCELLED":
                        node["status"] = "PENDING"
                        node["order_id"] = None
                        logger.debug(f"🔲 Reset cancelled node L{node['level_index']} to PENDING")
                
                if len(active_nodes) == 0 and len(pending_nodes) > 0:
                    logger.info(f"🔲 {asset}: Grid has {len(pending_nodes)} pending nodes but no active orders — deploying")
                    max_conc = 4
                    deploy_result = await grid.place_grid_orders(asset, config, current_price, max_concurrent=max_conc)
                    logger.info(f"🔲 {asset}: Deployed {deploy_result['placed']} orders, {deploy_result['failed']} failed")
                    if deploy_result.get("placed", 0) > 0:
                        import core.state as _st
                        _st.save_state()
                    continue
                
                fill_result = await grid.monitor_grid_fills(asset, config)
                if fill_result["fills_detected"] > 0:
                    logger.info(
                        f"🔲 {asset}: {fill_result['fills_detected']} fills, "
                        f"{fill_result['tp_orders_placed']} TP orders"
                    )
        except Exception as e:
            logger.error(f"❌ GRID monitor failed: {e}")


async def entry_scanner_loop(run_trade_fn, chat_id: str) -> None:
    cfg = get_config()
    interval = (cfg if isinstance(cfg, dict) else (cfg.model_dump() if hasattr(cfg, "model_dump") else cfg.dict())).get("intervals", {}).get("entry_scanner_sec", 1800)
    logger.info(f"🎯 Entry scanner (every {interval//60}min)")
    while True:
        await asyncio.sleep(interval)
        # Entry scanner logic – placeholder; actual signals are generated in full_analysis_loop
        # but we need to call run_trade when a signal appears. This is handled elsewhere.
        pass


async def full_analysis_loop(run_cycle_fn):
    """Background task: Run full portfolio analysis periodically."""
    import asyncio
    import logging
    from config_loader import get_config
    
    logger = logging.getLogger(__name__)
    cfg = get_config()
    hours = (cfg if isinstance(cfg, dict) else (cfg.model_dump() if hasattr(cfg, "model_dump") else cfg.dict())).get("intervals", {}).get("full_analysis_hours", 2)
    logger.info(f"🔄 Full analysis loop started (every {hours}h)")
    
    while True:
        try:
            logger.info("♻️ Executing full analysis cycle...")
            if run_cycle_fn:
                await run_cycle_fn()
            logger.info(f"💤 Full analysis complete. Sleeping {hours}h...")
        except Exception as e:
            logger.error(f"❌ Full analysis error: {e}")
        await asyncio.sleep(hours * 3600)



async def quick_signal_scanner(chat_id: str) -> None:
    cfg = get_config()
    interval = (cfg if isinstance(cfg, dict) else (cfg.model_dump() if hasattr(cfg, "model_dump") else cfg.dict())).get("intervals", {}).get("quick_scanner_sec", 900)
    threshold = (cfg if isinstance(cfg, dict) else (cfg.model_dump() if hasattr(cfg, "model_dump") else cfg.dict())).get("intervals", {}).get("big_move_threshold", 0.03)
    logger.info(f"🔄 Quick scanner (every {interval//60}min, {threshold*100:.0f}% threshold)")
    while True:
        await asyncio.sleep(interval)
        # Quick scanner logic – placeholder for now; you can add as needed
        pass


async def update_trailing_dca():
    """Background task: Update trailing DCA orders every 5 minutes."""
    while True:
        await asyncio.sleep(300)
        try:
            from core.state import OPEN_POSITIONS
            from core.dca_execution_engine import dca_execution_engine
            executor = app_context.executor
            dca = dca_execution_engine
            for asset, pos in OPEN_POSITIONS.items():
                dca_config = pos.get("dca")
                if dca_config and dca_config.get("trailing") and dca_config.get("enabled"):
                    # Check stabilization: ensure at least the base level is filled
                    if not dca_config.get("filled_levels"):
                        logger.debug(f"⏳ {asset} DCA not yet stabilized (no filled levels), skipping trailing update")
                        continue
                    mids = executor.info.all_mids()
                    current_price = float(mids.get(asset, 0))
                    if current_price > 0:
                        result = await dca.update_trailing_orders(asset, dca_config, current_price)
                        if result["updated"] > 0:
                            logger.info(f"🔄 Updated {result['updated']} trailing DCA orders for {asset}")
        except Exception as e:
            logger.error(f"❌ Trailing DCA update failed: {e}")


async def monitor_dca_profit_targets():
    """Background task: Check DCA profit targets every 2 minutes."""
    while True:
        await asyncio.sleep(120)
        try:
            from core.state import OPEN_POSITIONS
            from core.dca_execution_engine import dca_execution_engine
            executor = app_context.executor
            dca = dca_execution_engine
            for asset, pos in OPEN_POSITIONS.items():
                dca_config = pos.get("dca")
                if dca_config and dca_config.get("profit_target_pct", 0) > 0 and dca_config.get("enabled"):
                    mids = executor.info.all_mids()
                    current_price = float(mids.get(asset, 0))
                    if current_price > 0:
                        recommendation = dca.check_profit_target(asset, dca_config, current_price)
                        if recommendation:
                            side = dca_config.get("direction", "LONG")
                            close_side = "SELL" if side == "LONG" else "BUY"
                            result = await dca.close_dca_position(asset, dca_config, close_side)
                            if result["base_closed"]:
                                OPEN_POSITIONS.pop(asset, None)
                                import core.state as _st
                                _st.save_state()
                                logger.info(f"🎯 Auto-closed {asset} at {recommendation['pnl_pct']:.2f}% profit")
        except Exception as e:
            logger.error(f"❌ DCA profit target monitor failed: {e}")