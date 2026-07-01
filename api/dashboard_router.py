"""
Real-time Dashboard API Router.
Exposes bot state, positions, and performance metrics via REST API.
Read-only and secure.
"""
import logging
from fastapi import APIRouter, HTTPException
import core.state as state

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/status")
async def get_bot_status():
    """Get overall bot health and configuration status."""
    try:
        # Check if state module is loaded and has expected attributes
        has_positions = hasattr(state, 'OPEN_POSITIONS')
        pos_count = len(state.OPEN_POSITIONS) if has_positions else 0
        
        return {
            "status": "online",
            "version": "9.0",
            "open_positions": pos_count,
            "features": {
                "dynamic_sizing": True,
                "llm_reasoning": True,
                "pattern_analysis": True
            }
        }
    except Exception as e:
        logger.error(f"Dashboard status error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/positions")
async def get_open_positions():
    """Get all currently open positions with detailed metrics."""
    try:
        if not hasattr(state, 'OPEN_POSITIONS'):
            return {"positions": []}
            
        # Sanitize data: remove sensitive keys if any, format for frontend
        positions = []
        for symbol, pos in state.OPEN_POSITIONS.items():
            positions.append({
                "symbol": symbol,
                "side": pos.get("side"),
                "entry": pos.get("entry"),
                "size": pos.get("size"),
                "current_pnl_pct": pos.get("pnl_pct", 0), # If tracked in state
                "sl": pos.get("sl"),
                "tp1": pos.get("tp1"),
                "pattern": pos.get("last_pattern", "UNKNOWN"),
                "llm_reasoning": pos.get("llm_reasoning", "Pending analysis...")
            })
            
        return {"positions": positions}
    except Exception as e:
        logger.error(f"Dashboard positions error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch positions")

@router.get("/performance")
async def get_performance_metrics():
    """Get daily performance and LangSmith stats."""
    try:
        # Placeholder for daily PnL and LangSmith stats
        # In a full implementation, this would query the LangSmith monitor
        return {
            "daily_pnl": state.get_daily_pnl() if hasattr(state, 'get_daily_pnl') else 0.0,
            "total_trades_today": 0, # Placeholder
            "win_rate": 0.0 # Placeholder
        }
    except Exception as e:
        logger.error(f"Dashboard performance error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch performance")
