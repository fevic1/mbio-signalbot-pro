"""
MCP Tool Definitions and Registration
Binds existing bot capabilities to the Multi-MCP Registry.
"""
import logging
from typing import Dict, Any
from core.mcp_registry import mcp_registry
from core.app_context import app_context
from routes.dashboard_auth import verify_otp_for_user
from core.risk_manager import validate_portfolio_exposure, check_asset_correlation

logger = logging.getLogger(__name__)

# ============================================================
# VIBE-TRADING TOOLS
# ============================================================

async def get_account_balance() -> Dict[str, Any]:
    """Get current account balance and equity."""
    try:
        executor = app_context.executor
        balance = await executor.get_balance() if hasattr(executor, 'get_balance') else {"total": 0, "available": 0}
        return {"success": True, "data": balance}
    except Exception as e:
        logger.error(f"get_account_balance failed: {e}")
        return {"success": False, "error": str(e)}

async def get_market_regime(asset: str = "BTC") -> Dict[str, Any]:
    """Get current market regime analysis using GTJA-191 factors."""
    try:
        from core.strategy.regime_analyzer import RegimeAnalyzer
        import pandas as pd
        import requests
        import time
        
        url = "https://api.hyperliquid.xyz/info"
        end_time = int(time.time() * 1000)
        start_time = end_time - (100 * 3600 * 1000)
        
        resp = requests.post(url, json={
            "type": "candleSnapshot",
            "req": {"coin": asset, "interval": "1h", "startTime": start_time, "endTime": end_time}
        }, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        df = pd.DataFrame(data)
        df = df.rename(columns={'t': 'time', 'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 'v': 'volume'})
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        df = df.astype({'open': float, 'high': float, 'low': float, 'close': float, 'volume': float})
        
        analyzer = RegimeAnalyzer(lookback=20)
        regime_result = analyzer.analyze(df)
        
        return {"success": True, "data": regime_result} if regime_result else {"success": False, "error": "Analysis failed"}
    except Exception as e:
        logger.error(f"get_market_regime failed: {e}")
        return {"success": False, "error": str(e)}

async def place_grid(
    asset: str, lower_price: float, upper_price: float, 
    investment: float, nodes: int, otp: str
) -> Dict[str, Any]:
    """Deploy a new grid bot. REQUIRES OTP CONFIRMATION."""
    if not verify_otp_for_user("fixed@mbio.com", otp):
        return {"success": False, "error": "Invalid or expired OTP"}
    
    if lower_price >= upper_price or investment <= 0 or nodes < 2:
        return {"success": False, "error": "Invalid grid parameters"}
        
    try:
        from core.grid_manager import GridManager
        executor = app_context.executor
        grid_manager = GridManager(executor)
        
        result = grid_manager.create_grid(
            asset=asset, lower_price=lower_price, upper_price=upper_price,
            grid_quantity=nodes, investment_amount=investment,
            profit_per_grid_pct=0.5, exchange="hyperliquid"
        )
        logger.info(f"MCP: Grid deployed for {asset}")
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"place_grid failed: {e}")
        return {"success": False, "error": str(e)}

# ============================================================
# UNIFIED REGISTRATION FUNCTION
# ============================================================

async def init_mcp_tools():
    """Register ALL tools to their respective MCP servers in one unified pass."""
    # 1. Vibe-Trading Tools
    await mcp_registry.register_tool("vibe-trading", "get_account_balance", get_account_balance)
    await mcp_registry.register_tool("vibe-trading", "get_market_regime", get_market_regime)
    await mcp_registry.register_tool("vibe-trading", "place_grid", place_grid)
    
    # 2. Risk Analyzer Tools
    await mcp_registry.register_tool("risk-analyzer", "validate_portfolio_exposure", validate_portfolio_exposure)
    await mcp_registry.register_tool("risk-analyzer", "check_asset_correlation", check_asset_correlation)
    
    logger.info("✅ All MCP tools (Vibe-Trading + Risk Analyzer) registered successfully.")
