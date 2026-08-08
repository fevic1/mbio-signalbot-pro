"""Adaptive DCA policy and safety gates.

This module is deliberately exchange-agnostic. It decides whether an existing
DCA ladder should wait, be repriced, or request an accelerated entry. It never
places or cancels an exchange order and it never overrides risk limits.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class DCAAction(str, Enum):
    WAIT = "WAIT"
    REPRICE = "REPRICE"
    ACCELERATE = "ACCELERATE"
    PAUSE = "PAUSE"


@dataclass(frozen=True)
class AdaptiveDCAConfig:
    enabled: bool = True
    aggressive_enabled: bool = True
    order_ttl_seconds: float = 45.0
    min_reprice_distance_pct: float = 0.15
    acceleration_confidence: float = 0.72
    min_learner_score: float = 0.60
    max_acceleration_multiplier: float = 1.25
    max_order_age_seconds: float = 300.0


@dataclass(frozen=True)
class MarketSnapshot:
    price: float
    volatility: float = 0.0
    momentum: float = 0.0
    regime: str = "UNKNOWN"
    spread_pct: float = 0.0
    liquidity_score: float = 1.0


@dataclass(frozen=True)
class AIDCAAdvice:
    action: str = "WAIT"
    confidence: float = 0.0
    learner_score: float = 0.0
    max_price: float | None = None
    size_multiplier: float = 1.0
    valid_for_seconds: float = 30.0
    reason: str = ""


@dataclass(frozen=True)
class DCAActionDecision:
    action: DCAAction
    reason: str
    confidence: float
    target_price: float | None = None
    size_multiplier: float = 1.0


def _bounded(value: Any, low: float, high: float, default: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if number != number:
        return default
    return max(low, min(high, number))


def parse_ai_advice(raw: Mapping[str, Any] | None) -> AIDCAAdvice:
    """Normalize untrusted learner/LLM output into bounded values."""
    raw = raw or {}
    action = str(raw.get("action", "WAIT")).upper()
    if action not in {item.value for item in DCAAction}:
        action = DCAAction.WAIT.value
    return AIDCAAdvice(
        action=action,
        confidence=_bounded(raw.get("confidence", 0.0), 0.0, 1.0, 0.0),
        learner_score=_bounded(raw.get("learner_score", 0.0), 0.0, 1.0, 0.0),
        max_price=(
            _bounded(raw["max_price"], 0.0, float("inf"), 0.0)
            if raw.get("max_price") is not None
            else None
        ),
        size_multiplier=_bounded(raw.get("size_multiplier", 1.0), 0.1, 10.0, 1.0),
        valid_for_seconds=_bounded(raw.get("valid_for_seconds", 30.0), 1.0, 300.0, 30.0),
        reason=str(raw.get("reason", ""))[:500],
    )


def evaluate_dca_order(
    *,
    side: str,
    market: MarketSnapshot,
    order: Mapping[str, Any] | None,
    now_ts: float,
    config: AdaptiveDCAConfig | None = None,
    ai_advice: Mapping[str, Any] | None = None,
    risk_allowed: bool = True,
) -> DCAActionDecision:
    """Return the safest useful action for one pending DCA order.

    AI output is advisory only. An AI request can accelerate an order only when
    confidence, learner score, liquidity, momentum, and price bounds all pass.
    """
    cfg = config or AdaptiveDCAConfig()
    normalized_side = str(side).upper()
    if normalized_side not in {"LONG", "SHORT"}:
        return DCAActionDecision(DCAAction.PAUSE, "invalid side", 0.0)
    if not cfg.enabled:
        return DCAActionDecision(DCAAction.WAIT, "adaptive DCA disabled", 0.0)
    if not risk_allowed:
        return DCAActionDecision(DCAAction.PAUSE, "risk gate denied", 0.0)
    if market.price <= 0 or market.liquidity_score < 0:
        return DCAActionDecision(DCAAction.PAUSE, "invalid market snapshot", 0.0)
    if not order:
        return DCAActionDecision(DCAAction.WAIT, "no pending order", 0.0)

    try:
        order_price = float(order.get("price", 0.0))
        placed_at = float(order.get("placed_at_ts", now_ts))
    except (TypeError, ValueError):
        return DCAActionDecision(DCAAction.PAUSE, "invalid order metadata", 0.0)

    if order_price <= 0:
        return DCAActionDecision(DCAAction.PAUSE, "invalid order price", 0.0)

    age = max(0.0, now_ts - placed_at)
    if age > cfg.max_order_age_seconds:
        return DCAActionDecision(DCAAction.REPRICE, "order exceeded maximum age", 0.0, order_price)

    stale = age >= cfg.order_ttl_seconds
    advice = parse_ai_advice(ai_advice)
    ai_valid = (
        advice.action == DCAAction.ACCELERATE.value
        and advice.confidence >= cfg.acceleration_confidence
        and advice.learner_score >= cfg.min_learner_score
        and advice.valid_for_seconds > 0
    )

    if cfg.aggressive_enabled and ai_valid:
        if advice.max_price is not None:
            within_price_bound = (
                market.price <= advice.max_price
                if normalized_side == "LONG"
                else market.price >= advice.max_price
            )
        else:
            within_price_bound = True

        liquidity_ok = market.liquidity_score >= 0.50 and market.spread_pct <= 0.50
        momentum_aligned = (
            market.momentum <= -0.25
            if normalized_side == "LONG"
            else market.momentum >= 0.25
        )
        if within_price_bound and liquidity_ok and momentum_aligned:
            multiplier = min(advice.size_multiplier, cfg.max_acceleration_multiplier)
            return DCAActionDecision(
                DCAAction.ACCELERATE,
                advice.reason or "AI/learner acceleration approved",
                advice.confidence,
                market.price,
                multiplier,
            )

    if stale:
        target = order_price
        if normalized_side == "LONG":
            target = min(order_price, market.price)
        else:
            target = max(order_price, market.price)
        return DCAActionDecision(
            DCAAction.REPRICE,
            "pending order is stale",
            max(0.0, advice.confidence),
            target,
        )

    return DCAActionDecision(DCAAction.WAIT, "order remains valid", advice.confidence)
