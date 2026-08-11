import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List

import core.state as state

logger = logging.getLogger(__name__)

# Hunter Protocol Settings
STAGNATION_THRESHOLD = 3600  # 1 hour in seconds
MIN_VOTES_TO_PASS = 4        # Committee policy: 4 of 6 strategy votes conceptually pass
MIN_CONFIDENCE = 70           # Discovery/committee minimum
MAX_POSITIONS = 5             # Hunter safety ceiling; core execution remains authoritative


def update_hold_tracking(asset_name: str, signal: str):
    """Track how long an eligible open position has remained on HOLD."""
    if asset_name not in state.OPEN_POSITIONS:
        return

    pos = state.OPEN_POSITIONS[asset_name]

    # GRID and DCA positions have their own lifecycle managers.
    if (
        asset_name.startswith("GRID::")
        or pos.get("dca")
        or pos.get("strategy") in ["AUTO_DCA", "MANUAL_DCA"]
    ):
        return

    if "HOLD" in signal.upper():
        if "hold_since" not in pos:
            pos["hold_since"] = datetime.now(timezone.utc)
            logger.info(f"🐌 {asset_name} entered HOLD state. Stagnation timer started.")
    elif "hold_since" in pos:
        del pos["hold_since"]
        logger.info(f"🏃 {asset_name} broke out of HOLD state. Stagnation timer reset.")


def check_stagnant_positions() -> List[str]:
    """Return non-GRID/non-DCA positions held in HOLD for at least one hour."""
    stagnant_assets = []
    now = datetime.now(timezone.utc)

    for asset, pos in state.OPEN_POSITIONS.items():
        if asset.startswith("GRID::"):
            continue
        if pos.get("dca") or pos.get("strategy") in ["AUTO_DCA", "MANUAL_DCA"]:
            continue

        hold_since = pos.get("hold_since")
        if not hold_since:
            continue

        # Persisted timestamps can be strings after restart.
        if isinstance(hold_since, str):
            try:
                hold_since = datetime.fromisoformat(hold_since.replace("Z", "+00:00"))
            except ValueError:
                continue

        if hold_since.tzinfo is None:
            hold_since = hold_since.replace(tzinfo=timezone.utc)

        hold_duration = (now - hold_since).total_seconds()
        if hold_duration >= STAGNATION_THRESHOLD:
            stagnant_assets.append(asset)
            logger.warning(
                f"⚠️ {asset} has been stagnant (HOLD) for {hold_duration / 60:.1f} minutes!"
            )

    return stagnant_assets


def _active_hunter_positions() -> int:
    """Count real non-GRID positions against Hunter's local slot ceiling."""
    return sum(
        1
        for key in state.OPEN_POSITIONS
        if not key.startswith("GRID::")
    )


def _hunter_empty_slots() -> int:
    """Return locally available Hunter slots without an exchange query."""
    return max(0, MAX_POSITIONS - _active_hunter_positions())


async def _submit_to_core_trade_path(candidate: Dict):
    """Submit an approved Hunter candidate to the existing core trade lifecycle.

    Hunter does not size orders, call the exchange, create stop-loss/take-profit
    plans, or bypass capital/risk checks. The existing main.run_trade path owns
    those responsibilities for all normal signal entries.
    """
    asset = candidate.get("asset")
    signal = candidate.get("signal", "HOLD")
    confidence = int(candidate.get("confidence", 0) or 0)
    data = candidate.get("data") or {}

    if not asset or signal == "HOLD" or confidence < MIN_CONFIDENCE:
        return

    # Final Hunter gate immediately before handing the candidate to core.
    if _hunter_empty_slots() <= 0:
        logger.info(
            f"🏹 Hunter: Slots are full; not submitting {asset} to core trade path."
        )
        return
    if asset in state.OPEN_POSITIONS:
        logger.info(
            f"🏹 Hunter: {asset} is already open; not submitting duplicate trade."
        )
        return

    if not data or "1h" not in data:
        logger.warning(
            f"🏹 Hunter: {asset} has no committee-evaluation 1h data; not submitting."
        )
        return

    try:
        # Runtime import avoids the main -> hunter -> main import cycle.
        from main import run_trade

        logger.info(
            f"🏹 Hunter: Passing committee-approved {asset} {signal} "
            f"conf={confidence}% to canonical core trade path "
            f"(strategy={candidate.get('strategy', 'ENSEMBLE')})."
        )

        await run_trade(
            asset_name=asset,
            data=data,
            signal=signal,
            conf=confidence,
            reasoning=(
                f"Hunter opportunity approved by existing strategy committee; "
                f"winner={candidate.get('strategy', 'ENSEMBLE')}"
            ),
            provider="HunterCommittee",
        )
    except Exception as exc:
        logger.error(
            f"❌ Hunter: Core trade-path submission failed for {asset}: {exc}"
        )


