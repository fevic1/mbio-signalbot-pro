import asyncio
import logging
from core.app_context import app_context
from datetime import datetime, timezone
from typing import Dict, List
import core.state as state

logger = logging.getLogger(__name__)

# Hunter Protocol Settings
STAGNATION_THRESHOLD = 3600  # 1 hour in seconds
MIN_VOTES_TO_PASS = 4        # Needs 4 out of 6 strategy votes to be hunted
MIN_CONFIDENCE = 70          # Minimum confidence for a strategy vote
MAX_POSITIONS = 5            # Global safety limit for concurrent positions

def update_hold_tracking(asset_name: str, signal: str):
    """Tracks how long an open position has been receiving a HOLD signal."""
    if asset_name not in state.OPEN_POSITIONS:
        return
        
    pos = state.OPEN_POSITIONS[asset_name]
    
    # Do not track HOLD state for GRID or DCA positions
    if asset_name.startswith("GRID::") or pos.get("dca") or pos.get("strategy") in ["AUTO_DCA", "MANUAL_DCA"]:
        return

    if "HOLD" in signal.upper():
        if "hold_since" not in pos:
            pos["hold_since"] = datetime.now(timezone.utc)
            logger.info(f"🐌 {asset_name} entered HOLD state. Stagnation timer started.")
    else:
        if "hold_since" in pos:
            del pos["hold_since"]
            logger.info(f"🏃 {asset_name} broke out of HOLD state. Stagnation timer reset.")

def check_stagnant_positions() -> List[str]:
    """Returns a list of asset names that have been in HOLD for > 1 hour (Excludes GRID & DCA)."""
    stagnant_assets = []
    now = datetime.now(timezone.utc)
    
    for asset, pos in state.OPEN_POSITIONS.items():
        # 1. Skip GRID positions (managed by grid_monitor)
        if asset.startswith("GRID::"):
            continue
            
        # 2. Skip DCA positions (managed by dca_lifecycle)
        if pos.get("dca") or pos.get("strategy") in ["AUTO_DCA", "MANUAL_DCA"]:
            continue
            
        if "hold_since" in pos:
            hold_duration = (now - pos["hold_since"]).total_seconds()
            if hold_duration >= STAGNATION_THRESHOLD:
                stagnant_assets.append(asset)
                logger.warning(f"⚠️ {asset} has been stagnant (HOLD) for {hold_duration/60:.1f} minutes!")
                
    return stagnant_assets

async def run_hunter_protocol_idle(pending_signals: List[Dict], chat_id: int):
    """Main Hunter Protocol: Swap stagnant positions OR fill empty slots with high-conviction assets."""
    logger.info("🏹 Hunter Protocol: Scanning for swap or fill opportunities...")
    
    stagnant_assets = check_stagnant_positions()
    
    # Evaluate pending signals for hunted candidates
    hunted_candidates = []
    for signal_data in pending_signals:
        asset_name = signal_data.get("asset")
        signal = signal_data.get("signal", "")
        conf = signal_data.get("confidence", 0)
        
        # Skip if it's a stagnant asset, already open (including DCA/GRID), or HOLD signal
        if asset_name in stagnant_assets or asset_name in state.OPEN_POSITIONS or "HOLD" in signal.upper():
            continue
        
        # Check if it has high confidence (this is our "6 votes" proxy)
        if conf >= MIN_CONFIDENCE:
            hunted_candidates.append({
                "asset": asset_name,
                "signal": signal,
                "confidence": conf,
                "data": signal_data.get("data", {})
            })
            logger.info(f"🎯 Hunter Candidate: {asset_name} {signal} (conf={conf}%)")
    
    if not hunted_candidates and not stagnant_assets:
        logger.info("🏹 Hunter Protocol: No hunted candidates or stagnant positions found.")
        return
    
    # Sort candidates by confidence descending
    hunted_candidates.sort(key=lambda x: x["confidence"], reverse=True)
    
    # Step 1: Execute swaps for stagnant positions
    for stagnant_asset in stagnant_assets:
        if not hunted_candidates:
            break
        best_candidate = hunted_candidates.pop(0)
        await _execute_swap(stagnant_asset, best_candidate)

    # Step 2: Fill empty slots if available
    active_positions_count = len([k for k in state.OPEN_POSITIONS.keys() if not k.startswith("GRID::")])
    empty_slots = MAX_POSITIONS - active_positions_count
    
    if empty_slots > 0 and hunted_candidates:
        logger.info(f"🏹 Hunter Protocol: {empty_slots} empty slot(s) available. Filling with top candidates...")
        for _ in range(min(empty_slots, len(hunted_candidates))):
            best_candidate = hunted_candidates.pop(0)
            await _execute_fill(best_candidate)

