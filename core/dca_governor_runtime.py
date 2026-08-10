"""
MBIO DCA Governor Runtime Adapter.

The Governor owns policy decisions.
DCAExecutionBridge translates those decisions.
DCAManager remains the only exchange execution authority.

This adapter is deliberately separate from DCARuntimeCoordinator:
the coordinator reconciles exchange/persisted state; this module evaluates
the canonical Governor against that reconciled state.
"""

from __future__ import annotations

import inspect
import logging
import time
from dataclasses import fields, is_dataclass
from typing import Any

from core.dca_config import DCAConfig
from core.dca_execution_bridge import DCAExecutionBridge
from core.dca_governor import DCAGovernor

logger = logging.getLogger(__name__)


def _nested_config(cls: type, values: dict[str, Any]) -> Any:
    if not is_dataclass(cls):
        return cls(**values)

    allowed = {f.name for f in fields(cls)}
    kwargs = {}

    for key, value in values.items():
        if key not in allowed:
            continue
        kwargs[key] = value

    return cls(**kwargs)


def build_dca_config(raw: dict[str, Any]) -> DCAConfig:
    """
    Convert persisted/runtime DCA configuration into the canonical
    DCAConfig dataclass without inventing unsupported fields.
    """
    from core.dca_config import (
        DCAAdaptiveConfig,
        DCAAccelerationConfig,
        DCAProtectionConfig,
        DCAGuardrailConfig,
    )

    raw = dict(raw or {})
    adaptive = dict(raw.get("adaptive") or {})
    acceleration = dict(raw.get("acceleration") or {})
    protection = dict(raw.get("protection") or {})
    guardrails = dict(raw.get("guardrails") or {})

    nested = {
        "adaptive": _nested_config(DCAAdaptiveConfig, adaptive),
        "acceleration": _nested_config(DCAAccelerationConfig, acceleration),
        "protection": _nested_config(DCAProtectionConfig, protection),
        "guardrails": _nested_config(DCAGuardrailConfig, guardrails),
    }

    if "default_mode" not in raw:
        nested["default_mode"] = "HYBRID"

    # Only pass fields actually accepted by the canonical DCAConfig.
    accepted = {f.name for f in fields(DCAConfig)}
    kwargs = {}

    for key, value in raw.items():
        if key in accepted and key not in {
            "adaptive",
            "acceleration",
            "protection",
            "guardrails",
        }:
            kwargs[key] = value

    for key, value in nested.items():
        if key in accepted:
            kwargs[key] = value

    return DCAConfig(**kwargs)


class DCAGovernorRuntime:
    """
    Runtime owner for one process.

    Governor state is cached per asset/side. Exchange execution remains
    delegated through DCAExecutionBridge -> DCAManager.
    """

    def __init__(self, executor: Any):
        self.executor = executor
        self.bridge = DCAExecutionBridge(executor)
        self._governors: dict[str, DCAGovernor] = {}

    def _key(self, asset: str, side: str) -> str:
        return f"{asset}:{side}".upper()

    def _governor(self, asset: str, side: str, dca_config: dict, entry: float):
        key = self._key(asset, side)

        governor = self._governors.get(key)
        if governor is None:
            config = build_dca_config(dca_config)
            governor = DCAGovernor(config)
            governor.start_dca(
                asset=asset,
                side=side,
                entry_price=float(entry),
            )
            self._governors[key] = governor
            logger.info(
                "[DCA GOVERNOR] initialized asset=%s side=%s entry=%s",
                asset,
                side,
                entry,
            )

        return governor

    async def evaluate(
        self,
        *,
        asset: str,
        side: str,
        current_price: float,
        available_budget: float,
        dca_config: dict,
        entry_price: float,
        ai_confidence: float = 0.0,
        learner_score: float = 0.0,
    ) -> dict:
        if current_price <= 0 or entry_price <= 0:
            return {
                "status": "blocked",
                "action": "BLOCK",
                "reason": "invalid price state",
            }

        governor = self._governor(
            asset,
            side,
            dca_config,
            entry_price,
        )

        command = governor.tick(
            asset=asset,
            side=side,
            current_price=current_price,
            available_budget=available_budget,
            ai_confidence=ai_confidence,
            learner_score=learner_score,
        )

        result = await self.bridge.execute(command)

        logger.info(
            "[DCA GOVERNOR] asset=%s side=%s action=%s result=%s",
            asset,
            side,
            command.action,
            result.get("status") if isinstance(result, dict) else type(result).__name__,
        )

        if isinstance(result, dict):
            result.setdefault("governor_action", command.action)
            result.setdefault("governor_mode", command.state.mode.value)
            result.setdefault("governor_phase", command.state.phase.value)

        return result if isinstance(result, dict) else {
            "status": "completed",
            "governor_action": command.action,
            "result": result,
        }

    def forget(self, asset: str, side: str) -> None:
        self._governors.pop(self._key(asset, side), None)