async def run_hunter_protocol_idle(
    pending_signals: List[Dict],
    chat_id: int,
    system=None,
):
    """Process committee-approved opportunities without owning execution.

    Hunter's responsibilities stop at discovery, stagnation detection, duplicate
    filtering, slot gating, and forwarding an approved opportunity to the core
    trade lifecycle. It never constructs an order or calls the exchange directly.
    """
    logger.info("🏹 Hunter Protocol: Processing committee-approved opportunities...")

    stagnant_assets = check_stagnant_positions()
    empty_slots = _hunter_empty_slots()

    if empty_slots == 0 and not stagnant_assets:
        logger.info(
            f"🏹 Hunter Protocol: All {MAX_POSITIONS} trading slots are occupied; "
            "skipping hunt and execution."
        )
        return

    hunted_candidates = []
    for signal_data in pending_signals or []:
        asset_name = signal_data.get("asset")
        signal = signal_data.get("signal", "")
        confidence = int(signal_data.get("confidence", 0) or 0)

        if not asset_name:
            continue
        if asset_name in state.OPEN_POSITIONS:
            logger.debug(f"🏹 Hunter: duplicate open asset rejected: {asset_name}")
            continue
        if "HOLD" in signal.upper():
            continue
        if confidence < MIN_CONFIDENCE:
            continue
        if not signal_data.get("committee_passed", False):
            continue

        hunted_candidates.append(
            {
                "asset": asset_name,
                "signal": signal,
                "confidence": confidence,
                "strategy": signal_data.get("strategy", "ENSEMBLE"),
                "regime": signal_data.get("regime", "RANGING"),
                "data": signal_data.get("data", {}),
            }
        )
        logger.info(
            f"🎯 Hunter Candidate: {asset_name} {signal} "
            f"committee={signal_data.get('strategy', 'ENSEMBLE')} "
            f"conf={confidence}%"
        )

    hunted_candidates.sort(key=lambda item: item["confidence"], reverse=True)

    # A stagnant position is a monitoring/replacement condition, not permission
    # for Hunter to close or reverse it. The existing position lifecycle remains
    # the owner of position exits. Hunter only forwards a new entry when a real
    # slot is available.
    if stagnant_assets:
        logger.info(
            f"🏹 Hunter: {len(stagnant_assets)} stagnant position(s) detected; "
            "no direct Hunter close/swap execution. Waiting for the core position "
            "lifecycle to release a slot."
        )

    if not hunted_candidates:
        logger.info(
            "🏹 Hunter Protocol: No committee-approved candidates available for the core trade path."
        )
        return

    empty_slots = _hunter_empty_slots()
    if empty_slots <= 0:
        logger.info(
            "🏹 Hunter Protocol: No empty slots remain; no core trade submission."
        )
        return

    logger.info(
        f"🏹 Hunter Protocol: {empty_slots} empty slot(s); forwarding up to "
        f"{min(empty_slots, len(hunted_candidates))} committee-approved candidate(s) "
        "to the core trade path."
    )

    for candidate in hunted_candidates[:empty_slots]:
        if _hunter_empty_slots() <= 0:
            logger.info(
                "🏹 Hunter Protocol: Slot state changed to full; stopping submissions."
            )
            break
        await _submit_to_core_trade_path(candidate)


