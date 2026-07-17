"""
HIP-4 Metadata Manager — Institutional Standard Implementation
"""

import time
import logging
import threading
import requests
from typing import Optional, Dict, Any, List
from decimal import Decimal

logger = logging.getLogger(__name__)


class HIP4MetadataManager:
    _instance = None
    _lock = threading.Lock()
    _CACHE_TTL_SECONDS = 900  # Refresh every 15 minutes
    
    def __init__(self):
        self._metadata: Dict[str, Any] = {}
        self._asset_specs: Dict[str, Dict[str, Any]] = {}
        self._last_fetch_time: float = 0
        self._info_client = None
        self._initialized = False
        
    @classmethod
    def get_instance(cls) -> 'HIP4MetadataManager':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def initialize(self, info_client) -> bool:
        self._info_client = info_client
        return self._refresh_metadata()
    
    def _refresh_metadata(self) -> bool:
        try:
            if self._initialized and (time.time() - self._last_fetch_time) < self._CACHE_TTL_SECONDS:
                return True
            logger.info("📡 HIP-4: Refreshing asset universe metadata...")
            meta = self._info_client.meta()
            universe = meta.get("universe", [])
            
            new_specs = {}
            for asset in universe:
                name = asset.get("name")
                if name:
                    new_specs[name] = {
                        "szDecimals": asset.get("szDecimals", 0),
                        "maxLeverage": asset.get("maxLeverage", 0),
                        "onlyIsolated": asset.get("onlyIsolated", False),
                        "name": name
                    }
            
            with self._lock:
                self._metadata = meta
                self._asset_specs = new_specs
                self._last_fetch_time = time.time()
                self._initialized = True
            
            logger.info(f"✅ HIP-4: Loaded {len(new_specs)} assets from exchange")
            return True
            
        except Exception as e:
            logger.error(f"❌ HIP-4: Metadata refresh failed: {e}")
            if self._initialized:
                logger.warning("⚠️ HIP-4: Using stale cached metadata")
                return True
            return False
    
    def _ensure_fresh(self):
        if time.time() - self._last_fetch_time > self._CACHE_TTL_SECONDS:
            self._refresh_metadata()
    
    def get_asset_spec(self, coin: str) -> Optional[Dict[str, Any]]:
        self._ensure_fresh()
        return self._asset_specs.get(coin)
    
    def get_sz_decimals(self, coin: str) -> int:
        spec = self.get_asset_spec(coin)
        return spec.get("szDecimals", 0) if spec else 0
    
    def get_max_leverage(self, coin: str) -> int:
        spec = self.get_asset_spec(coin)
        return spec.get("maxLeverage", 1) if spec else 1
    
    def is_isolated_only(self, coin: str) -> bool:
        spec = self.get_asset_spec(coin)
        return spec.get("onlyIsolated", False) if spec else False
    
    def format_size(self, coin: str, size: float) -> float:
        sz_decimals = self.get_sz_decimals(coin)
        formatted = round(float(size), sz_decimals)
        return float(Decimal(str(formatted)).normalize())
    
    def is_asset_supported(self, coin: str) -> bool:
        self._ensure_fresh()
        return coin in self._asset_specs
    
    def get_all_supported_assets(self) -> List[str]:
        self._ensure_fresh()
        return list(self._asset_specs.keys())
    
    def get_universe_stats(self) -> Dict[str, int]:
        self._ensure_fresh()
        return {
            "total_assets": len(self._asset_specs),
            "cache_age_seconds": int(time.time() - self._last_fetch_time),
            "cache_ttl_seconds": self._CACHE_TTL_SECONDS
        }

    def resolve_universe(self, rules: dict) -> List[str]:
        """
        Dynamically resolve the trading universe based on YAML rules.
        Uses raw HTTP for metaAndAssetCtxs (SDK doesn't expose volume).
        """
        try:
            # Fetch metadata and asset contexts via raw HTTP
            resp = requests.post(
                "https://api.hyperliquid.xyz/info",
                json={"type": "metaAndAssetCtxs"},
                timeout=15
            )
            resp.raise_for_status()
            data = resp.json()
            
            # Hyperliquid returns a list: [meta_dict, [ctx1, ctx2, ...]]
            if isinstance(data, list) and len(data) >= 2:
                universe = data[0].get("universe", [])
                asset_ctxs = data[1]
            else:
                universe = data.get("universe", [])
                asset_ctxs = data.get("assetCtxs", [])
            
            candidates = []
            stablecoins = {"USDC", "USDT", "FDUSD", "DAI", "TUSD", "USDD", "PURR"}
            
            for i, asset in enumerate(universe):
                name = asset.get("name")
                if not name: 
                    continue
                
                # Skip stablecoins if requested
                if rules.get("exclude_stablecoins", True) and name in stablecoins:
                    continue
                
                # Skip SPOT assets
                if asset.get("isSpot", False): 
                    continue
                
                # Get 24h volume (returned as string in API)
                ctx = asset_ctxs[i] if i < len(asset_ctxs) else {}
                day_ntl_str = ctx.get("dayNtlVlm", "0")
                day_ntl = float(day_ntl_str) if day_ntl_str else 0.0
                
                if day_ntl >= rules.get("min_volume_usd", 0):
                    candidates.append({"name": name, "volume": day_ntl})
            
            # Sort by volume descending
            candidates.sort(key=lambda x: x["volume"], reverse=True)
            
            # Take top N
            top_n = rules.get("top_n", 50)
            resolved = [c["name"] for c in candidates[:top_n]]
            
            logger.info(f"✅ HIP-4: Dynamically resolved universe: {len(resolved)} assets (Top {top_n} by volume)")
            return resolved
            
        except Exception as e:
            logger.error(f"❌ HIP-4: Universe resolution failed: {e}. Falling back to static list.")
            return []

    def categorize_assets(self) -> dict:
        """
        Categorize the live universe into PERP, SPOT, and TRADFI.
        Matches Hyperliquid's exact exchange grouping.
        """
        self._ensure_fresh()
        categories = {"PERP": [], "SPOT": [], "TRADFI": []}
        
        # Known TRADFI tickers on Hyperliquid (Pre-market/Stocks)
        tradfi_tickers = {"AAPL", "TSLA", "NVDA", "AMZN", "META", "GOOGL", "SPY", "QQQ", "MSFT", "COIN", "MSTR", "AMD", "NFLX", "SMCI", "PLTR"}
        
        try:
            # Use cached metadata to avoid unnecessary API calls
            universe = self._metadata.get("universe", [])
            
            for asset in universe:
                name = asset.get("name")
                if not name: continue
                
                is_spot = asset.get("isSpot", False)
                
                # Categorization Logic
                if name in tradfi_tickers or "TRADFI" in name:
                    categories["TRADFI"].append(name)
                elif is_spot:
                    categories["SPOT"].append(name)
                else:
                    categories["PERP"].append(name)
                    
            logger.info(f"✅ HIP-4 Categorized: {len(categories['PERP'])} PERP | {len(categories['SPOT'])} SPOT | {len(categories['TRADFI'])} TRADFI")
            return categories
            
        except Exception as e:
            logger.error(f"❌ HIP-4 Categorization failed: {e}")
            return {"PERP": list(self._asset_specs.keys()), "SPOT": [], "TRADFI": []}

    def get_live_market_data(self) -> dict:
        """Fetch and cache live mid-prices, volumes, and funding rates (3s TTL)."""
        import time
        if not hasattr(self, '_last_market_fetch'):
            self._last_market_fetch = 0
            self._cached_market_data = {"prices": {}, "volumes": {}, "funding": {}}
            
        if time.time() - self._last_market_fetch < 3:
            return self._cached_market_data
            
        try:
            mids = self._info_client.all_mids()
            resp = requests.post("https://api.hyperliquid.xyz/info", json={"type": "metaAndAssetCtxs"}, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            universe = data[0].get("universe", []) if isinstance(data, list) else data.get("universe", [])
            ctxs = data[1] if isinstance(data, list) else data.get("assetCtxs", [])
            
            prices, volumes, funding = {}, {}, {}
            for i, asset in enumerate(universe):
                name = asset.get("name")
                if name:
                    prices[name] = float(mids.get(name, 0))
                    ctx = ctxs[i] if i < len(ctxs) else {}
                    volumes[name] = float(ctx.get("dayNtlVlm", 0))
                    funding[name] = float(ctx.get("funding", 0))
                    
            self._cached_market_data = {"prices": prices, "volumes": volumes, "funding": funding}
            self._last_market_fetch = time.time()
            return self._cached_market_data
        except Exception as e:
            logger.error(f"❌ HIP-4 Market data fetch failed: {e}")
            return self._cached_market_data
