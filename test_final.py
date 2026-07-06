import yaml, sys, logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
sys.path.insert(0, '/app')

try:
    with open('config/strategy_config.yaml') as f:
        cfg = yaml.safe_load(f)
    
    from core.hip4_metadata import HIP4MetadataManager
    from hyperliquid.info import Info
    from hyperliquid.utils import constants
    
    info = Info(constants.MAINNET_API_URL, skip_ws=True)
    manager = HIP4MetadataManager.get_instance()
    manager.initialize(info)
    
    rules = cfg.get("universe", {})
    resolved = manager.resolve_universe(rules)
    
    print(f'\n✅ SUCCESS: RESOLVED {len(resolved)} ASSETS')
    if resolved:
        print(f'   Top 10 by volume: {resolved[:10]}')
except Exception as e:
    print(f'❌ TEST FAILED: {e}')
    import traceback
    traceback.print_exc()
