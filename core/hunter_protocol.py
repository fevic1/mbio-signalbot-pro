import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List
import core.state as state
logger = logging.getLogger(__name__)

# Hunter Protocol Settings
STAGNATION_THRESHOLD = 3600  # 1 hour in seconds
MIN_VOTES_TO_PASS = 4        # Needs 4 out of 6 strategy votes to be hunted
MIN_CONFIDENCE = 70          # Minimum confidence for a strategy vote

def update_hold_tracking(asset_name: str, signal: str):
    """Tracks how long an open position has been receiving a HOLD signal."""
    if asset_name not in state.OPEN_POSITIONS:
        return
        
    pos = state.OPEN_POSITIONS[asset_name]
    
    if "HOLD" in signal.upper():
        if "hold_since" not in pos:
            pos["hold_since"] = datetime.now(timezone.utc)
            logger.info(f"🐌 {asset_name} entered HOLD state. Stagnation timer started.")
    else:
        if "hold_since" in pos:
            del pos["hold_since"]
            logger.info(f"🏃 {asset_name} broke out of HOLD state. Stagnation timer reset.")

def check_stagnant_positions() -> List[str]:
    """Returns a list of asset names that have been in HOLD for > 1 hour."""
    stagnant_assets = []
    now = datetime.now(timezone.utc)
    
    for asset, pos in state.OPEN_POSITIONS.items():
        if "hold_since" in pos:
            hold_duration = (now - pos["hold_since"]).total_seconds()
            if hold_duration >= STAGNATION_THRESHOLD:
                stagnant_assets.append(asset)
                logger.warning(f"⚠️ {asset} has been stagnant (HOLD) for {hold_duration/60:.1f} minutes!")
                
    return stagnant_assets

async def run_hunter_protocol_idle(pending_signals: List[Dict], chat_id: int):
    """Main Hunter Protocol: Swap stagnant positions for high-conviction assets."""
    logger.info("🏹 Hunter Protocol: Scanning for swap opportunities...")
    
    # Step 1: Find stagnant positions
    stagnant_assets = check_stagnant_positions()
    if not stagnant_assets:
        logger.info("🏹 Hunter Protocol: No stagnant positions found.")
        return
    
    logger.info(f"🏹 Hunter Protocol: Found {len(stagnant_assets)} stagnant position(s): {stagnant_assets}")
    
    # Step 2: Evaluate pending signals for hunted candidates
    hunted_candidates = []
    for signal_data in pending_signals:
        asset_name = signal_data.get("asset")
        signal = signal_data.get("signal", "")
        conf = signal_data.get("confidence", 0)
        
        # Skip if it's a stagnant asset or HOLD signal
        if asset_name in stagnant_assets or "HOLD" in signal.upper():
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
    
    if not hunted_candidates:
        logger.info("🏹 Hunter Protocol: No hunted candidates found.")
        return
    
    # Step 3: Pick the best hunted candidate
    best_candidate = max(hunted_candidates, key=lambda x: x["confidence"])
    logger.info(f"🏹 Hunter Protocol: Best target is {best_candidate['asset']} {best_candidate['signal']} (conf={best_candidate['confidence']}%)")
    
    # Step 4: Execute the swap (close stagnant, open hunted)
    stagnant_asset = stagnant_assets[0]  # Close the first stagnant position
    logger.info(f"🔄 Hunter Protocol: Swapping {stagnant_asset} → {best_candidate['asset']}")
    
    # TODO: Implement actual swap execution
    logger.info(f"🏹 Hunter Protocol: Would close {stagnant_asset} and open {best_candidate['asset']}")
async def hunter_monitor_loop():
    return  # DISABLED: Background task amputated
    """Continuous background monitor that runs every 5 minutes during sleep time."""
    logger.info("🏹 Hunter Monitor: Starting continuous background monitoring...")
    
    while True:
        try:
            await asyncio.sleep(300)  # 5 minutes
            
            logger.info("🏹 Hunter Monitor: Running periodic check...")
            
            # Step 1: Sync exchange positions with bot state
            from execution.hl_executor import HLExecutor
            
            executor = HLExecutor()
            exchange_positions = executor.get_open_positions()
            
            # Convert list to dictionary format expected by state.OPEN_POSITIONS
            synced_positions = {}
            for pos in exchange_positions:
                coin = pos.get("coin")
                if coin:
                    entry = float(pos.get("entry_price", 0))
                    size = float(pos.get("size", 0))
                    side = "BUY" if pos.get("side") == "long" else "SELL"
                    
                    # Calculate ATR-based SL/TP levels (2% of entry as ATR proxy)
                    atr = entry * 0.02
                    
                    if side == "BUY":
                        sl = entry - (1.5 * atr)
                        tp1 = entry + (1.0 * atr)
                        tp2 = entry + (2.0 * atr)
                        tp3 = entry + (3.0 * atr)
                    else:  # SELL
                        sl = entry + (1.5 * atr)
                        tp1 = entry - (1.0 * atr)
                        tp2 = entry - (2.0 * atr)
                        tp3 = entry - (3.0 * atr)
                    
                    synced_positions[coin] = {
                        "side": side,
                        "entry": entry,
                        "size": size,
                        "sl": sl,
                        "tp1": tp1,
                        "tp2": tp2,
                        "tp3": tp3,
                        "order_id": pos.get("order_id", "synced"),
                        "opened_at": datetime.now(timezone.utc),
                        "strategy": "Synced from exchange",
                        "tp1_hit": False,
                        "tp2_hit": False,
                        "tp3_hit": False
                    }
            
            # Update bot state with exchange reality
            state.OPEN_POSITIONS = synced_positions
            state.save_state()
            
            logger.info(f"🏹 Hunter Monitor: Synced {len(synced_positions)} positions from exchange with SL/TP levels")
            # Step 2: Check for stagnant positions (>1 hour of HOLD)
            stagnant_assets = check_stagnant_positions()
            
            if not stagnant_assets:
                logger.info("🏹 Hunter Monitor: No stagnant positions detected. All positions healthy.")
                continue
            
            # Step 3: Stagnant positions found - find hunted candidates to swap
            logger.warning(f"🏹 Hunter Monitor: Found {len(stagnant_assets)} stagnant position(s): {stagnant_assets}")
            
            try:
                from core.signal_generator import analyze_batch
                from config.config import get_config
                
                cfg = get_config()
                assets = cfg.get("trading", {}).get("assets", [])
                
                # Analyze all assets EXCEPT the stagnant ones
                items = {asset: {} for asset in assets if asset not in stagnant_assets}
                
                if not items:
                    logger.info("🏹 Hunter Monitor: No other assets to analyze for swap")
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
                
                # Step 4: Execute hunt if we have candidates
                if pending_signals:
                    logger.info(f"🏹 Hunter Monitor: Found {len(pending_signals)} hunted candidates for swap")
                    await run_hunter_protocol_idle(pending_signals, None)
                else:
                    logger.info("🏹 Hunter Monitor: No hunted candidates found. Stagnant positions remain.")
                    
            except Exception as e:
                logger.error(f"🏹 Hunter Monitor: Failed to analyze for swap: {e}")
                
        except Exception as e:
            logger.error(f"🏹 Hunter Monitor: Loop error: {e}")
            await asyncio.sleep(60)