async def _execute_swap(stagnant_asset: str, candidate: Dict):
    """Executes the swap: closes stagnant, opens candidate."""
    stagnant_pos = state.OPEN_POSITIONS.get(stagnant_asset)
    if not stagnant_pos:
        logger.warning(f"🏹 Hunter Protocol: Stagnant asset {stagnant_asset} not found in state.")
        return

    logger.info(f"🔄 Hunter Protocol: Swapping {stagnant_asset} → {candidate['asset']}")
    
    try:
        from execution.hl_executor import execute_hl_order
        from core.data_fetcher import get_mtf_data
        
        # 1. Close the stagnant position (reduce_only)
        close_side = "SELL" if stagnant_pos.get("side") == "BUY" else "BUY"
        close_size = stagnant_pos.get("size", 0)
        
        logger.info(f"🏹 Closing stagnant position: {stagnant_asset} {close_side} {close_size}")
        close_result = execute_hl_order(
            coin=stagnant_asset,
            side=close_side,
            size=close_size,
            reduce_only=True,
            strategy="HUNTER_SWAP",
            regime="SIDEWAYS"
        )
        
        if not close_result.get("success"):
            logger.error(f"❌ Hunter Protocol: Failed to close {stagnant_asset}: {close_result.get('error')}")
            return
            
        # Remove from state
        if stagnant_asset in state.OPEN_POSITIONS:
            del state.OPEN_POSITIONS[stagnant_asset]
            state.save_state()
        logger.info(f"✅ Hunter Protocol: Successfully closed {stagnant_asset}")
        
        # 2. Open the new hunted position
        data = get_mtf_data(f"{candidate['asset']}-USD")
        if not data or "1h" not in data:
            logger.error(f"❌ Hunter Protocol: Failed to fetch market data for {candidate['asset']}")
            return
            
        current_price = float(data["1h"]["price"])
        target_notional = 12.0  # Safely above $10 min notional rule
        new_size = round(target_notional / current_price, 4)
        
        if new_size * current_price < 10.0:
            new_size = round(11.0 / current_price, 4)
            
        open_side = "BUY" if candidate['signal'] == "BUY" else "SELL"
        
        logger.info(f"🏹 Opening hunted position: {candidate['asset']} {open_side} {new_size} @ ~${current_price}")
        open_result = execute_hl_order(
            coin=candidate['asset'],
            side=open_side,
            size=new_size,
            reduce_only=False,
            strategy="HUNTER_SWAP",
            regime="SIDEWAYS"
        )
        
        if open_result.get("success"):
            logger.info(f"✅ Hunter Protocol: Successfully opened {candidate['asset']} {open_side}")
        else:
            logger.error(f"❌ Hunter Protocol: Failed to open {candidate['asset']}: {open_result.get('error')}")
            
    except Exception as e:
        logger.error(f"❌ Hunter Protocol: Swap execution failed: {e}")

async def _execute_fill(candidate: Dict):
    """Executes a fill for an empty slot."""
    logger.info(f"🏹 Hunter Protocol: Filling empty slot with {candidate['asset']} {candidate['signal']}")
    
    try:
        from execution.hl_executor import execute_hl_order
        from core.data_fetcher import get_mtf_data
        
        data = get_mtf_data(f"{candidate['asset']}-USD")
        if not data or "1h" not in data:
            logger.error(f"❌ Hunter Protocol: Failed to fetch market data for {candidate['asset']}")
            return
            
        current_price = float(data["1h"]["price"])
        target_notional = 12.0
        new_size = round(target_notional / current_price, 4)
        
        if new_size * current_price < 10.0:
            new_size = round(11.0 / current_price, 4)
            
        open_side = "BUY" if candidate['signal'] == "BUY" else "SELL"
        
        logger.info(f"🏹 Opening new position: {candidate['asset']} {open_side} {new_size} @ ~${current_price}")
        open_result = execute_hl_order(
            coin=candidate['asset'],
            side=open_side,
            size=new_size,
            reduce_only=False,
            strategy="HUNTER_FILL",
            regime="SIDEWAYS"
        )
        
        if open_result.get("success"):
            logger.info(f"✅ Hunter Protocol: Successfully filled slot with {candidate['asset']} {open_side}")
        else:
            logger.error(f"❌ Hunter Protocol: Failed to open {candidate['asset']}: {open_result.get('error')}")
            
    except Exception as e:
        logger.error(f"❌ Hunter Protocol: Fill execution failed: {e}")

async def hunter_monitor_loop():
    """Continuous background monitor that runs every 5 minutes."""
    logger.info("🏹 Hunter Monitor: Starting continuous background monitoring...")
    
    while True:
        try:
            await asyncio.sleep(300)  # 5 minutes
            
            logger.info("🏹 Hunter Monitor: Running periodic check...")
            
            try:
                from core.signal_generator import analyze_batch
                from config.config import get_config
                
                cfg = get_config()
                assets = cfg.get("hyperliquid", {}).get("assets", [])
                
                # Analyze all assets EXCEPT the ones we already have open
                open_assets = set(state.OPEN_POSITIONS.keys())
                items = {asset: {} for asset in assets if asset not in open_assets}
                
                if not items:
                    logger.info("🏹 Hunter Monitor: No new assets to analyze.")
                    continue
                
                results, provider = await analyze_batch(items, cfg)
                
                # Build pending signals for hunting
                pending_signals = []
                for asset_name, data in items.items():
                    result = results.get(asset_name) or {}
                    signal = result.get("signal", "HOLD")
                    conf = result.get("confidence", 50)
                    
                    if conf >= MIN_CONFIDENCE and "HOLD" not in signal.upper():
                        pending_signals.append({
                            "asset": asset_name,
                            "signal": signal,
                            "confidence": conf,
                            "data": data
                        })
                
                # Execute hunt (swap or fill)
                stagnant_assets = check_stagnant_positions()
                if pending_signals or stagnant_assets:
                    await run_hunter_protocol_idle(pending_signals, None)
                else:
                    logger.info("🏹 Hunter Monitor: No hunted candidates or stagnant positions. All healthy.")
                    
            except Exception as e:
                logger.error(f"🏹 Hunter Monitor: Failed to analyze for swap/fill: {e}")
                
        except Exception as e:
            logger.error(f"🏹 Hunter Monitor: Loop error: {e}")
            await asyncio.sleep(60)
