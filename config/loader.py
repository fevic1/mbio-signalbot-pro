"""
Configuration Loader
Loads settings from YAML and environment variables
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class Config:
    """Singleton configuration manager"""
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance
    
    def _load(self):
        load_dotenv(override=True) # FIX: Allow reloading changed env vars
        # Load environment variables
        load_dotenv()
        
        # Load YAML config
        config_path = Path(__file__).parent / "settings.yaml"
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)
        
        # Override with environment variables
        self._apply_env_overrides()
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides"""
        env_mappings = {
            'TELEGRAM_BOT_TOKEN': ('telegram', 'bot_token'),
            'TELEGRAM_CHAT_ID': ('telegram', 'chat_id'),
            'GROQ_API_KEY': ('ai', 'groq_api_key'),
            'CEREBRAS_API_KEY': ('ai', 'cerebras_api_key'),
            'OPENROUTER_API_KEY': ('ai', 'openrouter_api_key'),
            'HL_NETWORK': ('hyperliquid', 'network'),
            'HL_ACCOUNT_ADDRESS': ('hyperliquid', 'account_address'),
            'HL_PRIVATE_KEY': ('hyperliquid', 'private_key'),
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.environ.get(env_var)
            if value:
                # Navigate nested dict
                d = self._config
                for key in config_path[:-1]:
                    d = d.setdefault(key, {})
                d[config_path[-1]] = value
    
    def get(self, *keys: str, default: Any = None) -> Any:
        """Get nested config value: config.get('risk', 'max_open_positions')"""
        d = self._config
        for key in keys:
            if isinstance(d, dict):
                d = d.get(key)
            else:
                return default
            if d is None:
                return default
        return d
    
    def get_all_assets(self) -> Dict[str, str]:
        """Get all assets from all tiers"""
        assets = {}
        for tier in ['tier1', 'tier2', 'tier3']:
            tier_assets = self.get('assets', tier, default={})
            assets.update(tier_assets)
        return assets
    
    def get_tier_assets(self, tier: str) -> Dict[str, str]:
        """Get assets for specific tier"""
        return self.get('assets', tier, default={})
    
    def reload(self):
        """Reload configuration"""
        self._load()


# Global config instance
config = Config()
