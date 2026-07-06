import sys, logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
sys.path.insert(0, '/app')

try:
    from core.hip4_metadata import HIP4MetadataManager
    from hyperliquid.info import Info
    from hyperliquid.utils import constants
    
    info = Info(constants.MAINNET_API_URL, skip_ws=True)
    manager = HIP4MetadataManager.get_instance()
    manager.initialize(info)
    
    print("\n📊 EXECUTING LIVE CATEGORIZATION...")
    categories = manager.categorize_assets()
    
    print(f"\n✅ SUCCESS: ASSETS CATEGORIZED")
    print(f"   -> PERP (Perpetual Futures): {len(categories['PERP'])} assets")
    print(f"      Sample: {categories['PERP'][:5]}")
    print(f"   -> SPOT (Spot Markets):      {len(categories['SPOT'])} assets")
    print(f"      Sample: {categories['SPOT'][:5]}")
    print(f"   -> TRADFI (Stocks/Indices):  {len(categories['TRADFI'])} assets")
    print(f"      Sample: {categories['TRADFI'][:5]}")
    
except Exception as e:
    print(f'❌ TEST FAILED: {e}')
    import traceback
    traceback.print_exc()
