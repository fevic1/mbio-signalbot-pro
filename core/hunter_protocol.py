import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List

import core.state as state
from core.exchange_limits import get_exchange_limits

logger = logging.getLogger(__name__)

# Hunter Protocol Settings
STAGNATION_THRESHOLD = 3600  # 1 hour in seconds
MIN_VOTES_TO_PASS = 4        # Six-strategy committee requires 4/6
MIN_CONFIDENCE = 70           # Committee confidence gate
MAX_POSITIONS = 5             # Global safety limit for concurrent positions


def update_hold_tracking(asset_name: str, signal: str):
    """Track how long an open position has been receiving a HOLD signal."""
    if asset_name not in state.OPEN_POSITIONS:
        return

    pos = state.OPEN_POSITIONS[asset_name]

    if asset_name.startswith("GRID::") or pos.get("dca") or pos.get("strategy") in [
        "AUTO_DCA",
        "MANUAL_DCA",
    ]:
        return

    if "HOLD" in signal.upper():
        if "hold_since" not in pos:
            pos["hold_since"] = datetime.now(timezone.utc)
            logger.info("🐌 %s entered HOLD state. Stagnation timer started.", asset_name)
    else:
        if "hold_since" in pos:
            del pos["hold_since"]
            logger.info("🏃 %s broke out of HOLD state. Stagnation timer reset.", asset_name)


def check_stagnant_positions() -> List[str]:
    """Return positions held in HOLD for at least one hour, excluding GRID/DCA."""
    stagnant_assets = []
    now = datetime.now(timezone.utc)

    for asset, pos in state.OPEN_POSITIONS.items():
        if asset.startswith("GRID::"):
            continue
        if pos.get("dca") or pos.get("strategy") in ["AUTO_DCA", "MANUAL_DCA"]:
            continue

        if "hold_since" in pos:
            hold_duration = (now - pos["hold_since"]).total_seconds()
            if hold_duration >= STAGNATION_THRESHOLD:
                stagnant_assets.append(asset)
                logger.warning(
                    "⚠️ %s has been stagnant (HOLD) for %.1f minutes!",
                    asset,
                    hold_duration / 60,
                )

    return stagnant_assets


async def run_hunter_protocol_idle(
    pending_signals: List[Dict],
    chat_id: int | None,
    system=None,
):
    """Execute only committee-approved Hunter opportunities."""
    logger.info("🏹 Hunter Protocol: Scanning for committee-approved opportunities...")

    stagnant_assets = check_stagnant_positions()
    hunted_candidates = []

    for signal_data in pending_signals:
        asset_name = signal_data.get("asset")
        signal = str(signal_data.get("signal", "HOLD")).upper()
        conf = int(signal_data.get("confidence", 0) or 0)
        committee_approved = bool(signal_data.get("committee_approved", False))

        if asset_name in stagnant_assets or asset_name in state.OPEN_POSITIONS:
            continue

        if not committee_approved:
            logger.info(
                "🏹 Hunter rejected %s: no six-strategy committee approval.",
                asset_name,
            )
            continue

        if signal not in {"BUY", "SELL"}:
            continue

        if conf < MIN_CONFIDENCE:
            logger.info(
                "🏹 Hunter rejected %s: committee confidence %d%% < %d%%.",
                asset_name,
                conf,
                MIN_CONFIDENCE,
            )
            continue

        hunted_candidates.append({
            "asset": asset_name,
            "signal": signal,
            "confidence": conf,
            "committee_approved": True,
            "strategy": "ENSEMBLE",
            "data": signal_data.get("data", {}),
        })
        logger.info(
            "🎯 Hunter Candidate: %s %s (committee=%d/6, conf=%d%%)",
            asset_name,
            signal,
            MIN_VOTES_TO_PASS,
            conf,
        )

    if not hunted_candidates:
        logger.info("🏹 Hunter Protocol: No committee-approved candidates found.")
        return

    hunted_candidates.sort(key=lambda x: x["confidence"], reverse=True)

    # Swap stagnant positions only after a fresh committee-approved candidate exists.
    for stagnant_asset in stagnant_assets:
        if not hunted_candidates:
            break
        best_candidate = hunted_candidates.pop(0)
        await _execute_swap(stagnant_asset, best_candidate)

    active_positions_count = len(
        [k for k in state.OPEN_POSITIONS.keys() if not k.startswith("GRID::")]
    )
    empty_slots = MAX_POSITIONS - active_positions_count

    if empty_slots > 0 and hunted_candidates:
        logger.info(
            "🏹 Hunter Protocol: %d empty slot(s) available. Filling with committee winners...",
            empty_slots,
        )
        for _ in range(min(empty_slots, len(hunted_candidates))):
            best_candidate = hunted_candidates.pop(0)
            await _execute_fill(best_candidate)


