"""
Strategy Registry — Maps strategy IDs to their Python classes.
Add new strategies here. Only the active strategy runs per cycle.
"""
from strategies.tv_bos_v6 import TVBOSV6Strategy
from strategies.tv_smc_fvg import TVSMCFVGStrategy

STRATEGY_REGISTRY = {
    "TV_BOS_V6": TVBOSV6Strategy,
    "TV_SMC_FVG": TVSMCFVGStrategy,
}

def get_strategy_class(strategy_id: str):
    """Return the strategy class for a given ID, or None."""
    return STRATEGY_REGISTRY.get(strategy_id)

def list_strategies() -> list:
    """Return list of available strategy IDs."""
    return list(STRATEGY_REGISTRY.keys())
