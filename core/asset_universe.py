"""
core/asset_universe.py - Live Asset Universe from Hyperliquid HIP-4
Self-contained. No dependency on HIP4MetadataManager or HL SDK client.
Direct HTTP to HL info API with 5-minute cache per Rate Limiting Discipline.
"""
import logging
import time
import threading
from typing import Optional, List, Dict
import requests

logger = logging.getLogger(__name__)

HL_INFO_URL = "https://api.hyperliquid.xyz/info"
REFRESH_INTERVAL = 300  # 5 minutes per Rate Limiting Discipline
REQUEST_TIMEOUT = 15
MIN_ASSETS = 10

DEFAULT_EXCLUSIONS = {"USDC", "USDT"}

_TICK_FALLBACK = {
    "BTC": 1.0, "ETH": 0.1, "SOL": 0.01, "BNB": 0.01,
    "XRP": 0.0001, "DOGE": 0.00001, "AVAX": 0.01,
    "LINK": 0.001, "HYPE": 0.001, "MATIC": 0.0001,
}


class _AssetMeta:
    __slots__ = ("name", "sz_dec", "max_lev", "only_isolated", "is_delisted", "tick")

    def __init__(self, name, sz_dec, max_lev, only_isolated, is_delisted, tick):
        self.name = name
        self.sz_dec = sz_dec
        self.max_lev = max_lev
        self.only_isolated = only_isolated
        self.is_delisted = is_delisted
        self.tick = tick


