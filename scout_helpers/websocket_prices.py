import os
from hyperliquid.info import Info
from dotenv import load_dotenv

# Ensure environment variables are loaded
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=os.path.join(base_dir, '.env'))

def fetch_market_context_node(state: dict) -> dict:
    """
    LangGraph State Node: Fetches live data from Hyperliquid 
    to clear out stale/mocked state parameters.
    """
    print("\n--- INGESTING LIVE MARKET CONTEXT ---")
    
    # 1. Initialize Info client
    info = Info("https://api.hyperliquid.xyz", skip_ws=True)
    
    # 2. Extract targeted asset from upstream state context (Default to BTC)
    target_coin = state.get("target_coin", "BTC")
    print(f"Targeting Asset: {target_coin}")
    
    try:
        # 3. Retrieve raw market metadata and context layers
        meta, asset_ctxs = info.meta_and_asset_ctxs()
        
        # 4. Map string identity to the corresponding universe matrix index
        coin_idx = next((i for i, u in enumerate(meta['universe']) if u['name'] == target_coin), None)
        
        if coin_idx is not None:
            live_price = float(asset_ctxs[coin_idx]['midPx'])
            volume_24h = float(asset_ctxs[coin_idx].get('dayNtlVlm', 0.0))
            market_status = "stable_asset" if target_coin in ["PURR", "USDC"] else "volatile"
            print(f"Successfully retrieved live telemetry. Price: {live_price} | 24h Vol: ${volume_24h:,.2f}")
        else:
            print(f"⚠️ Warning: {target_coin} not found in exchange universe. Defaulting metrics.")
            live_price = 0.0
            volume_24h = 0.0
            market_status = "unknown_asset"
            
    except Exception as e:
        print(f"❌ Failed to fetch live exchange info: {str(e)}. Falling back safely.")
        live_price = 0.0
        volume_24h = 0.0
        market_status = "api_error"

    # 5. Return the updated dictionary to commit changes directly to graph state
    return {
        "market_data": {
            "coin": target_coin,
            "mid_price": str(live_price),
            "status": market_status,
            "volume_24h": str(volume_24h)
        }
    }
