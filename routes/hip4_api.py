from routes.dashboard_auth import get_current_user
"""
HIP-4 Market Spec API Routes
Phase 13: Multi-Asset Integration for MBIO SignalBot Pro

Endpoints:
  GET /api/hip4/specs?asset=BTC       — HIP-4 compliant market specification
  GET /api/hyperliquid/assets?type=PERP — Filtered asset list (PERP/SPOT/TRADFI)
  GET /api/hyperliquid/positions       — Unified positions across all asset types

All specs fetched LIVE from Hyperliquid API — no mock data.
Authentication: Cookie session (get_current_user dependency).
"""

import logging
from fastapi import APIRouter, Depends, Query
from typing import Optional

from execution.hyperliquid_client import HyperliquidClient

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_client() -> HyperliquidClient:
    """Get or create HyperliquidClient singleton."""
    return HyperliquidClient()


@router.get("/api/hip4/specs")
async def get_hip4_specs(asset: str = Query("BTC", description="Asset symbol")):
    """Fetch HIP-4 compliant market specification for an asset.
    
    Returns: tick_size, lot_size, min_notional, max_leverage, sz_decimals, status
    All values fetched LIVE from Hyperliquid metadata.
    """
    try:
        client = _get_client()
        spec = client.get_hip4_market_spec(asset)
        if not spec:
            return {"success": False, "error": f"HIP-4 spec not found for {asset}"}
        return {"success": True, "spec": spec}
    except Exception as e:
        logger.error(f"HIP-4 spec error for {asset}: {e}")
        return {"success": False, "error": str(e)}


@router.get("/api/hyperliquid/assets")
async def get_assets(
    type: Optional[str] = Query(None, description="Filter by type: PERP, SPOT, TRADFI")
):
    """Return list of all supported assets, optionally filtered by type.
    
    Supports: PERP (perpetuals), SPOT (crypto tokens), TRADFI (stocks)
    """
    try:
        client = _get_client()
        valid_types = ["PERP", "SPOT", "TRADFI"]
        
        filter_type = None
        if type:
            upper_type = type.upper()
            if upper_type not in valid_types:
                return {
                    "success": False,
                    "error": f"Invalid type '{type}'. Valid: {valid_types}",
                    "assets": []
                }
            filter_type = upper_type
        
        assets = client.get_all_assets(asset_type=filter_type)
        return {"success": True, "count": len(assets), "assets": assets}
    except Exception as e:
        logger.error(f"Asset list error: {e}")
        return {"success": False, "error": str(e), "assets": []}


@router.get("/api/hyperliquid/positions")
async def get_unified_positions():
    """Fetch unified positions across Perps + Spot/TradFi.
    
    Returns all open positions with asset type, side, size, entry, uPnL, leverage.
    """
    try:
        client = _get_client()
        positions = client.get_open_positions()
        return {"success": True, "count": len(positions), "positions": positions}
    except Exception as e:
        logger.error(f"Unified positions error: {e}")
        return {"success": False, "error": str(e), "positions": []}


@router.get("/api/hip4/validate")
async def validate_order(
    asset: str = Query(..., description="Asset symbol"),
    price: float = Query(..., description="Order price"),
    size: float = Query(..., description="Order size"),
):
    """Validate an order against HIP-4 market rules before submission.
    
    Checks: price tick alignment, size lot alignment, minimum notional.
    Returns rounded valid values or error message.
    """
    try:
        client = _get_client()
        result = client.validate_hip4_order(asset, price, size)
        return {"success": result["valid"], **result}
    except Exception as e:
        logger.error(f"HIP-4 validation error: {e}")
        return {"success": False, "error": str(e)}


@router.get("/api/hip4/price")
async def get_asset_price(asset: str = Query(..., description="Asset symbol")):
    """Get current mid price for any asset type (Perp/Spot/TradFi)."""
    try:
        client = _get_client()
        price = client.get_price(asset)
        if price <= 0:
            return {"success": False, "error": f"Could not fetch price for {asset}"}
        return {"success": True, "asset": asset.upper(), "price": price}
    except Exception as e:
        logger.error(f"Price fetch error for {asset}: {e}")
        return {"success": False, "error": str(e)}


@router.get("/assets/categorized")
async def get_categorized_assets(user: dict = Depends(get_current_user)):
    """Return assets grouped by PERP, SPOT, and TRADFI."""
    try:
        from core.hip4_metadata import HIP4MetadataManager
        manager = HIP4MetadataManager.get_instance()
        categories = manager.categorize_assets()
        
        return {
            "success": True,
            "categories": categories,
            "summary": {
                "PERP": len(categories.get("PERP", [])),
                "SPOT": len(categories.get("SPOT", [])),
                "TRADFI": len(categories.get("TRADFI", [])),
                "total": sum(len(v) for v in categories.values())
            }
        }
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to categorize assets: {e}")
        return {"success": False, "error": str(e), "categories": {"PERP": [], "SPOT": [], "TRADFI": []}}
