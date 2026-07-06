import yaml, sys, logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
sys.path.insert(0, '/app')

try:
    with open('config/strategy_config.yaml') as f:
        cfg = yaml.safe_load(f)
    print(f'✅ YAML parsed inside container. Universe rules found: {cfg.get("universe") is not None}')
    
    from core.hip4_metadata import HIP4MetadataManager
    from hyperliquid.info import Info
    from hyperliquid.utils import constants
    
    print("🔌 Connecting to Hyperliquid Mainnet...")
    info = Info(constants.MAINNET_API_URL, skip_ws=True)
    manager = HIP4MetadataManager.get_instance()
    manager.initialize(info)
    
    rules = cfg.get("universe", {})
    print(f"📡 Resolving universe with rules: {rules}")
    resolved = manager.resolve_universe(rules)
    
    print(f'✅ SUCCESS: RESOLVED {len(resolved)} ASSETS')
    if resolved:
        print(f'   Top 5 by volume: {resolved[:5]}')
except Exception as e:
    print(f'❌ TEST FAILED: {e}')
    import traceback
    traceback.print_exc()
