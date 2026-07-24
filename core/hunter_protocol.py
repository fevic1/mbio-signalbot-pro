import os
import asyncio
import logging
from core.app_context import app_context
from datetime import datetime, timezone
from typing import Dict, List
import core.state as state
from core.exchange_limits import get_exchange_limits

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

async def run_hunter_protocol_idle(pending_signals: List[Dict], chat_id: int, system=None):
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
        close_size = float(stagnant_pos.get("size", 0))
        
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
        
        if new_size * current_price < get_exchange_limits()["min_notional_usd"]:
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
        
        if new_size * current_price < get_exchange_limits()["min_notional_usd"]:
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

async def hunter_monitor_loop(system=None):
    """Continuous background monitor. Checks stagnant positions every 5 mins, analyzes assets in staggered 30-min phases."""
    logger.info("🏹 Hunter Monitor: Starting continuous background monitoring (Staggered 30-min phases)...")
    if system and system.event_bus:
        from aios.events import Event

        system.event_bus.publish(
            Event(
                "hunter.scan.started",
                source="hunter_protocol",
                payload={
                    "interval": 300,
                },
            )
        )

    
    current_phase = 1  # Tracks which phase to run (1, 2, or 3)
    iteration = 0      # Tracks 5-minute intervals
    
    while True:
        try:
            # Wait 5 minutes between loop iterations
            await asyncio.sleep(300)
            iteration += 1
            
            # 1. ALWAYS check for stagnant positions every 5 minutes
            stagnant_assets = check_stagnant_positions()
            if stagnant_assets:
                logger.info(f"🏹 Hunter Monitor: Found {len(stagnant_assets)} stagnant assets. Executing hunt...")
                await run_hunter_protocol_idle([], stagnant_assets)
            
            # 2. Every 30 minutes (6 iterations of 5 mins), analyze the next phase of assets
            if iteration % 6 == 0:
                logger.info(f"🏹 Hunter Monitor: Running Phase {current_phase} asset analysis...")
                
                try:
                    from core.signal_generator import analyze_batch
                    from config.config import get_config
                    
                    cfg = get_config()
                    ex_name = os.getenv("DEFAULT_EXCHANGE", "hyperliquid").lower()
                    assets = cfg.get(ex_name, {}).get("assets", [])
                    
                    # Analyze all assets EXCEPT the ones we already have open
                    open_assets = set(state.OPEN_POSITIONS.keys())
                    from core.data_fetcher import get_mtf_data

                    items = {}

                    for asset in assets:
                        if asset in open_assets:
                            continue

                        items[asset] = get_mtf_data(asset)
                    
                    if not items:
                        logger.info("🏹 Hunter Monitor: No new assets to analyze.")
                    else:
                        BATCH_SIZE = 15
                        items_list = list(items.items())
                        
                        # Calculate the slice for the current phase
                        start_idx = (current_phase - 1) * BATCH_SIZE
                        end_idx = start_idx + BATCH_SIZE
                        chunk = dict(items_list[start_idx:end_idx])
                        
                        if chunk:
                            logger.info(f"🧠 Analyzing asset Phase {current_phase} ({len(chunk)} assets)...")
                            results = {}
                            provider = "aios"

                            if system and system.orchestrator:

                                logger.info("🧠 AIOS Hunter bridge activated")

                                task = system.orchestrator.submit_task(
                                    name="market_analysis",
                                    category="trading",
                                    context={
                                        "market_data": chunk
                                    },
                                )

                                system.orchestrator.assign_agent(
                                    task["id"],
                                    "market_analysis",
                                )

                                logger.info(
                                    f"🧠 AIOS executing task {task['id']}"
                                )

                                execution = await system.orchestrator.execute_task(
                                    task["id"]
                                )

                                logger.info(
                                    f"🧠 AIOS execution complete: {execution.status}"
                                )

                                market_result = execution.results.get(
                                    "market_analysis",
                                    {}
                                )

                                content = market_result.get(
                                    "content",
                                    {}
                                )

                                if isinstance(content, dict):

                                    confidence = content.get(
                                        "confidence",
                                        0,
                                    )

                                    if confidence <= 1:
                                        confidence *= 100

                                    results = {
                                        asset: {
                                            "signal": (
                                                "BUY"
                                                if content.get("trend") == "bullish"
                                                else "SELL"
                                                if content.get("trend") == "bearish"
                                                else "HOLD"
                                            ),
                                            "confidence": int(confidence),
                                            "reasoning": {
                                                "trend": content.get("trend"),
                                                "momentum": content.get("momentum"),
                                                "volatility": content.get("volatility"),
                                                "risk": content.get("risk"),
                                            },
                                        }
                                        for asset in chunk
                                    }

                                else:
                                    results = {}


                            else:
                                raise RuntimeError(
                                    "AIOS orchestrator unavailable. "
                                    "Hunter requires AIOS intelligence path."
                                )
                            
                            # Build pending signals for hunting
                            pending_signals = []
                            for asset_name, data in chunk.items():
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
                            
                            # Execute hunt through AIOS risk gate
                            if pending_signals:

                                if not system or not system.orchestrator:
                                    raise RuntimeError(
                                        "AIOS unavailable. Execution blocked."
                                    )

                                risk_task = system.orchestrator.submit_task(
                                    name="risk_analysis",
                                    category="trading",
                                    context={
                                        "signals": pending_signals,
                                        "market_analysis": content,
                                    },
                                )

                                system.orchestrator.assign_agent(
                                    risk_task["id"],
                                    "risk_analysis",
                                )

                                risk_execution = await system.orchestrator.execute_task(
                                    risk_task["id"]
                                )

                                risk_result = risk_execution.results.get(
                                    "risk_analysis",
                                    {}
                                )

                                risk_content = risk_result.get(
                                    "content",
                                    {}
                                )

                                risk_level = (
                                    risk_content
                                    .get("risk", {})
                                    .get("analysis", "high")
                                )

                                if risk_level != "high":

                                    verify_task = system.orchestrator.submit_task(
                                        name="verification",
                                        category="trading",
                                        context={
                                            "signals": pending_signals,
                                            "market_analysis": content,
                                            "risk_analysis": risk_content,
                                        },
                                    )

                                    system.orchestrator.assign_agent(
                                        verify_task["id"],
                                        "verification",
                                    )

                                    verification_execution = await system.orchestrator.execute_task(
                                        verify_task["id"]
                                    )

                                    verification_result = verification_execution.results.get(
                                        "verification",
                                        {}
                                    )

                                    verification_content = verification_result.get(
                                        "content",
                                        {}
                                    )

                                    confidence = verification_content.get(
                                        "confidence",
                                        0,
                                    )

                                    if confidence <= 1:
                                        confidence *= 100

                                    if confidence >= 50:

                                        approval_task = system.orchestrator.submit_task(
                                            name="execution_approval",
                                            category="trading",
                                            context={
                                                "signals": pending_signals,
                                                "risk": risk_content,
                                                "verification": verification_content,
                                            },
                                        )

                                        system.orchestrator.assign_agent(
                                            approval_task["id"],
                                            "execution_approval",
                                        )

                                        approval_execution = await system.orchestrator.execute_task(
                                            approval_task["id"]
                                        )

                                        approval_result = approval_execution.results.get(
                                            "execution_approval",
                                            {}
                                        )

                                        approval_content = approval_result.get(
                                            "content",
                                            {}
                                        )

                                        approved = approval_content.get(
                                            "approved",
                                            False,
                                        )

                                        if approved:

                                            from aios.memory import (
                                                EventStore,
                                                create_decision_event,
                                            )

                                            event_store = EventStore()

                                            for signal in pending_signals:

                                                event = create_decision_event(
                                                    asset=signal.get("asset"),
                                                    signal=signal.get("signal"),
                                                    market_analysis=content,
                                                    risk_analysis=risk_content,
                                                    verification=verification_content,
                                                    approval=approval_content,
                                                    executed=True,
                                                )

                                                event_store.append(event)

                                            logger.info(
                                                "🧠 Hunter decision stored in AIOS memory"
                                            )

                                            await run_hunter_protocol_idle(
                                                pending_signals,
                                                None,
                                                system=system,
                                            )
                                        else:
                                            logger.warning(
                                                "Hunter blocked by AIOS execution approval gate"
                                            )

                                    else:
                                        logger.warning(
                                            "Hunter blocked by AIOS verification gate"
                                        )

                                else:

                                    logger.warning(
                                        "🏹 Hunter blocked by AIOS risk gate"
                                    )

                            else:
                                logger.info("🏹 Hunter Monitor: No hunted candidates in this phase. All healthy.")
                        else:
                            logger.info(f"🏹 Hunter Monitor: Phase {current_phase} has no assets to analyze.")
                            
                except Exception as e:
                    import traceback
                    logger.error(f"🏹 Hunter Monitor: Failed to analyze Phase {current_phase}: {e}\n{traceback.format_exc()}")
                
                # Advance to the next phase (1 -> 2 -> 3 -> 1)
                current_phase = (current_phase % 3) + 1
                
        except Exception as e:
            logger.error(f"🏹 Hunter Monitor: Loop error: {e}")
            await asyncio.sleep(60)
