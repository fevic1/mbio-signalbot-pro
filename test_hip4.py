import sys
sys.path.insert(0, '/app')

try:
    from core.hip4_metadata import HIP4MetadataManager
    from hyperliquid.info import Info
    from hyperliquid.utils import constants
    
    print("🔌 Connecting to Hyperliquid Mainnet for verification...")
    info = Info(constants.MAINNET_API_URL, skip_ws=True)
    
    print("📡 Initializing HIP-4 Metadata Manager...")
    manager = HIP4MetadataManager.get_instance()
    success = manager.initialize(info)
    
    if success:
        stats = manager.get_universe_stats()
        assets = manager.get_all_supported_assets()
        
        print(f"\n✅ HIP-4 CACHE STATUS: ACTIVE")
        print(f"   -> Total Assets Loaded: {stats['total_assets']}")
        print(f"   -> Cache Age: {stats['cache_age_seconds']}s")
        print(f"   -> Sample Assets: {assets[:5]}")
        print(f"   -> BTC szDecimals: {manager.get_sz_decimals('BTC')}")
        print(f"   -> SOL szDecimals: {manager.get_sz_decimals('SOL')}")
        print(f"   -> HYPE szDecimals: {manager.get_sz_decimals('HYPE')}")
    else:
        print("❌ Manager initialization returned False.")
        
except Exception as e:
    print(f"❌ VERIFICATION FAILED: {e}")
    import traceback
    traceback.print_exc()
