"""
config/config.py — Institutional-grade configuration with Pydantic validation.
Loads from environment variables with YAML fallback. Secure and type-safe.
"""
import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

class TradingConfig(BaseModel):
    """Trading parameters with validation."""
    max_open_positions: int = Field(default=2, ge=1, le=10)
    entry_min_confidence: int = Field(default=80, ge=50, le=100)
    risk_pct_per_trade: float = Field(default=0.02, ge=0.001, le=0.1)
    small_account_threshold: float = Field(default=100.0, gt=0)
    small_account_max_pct: float = Field(default=0.50, gt=0, le=1.0)
    large_account_max_pct: float = Field(default=0.20, gt=0, le=1.0)
    min_order_value_usd: float = Field(default=10.0, gt=0)
    drawdown_halt_pct: float = Field(default=-15.0, le=0)
    correlation_block: bool = True
    correlated_groups: List[List[str]] = Field(default=[["BTC", "ETH"], ["SOL", "DOGE"]])

class SignalsConfig(BaseModel):
    """Signal thresholds."""
    strong_buy_1d_rsi_max: int = Field(default=32, ge=0, le=100)
    strong_buy_1h_rsi_max: int = Field(default=45, ge=0, le=100)
    buy_1d_rsi_max: int = Field(default=38, ge=0, le=100)
    strong_sell_1d_rsi_min: int = Field(default=68, ge=0, le=100)
    strong_sell_1h_rsi_min: int = Field(default=58, ge=0, le=100)
    sell_1d_rsi_min: int = Field(default=62, ge=0, le=100)

class TradePlanConfig(BaseModel):
    """Trade plan ATR multipliers."""
    sl_atr_multiplier: float = Field(default=1.5, gt=0)
    tp1_atr_multiplier: float = Field(default=1.0, gt=0)
    tp2_atr_multiplier: float = Field(default=2.0, gt=0)
    tp3_atr_multiplier: float = Field(default=3.0, gt=0)
    min_atr_pct: float = Field(default=0.02, gt=0)

class IntervalsConfig(BaseModel):
    """Timing intervals."""
    position_monitor_sec: int = Field(default=60, ge=10)
    quick_scanner_sec: int = Field(default=900, ge=60)
    entry_scanner_sec: int = Field(default=1800, ge=60)
    full_analysis_hours: int = Field(default=2, ge=1)
    big_move_threshold: float = Field(default=0.03, gt=0)
    cache_price_threshold: float = Field(default=0.02, gt=0)

class AIConfig(BaseModel):
    """AI provider settings."""
    batch_size: int = Field(default=2, ge=1, le=10)
    max_retries: int = Field(default=3, ge=1, le=5)
    retry_backoff_sec: int = Field(default=10, ge=1)
    provider_order: List[str] = Field(default=["groq", "cerebras", "openrouter"])
    models: Dict[str, str] = Field(default={
        "groq": "llama-3.3-70b-versatile",
        "cerebras": "llama3.1-70b",
        "openrouter": "meta-llama/llama-3.3-70b-instruct"
    })

class HyperliquidConfig(BaseModel):
    """Hyperliquid precision rules."""
    assets: List[str] = Field(default=["BTC", "ETH", "SOL", "XRP", "DOGE"])
    precision: Dict[str, Dict[str, float]] = Field(default={
        "BTC": {"tick_size": 0.1, "price_dec": 1, "sz_dec": 5},
        "ETH": {"tick_size": 0.01, "price_dec": 2, "sz_dec": 4},
        "SOL": {"tick_size": 0.01, "price_dec": 2, "sz_dec": 2},
        "XRP": {"tick_size": 0.0001, "price_dec": 4, "sz_dec": 0},
        "DOGE": {"tick_size": 0.00001, "price_dec": 5, "sz_dec": 0},
    })
    
    @validator("precision", pre=True)
    def parse_precision(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

class AppConfig(BaseModel):

    def get(self, key: str, default=None):
        """Backward compatibility for dict-like .get() access."""
        data = self.model_dump() if hasattr(self, 'model_dump') else self.dict()
        return data.get(key, default)

    """Root configuration."""
    trading: TradingConfig = Field(default_factory=TradingConfig)
    signals: SignalsConfig = Field(default_factory=SignalsConfig)
    trade_plan: TradePlanConfig = Field(default_factory=TradePlanConfig)
    intervals: IntervalsConfig = Field(default_factory=IntervalsConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    hyperliquid: HyperliquidConfig = Field(default_factory=HyperliquidConfig)
    assets: Dict[str, Dict[str, str]] = Field(default={
        "crypto": {
            "BTC": "BTC-USD",
            "ETH": "ETH-USD",
            "SOL": "SOL-USD",
            "XRP": "XRP-USD",
            "DOGE": "DOGE-USD",
            "HYPE": "HYPE-USD",
            "AVAX": "AVAX-USD",
            "LINK": "LINK-USD"
        }
    })

@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    """Load configuration with environment variable overrides."""
    config_path = Path(os.getenv("MBIO_CONFIG_PATH", "config/strategy_config.yaml"))
    
    # Load YAML base config
    yaml_config = {}
    if config_path.exists():
        try:
            with open(config_path) as f:
                yaml_config = yaml.safe_load(f) or {}
            logger.info(f"✅ Config loaded from {config_path}")
        except Exception as e:
            logger.error(f"❌ Config parse error: {e}")
    
    # Override with environment variables
    if os.getenv("TRADING_MAX_POSITIONS"):
        yaml_config.setdefault("trading", {})["max_open_positions"] = int(os.getenv("TRADING_MAX_POSITIONS"))
    
    if os.getenv("TRADING_TICK_SIZES"):
        try:
            tick_sizes = json.loads(os.getenv("TRADING_TICK_SIZES"))
            yaml_config.setdefault("hyperliquid", {})["precision"] = tick_sizes
        except json.JSONDecodeError:
            logger.error("❌ Invalid TRADING_TICK_SIZES JSON")
    
    # Validate and return
    universe_rules = yaml_config.get("universe", {})
    if universe_rules.get("mode") == "dynamic":
        try:
            from core.hip4_metadata import HIP4MetadataManager
            from hyperliquid.info import Info
            from hyperliquid.utils import constants
            
            info = Info(constants.MAINNET_API_URL, skip_ws=True)
            manager = HIP4MetadataManager.get_instance()
            manager.initialize(info)
            
            resolved_assets = manager.resolve_universe(universe_rules)
            if resolved_assets:
                yaml_config.setdefault("hyperliquid", {})["assets"] = resolved_assets
                logger.info(f"🌍 Dynamic Universe injected into config: {len(resolved_assets)} assets")
        except Exception as e:
            logger.error(f"❌ Dynamic Universe injection failed: {e}")
    # ------------------------------------

    try:
        config = AppConfig(**yaml_config)
        logger.info(f"✅ Configuration validated: {config.trading.max_open_positions} max positions")
        return config
    except Exception as e:
        logger.error(f"❌ Configuration validation failed: {e}")
        # Return defaults if validation fails
        return AppConfig()

# Backward compatibility wrapper
def get_config_dict() -> dict:
    """Return config as dict for backward compatibility."""
    config = get_config()
    return config.dict()
