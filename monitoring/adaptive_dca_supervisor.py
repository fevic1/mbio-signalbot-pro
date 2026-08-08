"""Fast adaptive-DCA supervisor.

Runs independently from the legacy five-minute trailing task. It delegates all
order decisions to DCAManager and never writes exchange orders itself.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Callable

from config_loader import get_config
from core.app_context import app_context
from core.dca_manager import DCAManager
import core.state as state

logger = logging.getLogger(__name__)


def _interval_seconds() -> float:
    cfg = get_config().get("dca", {}) or {}
    adaptive = cfg.get("adaptive", {}) or {}
    try:
        return max(2.0, min(60.0, float(adaptive.get("monitor_interval_sec", 10.0))))
    except (TypeError, ValueError):
        return 10.0


async def adaptive_dca_supervisor_loop(
    *,
    executor_factory: Callable[[], object] | None = None,
) -> None:
    """Continuously reassess live DCA positions.

    The supervisor is intentionally small. DCAManager owns all order/risk logic.
    """
    logger.info("Adaptive DCA supervisor started")
    while True:
        try:
            executor = executor_factory() if executor_factory else app_context.executor
            manager = DCAManager(executor)
            mids = executor.info.all_mids() or {}

            for asset, position in list(state.OPEN_POSITIONS.items()):
                if str(asset).startswith("GRID::"):
                    continue
                dca_config = position.get("dca")
                if not isinstance(dca_config, dict):
                    continue
                if not dca_config.get("enabled"):
                    continue

                current_price = float(mids.get(asset, 0) or 0)
                if current_price <= 0:
                    continue

                result = await manager.monitor_adaptive_dca(
                    asset, dca_config, current_price
                )
                action = result.get("action", "WAIT")
                if action != "WAIT" or result.get("errors"):
                    logger.info(
                        "Adaptive DCA %s: action=%s updated=%s cancelled=%s errors=%s",
                        asset,
                        action,
                        result.get("updated", 0),
                        result.get("cancelled", 0),
                        len(result.get("errors", [])),
                    )
        except asyncio.CancelledError:
            logger.info("Adaptive DCA supervisor cancelled")
            raise
        except Exception as exc:
            logger.exception("Adaptive DCA supervisor tick failed: %s", exc)

        await asyncio.sleep(_interval_seconds())