async def _execute_swap(stagnant_asset: str, candidate: Dict):
    """Close a stagnant position, then open a committee-approved replacement."""
    stagnant_pos = state.OPEN_POSITIONS.get(stagnant_asset)
    if not stagnant_pos:
        logger.warning(
            "🏹 Hunter Protocol: Stagnant asset %s not found in state.",
            stagnant_asset,
        )
        return

    logger.info(
        "🔄 Hunter Protocol: Swapping %s → %s after committee approval",
        stagnant_asset,
        candidate["asset"],
    )

    try:
        from execution.hl_executor import execute_hl_order
        from core.data_fetcher import get_mtf_data

        close_side = "SELL" if stagnant_pos.get("side") == "BUY" else "BUY"
        close_size = float(stagnant_pos.get("size", 0))

        close_result = execute_hl_order(
            coin=stagnant_asset,
            side=close_side,
            size=close_size,
            reduce_only=True,
            strategy="HUNTER_SWAP",
            regime="SIDEWAYS",
            execution_label="QT_EXIT",
        )

        if not close_result.get("success"):
            logger.error(
                "❌ Hunter Protocol: Failed to close %s: %s",
                stagnant_asset,
                close_result.get("error"),
            )
            return

        if stagnant_asset in state.OPEN_POSITIONS:
            del state.OPEN_POSITIONS[stagnant_asset]
            state.save_state()

        data = get_mtf_data(f"{candidate['asset']}-USD")
        if not data or "1h" not in data:
            logger.error(
                "❌ Hunter Protocol: Failed to fetch market data for %s",
                candidate["asset"],
            )
            return

        current_price = float(data["1h"]["price"])
        target_notional = 12.0
        new_size = round(target_notional / current_price, 4)

        if new_size * current_price < get_exchange_limits()["min_notional_usd"]:
            new_size = round(11.0 / current_price, 4)

        open_side = "BUY" if candidate["signal"] == "BUY" else "SELL"
        open_result = execute_hl_order(
            coin=candidate["asset"],
            side=open_side,
            size=new_size,
            reduce_only=False,
            strategy="HUNTER_SWAP",
            regime="SIDEWAYS",
            execution_label="QT_ENTRY",
        )

        if open_result.get("success"):
            logger.info(
                "✅ Hunter Protocol: Successfully opened %s %s",
                candidate["asset"],
                open_side,
            )
        else:
            logger.error(
                "❌ Hunter Protocol: Failed to open %s: %s",
                candidate["asset"],
                open_result.get("error"),
            )

    except Exception as e:
        logger.error("❌ Hunter Protocol: Swap execution failed: %s", e)


async def _execute_fill(candidate: Dict):
    """Fill an empty slot with a committee-approved opportunity."""
    logger.info(
        "🏹 Hunter Protocol: Filling empty slot with %s %s",
        candidate["asset"],
        candidate["signal"],
    )

    if not candidate.get("committee_approved"):
        logger.error("❌ Hunter Protocol: Refusing non-committee candidate %s", candidate["asset"])
        return

    try:
        from execution.hl_executor import execute_hl_order
        from core.data_fetcher import get_mtf_data

        data = get_mtf_data(f"{candidate['asset']}-USD")
        if not data or "1h" not in data:
            logger.error(
                "❌ Hunter Protocol: Failed to fetch market data for %s",
                candidate["asset"],
            )
            return

        current_price = float(data["1h"]["price"])
        target_notional = 12.0
        new_size = round(target_notional / current_price, 4)

        if new_size * current_price < get_exchange_limits()["min_notional_usd"]:
            new_size = round(11.0 / current_price, 4)

        open_side = "BUY" if candidate["signal"] == "BUY" else "SELL"
        open_result = execute_hl_order(
            coin=candidate["asset"],
            side=open_side,
            size=new_size,
            reduce_only=False,
            strategy="HUNTER_FILL",
            regime="SIDEWAYS",
            execution_label="QT_ENTRY",
        )

        if open_result.get("success"):
            logger.info(
                "✅ Hunter Protocol: Successfully filled slot with %s %s",
                candidate["asset"],
                open_side,
            )
        else:
            logger.error(
                "❌ Hunter Protocol: Failed to open %s: %s",
                candidate["asset"],
                open_result.get("error"),
            )

    except Exception as e:
        logger.error("❌ Hunter Protocol: Fill execution failed: %s", e)


