"""Institutional adaptive-DCA supervisor.

The supervisor is the runtime heartbeat. It first reconciles persisted DCA
state with exchange state, then delegates adaptive policy/execution to
DCAManager. It never places exchange orders directly.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Callable

from config_loader import get_config
from core.app_context import app_context
from core.dca_manager import DCAManager
from core.dca_runtime import DCARuntimeCoordinator
from core.dca_governor_runtime import DCAGovernorRuntime
import core.state as state

logger = logging.getLogger(__name__)


def _interval_seconds() -> float:
    cfg = get_config().get("dca", {}) or {}
    adaptive = cfg.get("adaptive", {}) or {}
    try:
        return max(2.0, min(60.0, float(adaptive.get("monitor_interval_sec", 5.0))))
    except (TypeError, ValueError):
        return 5.0


async def adaptive_dca_supervisor_loop(
    *,
    executor_factory: Callable[[], object] | None = None,
) -> None:
    """Continuously reconcile and reassess every live DCA position."""
    logger.info("Adaptive DCA supervisor started")

    # These objects must survive across supervisor heartbeats.
    # DCAGovernor owns canonical plan/state, so recreating it every tick
    # would destroy lifecycle state and restart the DCA ladder.
    executor = executor_factory() if executor_factory else app_context.executor
    manager = DCAManager(executor)
    runtime = DCARuntimeCoordinator(manager)
    governor_runtime = DCAGovernorRuntime(executor)

    while True:
        try:
            cfg = get_config().get("dca", {}) or {}
            global_adaptive = cfg.get("adaptive", {}) or {}
            mids = executor.info.all_mids() or {}

            for asset, position in list(state.OPEN_POSITIONS.items()):
                if str(asset).startswith("GRID::"):
                    continue
                dca_config = position.get("dca")
                if not isinstance(dca_config, dict) or not dca_config.get("enabled"):
                    continue

                # Global policy is the source of defaults; persisted per-position
                # values win when explicitly present.
                adaptive_config = dca_config.setdefault("adaptive", {})
                for key, value in global_adaptive.items():
                    adaptive_config.setdefault(key, value)

                # Reconcile exchange order IDs, fills, partial fills, external
                # cancellations, restart recovery, and remaining ladder state
                # before any adaptive decision is allowed to act.
                try:
                    runtime_result = await runtime.ensure(asset, position)
                    if runtime_result.get("action") not in {"SYNC"}:
                        logger.info(
                            "DCA runtime %s: action=%s",
                            asset,
                            runtime_result.get("action"),
                        )
                except Exception as exc:
                    # Fail closed for this asset. Do not allow adaptive policy to
                    # place new exposure when exchange reconciliation failed.
                    logger.exception("DCA runtime reconciliation failed %s: %s", asset, exc)
                    continue

                current_price = float(mids.get(asset, 0) or 0)
                if current_price <= 0:
                    continue

                direction = str(
                    dca_config.get(
                        "direction",
                        "LONG" if str(position.get("side", "BUY")).upper() == "BUY" else "SHORT",
                    )
                ).upper()

                try:
                    entry_price = float(
                        dca_config.get(
                            "avg_entry",
                            position.get("entry", position.get("entry_price", 0)),
                        )
                        or 0
                    )
                    available_budget = float(
                        dca_config.get(
                            "available_budget",
                            global_adaptive.get("risk_budget_usd", 0) or 0,
                        )
                        or 0
                    )

                    result = await governor_runtime.evaluate(
                        asset=asset,
                        side=direction,
                        current_price=current_price,
                        available_budget=available_budget,
                        dca_config=dca_config,
                        entry_price=entry_price,
                        ai_confidence=float(
                            dca_config.get(
                                "ai_confidence",
                                global_adaptive.get("acceleration_confidence", 0),
                            )
                            or 0
                        ),
                        learner_score=float(
                            dca_config.get(
                                "learner_score",
                                global_adaptive.get("min_learner_score", 0),
                            )
                            or 0
                        ),
                    )
                except Exception as exc:
                    # Fail closed. Existing reconciliation has already completed.
                    logger.exception(
                        "DCA Governor evaluation failed %s: %s",
                        asset,
                        exc,
                    )
                    continue
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
