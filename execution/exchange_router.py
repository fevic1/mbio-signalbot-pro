"""
Exchange Router — Dynamic registry-based routing.
Zero hardcoded exchange names. Add exchanges via registration only.
"""
import logging
import os
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)

# Registry: Populated at startup from config/env
EXECUTOR_REGISTRY: Dict[str, Callable] = {}

def register_executor(exchange_name: str, executor_func: Callable):
    """Register an exchange executor. Called during app initialization."""
    EXECUTOR_REGISTRY[exchange_name.lower()] = executor_func
    logger.info(f"📝 Registered executor for: {exchange_name}")

def execute_order_for_exchange(exchange: str, **kwargs) -> Dict[str, Any]:
    """Route order via registry. Raises if exchange not registered."""
    key = exchange.lower()
    if key not in EXECUTOR_REGISTRY:
        available = ", ".join(EXECUTOR_REGISTRY.keys())
        raise ValueError(f"Unknown exchange '{exchange}'. Available: {available}")
    
    return EXECUTOR_REGISTRY[key](**kwargs)

# Initialize registry from environment/config at module load
def _init_registry():
    default_ex = os.getenv("DEFAULT_EXCHANGE", "").lower()
    if default_ex in ("hyperliquid", ""):
        from execution.hl_executor import execute_hl_order
        register_executor("hyperliquid", execute_hl_order)
    # Future: elif default_ex == "binance": register...
    # Future: elif default_ex == "okx": register...

_init_registry()