async def hunter_monitor_loop(system=None):
    """Continuous Hunter monitor with a canonical six-strategy decision gate."""
    logger.info(
        "🏹 Hunter Monitor: Starting continuous background monitoring (5-min checks, 30-min Top-10 committee scans)..."
    )

    iteration = 0
    strategy_manager = None

    while True:
        try:
            await asyncio.sleep(300)
            iteration += 1

            stagnant_assets = check_stagnant_positions()
            if stagnant_assets:
                logger.info(
                    "🏹 Hunter Monitor: Found %d stagnant asset(s). Waiting for a fresh committee-approved replacement.",
                    len(stagnant_assets),
                )

            if iteration % 6 != 0:
                continue

            logger.info("🏹 Hunter Monitor: Running canonical Top-10 committee analysis...")

            try:
                from core.signal_generator import analyze_batch
                from core.asset_universe import get_universe
                from core.data_fetcher import get_mtf_data
                from config_loader import get_config
                from core.strategy_manager import StrategyManager

                if strategy_manager is None:
                    strategy_manager = StrategyManager()

                selected_assets = get_universe().signal_scanner_coins()
                open_assets = set(state.OPEN_POSITIONS.keys())
                selected_assets = [
                    asset for asset in selected_assets
                    if asset not in open_assets
                ]

                items = {
                    asset: get_mtf_data(asset)
                    for asset in selected_assets[:10]
                }

                if not items:
                    logger.info("🏹 Hunter Monitor: No Top-10 assets available to analyze.")
                    continue

                results, provider = await analyze_batch(items, get_config())
                logger.info("🧠 MBIO Hunter intelligence provider: %s", provider)

                if provider == "failed":
                    logger.warning("🏹 Hunter: MBIO intelligence returned no valid signals.")
                    continue

                pending_signals = []
                for asset_name, data in items.items():
                    result = results.get(asset_name) or {}
                    llm_signal = str(result.get("signal", "HOLD")).upper()
                    llm_conf = int(result.get("confidence", 0) or 0)

                    committee_signal, committee_conf, _ = await strategy_manager.get_trade_signal(
                        data,
                        llm_signal=llm_signal,
                        llm_confidence=llm_conf,
                    )

                    logger.info(
                        "🏹 Hunter committee: %s MBIO=%s/%d%% -> %s/%d%%",
                        asset_name,
                        llm_signal,
                        llm_conf,
                        committee_signal,
                        committee_conf,
                    )

                    if committee_signal in {"BUY", "SELL"} and committee_conf >= MIN_CONFIDENCE:
                        pending_signals.append({
                            "asset": asset_name,
                            "signal": committee_signal,
                            "confidence": committee_conf,
                            "committee_approved": True,
                            "strategy": "ENSEMBLE",
                            "regime": strategy_manager.current_regime,
                            "data": data,
                        })

                if pending_signals:
                    await run_hunter_protocol_idle(
                        pending_signals,
                        None,
                        system=system,
                    )
                else:
                    logger.info(
                        "🏹 Hunter Monitor: No 4/6 committee-approved opportunities in Top-10."
                    )

            except Exception as e:
                import traceback
                logger.error(
                    "🏹 Hunter Monitor: Failed to analyze Top-10 committee: %s\n%s",
                    e,
                    traceback.format_exc(),
                )

        except Exception as e:
            logger.error("🏹 Hunter Monitor: Loop error: %s", e)
            await asyncio.sleep(60)
