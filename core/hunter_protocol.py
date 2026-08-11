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
            
        # 2. Skip DCA positions (managed by DCAExecutionEngine)
        if pos.get("dca") or pos.get("strategy") in ["AUTO_DCA", "MANUAL_DCA"]:
            continue
            
        if "hold_since" in pos:
            hold_duration = (now - pos["hold_since"]).total_seconds()
            if hold_duration >= STAGNATION_THRESHOLD:
                stagnant_assets.append(asset)
                logger.warning(f"⚠️ {asset} has been stagnant (HOLD) for {hold_duration/60:.1f} minutes!")
                
    return stagnant_assets

def _active_hunter_positions() -> int:
    """Count positions that consume Hunter's finite trading slots."""
    return len([
        key for key, pos in state.OPEN_POSITIONS.items()
        if not key.startswith("GRID::")
    ])


def _hunter_empty_slots() -> int:
    """Return currently available Hunter slots without querying the exchange."""
    return max(0, MAX_POSITIONS - _active_hunter_positions())

async def run_hunter_protocol_idle(pending_signals: List[Dict], chat_id: int, system=None):
    """Main Hunter Protocol: swap stagnant positions or fill genuinely empty slots."""
    logger.info("🏹 Hunter Protocol: Scanning for swap or fill opportunities...")
    
    stagnant_assets = check_stagnant_positions()
    
    # A full book with no stagnant position has nothing Hunter can execute.
    # Stop here before market-data/analysis or execution APIs are touched.
    empty_slots = _hunter_empty_slots()
    if empty_slots == 0 and not stagnant_assets:
        logger.info(
            f"🏹 Hunter Protocol: All {MAX_POSITIONS} trading slots are occupied; "
            "no stagnant positions. Skipping hunt and execution."
        )
        return

    # Pending signals have already passed the existing StrategyManager committee.
    # Hunter only performs final slot/duplicate safety filtering here.
    hunted_candidates = []
    for signal_data in pending_signals or []:
        asset_name = signal_data.get("asset")
        signal = signal_data.get("signal", "")
        conf = signal_data.get("confidence", 0)
        
        if not asset_name:
            continue
        
        # Skip already-open assets and HOLD results. DCA/GRID entries are also
        # represented in OPEN_POSITIONS and therefore consume the duplicate gate.
        if asset_name in state.OPEN_POSITIONS or "HOLD" in signal.upper():
            continue
        
        if conf >= MIN_CONFIDENCE and signal_data.get("committee_passed", False):
            hunted_candidates.append({
                "asset": asset_name,
                "signal": signal,
                "confidence": conf,
                "strategy": signal_data.get("strategy", "ENSEMBLE"),
                "regime": signal_data.get("regime", "RANGING"),
                "data": signal_data.get("data", {})
            })
            logger.info(
                f"🎯 Hunter Candidate: {asset_name} {signal} "
                f"committee={signal_data.get('strategy', 'ENSEMBLE')} conf={conf}%"
            )
    
    if not hunted_candidates and not stagnant_assets:
        logger.info("🏹 Hunter Protocol: No committee-approved candidates or stagnant positions found.")
        return
    
    # Highest committee confidence is considered first; the committee itself
    # remains the sole strategy decision authority.
    hunted_candidates.sort(key=lambda x: x["confidence"], reverse=True)
    
    # Step 1: Execute swaps for stagnant positions.
    for stagnant_asset in stagnant_assets:
        if not hunted_candidates:
            break
        best_candidate = hunted_candidates.pop(0)
        await _execute_swap(stagnant_asset, best_candidate)

    # Step 2: Fill only slots that are still available after any swaps.
    empty_slots = _hunter_empty_slots()
    if empty_slots <= 0:
        logger.info(
            f"🏹 Hunter Protocol: No empty slots remain after stagnant-position handling. "
            "No fill execution API call."
        )
        return

    if hunted_candidates:
        logger.info(
            f"🏹 Hunter Protocol: {empty_slots} empty slot(s) available. "
            f"Filling from {len(hunted_candidates)} committee-approved candidate(s)..."
        )
        for _ in range(min(empty_slots, len(hunted_candidates))):
            # Re-check immediately before every execution to prevent a stale
            # slot calculation from producing an over-cap fill.
            if _hunter_empty_slots() <= 0:
                logger.info("🏹 Hunter Protocol: Slots became full; stopping fill execution.")
                break
            best_candidate = hunted_candidates.pop(0)
            await _execute_fill(best_candidate)

