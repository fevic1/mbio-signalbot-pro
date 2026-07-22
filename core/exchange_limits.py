"""
core/exchange_limits.py — Exchange Limits Loader
Single source of truth for exchange-specific trading constraints.
Per CODING_STANDARD: No magic numbers. No duplicated business logic.
Dependency injection via function call, not global state.
"""
import logging
import os
from functools import lru_cache
from typing import Dict, Any

import yaml

logger = logging.getLogger(__name__)

_DEFAULT_LIMITS: Dict[str, Any] = {
    "min_notional_usd": 10.0,
    "min_notional_buffer": 1.15,
    "min_balance_for_trading": 12.0,
    "max_leverage": 20,
    "api_rate_limit_per_second": 10,
    "api_rate_limit_burst": 20,
}


@lru_cache(maxsize=1)
def _load_all_limits() -> Dict[str, Any]:
    """Load config/exchange_limits.yaml once (cached). Returns {} on any failure.
    Single file-read shared by get_exchange_limits and is_exchange_configured
    (CODING_STANDARD: no duplicated business logic)."""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "config",
        "exchange_limits.yaml",
    )
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            logger.error("❌ exchange_limits.yaml has invalid structure")
            return {}
        return data
    except FileNotFoundError:
        logger.warning(f"⚠️ exchange_limits.yaml not found at {config_path}")
        return {}
    except Exception as e:
        logger.error(f"❌ Failed to load exchange_limits.yaml: {type(e).__name__}: {e}")
        return {}


def is_exchange_configured(exchange: str) -> bool:
    """True iff the exchange has an explicit limits block in exchange_limits.yaml.
    Trading paths MUST gate on this and refuse to trade on an unconfigured exchange,
    so one exchange's minimums can never silently govern another's orders.
    (Multi-exchange safety; EXECUTION_RULES.)"""
    key = (exchange or "").lower().strip()
    return isinstance(_load_all_limits().get(key), dict)


@lru_cache(maxsize=16)
def get_exchange_limits(exchange: str = "hyperliquid") -> Dict[str, Any]:
    """Load exchange-specific limits. config/exchange_limits.yaml is authoritative;
    _DEFAULT_LIMITS is a conservative resilience fallback for partial/missing config.
    Callers that must not inherit another exchange's numbers gate on
    is_exchange_configured(exchange) FIRST."""
    exchange = (exchange or "hyperliquid").lower().strip()
    all_limits = _load_all_limits()
    exchange_limits = all_limits.get(exchange)
    result = _DEFAULT_LIMITS.copy()
    if isinstance(exchange_limits, dict):
        result.update(exchange_limits)
        logger.info(
            f"✅ Loaded exchange limits for '{exchange}': "
            f"min_notional=${result['min_notional_usd']}, "
            f"buffer={result['min_notional_buffer']}x, "
            f"min_balance=${result['min_balance_for_trading']}"
        )
    else:
        logger.warning(
            f"⚠️ No limits configured for exchange '{exchange}'; using conservative "
            f"defaults. Strict callers must check is_exchange_configured() first."
        )
    return result


def get_effective_min_notional(exchange: str = "hyperliquid") -> float:
    """Get min notional including buffer. Use this for order validation."""
    limits = get_exchange_limits(exchange)
    return limits["min_notional_usd"] * limits["min_notional_buffer"]


def can_trade(balance: float, exchange: str = "hyperliquid") -> bool:
    """Check if account balance is sufficient for any valid trade."""
    limits = get_exchange_limits(exchange)
    return balance >= limits["min_balance_for_trading"]