async def hunter_monitor_loop(system=None):
    """Continuously discover opportunities and invoke the existing committee."""
    logger.info(
        "🏹 Hunter Monitor: Starting continuous background monitoring "
        "(Staggered 30-min phases)..."
    )
    logger.info(
        "🏹 Hunter Monitor: Execution authority remains in the canonical core trade path."
    )

    iteration = 0

    while True:
        try:
            await asyncio.sleep(300)
            iteration += 1

            stagnant_assets = check_stagnant_positions()
            if stagnant_assets:
                logger.info(
                    f"🏹 Hunter Monitor: Found {len(stagnant_assets)} stagnant asset(s). "
                    "Waiting for committee-approved replacement opportunities."
                )

            if iteration % 6 != 0:
                continue

            empty_slots = _hunter_empty_slots()
            if empty_slots == 0 and not stagnant_assets:
                logger.info(
                    f"🏹 Hunter Monitor: All {MAX_POSITIONS} trading slots are full; "
                    "skipping discovery, committee, and execution calls."
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

                # Discovery uses the same live signal-scanner universe as the
                # primary scanner. Hunter does not invent a second universe.
                selected_assets = get_universe().signal_scanner_coins()

                # Never send already-open assets into discovery/committee work.
                open_assets = set(state.OPEN_POSITIONS.keys())
                selected_assets = [
                    asset for asset in selected_assets
                    if asset not in open_assets
                ]

                # Keep discovery bounded. This is NOT the committee; only
                # prefiltered candidates reach the canonical StrategyManager.
                chunk_assets = selected_assets[:10]
                items = {
                    asset: get_mtf_data(asset)
                    for asset in chunk_assets
                }
                items = {
                    asset: data
                    for asset, data in items.items()
                    if data
                }

                if not items:
                    logger.info(
                        "🏹 Hunter Monitor: No candidate market data available "
                        "after slot/open-position filtering."
                    )
                    continue

                logger.info(
                    f"🔎 Hunter Monitor: Prefiltering {len(items)} discovery "
                    "candidate(s) before strategy committee..."
                )

                # Discovery only. This does not select the execution strategy.
                results, provider = await analyze_batch(items, get_config())
                logger.info(f"🧠 Hunter discovery provider: {provider}")

                committee = StrategyManager()
                pending_signals = []

                for asset_name, data in items.items():
                    result = results.get(asset_name) or {}
                    discovery_signal = result.get("signal", "HOLD")
                    discovery_conf = int(result.get("confidence", 0) or 0)

                    # Avoid unnecessary committee churn. The canonical committee
                    # still makes the actual opportunity decision.
                    if (
                        discovery_conf < MIN_CONFIDENCE
                        or "HOLD" in discovery_signal.upper()
                    ):
                        logger.debug(
                            f"🏹 Hunter prefilter rejected {asset_name}: "
                            f"signal={discovery_signal} conf={discovery_conf}%"
                        )
                        continue

                    committee_signal, committee_conf, committee_strategy = (
                        await committee.get_trade_signal(data)
                    )

                    logger.info(
                        f"🗳️ Hunter Committee: {asset_name} | "
                        f"signal={committee_signal} conf={committee_conf}% "
                        f"winner={committee_strategy}"
                    )

                    if (
                        committee_signal == "HOLD"
                        or int(committee_conf or 0) < MIN_CONFIDENCE
                    ):
                        logger.info(
                            f"🏹 Hunter rejected by committee: {asset_name} | "
                            f"signal={committee_signal} conf={committee_conf}%"
                        )
                        continue

                    regime = getattr(committee, "current_regime", "RANGING")
                    pending_signals.append(
                        {
                            "asset": asset_name,
                            "signal": committee_signal,
                            "confidence": int(committee_conf),
                            "regime": regime,
                            "strategy": committee_strategy,
                            "committee_passed": True,
                            "data": data,
                        }
                    )

                if pending_signals:
                    await run_hunter_protocol_idle(
                        pending_signals,
                        None,
                        system=system,
                    )
                else:
                    logger.info(
                        "🏹 Hunter Monitor: No committee-approved opportunities in this phase."
                    )

            except Exception as exc:
                logger.exception(
                    f"🏹 Hunter Monitor: Failed to analyze opportunity universe: {exc}"
                )

        except asyncio.CancelledError:
            logger.info("🏹 Hunter Monitor: Cancelled")
            raise
        except Exception as exc:
            logger.error(f"🏹 Hunter Monitor: Loop error: {exc}")
            await asyncio.sleep(60)
