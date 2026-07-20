import sys
import shutil
from datetime import datetime

DRY_RUN = "--dry-run" in sys.argv
RESULTS = []


def patch(filepath, description, old, new):
    try:
        with open(filepath, "r") as f:
            code = f.read()
        if old not in code:
            RESULTS.append(("SKIP", filepath, description + " -- pattern not found"))
            return False
        if new in code:
            RESULTS.append(("ALREADY", filepath, description + " -- already applied"))
            return True
        if DRY_RUN:
            RESULTS.append(("DRY-RUN", filepath, description))
            return True
        backup = filepath + ".bak." + datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(filepath, backup)
        code = code.replace(old, new, 1)
        with open(filepath, "w") as f:
            f.write(code)
        RESULTS.append(("APPLIED", filepath, description))
        return True
    except FileNotFoundError:
        RESULTS.append(("MISSING", filepath, description + " -- file not found"))
        return False
    except Exception as e:
        RESULTS.append(("ERROR", filepath, description + " -- " + str(e)))
        return False


# PATCH 1: main.py - Add AssetUniverse import
patch("main.py", "Add AssetUniverse import",
    "from db import init_db, save_signal",
    "from db import init_db, save_signal\nfrom core.asset_universe import init_asset_universe, get_universe")

# PATCH 2: main.py - Replace hl_assets YAML gate with live universe
patch("main.py", "Replace hl_assets YAML gate with live universe",
    '    hl_assets = cfg.get("hyperliquid", {}).get("assets", [])\n    hl_map = {asset: asset for asset in hl_assets}\n    if asset_name not in hl_map:\n        logger.warning(f"Asset {asset_name} not in Hyperliquid config")\n        return None',
    '    # Live asset gate from HIP-4 universe\n    try:\n        _universe = get_universe()\n        if not _universe.exists(asset_name):\n            logger.warning(f"Asset {asset_name} not in live HL universe")\n            return None\n        hl_map = {asset_name: asset_name}\n    except Exception as _ue:\n        logger.warning(f"Universe check failed ({_ue}), falling back to YAML")\n        hl_assets = cfg.get("hyperliquid", {}).get("assets", [])\n        hl_map = {asset: asset for asset in hl_assets}\n        if asset_name not in hl_map:\n            logger.warning(f"Asset {asset_name} not in Hyperliquid config")\n            return None')

# PATCH 3: main.py - Initialize AssetUniverse at startup
patch("main.py", "Initialize AssetUniverse at startup",
    "    init_ai_clients()",
    "    init_ai_clients()\n    init_asset_universe()  # Load live asset universe from HIP-4")

# PATCH 4: data_fetcher.py - Add AssetUniverse import
patch("core/data_fetcher.py", "Add AssetUniverse import to data_fetcher",
    "logger = logging.getLogger(__name__)",
    "logger = logging.getLogger(__name__)\n\ntry:\n    from core.asset_universe import get_universe as _get_universe\n    _UNIVERSE_AVAILABLE = True\nexcept ImportError:\n    _UNIVERSE_AVAILABLE = False")

# PATCH 5: data_fetcher.py - Replace _TICKER_TO_COIN in get_current_price
patch("core/data_fetcher.py", "Replace _TICKER_TO_COIN in get_current_price",
    '    coin = _TICKER_TO_COIN.get(ticker_symbol, ticker_symbol.replace("-USD", ""))\n    return get_cached_price(coin)',
    '    if _UNIVERSE_AVAILABLE:\n        coin = _get_universe().to_coin(ticker_symbol)\n    else:\n        coin = _TICKER_TO_COIN.get(ticker_symbol, ticker_symbol.replace("-USD", ""))\n    return get_cached_price(coin)')

# PATCH 6: strategy_config.yaml - Deprecate hardcoded assets
patch("config/strategy_config.yaml", "Deprecate hardcoded assets section",
    "assets:\n  crypto:",
    "# DEPRECATED: assets below are fallback only. Live HIP-4 universe is source of truth.\nassets:\n  crypto:")


# Report
print("\n" + "=" * 68)
print("  AssetUniverse Wiring Report")
print("=" * 68)
for status, fp, desc in RESULTS:
    icon = {"APPLIED": "OK", "ALREADY": "OK", "DRY-RUN": "TEST", "SKIP": "SKIP", "MISSING": "FAIL", "ERROR": "FAIL"}.get(status, "?")
    print(f"  [{icon:4s}] {fp}")
    print(f"         {desc}")
print("=" * 68)
failures = [r for r in RESULTS if r[0] in ("MISSING", "ERROR")]
applied = [r for r in RESULTS if r[0] == "APPLIED"]
print(f"  Applied: {len(applied)} | Failures: {len(failures)}")
if DRY_RUN:
    print("  [DRY RUN - no files modified]")
print()
sys.exit(0 if not failures else 1)
