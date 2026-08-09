import asyncio
import logging
from core.market_cache import market_cache
from core.dca_execution_engine import dca_execution_engine

import core.state as state

logger = logging.getLogger(__name__)


async def _verified_fill_oids(executor, asset: str) -> set[str]:
    """Return order IDs proven filled by the exchange fill ledger.

    A resting order disappearing from openOrders is not sufficient evidence of a
    fill because cancellation, expiry, restart recovery, and transient exchange
    responses can all remove an order from the live set.
    """
    try:
        info = getattr(executor, "info", None)
        if info is None:
            return set()

        user_fills = getattr(info, "user_fills", None)
        if not callable(user_fills):
            logger.warning("DCA fill verification unavailable for %s: user_fills missing", asset)
            return set()

        address = getattr(executor, "address", None)
        if not address:
            return set()

        fills = await asyncio.to_thread(user_fills, address)
        if not isinstance(fills, list):
            return set()

        verified: set[str] = set()
        for fill in fills:
            if not isinstance(fill, dict) or str(fill.get("coin", "")) != asset:
                continue
            oid = fill.get("oid")
            if oid not in (None, "", 0, "0"):
                verified.add(str(oid))
        return verified
    except Exception:
        logger.exception("DCA fill verification failed for %s", asset)
        return set()


async def reconcile_dca_position(asset: str, position: dict):
    """Reconcile DCA orders without treating disappearance as proof of fill."""
    try:
        dca = position.get("dca")
        if not dca:
            return

        active_orders = dca.get("active_orders", [])
        if not active_orders:
            return

        processed = set(dca.get("processed_fills", []))
        from core.app_context import app_context
        executor = app_context.executor

        exchange_orders = market_cache.orders()
        exchange_positions = market_cache.positions()
        live_ids = {
            str(o.get("oid"))
            for o in exchange_orders
            if o.get("coin") == asset and o.get("oid") not in (None, "", 0, "0")
        }

        missing_ids = {
            str(order.get("order_id"))
            for order in active_orders
            if order.get("order_id") not in (None, "", 0, "0")
            and str(order.get("order_id")) not in live_ids
            and str(order.get("order_id")) not in processed
        }
        if not missing_ids:
            return

        verified_fills = await _verified_fill_oids(executor, asset)
        if not verified_fills:
            logger.info(
                "DCA order reconciliation deferred %s: missing=%s no verified fill",
                asset,
                sorted(missing_ids),
            )
            return

        for order in list(active_orders):
            raw_oid = order.get("order_id")
            if raw_oid in (None, "", 0, "0"):
                active_orders.remove(order)
                continue

            oid = str(raw_oid)
            if oid in processed or oid in live_ids:
                continue
            if oid not in verified_fills:
                logger.info("DCA order disappeared without fill proof %s order=%s", asset, oid)
                continue

            logger.info("DCA verified fill %s order=%s", asset, oid)
            order["status"] = "FILLED"

            level = order.get("level")
            if level not in dca.setdefault("filled_levels", []):
                dca["filled_levels"].append(level)

            active_orders.remove(order)
            processed.add(oid)

            exchange_position = next(
                (p for p in exchange_positions if p.get("coin") == asset),
                None,
            )
            if exchange_position:
                position["size"] = float(
                    exchange_position.get("size", position.get("size", 0))
                )
                position["entry"] = float(
                    exchange_position.get(
                        "entryPx",
                        exchange_position.get("entry_price", position.get("entry", 0)),
                    )
                )
                position["avg_entry"] = position["entry"]

            try:
                await dca_execution_engine.on_fill(asset, position)
            except Exception:
                logger.exception("DCA lifecycle failed for %s", asset)

            dca["processed_fills"] = list(processed)
            state.save_state()
            break

    except Exception:
        logger.exception("DCA reconcile failed: %s", asset)


async def recover_dca_positions():
    """Recover persisted DCA positions from exchange state without claiming unrelated orders."""
    logger.info("Recovering DCA positions from exchange...")

    try:
        positions = market_cache.positions()
        orders = market_cache.orders()
    except Exception:
        logger.exception("Failed to fetch exchange state")
        return

    restored = 0
    for coin, pos in list(state.OPEN_POSITIONS.items()):
        dca = pos.get("dca")
        if not isinstance(dca, dict) or not dca.get("enabled"):
            continue

        exchange_position = next(
            (p for p in positions if p.get("coin") == coin),
            None,
        )
        if not exchange_position:
            continue

        pos["entry"] = float(exchange_position.get("entryPx", exchange_position.get("entry_price", pos.get("entry", 0))) or 0)
        pos["avg_entry"] = pos["entry"]
        pos["size"] = abs(float(exchange_position.get("szi", exchange_position.get("size", pos.get("size", 0))) or 0))

        active = []
        for order in orders:
            if order.get("coin") != coin:
                continue
            oid = order.get("oid")
            if oid in (None, "", 0, "0"):
                continue
            active.append({
                "order_id": oid,
                "price": order.get("limitPx"),
                "size": order.get("sz"),
                "side": order.get("side"),
                "status": "OPEN",
            })

        dca["active_orders"] = active
        dca.setdefault("filled_levels", [])
        dca.setdefault("processed_fills", [])
        restored += 1

    state.save_state()
    logger.info("Recovered %d persisted DCA position(s)", restored)


async def monitor_dca_fills():
    print("######## DCA FILL MONITOR STARTED ########", flush=True)
    logger.info("DCA Fill Monitor started")
    await recover_dca_positions()

    while True:
        try:
            for asset, position in list(state.OPEN_POSITIONS.items()):
                if position.get("dca"):
                    await reconcile_dca_position(asset, position)
        except Exception:
            logger.exception("DCA Fill Monitor")
        await asyncio.sleep(5)
