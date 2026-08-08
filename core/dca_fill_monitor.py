import asyncio
import logging
from core.market_cache import market_cache
from core.dca_execution_engine import dca_execution_engine

import core.state as state

logger = logging.getLogger(__name__)


async def reconcile_dca_position(asset: str, position: dict):
    """
    Reconcile DCA fills against the exchange.
    """

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
            if o.get("coin") == asset
        }

        for order in list(active_orders):

            raw_oid = order.get("order_id")

            if raw_oid in (None, "", 0, "0"):
                active_orders.remove(order)
                continue

            oid = str(raw_oid)

            if oid in processed:
                continue

            if oid in live_ids:
                continue

            logger.info(
                "DCA fill detected %s order=%s",
                asset,
                oid,
            )

            order["status"] = "FILLED"

            level = order.get("level")
            if level not in dca.setdefault("filled_levels", []):
                dca["filled_levels"].append(level)

            active_orders.remove(order)
            processed.add(oid)

            exchange_position = next(
                (
                    p
                    for p in exchange_positions
                    if p.get("coin") == asset
                ),
                None,
            )

            if exchange_position:
                position["size"] = float(
                    exchange_position.get(
                        "size",
                        position.get("size", 0),
                    )
                )

                position["entry"] = float(
                    exchange_position.get(
                        "entryPx",
                        exchange_position.get(
                            "entry_price",
                            position.get("entry", 0),
                        ),
                    )
                )

                position["avg_entry"] = position["entry"]

                logger.info(
                    "Updated %s size=%s entry=%s",
                    asset,
                    position["size"],
                    position["entry"],
                )

            try:
                await dca_execution_engine.on_fill(asset, position)
            except Exception:
                logger.exception(
                    "DCA lifecycle failed for %s",
                    asset,
                )

            dca["processed_fills"] = list(processed)
            state.save_state()

            break

    except Exception:
        logger.exception(
            "DCA reconcile failed: %s",
            asset,
        )


async def recover_dca_positions():
    logger.info("Recovering DCA positions from exchange...")

    from core.app_context import app_context

    executor = app_context.executor

    try:
        positions = market_cache.positions()
        orders = market_cache.orders()
    except Exception:
        logger.exception("Failed to fetch exchange state")
        return

    restored = 0

    for pos in state.OPEN_POSITIONS.values():
        dca = pos.get("dca")
        if not dca:
            continue

        dca["active_orders"] = [
            o
            for o in dca.get("active_orders", [])
            if o.get("order_id") not in (None, "", 0, "0")
        ]

    for p in positions:

        coin = p.get("coin")
        if not coin:
            continue

        if coin not in state.OPEN_POSITIONS:
            state.OPEN_POSITIONS[coin] = {}

        pos = state.OPEN_POSITIONS[coin]

        pos["entry"] = float(
            p.get("entryPx", p.get("entry_price", 0))
        )

        pos["avg_entry"] = pos["entry"]

        pos["size"] = abs(
            float(
                p.get("szi", p.get("size", 0))
            )
        )

        pos.setdefault("side", "BUY")

        active = []

        for o in orders:
            if o.get("coin") != coin:
                continue

            oid = o.get("oid")
            if oid in (None, "", 0, "0"):
                continue

            active.append(
                {
                    "order_id": oid,
                    "price": o.get("limitPx"),
                    "size": o.get("sz"),
                    "status": "OPEN",
                }
            )

        if active:
            pos["dca"] = {
                "enabled": True,
                "direction": (
                    "LONG"
                    if pos.get("side", "BUY") == "BUY"
                    else "SHORT"
                ),
                "base_size": float(pos["size"]),
                "levels": max(3, len(active)),
                "spacing_pct": 1.2,
                "size_multiplier": 1.25,
                "profit_target_pct": 0.0,
                "trailing_offset_pct": 0.8,
                "avg_entry": float(pos["entry"]),
                "total_invested": float(pos["entry"]) * float(pos["size"]),
                "active_orders": active,
                "filled_levels": [],
                "processed_fills": [],
            }

            restored += 1

    state.save_state()

    logger.info(
        "Recovered %d DCA position(s)",
        restored,
    )


async def monitor_dca_fills():
    print(
        "######## DCA FILL MONITOR STARTED ########",
        flush=True,
    )

    logger.info("DCA Fill Monitor started")

    await recover_dca_positions()

    while True:
        try:
            for asset, position in list(state.OPEN_POSITIONS.items()):
                if position.get("dca"):
                    await reconcile_dca_position(
                        asset,
                        position,
                    )

        except Exception:
            logger.exception("DCA Fill Monitor")

        await asyncio.sleep(5)