async def _execute_swap(stagnant_asset: str, candidate: Dict):
    """Executes the swap: closes stagnant, opens committee-approved candidate."""
    stagnant_pos = state.OPEN_POSITIONS.get(stagnant_asset)
    if not stagnant_pos:
        logger.warning(f"🏹 Hunter Protocol: Stagnant asset {stagnant_asset} not found in state.")
        return

    logger.info(f"🔄 Hunter Protocol: Swapping {stagnant_asset} → {candidate['asset']}")
    
    try:
        from execution.hl_executor import execute_hl_order
        
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
            regime=candidate.get("regime", "SIDEWAYS"),
            execution_label="QT_EXIT"
        )
        
        if not close_result.get("success"):
            logger.error(f"❌ Hunter Protocol: Failed to close {stagnant_asset}: {close_result.get('error')}")
            return
            
        # Remove from state
        if stagnant_asset in state.OPEN_POSITIONS:
            del state.OPEN_POSITIONS[stagnant_asset]
            state.save_state()
        logger.info(f"✅ Hunter Protocol: Successfully closed {stagnant_asset}")
        
        # 2. Open the new committee-approved hunted position using the data
        # already collected for committee evaluation. Do not refetch it.
        data = candidate.get("data") or {}
        if not data or "1h" not in data:
            logger.error(f"❌ Hunter Protocol: Committee candidate has no usable 1h data for {candidate['asset']}")
            return
            
        current_price = float(data["1h"]["price"])
        target_notional = 12.0  # Safely above $10 min notional rule
        new_size = round(target_notional / current_price, 4)
        
        if new_size * current_price < get_exchange_limits()["min_notional_usd"]:
            new_size = round(11.0 / current_price, 4)
            
        open_side = "BUY" if candidate['signal'] == "BUY" else "SELL"
        
        logger.info(
            f"🏹 Opening hunted position: {candidate['asset']} {open_side} {new_size} "
            f"@ ~${current_price} | committee={candidate.get('strategy', 'ENSEMBLE')}"
        )
        open_result = execute_hl_order(
            coin=candidate['asset'],
            side=open_side,
            size=new_size,
            reduce_only=False,
            strategy="HUNTER_SWAP",
            regime=candidate.get("regime", "SIDEWAYS"),
            execution_label="QT_ENTRY"
        )
        
        if open_result.get("success"):
            logger.info(f"✅ Hunter Protocol: Successfully opened {candidate['asset']} {open_side}")
        else:
            logger.error(f"❌ Hunter Protocol: Failed to open {candidate['asset']}: {open_result.get('error')}")
            
    except Exception as e:
        logger.error(f"❌ Hunter Protocol: Swap execution failed: {e}")

async def _execute_fill(candidate: Dict):
    """Executes a fill only when a slot is still available."""
    # Final local gate immediately before any execution API call.
    if _hunter_empty_slots() <= 0:
        logger.info(
            f"🏹 Hunter Protocol: Slots are full; refusing fill for {candidate.get('asset')}. "
            "No execution API call."
        )
        return

    logger.info(f"🏹 Hunter Protocol: Filling empty slot with {candidate['asset']} {candidate['signal']}")
    
    try:
        from execution.hl_executor import execute_hl_order
        
        # Reuse committee-evaluation market data instead of issuing another
        # market-data request just before execution.
        data = candidate.get("data") or {}
        if not data or "1h" not in data:
            logger.error(f"❌ Hunter Protocol: Committee candidate has no usable 1h data for {candidate['asset']}")
            return
            
        current_price = float(data["1h"]["price"])
        target_notional = 12.0
        new_size = round(target_notional / current_price, 4)
        
        if new_size * current_price < get_exchange_limits()["min_notional_usd"]:
            new_size = round(11.0 / current_price, 4)
            
        open_side = "BUY" if candidate['signal'] == "BUY" else "SELL"
        
        logger.info(
            f"🏹 Opening new position: {candidate['asset']} {open_side} {new_size} "
            f"@ ~${current_price} | committee={candidate.get('strategy', 'ENSEMBLE')}"
        )
        open_result = execute_hl_order(
            coin=candidate['asset'],
            side=open_side,
            size=new_size,
            reduce_only=False,
            strategy="HUNTER_FILL",
            regime=candidate.get("regime", "SIDEWAYS"),
            execution_label="QT_ENTRY"
        )
        
        if open_result.get("success"):
            logger.info(f"✅ Hunter Protocol: Successfully filled slot with {candidate['asset']} {open_side}")
        else:
            logger.error(f"❌ Hunter Protocol: Failed to open {candidate['asset']}: {open_result.get('error')}")
            
    except Exception as e:
        logger.error(f"❌ Hunter Protocol: Fill execution failed: {e}")

