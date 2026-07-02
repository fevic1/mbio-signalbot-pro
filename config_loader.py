"""
config_loader.py — Load and cache strategy configuration.
Guarantees dict return type for safe .get() access.
"""
import os
import yaml
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

CONFIG_PATH = os.getenv("CONFIG_PATH", "config/strategy_config.yaml")

@lru_cache(maxsize=1)
def get_config() -> dict:
    """
    Load strategy configuration from YAML file.
    
    Returns:
        dict: Configuration dictionary (never a list or other type)
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config parses as non-dict
    """
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")
    
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    
    # CRITICAL: Ensure we always return a dict
    if cfg is None:
        logger.warning(f"⚠️ Config file {CONFIG_PATH} is empty — using defaults")
        return {}
    
    if not isinstance(cfg, dict):
        raise ValueError(
            f"Config must parse as dict, got {type(cfg).__name__}. "
            f"Check {CONFIG_PATH} for YAML syntax issues (e.g., root-level list)."
        )
    
    logger.info(f"✅ Config loaded from {CONFIG_PATH}")
    return cfg


def reload_config() -> dict:
    """Force reload config (bypasses lru_cache)."""
    get_config.cache_clear()
    return get_config()