class AssetUniverse:
    """Thread-safe singleton. Auto-refreshes every 5 minutes."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                inst = super().__new__(cls)
                inst._assets: Dict[str, _AssetMeta] = {}
                inst._last_refresh: float = 0.0
                inst._refresh_lock = threading.Lock()
                inst._exclusions: set = set(DEFAULT_EXCLUSIONS)
                inst._initialized: bool = False
                cls._instance = inst
        return cls._instance

    # ── Public API (unchanged interface) ──────────────────────────────

    def sz_decimals(self, coin: str) -> int:
        meta = self._get(coin)
        return meta.sz_dec if meta else 4

    def tick_size(self, coin: str) -> float:
        meta = self._get(coin)
        return meta.tick if meta else 0.0001

    def max_leverage(self, coin: str) -> int:
        meta = self._get(coin)
        return meta.max_lev if meta else 10

    def exists(self, coin: str) -> bool:
        self._ensure_fresh()
        return coin.upper() in self._assets

    def to_ticker(self, coin: str) -> str:
        return f"{coin.upper()}-USD"

    def to_coin(self, ticker: str) -> str:
        return ticker.replace("-USD", "").replace("USDT", "").upper()

    def tradeable_coins(self) -> List[str]:
        self._ensure_fresh()
        return sorted([
            n for n, m in self._assets.items()
            if n not in self._exclusions
            and not m.is_delisted
            and not m.only_isolated
        ])

    def signal_scanner_coins(self) -> List[str]:
        return self.tradeable_coins()

    def total_assets(self) -> int:
        return len(self._assets)

    def last_refresh_age(self) -> float:
        return time.time() - self._last_refresh

    def force_refresh(self) -> bool:
        return self._refresh()

    def start_background_refresh(self):
        t = threading.Thread(target=self._bg_loop, daemon=True)
        t.start()
        logger.info(f"AssetUniverse: background refresh started ({REFRESH_INTERVAL}s)")

    # ── Internal ──────────────────────────────────────────────────────

    def _get(self, coin: str) -> Optional[_AssetMeta]:
        self._ensure_fresh()
        return self._assets.get(coin.upper())

    def _ensure_fresh(self):
        if not self._initialized or (time.time() - self._last_refresh) > REFRESH_INTERVAL:
            with self._refresh_lock:
                if not self._initialized or (time.time() - self._last_refresh) > REFRESH_INTERVAL:
                    self._refresh()

    def _refresh(self) -> bool:
        try:
            r = requests.post(HL_INFO_URL, json={"type": "meta"}, timeout=REQUEST_TIMEOUT)
            if r.status_code != 200:
                logger.error(f"AssetUniverse: HTTP {r.status_code}")
                return False

            universe = r.json().get("universe", [])
            if len(universe) < MIN_ASSETS:
                logger.error(f"AssetUniverse: only {len(universe)} assets — skipping")
                return False

            # Fetch prices for tick derivation
            prices = self._fetch_prices()

            new_assets = {}
            for a in universe:
                name = a.get("name", "").upper()
                if not name:
                    continue
                sz = int(a.get("szDecimals", 4))
                ml = int(a.get("maxLeverage", 10))
                iso = bool(a.get("onlyIsolated", False))
                tick = self._derive_tick(name, prices.get(name, 0))
                dl = bool(a.get("isDelisted", False))
                new_assets[name] = _AssetMeta(name, sz, ml, iso, dl, tick)

            # Fetch Spot Meta - Construct pair names from token indices
            new_spot = []
            try:
                r_spot = requests.post(HL_INFO_URL, json={"type": "spotMeta"}, timeout=REQUEST_TIMEOUT)
                if r_spot.status_code == 200:
                    spot_data = r_spot.json()
                    # Build token index -> name map
                    token_map = {t["index"]: t.get("name", "") for t in spot_data.get("tokens", [])}
                    token_details = {t["index"]: t for t in spot_data.get("tokens", [])}
                    
                    for pair in spot_data.get("universe", []):
                        # Get token indices [base, quote]
                        token_indices = pair.get("tokens", [])
                        if len(token_indices) >= 2:
                            base_idx = token_indices[0]
                            quote_idx = token_indices[1]
                            
                            # Construct pair name from token names
                            base_name = token_map.get(base_idx, "")
                            quote_name = token_map.get(quote_idx, "")
                            
                            # Skip if we can't resolve token names
                            if not base_name or not quote_name:
                                continue
                            
                            # Normalize token names: strip "U" prefix from crypto assets (UBTC->BTC, UETH->ETH)
                            # Keep stablecoins as-is (USDC, USDT, USDH, USDE)
                            stablecoins = {"USDC", "USDT", "USDH", "USDE", "USD", "DAI", "FRAX"}
                            
                            def normalize_token_name(name):
                                if name.startswith("U") and len(name) > 2 and name not in stablecoins:
                                    return name[1:]  # Strip "U" prefix
                                return name
                            
                            base_display = normalize_token_name(base_name)
                            quote_display = normalize_token_name(quote_name)
                            
                            # Construct the pair name (e.g., "BTC/USDC")
                            pair_name = f"{base_display}/{quote_display}"
                            
                            # Get szDecimals from the base token
                            sz_dec = token_details.get(base_idx, {}).get("szDecimals", 4)
                            
                            # Skip USDC/USDC or other same-token pairs
                            if base_name == quote_name:
                                continue
                            
                            new_spot.append({
                                "name": pair_name,
                                "sz_decimals": sz_dec,
                                "is_canonical": pair.get("isCanonical", False),
                                "index": pair.get("index", 0)
                            })
            except Exception as e:
                logger.error(f"AssetUniverse spot fetch error: {e}")

            # Fetch Volume Contexts for Trending
            new_volume = {}
            try:
                r_ctx = requests.post(HL_INFO_URL, json={"type": "metaAndAssetCtxs"}, timeout=REQUEST_TIMEOUT)
                if r_ctx.status_code == 200:
                    ctx_data = r_ctx.json()
                    if isinstance(ctx_data, list) and len(ctx_data) == 2:
                        meta_universe = ctx_data[0].get("universe", [])
                        ctxs = ctx_data[1]
                        for a, c in zip(meta_universe, ctxs):
                            name = a.get("name", "").upper()
                            vol = float(c.get("dayNtlVlm", 0))
                            if name:
                                new_volume[name] = vol
            except Exception as e:
                logger.error(f"AssetUniverse volume fetch error: {e}")

            self._assets = new_assets
            self._spot_pairs = new_spot
            self._volume_ctxs = new_volume
            self._last_refresh = time.time()
            self._initialized = True
            logger.info(f"AssetUniverse: {len(new_assets)} perps, {len(new_spot)} spot pairs loaded")
            return True

        except Exception as e:
            logger.error(f"AssetUniverse refresh error: {e}", exc_info=True)
            return False

    def _fetch_prices(self) -> Dict[str, float]:
        try:
            r = requests.post(HL_INFO_URL, json={"type": "allMids"}, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                return {k: float(v) for k, v in r.json().items()}
        except Exception:
            pass
        return {}

    def _derive_tick(self, coin: str, price: float) -> float:
        if coin in _TICK_FALLBACK:
            return _TICK_FALLBACK[coin]
        if price <= 0:
            return 0.0001
        if price >= 10000: return 1.0
        if price >= 1000:  return 0.1
        if price >= 100:   return 0.01
        if price >= 10:    return 0.001
        if price >= 1:     return 0.0001
        if price >= 0.1:   return 0.00001
        return 0.000001

    def get_categorized_assets(self) -> dict:
        """Return assets grouped by PERP, SPOT, TRENDING."""
        self._ensure_fresh()
        
        # PERP: All non-delisted tradeable coins
        perp_coins = self.tradeable_coins()
        
        # SPOT: Canonical spot pairs
        spot_coins = [p["name"] for p in self._spot_pairs]
        
        # TRENDING: Top 10 by volume
        sorted_by_vol = sorted(self._volume_ctxs.items(), key=lambda x: x[1], reverse=True)
        trending_coins = [name for name, vol in sorted_by_vol[:10]]
        
        return {
            "PERP": perp_coins,
            "SPOT": spot_coins,
            "TRENDING": trending_coins,
            "last_refresh": self._last_refresh
        }

    def _bg_loop(self):
        while True:
            time.sleep(REFRESH_INTERVAL)
            try:
                self._refresh()
            except Exception as e:
                logger.error(f"AssetUniverse bg refresh error: {e}")


def get_universe() -> AssetUniverse:
    return AssetUniverse()


def init_asset_universe() -> AssetUniverse:
    u = get_universe()
    if not u._initialized:
        u.force_refresh()
    if u._initialized:
        u.start_background_refresh()
        logger.info(f"AssetUniverse initialized: {u.total_assets()} assets from HIP-4")
    else:
        logger.error("AssetUniverse FAILED to initialize — check HL connectivity")
    return u