async def hunter_monitor_loop(system=None):
    """Continuous Hunter monitor with local slot gating and the existing six-strategy committee."""
    logger.info("🏹 Hunter Monitor: Starting continuous background monitoring (Staggered 30-min phases)...")
    # Hunter does not own strategy selection. StrategyManager remains the
    # canonical six-strategy committee and MetaLearner remains its learning layer.
    
    iteration = 0      # Tracks 5-minute intervals
    
    while True:
        try:
            # Wait 5 minutes between loop iterations
            await asyncio.sleep(300)
            iteration += 1
            
            # 1. ALWAYS check for stagnant positions every 5 minutes.
            stagnant_assets = check_stagnant_positions()
            if stagnant_assets:
                logger.info(
                    f"🏹 Hunter Monitor: Found {len(stagnant_assets)} stagnant asset(s). "
                    "Waiting for committee-approved replacement opportunities."
                )
            
            # 2. Every 30 minutes, hunt only when there is a reason to hunt.
            if iteration % 6 == 0:
                empty_slots = _hunter_empty_slots()
                if empty_slots == 0 and not stagnant_assets:
                    logger.info(
                        f"🏹 Hunter Monitor: All {MAX_POSITIONS} trading slots are full; "
                        "skipping Top-10 analysis and execution API calls."
                    )
                    continue

                logger.info(
                    f"🏹 Hunter Monitor: Running opportunity analysis "
                    f"({empty_slots} empty slot(s), {len(stagnant_assets)} stagnant)..."
                )
                
                try:
                    from core.signal_generator import analyze_batch
                    from core.asset_universe import get_universe
                    from core.data_fetcher import get_mtf_data
                    from config_loader import get_config
                    from core.strategy_manager import StrategyManager

                    # HARD GATE: Hunter uses the same live signal-scanning universe
                    # as the primary scanner, then filters candidates before the
                    # existing six-strategy committee is invoked.
                    selected_assets = get_universe().signal_scanner_coins()

                    # Never analyze assets that are already open.
                    open_assets = set(state.OPEN_POSITIONS.keys())
                    selected_assets = [
                        asset for asset in selected_assets
                        if asset not in open_assets
                    ]

                    # Keep the discovery stage bounded. These assets are NOT all
                    # sent to the committee; MBIO intelligence prefilters them.
                    chunk_assets = selected_assets[:10]
                    items = {
                        asset: get_mtf_data(asset)
                        for asset in chunk_assets
                    }
                    items = {asset: data for asset, data in items.items() if data}

                    if not items:
                        logger.info("🏹 Hunter Monitor: No candidate market data available after slot/open-position filtering.")
                        continue

                    logger.info(
                        f"🔎 Hunter Monitor: Prefiltering {len(items)} discovery candidate(s) "
                        "before strategy committee..."
                    )

                    # Discovery/prefilter only. This does NOT replace the strategy
                    # committee and does NOT select the execution strategy.
                    results, provider = await analyze_batch(items, get_config())
                    logger.info(f"🧠 Hunter discovery provider: {provider}")

                    committee = StrategyManager()
                    pending_signals = []

                    for asset_name, data in items.items():
                        result = results.get(asset_name) or {}
                        discovery_signal = result.get("signal", "HOLD")
                        discovery_conf = result.get("confidence", 0)

                        # Avoid sending every discovered asset through all six
                        # strategies. Only actionable discovery candidates reach
                        # the canonical committee.
                        if discovery_conf < MIN_CONFIDENCE or "HOLD" in discovery_signal.upper():
                            logger.debug(
                                f"🏹 Hunter prefilter rejected {asset_name}: "
                                f"signal={discovery_signal} conf={discovery_conf}%"
                            )
                            continue

                        # THIS IS THE EXISTING COMMITTEE. Hunter does not reproduce
                        # its voting, weighting, MetaLearner, or regime-gate logic.
                        committee_signal, committee_conf, committee_strategy = await committee.get_trade_signal(data)

                        logger.info(
                            f"🗳️ Hunter Committee: {asset_name} | "
                            f"signal={committee_signal} conf={committee_conf}% "
                            f"winner={committee_strategy}"
                        )

                        if committee_signal == "HOLD" or committee_conf < MIN_CONFIDENCE:
                            logger.info(
                                f"🏹 Hunter rejected by committee: {asset_name} | "
                                f"signal={committee_signal} conf={committee_conf}%"
                            )
                            continue

                        regime = getattr(committee, "current_regime", "RANGING")
                        pending_signals.append({
                            "asset": asset_name,
                            "signal": committee_signal,
                            "confidence": committee_conf,
                            "regime": regime,
                            "strategy": committee_strategy,
                            "committee_passed": True,
                            "data": data,
                        })

                    if pending_signals:
                        await run_hunter_protocol_idle(
                            pending_signals,
                            None,
                            system=system,
                        )
                    else:
                        logger.info("🏹 Hunter Monitor: No committee-approved opportunities in this phase.")
                            
                except Exception as e:
                    import traceback
                    logger.error(
                        f"🏹 Hunter Monitor: Failed to analyze opportunity universe: "
                        f"{e}\n{traceback.format_exc()}"
                    )
                
        except Exception as e:
            logger.error(f"🏹 Hunter Monitor: Loop error: {e}")
            await asyncio.sleep(60)