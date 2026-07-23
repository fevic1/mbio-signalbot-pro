"""
monitoring/alert_manager.py — All Telegram notifications and command handlers.
No trading logic here. Receives data, formats messages, sends them.
Command handlers call execution helpers but never own position state.
"""

import asyncio
import os
import re
import logging
from core.app_context import app_context
from datetime import datetime, timezone
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from core.dca_lifecycle import handle_position_close_event
from core.trade_ledger import record_trade
from core.grid_persistence import save_grid_state, clear_grid_state
import core.state as state
from core.executor_utils import run_executor_method

os.environ.setdefault("CHROMA_TELEMETRY_DISABLED", "true")

# Global application reference — set by main.py after initialize()
_application = None

# Safe notification wrapper — prevents "bot not initialised" errors
_bot_ready = False


def set_bot_ready(ready: bool = True):
    """Call after application.initialize() completes."""
    global _bot_ready
    _bot_ready = ready


async def safe_send_message(chat_id, text, parse_mode=None):
    """Send message only if bot is initialized. Silently skip otherwise."""
    global _bot_ready
    if not _bot_ready:
        return
    try:
        if hasattr(_application, 'bot') and _application.bot:
            await _application.bot.send_message(
                chat_id=chat_id, text=text, parse_mode=parse_mode
            )
    except Exception:
        pass  # Silent fail during init race


logger = logging.getLogger(__name__)

_bot: Bot | None = None


def init_telegram_bot(token: str) -> Bot:
    global _bot
    _bot = Bot(token=token)
    return _bot


def get_bot() -> Bot:
    if _bot is None and _application is not None:
        return _application.bot
    if _bot is None:
        logger.warning("⚠️ Telegram bot not ready")
        return None
    return _bot


# ------------------------------------------------------------------
# Signal / execution / TP / closure messages
# ------------------------------------------------------------------

async def send_signal(
    asset_name: str,
    data: dict,
    signal: str,
    confidence: int,
    reasoning: str,
    trade_plan: tuple,
    provider: str,
    chat_id: str,
    cached: bool = False,
) -> None:
    entry, sl, tp1, tp2, tp3 = trade_plan
    emoji = "🟢" if "BUY" in signal else "🔴" if "SELL" in signal else "⚪"
    filled = min(10, max(0, int(confidence / 10)))
    meter = "█" * filled + "░" * (10 - filled)
    plan = (
        f"💰 Entry: `${entry}`\n🛡 SL: `${sl}`\n"
        f"🏁 TP1: `${tp1}`\n🏁 TP2: `${tp2}`\n🏁 TP3: `${tp3}`"
        if entry else "💼 No trade plan for HOLD"
    )
    cache_note = " 💾 CACHED" if cached else ""

    msg = (
        f"⚡️ *MBIO SIGNAL: {asset_name}* ⚡️{cache_note}\n"
        f"{emoji} {signal} | Conf: {confidence}% [{meter}]\n"
        f"🤖 Model: {provider}\n\n"
        f"{plan}\n\n"
        f"📊 1H RSI: {data['1h']['rsi']} | "
        f"4H RSI: {data['4h']['rsi']} | "
        f"1D RSI: {data['1d']['rsi']}\n"
        f"🧠 {reasoning}\n"
        f"⚠️ _DYOR_"
    )
    await safe_send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")


async def send_execution(
    asset_name: str,
    side: str,
    size: float,
    entry_price: float,
    sl_price: float,
    tp1_price: float,
    tp2_price: float,
    tp3_price: float,
    order_id: str,
    chat_id: str,
) -> None:
    emoji = "🟢" if side == "BUY" else "🔴"
    direction = "LONG" if side == "BUY" else "SHORT"
    msg = (
        f"{emoji} *MBIO EXECUTION: {asset_name}* {emoji}\n"
        f"──────────────────────────\n"
        f"📊 Direction: {direction}\n"
        f"💰 Entry: ${entry_price:.4f}\n"
        f"📦 Size: {size} {asset_name}\n"
        f"💵 Value: ${size * entry_price:.2f}\n"
        f"🛡 SL: ${sl_price:.4f}\n"
        f"🏁 TP1: ${tp1_price:.4f}\n"
        f"🏁 TP2: ${tp2_price:.4f}\n"
        f"🏁 TP3: ${tp3_price:.4f}\n"
        f"🆔 Order: {order_id}\n"
        f"⏰ {datetime.now(timezone.utc).strftime('%H:%M:%S')} UTC"
    )
    await safe_send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")


async def send_tp_hit(
    asset_name: str,
    tp_level: str,
    current_price: float,
    entry_price: float,
    chat_id: str,
) -> None:
    pos = state.OPEN_POSITIONS.get(asset_name, {})
    side = pos.get("side", "BUY")
    profit_pct = (
        ((current_price - entry_price) / entry_price * 100)
        if side == "BUY"
        else ((entry_price - current_price) / entry_price * 100)
    )
    msg = (
        f"🎯 *MBIO {tp_level} HIT: {asset_name}* 🎯\n"
        f"💰 Entry: ${entry_price:,.4f}\n"
        f"🎯 {tp_level}: ${current_price:,.4f}\n"
        f"📈 Profit so far: {profit_pct:+.2f}%\n"
        f"✅ SL moved to breakeven"
    )
    await safe_send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")


async def send_closure(
    asset_name: str,
    side: str,
    entry_price: float,
    exit_price: float,
    size: float,
    pnl_usd: float,
    pnl_percent: float,
    reason: str,
    chat_id: str,
    tp_hit: str | None = None,
) -> None:
    emoji = "✅" if pnl_usd > 0 else "❌"
    direction = "LONG" if side == "BUY" else "SHORT"
    msg = (
        f"{emoji} *MBIO CLOSED: {asset_name}* {emoji}\n"
        f"📊 {direction} | Size: {size}\n"
        f"💰 Entry: ${entry_price:,.4f} → Exit: ${exit_price:,.4f}\n"
        f"💰 PnL: ${pnl_usd:+,.2f} ({pnl_percent:+.2f}%)\n"
        f"📝 {reason}\n"
        f"{'🎉 Profit!' if pnl_usd > 0 else '🛑 Loss'}"
    )
    await safe_send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")


async def send_drawdown_halt(daily_pnl: float, threshold: float, chat_id: str) -> None:
    msg = (
        f"🛑 *DRAWDOWN HALT TRIGGERED*\n"
        f"Daily PnL: {daily_pnl:.2f}%\n"
        f"Threshold: {threshold:.1f}%\n"
        f"All new positions are blocked for the rest of the day."
    )
    await safe_send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")


# ------------------------------------------------------------------
# Telegram command handlers
# ------------------------------------------------------------------

def _make_close_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(f"❌ Close {asset}", callback_data=f"close_{asset}")]
        for asset in state.OPEN_POSITIONS.keys()
    ]
    keyboard.append([InlineKeyboardButton("❌ Close All", callback_data="close_all")])
    return InlineKeyboardMarkup(keyboard)


async def _safe_send_telegram(chat_id, text: str, parse_mode='HTML'):
    """Send Telegram message with automatic fallback to plain text on parse failure."""
    try:
        bot = get_bot()
        if bot and chat_id:
            await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
    except Exception:
        # Fallback: strip all formatting and resend as plain text
        plain = re.sub(r'<[^>]+>', '', str(text))
        plain = re.sub(r'[*_`~\[\](){}#+\-=|.!>\\]', '', plain)
        try:
            bot = get_bot()
            if bot and chat_id:
                await bot.send_message(chat_id=chat_id, text=plain[:4000])
        except Exception as e2:
            logger.warning(f"⚠️ Telegram send failed completely: {e2}")


async def cmd_positions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not state.OPEN_POSITIONS:
        await update.message.reply_text("📭 No open positions.")
        return

    from core.data_fetcher import get_current_price
    from config_loader import get_config

    cfg = get_config()
    assets_map = (cfg if isinstance(cfg, dict) else (cfg.model_dump() if hasattr(cfg, "model_dump") else cfg.dict())).get("assets", {}).get("crypto", {})

    msg = "📊 <b>MBIO OPEN POSITIONS</b>\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━\n"

    for asset, pos in state.OPEN_POSITIONS.items():
        # Skip phantom GRID:: entries with zero size (config placeholders, not real positions)
        if asset.startswith("GRID::") and float(pos.get("size", 0) or 0) == 0:
            continue
        side = pos.get("side", "BUY")
        direction = "LONG 🟢" if side == "BUY" else "SHORT 🔴"
        entry = float(pos.get("entry", 0))
        size = float(pos.get("size", 0))
        sl = float(pos.get("sl", 0))
        tp1 = float(pos.get("tp1", 0))
        tp2 = float(pos.get("tp2", 0))
        tp3 = float(pos.get("tp3", 0))

        ticker = assets_map.get(asset, f"{asset}-USD")
        try:
            current = get_current_price(ticker)
            if side == "BUY":
                pnl = (current - entry) * size
                pnl_pct = ((current - entry) / entry) * 100 if entry else 0
            else:
                pnl = (entry - current) * size
                pnl_pct = ((entry - current) / entry) * 100 if entry else 0
        except Exception:
            current = pnl = pnl_pct = 0

        pnl_emoji = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
        pnl_sign = "+" if pnl >= 0 else ""

        msg += f"\n🪙 <b>Asset:</b> <code>{asset}</code>\n"
        msg += f"📈 <b>Direction:</b> {direction}\n\n"
        msg += f"💵 <b>Entry:</b> <code>${entry:,.4f}</code>\n"
        msg += f"📦 <b>Size:</b> <code>{size:.4f}</code>\n"
        msg += f"💎 <b>Value:</b> <code>${size * entry:,.2f}</code>\n\n"

        msg += f"📈 <b>PERFORMANCE &amp; RISK</b>\n"
        msg += f"├─ {pnl_emoji} <b>uPnL:</b> <code>{pnl_sign}${pnl:,.2f}</code> ({pnl_sign}{pnl_pct:.2f}%)\n"
        msg += f"├─ 🛡 <b>SL:</b> <code>${sl:,.4f}</code>\n"
        msg += f"├─ 🏁 <b>TP1:</b> <code>${tp1:,.4f}</code>\n"
        msg += f"├─ 🏁 <b>TP2:</b> <code>${tp2:,.4f}</code>\n"
        msg += f"└─ 🏁 <b>TP3:</b> <code>${tp3:,.4f}</code>\n"
        reasoning_data = pos.get("llm_reasoning", {})
        if reasoning_data:
            msg += f"🧠 <b>Reasoning:</b> {reasoning_data.get('reasoning', 'N/A')}\n"
            msg += f"🤖 <b>Provider:</b> {reasoning_data.get('provider', 'N/A')}\n"
            msg += f"🎯 <b>Confidence:</b> {reasoning_data.get('confidence', 0)}%\n"

        msg += "━━━━━━━━━━━━━━━━━━━━━━\n"

    await update.message.reply_text(
        msg,
        parse_mode="HTML",
        reply_markup=_make_close_keyboard()
    )


async def cmd_close(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Close a position (full or partial) including all DCA levels."""
    if not update.message or not update.message.text:
        return

    parts = update.message.text.split()
    if len(parts) < 2:
        await update.message.reply_text(
            "Usage: /close <ASSET> [PERCENT]\nExamples:\n/close BTC (full)\n/close BTC 50% (half)"
        )
        return

    asset = parts[1].upper()
    percent = 100.0
    if len(parts) > 2:
        pct_str = parts[2].replace('%', '').replace('percent', '')
        try:
            percent = float(pct_str)
            if not 0 < percent <= 100:
                await update.message.reply_text("❌ Percent must be between 0 and 100")
                return
        except ValueError:
            await update.message.reply_text("❌ Invalid percent format. Use: 50 or 50%")
            return

    if asset not in state.OPEN_POSITIONS:
        await update.message.reply_text(f"❌ No open position for {asset}")
        return

    try:
        pos = state.OPEN_POSITIONS[asset]

        # Query live exchange using verified normalized format
        from core.app_context import app_context
        _live_positions = (await run_executor_method(app_context.executor.get_open_positions)) or []
        _live_pos = None
        for _item in _live_positions:
            if isinstance(_item, dict) and _item.get("coin") == asset:
                _live_pos = _item
                break

        if not _live_pos:
            await update.message.reply_text(f"❌ No live position for {asset} on exchange")
            return

        size = float(_live_pos.get("size", 0))
        _side_str = str(_live_pos.get("side", "")).lower()

        if size <= 0:
            await update.message.reply_text(f"❌ Position size is 0 for {asset}")
            return

        close_side = "SELL" if _side_str == "long" else "BUY"
        close_size = size * (percent / 100.0)

        logger.info(f"🔍 Closing {asset}: EXCHANGE side={_side_str} size={size} → {close_side} {close_size} ({percent}%)")

        # DCA-AWARE CLOSE
        dca_config = pos.get("dca")
        if dca_config and dca_config.get("enabled"):
            from core.dca_manager import DCAManager
            dca = DCAManager(_exec)
            dca.active_dca[asset] = dca_config

            if percent >= 100:
                result = await dca.close_dca_position(asset, dca_config, close_side)
                exit_price = float(result.get("avg_price", 0))
                pnl_usd = float(result.get("total_pnl", 0))

                msg = f"✅ Closed {asset} DCA position\n"
                msg += f"├ Base closed: {'Yes' if result['base_closed'] else 'No'}\n"
                msg += f"├ DCA orders cancelled: {result['dca_cancelled']}\n"
                msg += f"├ Total PnL: ${pnl_usd:+.4f}\n"
                if result["errors"]:
                    msg += f"└ Errors: {', '.join(result['errors'][:3])}"

                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=msg,
                    parse_mode='HTML'
                )
                record_trade("close", asset, "DCA", close_side, close_size, exit_price, pnl=pnl_usd, order_id=result.get("order_id"))

                if percent >= 100:
                    state.OPEN_POSITIONS.pop(asset, None)
                else:
                    pos["size"] = size - close_size
                state.save_state()
            else:
                # Partial DCA close
                from execution.hl_executor import execute_hl_order
                result = await asyncio.to_thread(
                    execute_hl_order,
                    coin=asset,
                    side=close_side,
                    size=close_size,
                )
                exit_price = float(result.get("avg_price", 0))
                entry_price = float(pos.get("entry", 0))
                if close_side == "SELL":
                    pnl_usd = (exit_price - entry_price) * close_size
                else:
                    pnl_usd = (entry_price - exit_price) * close_size

                record_trade("close", asset, "DCA", close_side, close_size, exit_price, pnl=pnl_usd, order_id=result.get("order_id"))
                pos["size"] = size - close_size
                state.save_state()
                await update.message.reply_text(f"✅ Closed {percent}% of {asset}. PnL: ${pnl_usd:+.4f}")
        else:
            # NON-DCA CLOSE
            from execution.hl_executor import execute_hl_order
            result = await asyncio.to_thread(
                execute_hl_order,
                coin=asset,
                side=close_side,
                size=close_size,
            )

            if result and result.get("success"):
                exit_price = float(result.get("avg_price", 0))
                entry_price = float(pos.get("entry", 0))

                if close_side == "SELL":
                    pnl_usd = (exit_price - entry_price) * close_size
                else:
                    pnl_usd = (entry_price - exit_price) * close_size

                record_trade("close", asset, "MANUAL", close_side, close_size, exit_price, pnl=pnl_usd, order_id=result.get("order_id"))

                if percent >= 100:
                    state.OPEN_POSITIONS.pop(asset, None)
                else:
                    pos["size"] = size - close_size
                state.save_state()
                await update.message.reply_text(f"✅ Closed {percent}% of {asset}. PnL: ${pnl_usd:+.4f}")
            else:
                await update.message.reply_text(f"❌ Failed to close {asset}: {result.get('error', 'Unknown')}")

    except Exception as e:
        logger.error(f"❌ Error in cmd_close: {e}")
        await update.message.reply_text(f"💥 Error: {str(e)}")


async def cmd_closeall(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not state.OPEN_POSITIONS:
        await update.message.reply_text("📭 No open positions to close.")
        return

    count = len(state.OPEN_POSITIONS)
    await update.message.reply_text(f"⏳ Closing {count} position(s)...")

    closed, failed = 0, 0
    for asset in list(state.OPEN_POSITIONS.keys()):
        success = await _close_position(asset)
        if success:
            closed += 1
        else:
            failed += 1

    await update.message.reply_text(f"✅ Closed: {closed}\n❌ Failed: {failed}")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "close_all":
        if not state.OPEN_POSITIONS:
            await query.edit_message_text("📭 No open positions to close.")
            return
        count = len(state.OPEN_POSITIONS)
        closed = 0
        await query.edit_message_text(f"⏳ Closing {count} position(s)...")
        for asset in list(state.OPEN_POSITIONS.keys()):
            if await _close_position(asset):
                closed += 1
        await query.message.reply_text(f"✅ Closed {closed}/{count} positions")

    elif data.startswith("close_"):
        asset = data.replace("close_", "")
        if asset not in state.OPEN_POSITIONS:
            await query.edit_message_text(f"❌ No position for {asset}")
            return
        success = await _close_position(asset)
        if success:
            await query.edit_message_text(f"✅ {asset} position closed!")
        else:
            await query.edit_message_text(f"❌ Failed to close {asset}")


async def _close_position(asset: str, reply_fn=None) -> bool:
    """Execute a market close for an open position."""
    from execution.hl_executor import execute_hl_order
    from config_loader import get_config

    cfg = get_config()
    hl_assets = {a: a for a in (cfg if isinstance(cfg, dict) else (cfg.model_dump() if hasattr(cfg, "model_dump") else cfg.dict())).get("hyperliquid", {}).get("assets", [])}

    try:
        pos = state.OPEN_POSITIONS[asset]
        side = "SELL" if pos.get("side", "BUY") == "BUY" else "BUY"

        result = await asyncio.to_thread(
            execute_hl_order,
            coin=hl_assets.get(asset, asset),
            side=side,
            size=pos["size"],
        )

        if result.get("status") == "success" or result.get("success"):
            exit_price = float(result.get("avg_price", 0))
            if exit_price == 0:
                from core.data_fetcher import get_current_price
                exit_price = get_current_price(f"{asset}-USD")

            entry_price = pos.get("entry", 0)
            trade_size = pos.get("size", 0)
            trade_side = pos.get("side", "BUY")

            if trade_side == "BUY":
                pnl_pct = ((exit_price - entry_price) / entry_price) * 100
                pnl_usd = (exit_price - entry_price) * trade_size
            else:
                pnl_pct = ((entry_price - exit_price) / entry_price) * 100
                pnl_usd = (entry_price - exit_price) * trade_size

            try:
                from core.performance_tracker import get_performance_tracker
                tracker = get_performance_tracker()
                tracker.record_close_trade(
                    asset=asset,
                    exit_price=exit_price,
                    close_reason="Manual Close"
                )
                logger.info(f"✅ Trade recorded for {asset}")
            except Exception as e:
                logger.error(f"Failed to record trade: {e}")

            del state.OPEN_POSITIONS[asset]

            try:
                state.save_state()
            except Exception as e:
                logger.error(f"Failed to save state: {e}")

            if reply_fn:
                await reply_fn(f"✅ {asset} closed! PnL: ${pnl_usd:+.2f} ({pnl_pct:+.2f}%)")
            return True
        else:
            reason = result.get("reason", result.get("error", "Unknown error"))
            if reply_fn:
                await reply_fn(f"❌ Failed to close {asset}: {reason}")
            return False

    except Exception as e:
        logger.error(f"Close position error for {asset}: {e}")
        if reply_fn:
            await reply_fn(f"❌ Error closing {asset}: {e}")
        return False


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send live bot status summary to Telegram."""
    try:
        from config_loader import get_config
        from core.data_fetcher import get_account_balance

        cfg = get_config()
        balance = get_account_balance()
        positions = state.OPEN_POSITIONS

        notional = sum(p.get("size", 0) * p.get("entry", 0) for p in positions.values())
        deployed_pct = (notional / balance * 100) if balance > 0 else 0

        intervals = (cfg if isinstance(cfg, dict) else (cfg.model_dump() if hasattr(cfg, "model_dump") else cfg.dict())).get("intervals", {})
        quick_min = intervals.get("quick_scanner_sec", 900) // 60
        entry_min = intervals.get("entry_scanner_sec", 1800) // 60
        full_hours = intervals.get("full_analysis_hours", 2)

        ai_cfg = (cfg if isinstance(cfg, dict) else (cfg.model_dump() if hasattr(cfg, "model_dump") else cfg.dict())).get("ai", {})
        providers = ", ".join(ai_cfg.get("provider_order", ["groq", "cerebras", "openrouter"]))

        try:
            from core.performance_tracker import get_performance_tracker
            from core.data_fetcher import get_current_price

            tracker = get_performance_tracker()
            current_prices = {}
            for asset in state.OPEN_POSITIONS.keys():
                try:
                    current_prices[asset] = get_current_price(f"{asset}-USD")
                except Exception:
                    pass

            stats = tracker.get_performance_stats(current_prices)
            realized_pnl_usd = stats["realized_pnl_usd"]
            unrealized_pnl_usd = stats["unrealized_pnl_usd"]
            total_pnl_usd = realized_pnl_usd + unrealized_pnl_usd
            daily_pnl = stats["realized_pnl_pct"] + stats["unrealized_pnl_pct"]

            if stats['closed_trades'] > 0:
                win_rate_str = f"{stats['win_rate']:.1f}% ({stats['closed_trades']} closed)"
            else:
                win_rate_str = f"N/A ({stats['open_trades']} open, 0 closed)"

            top_strat = stats["best_strategy"]
        except Exception as e:
            logger.error(f"Failed to get performance stats: {e}", exc_info=True)
            daily_pnl = 0.0
            realized_pnl_usd = 0.0
            unrealized_pnl_usd = 0.0
            total_pnl_usd = 0.0
            win_rate_str = "N/A"
            top_strat = "N/A"

        try:
            from core.meta_learner import get_meta_learner
            meta = get_meta_learner()
            regime = "RANGING"
            weights = meta.get_weights(regime)
            if weights:
                best_strat = max(weights, key=weights.get)
                top_strat = f"{best_strat} ({weights[best_strat]*100:.0f}%)"
        except Exception:
            pass

        now_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

        deploy_bar_filled = min(10, int(deployed_pct / 100))
        deploy_bar_empty = max(0, 10 - deploy_bar_filled)
        deploy_icon = '🟢' if deployed_pct <= 500 else '🟡' if deployed_pct <= 700 else '🔴'
        pnl_icon = '🟢' if daily_pnl > 0 else '🔴' if daily_pnl < 0 else '🟡'

        msg = (
            f"╔═══════════════════════════════════╗\n"
            f"║  🤖 <b>MBIO SIGNALBOT PRO v9.0</b>  ║\n"
            f"╚═══════════════════════════════════╝\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💼 <b>ACCOUNT OVERVIEW</b>\n"
            f"├─ 💰 Balance: <b>${balance:.2f}</b>\n"
            f"├─ 📊 Positions: <b>{len(positions)}</b> active\n"
            f"├─ 💵 Notional: <b>${notional:.2f}</b>\n"
            f"└─ 🔒 Deployed: <b>{deployed_pct:.0f}%</b> {deploy_icon}\n"
            f"      <code>{'█' * deploy_bar_filled}{'░' * deploy_bar_empty}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📈 <b>PERFORMANCE METRICS</b>\n"
            f"├─ {pnl_icon} Daily PnL: <b>{daily_pnl:+.2f}%</b>\n"
            f"├─ 💰 Realized: <b>${realized_pnl_usd:+.2f}</b> (closed trades)\n"
            f"├─ 📊 Unrealized: <b>${unrealized_pnl_usd:+.2f}</b> (open positions)\n"
            f"├─ 💹 Total PnL: <b>${total_pnl_usd:+.2f}</b>\n"
            f"├─ 🎯 Win Rate: <b>{win_rate_str}</b>\n"
            f"└─ 🏆 Top Strategy: <b>{top_strat}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚙️ <b>SYSTEM STATUS</b>\n"
            f"├─ 🔄 Position Monitor: <b>60s</b> ✅\n"
            f"├─ 🔍 Quick Scanner: <b>{quick_min}min</b> ✅\n"
            f"├─ 🎯 Entry Scanner: <b>{entry_min}min</b> ✅\n"
            f"├─ 🔄 Full Analysis: <b>{full_hours}h</b>\n"
            f"└─ 🧠 AI Providers: <b>{providers}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🛡️ <i>Risk Limit: 500% max for NEW trades</i>\n"
            f"<code>{now_str}</code>"
        )

        await update.message.reply_text(msg, parse_mode="HTML")

    except Exception as e:
        logger.error(f"❌ /status failed: {e}")
        await update.message.reply_text("⚠️ Could not fetch bot status. Check logs.")


# ============================================================
# 🏹 FEE-AWARE RATCHET TOGGLE
# ============================================================

async def cmd_ratchet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from core.profit_ratchet import toggle_ratchet
    new_state = toggle_ratchet()
    status = "🟢 ON" if new_state else "🔴 OFF"
    msg = f"🏹 <b>Profit Ratchet</b>\n━━━━━━━━━━━━━━━━━━━━\nStatus: {status}\n\n"
    if new_state:
        msg += "Now securing partial profit on all open positions."
    else:
        msg += "Ratchet disabled. Relying on standard TP/SL."
    await update.message.reply_text(msg, parse_mode="HTML")


async def cmd_signal_source(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Toggle signal source: internal / tradingview / both"""
    import yaml
    import config_loader

    args = context.args
    valid = ["internal", "tradingview", "both"]

    if args and args[0].lower() in valid:
        new_mode = args[0].lower()
    else:
        cfg = config_loader.get_config()
        current = (cfg if isinstance(cfg, dict) else (cfg.model_dump() if hasattr(cfg, "model_dump") else cfg.dict())).get("execution", {}).get("signal_source", "both")
        idx = valid.index(current) if current in valid else 2
        new_mode = valid[(idx + 1) % len(valid)]

    yaml_path = "config/strategy_config.yaml"
    with open(yaml_path, 'r') as f:
        cfg = yaml.safe_load(f) or {}
    cfg.setdefault("execution", {})["signal_source"] = new_mode
    with open(yaml_path, 'w') as f:
        yaml.dump(cfg, f, default_flow_style=False, sort_keys=False)

    icons = {"internal": "🧠", "tradingview": "📡", "both": "🔄"}
    msg = f"{icons.get(new_mode, '❓')} <b>Signal Source</b>\n━━━━━━━━━━━━━━━━━━━━\nMode: <b>{new_mode.upper()}</b>\n\n"
    if new_mode == "internal":
        msg += "Using only internal AI/Deterministic signals."
    elif new_mode == "tradingview":
        msg += "Using only TradingView webhook signals."
    else:
        msg += "Accepting signals from BOTH sources."
    await update.message.reply_text(msg, parse_mode="HTML")


async def cmd_strategy_select(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Select active trading strategy from registry."""
    import yaml
    from core.strategy_registry import list_strategies

    args = context.args
    valid = list_strategies()
    yaml_path = "config/strategy_config.yaml"

    if args and args[0].upper() in valid:
        new_strat = args[0].upper()
    elif args and args[0].lower() == "list":
        msg = "📋 <b>Available Strategies</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        with open(yaml_path, 'r') as f:
            cfg = yaml.safe_load(f) or {}
        current = (cfg if isinstance(cfg, dict) else (cfg.model_dump() if hasattr(cfg, "model_dump") else cfg.dict())).get("execution", {}).get("active_strategy", "NONE")
        for s in valid:
            icon = "🟢" if s == current else "⚪"
            msg += f"{icon} <code>{s}</code>\n"
        await update.message.reply_text(msg, parse_mode="HTML")
        return
    else:
        msg = "❓ Usage: <code>/strategy &lt;ID&gt;</code> or <code>/strategy list</code>\n\nAvailable:\n"
        for s in valid:
            msg += f"• <code>{s}</code>\n"
        await update.message.reply_text(msg, parse_mode="HTML")
        return

    with open(yaml_path, 'r') as f:
        cfg = yaml.safe_load(f) or {}
    cfg.setdefault("execution", {})["active_strategy"] = new_strat
    with open(yaml_path, 'w') as f:
        yaml.dump(cfg, f, default_flow_style=False, sort_keys=False)

    await update.message.reply_text(
        f"🔄 <b>Active Strategy Changed</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        f"Now using: <b>{new_strat}</b>\n\n"
        f"Next analysis cycle will use this strategy.",
        parse_mode="HTML"
    )


async def cmd_dca_chart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show DCA levels as ASCII chart in Telegram."""
    if not update.message or not update.message.text:
        return

    parts = update.message.text.split()
    if len(parts) < 2:
        await update.message.reply_text("Usage: /dca_chart <ASSET>\nExample: /dca_chart BTC")
        return

    asset = parts[1].upper()

    try:
        pos = state.OPEN_POSITIONS.get(asset)
        if not pos:
            await update.message.reply_text(f"❌ No position found for {asset}")
            return

        dca_config = pos.get("dca")
        if not dca_config or not dca_config.get("enabled"):
            await update.message.reply_text(f"ℹ️ {asset} has no active DCA configuration")
            return

        # HLExecutor now from app_context
        executor = app_context.executor
        mids = executor.info.all_mids()
        current_price = float(mids.get(asset, 0))
        if current_price <= 0:
            from core.data_fetcher import get_current_price
            current_price = get_current_price(f"{asset}-USD")

        entry = float(pos.get("entry", 0))
        side = pos.get("side", "BUY")

        lines = []
        lines.append(f"📊 DCA Chart: {asset}")
        lines.append("━" * 40)
        lines.append(f"Current: ${current_price:,.2f} {'📈' if current_price > entry else '📉'}")
        lines.append(f"Entry:   ${entry:,.2f} ({side.upper()})")
        lines.append("")

        levels = dca_config.get("active_orders", []) + dca_config.get("filled_levels", [])
        if not levels:
            lines.append("No DCA levels active")
        else:
            levels_sorted = sorted(levels, key=lambda x: abs(x.get("price", 0) - current_price))
            for level in levels_sorted:
                price = float(level.get("price", 0))
                lvl_size = float(level.get("size", 0))
                lvl_status = level.get("status", "unknown")
                level_num = level.get("level", "?")

                distance_pct = ((price - current_price) / current_price) * 100
                arrow = "↓" if price < current_price else "↑" if price > current_price else "→"
                status_icon = "✅" if lvl_status == "filled" else "⏳" if lvl_status == "active" else "❌"

                lines.append(f"L{level_num}: ${price:,.2f} {arrow} {abs(distance_pct):.2f}% | {lvl_size:.6f} {status_icon}")

            total_size = sum(float(l.get("size", 0)) for l in levels)
            lines.append("")
            lines.append(f"Total DCA size: {total_size:.6f}")

            target_pct = dca_config.get("profit_target_pct", 0)
            if target_pct:
                pnl_pct = ((current_price - entry) / entry) * 100 if side == "BUY" else ((entry - current_price) / entry) * 100
                tgt_status = "🎯 HIT" if pnl_pct >= target_pct else f"⏳ {pnl_pct:.1f}%/{target_pct}%"
                lines.append(f"Profit target: {tgt_status}")

        chart = "\n".join(lines)
        await update.message.reply_text(chart)

    except Exception as e:
        logger.error(f"❌ Error in cmd_dca_chart: {e}")
        await update.message.reply_text(f"💥 Error: {str(e)}")


async def cmd_open_grid(update, context):
    if not update.message or not update.message.text:
        return
    
    parts = update.message.text.split()
    if len(parts) < 5:
        await update.message.reply_text(
            "🔲 <b>GRID Bot Setup</b>\n\n"
            "Usage: <code>/open_grid &lt;ASSET&gt; &lt;LOWER&gt; &lt;UPPER&gt; &lt;LEVELS&gt; [INVESTMENT] [PROFIT_PCT]</code>\n\n"
            "Examples:\n"
            "<code>/open_grid BTC 59000 61000 10 100 0.5</code> (full)\n"
            "<code>/open_grid BTC 59000 61000 10</code> (config defaults)\n"
            "<code>/open_grid BTC 0 0 10</code> (adaptive ATR range)",
            parse_mode='HTML'
        )
        return
    
    # PHASE 1: Parse parameters with optional config defaults
    try:
        import config_loader as _cfg_mod_early
        _grid_defaults = _cfg_mod_early.get_config().get("grid", {})
        
        asset = parts[1].strip().upper()
        lower_price = float(parts[2])
        upper_price = float(parts[3])
        grid_quantity = int(parts[4])
        investment = float(parts[5]) if len(parts) > 5 else float(_grid_defaults.get("min_investment_usd", 30))
        profit_pct = float(parts[6]) if len(parts) > 6 else float(_grid_defaults.get("default_profit_per_grid_pct", 0.5))
    except (ValueError, IndexError) as e:
        await update.message.reply_text(f"❌ Invalid parameter: {e}")
        return
    
    # PHASE 2: Validate (no network, no state)
    import config_loader as _cfg_mod
    min_investment = float(_cfg_mod.get_config().get("grid", {}).get("min_investment_usd", 10))
    
    if lower_price <= 0 or upper_price <= 0:
        # Adaptive mode
        try:
            from core.grid_manager import _get_atr_and_price_history, _get_live_price, compute_adaptive_grid
            current_price = _get_live_price(asset)
            if current_price > 0:
                atr, history = _get_atr_and_price_history(asset)
                lower_price, upper_price, step_size, mode, trend_str = compute_adaptive_grid(
                    asset, current_price, atr, history, grid_quantity
                )
            else:
                await update.message.reply_text("❌ Cannot fetch live price for adaptive calculation")
                return
        except Exception as e:
            await update.message.reply_text(f"❌ Adaptive grid calculation failed: {e}")
            return
    
    if lower_price >= upper_price:
        await update.message.reply_text("❌ Lower price must be less than upper price")
        return
    if grid_quantity < 2 or grid_quantity > 50:
        await update.message.reply_text("❌ Grid quantity must be between 2 and 50")
        return
    if investment <= 0:
        await update.message.reply_text("❌ Investment must be positive")
        return
    if investment < min_investment:
        await update.message.reply_text(
            f"❌ Investment too low. Minimum ${min_investment} USDC required.\n\n"
            f"Try: <code>/open_grid BTC 59000 61000 5 {min_investment} 0.5</code>",
            parse_mode='HTML'
        )
        return
    
    # PHASE 3: Execute (network + state mutations)
    try:
        # HLExecutor now from app_context
        from core.grid_manager import GridManager, grid_state_key
        
        executor = app_context.executor
        mids = executor.info.all_mids()
        current_price = float(mids.get(asset, 0))
        if current_price <= 0:
            await update.message.reply_text(f"❌ Could not fetch price for {asset}")
            return
        
        grid = GridManager(executor)
        import os
        _exchange = os.getenv("DEFAULT_EXCHANGE", "hyperliquid").lower().strip()
        config = await grid.create_grid(asset, lower_price, upper_price, grid_quantity, investment, profit_pct, exchange=_exchange)
        
        _grid_cfg = _cfg_mod.get_config().get("grid", {}).get("reversal", {})
        max_conc = _grid_cfg.get("max_concurrent_orders", 4)
        result = await grid.place_grid_orders(asset, config, current_price, max_concurrent=max_conc)
        
        state.OPEN_POSITIONS[grid_state_key(asset)] = config
        state.save_state()
        
        spacing_val = config.get('step_size', config.get('grid_spacing', 0))
        msg = (
            f"✅ <b>GRID Bot Activated: {asset}</b>\n\n"
            f"📊 Range: ${lower_price:,.2f}-${upper_price:,.2f}\n"
            f"🔢 Levels: {grid_quantity} (spacing: ${spacing_val:.2f})\n"
            f"💰 Investment: ${investment:.2f}\n"
            f"🎯 Profit/Grid: {profit_pct}%\n\n"
            f"📈 Orders placed: {result['placed']}/{grid_quantity}\n"
            f"❌ Failed: {result['failed']}"
        )
        if result["errors"]:
            msg += f"\n⚠️ Errors: {', '.join(result['errors'][:3])}"
        
        record_trade("open", asset, "GRID", "BOTH", investment, current_price,
                     metadata={"range": f"{lower_price}-{upper_price}", "levels": grid_quantity, "profit_pct": profit_pct})
        save_grid_state(state.OPEN_POSITIONS)
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=msg,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"❌ Error in cmd_open_grid: {e}", exc_info=True)
        await update.message.reply_text(f"💥 Error: {str(e)}")

async def cmd_grid_status(update, context):
    """Display grid status using HTML parse mode."""
    chat_id = update.effective_chat.id
    try:
        args = context.args
        asset = args[0].upper() if args else None

        import core.state as gs_state
        from core.grid_manager import is_grid_position, grid_asset_from_key

        grids_found = []
        for key, config in gs_state.OPEN_POSITIONS.items():
            if not is_grid_position(key):
                continue
            grid_asset = grid_asset_from_key(key)
            if asset and grid_asset != asset:
                continue
            grids_found.append((grid_asset, config))

        if not grids_found:
            target = f" for {asset}" if asset else ""
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"ℹ️ No active GRID bot{target}."
            )
            return

        lines = []
        for grid_asset, config in grids_found:
            mode = config.get("mode", "RANGE")
            mode_icon = "🚀" if mode == "TREND" else "🔲"
            lower = config.get("lower_price", 0)
            upper = config.get("upper_price", 0)
            step = config.get("step_size", config.get("spacing", 0))
            cycles = config.get("completed_cycles", 0)
            pnl = config.get("total_realized_pnl", 0.0)
            nodes = config.get("nodes", [])
            active = len([n for n in nodes if n.get("status") == "OPEN"])
            total = len(nodes)

            lines.append(f"<b>{mode_icon} Grid Status: {grid_asset}</b>")
            lines.append("━━━━━━━━━━━━━━━━━━━━")
            lines.append(f"💹 Mode: <b>{mode}</b>")
            lines.append(f"🔒 Range: ${lower:.2f} — ${upper:.2f}")
            lines.append(f"📏 Step: ${step:.2f}")
            lines.append(f"📋 Nodes: {active}/{total} resting")
            lines.append(f"🔄 Cycles: {cycles}")
            lines.append(f"💰 PnL: ${pnl:+.4f}")
            lines.append("━━━━━━━━━━━━━━━━━━━━")

        message = "\n\n".join(lines)

        await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Grid status error: {e}", exc_info=True)
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Grid status error: {str(e)[:100]}"
            )
        except Exception:
            pass


async def cmd_close_grid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Close a GRID bot. Only touches GRID:: namespaced state — DCA unaffected."""
    if not update.message or not update.message.text:
        return

    parts = update.message.text.split()
    if len(parts) < 2:
        await update.message.reply_text("Usage: <code>/close_grid &lt;ASSET&gt;</code>", parse_mode='HTML')
        return

    asset = parts[1].strip().upper()

    try:
        from core.grid_manager import GridManager, grid_state_key
        # HLExecutor now from app_context

        executor = app_context.executor
        grid = GridManager(executor)
        key = grid_state_key(asset)
        config = state.OPEN_POSITIONS.get(key)

        if not config or not config.get("enabled"):
            await update.message.reply_text(f"❌ No active GRID bot for {asset}")
            return

        await update.message.reply_text(f"🔄 Closing GRID bot for {asset}...")

        result = await grid.close_grid(asset, config)

        # Remove ONLY the grid state key — DCA state untouched
        state.OPEN_POSITIONS.pop(key, None)
        state.save_state()

        msg = (
            f"✅ <b>GRID Closed: {asset}</b>\n\n"
            f"🗑️ Orders cancelled: {result['orders_cancelled']}\n"
            f"🗑️ Positions closed: {result['positions_closed']}\n"
            f"💵 Total PnL: ${result['total_pnl']:+.4f}"
        )
        if result["errors"]:
            msg += f"\n⚠️ Errors: {', '.join(result['errors'][:3])}"

        record_trade("close", asset, "GRID", "CLOSE_ALL", 0, 0,
                     pnl=result["total_pnl"],
                     metadata={"orders_cancelled": result["orders_cancelled"], "positions_closed": result["positions_closed"]})

        clear_grid_state(asset)

        await update.message.reply_text(msg, parse_mode='HTML')

    except Exception as e:
        logger.error(f"❌ Error in cmd_close_grid: {e}")
        await update.message.reply_text(f"💥 Error: {str(e)}")


async def send_grid_alert(message: str) -> None:
    """Send grid event notification to Telegram."""
    try:
        chat_id = getattr(state, 'TELEGRAM_CHAT_ID', None)
        if chat_id:
            await _safe_send_telegram(chat_id, text=message)
    except Exception as e:
        logger.warning(f"⚠️ Failed to send grid alert: {e}")


async def grid_monitor_task():
    """Background task: Monitor reversal grid fills via position snapshot comparison."""
    import asyncio
    import core.state as gs_state
    from core.grid_manager import GridManager, is_grid_position, grid_asset_from_key
    # HLExecutor now from app_context

    logger.info("📋 grid_monitor task loop started")

    while True:
        try:
            await asyncio.sleep(120)

            executor = app_context.executor
            grid_mgr = GridManager(executor)

            for key in list(gs_state.OPEN_POSITIONS.keys()):
                if not is_grid_position(key):
                    continue

                config = gs_state.OPEN_POSITIONS[key]
                if not config.get("enabled", False):
                    continue

                asset = grid_asset_from_key(key)

                sync_result = await grid_mgr.sync_pending_orders(asset, config)
                fills = sync_result.get("fills_detected", 0)
                errors = sync_result.get("errors", [])

                active_nodes = len([n for n in config.get("nodes", []) if n.get("status") == "OPEN"])
                total_nodes = len(config.get("nodes", []))
                cycles = config.get("completed_cycles", 0)
                pnl = config.get("total_realized_pnl", 0.0)

                if fills > 0:
                    logger.info(f"🔲 {asset}: {fills} fills detected | {active_nodes}/{total_nodes} nodes active | Cycles: {cycles} | PnL: ${pnl:+.4f}")

                    alert_msg = (
                        f"🔄 <b>GRID REVERSAL: {asset}</b>\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"📊 Fills: {fills} | Cycles: {cycles}\n"
                        f"💰 Session PnL: ${pnl:+.4f}\n"
                        f"🔢 Active Nodes: {active_nodes}/{total_nodes}\n"
                        f"⏰ {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}"
                    )
                    await send_grid_alert(alert_msg)
                else:
                    logger.info(f"🔲 {asset}: monitoring | {active_nodes}/{total_nodes} nodes resting | Cycles: {cycles} | PnL: ${pnl:+.4f}")

                _cycle_count = config.get("_monitor_cycles", 0) + 1
                config["_monitor_cycles"] = _cycle_count
                if _cycle_count % 15 == 0 and cycles > 0:
                    status_msg = (
                        f"📊 <b>GRID STATUS: {asset}</b>\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"🔢 Nodes: {active_nodes}/{total_nodes} resting\n"
                        f"🔄 Cycles: {cycles} | PnL: ${pnl:+.4f}\n"
                        f"⏰ {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}"
                    )
                    await send_grid_alert(status_msg)

                for err in errors:
                    logger.warning(f"⚠️ Grid monitor {asset}: {err}")

                gs_state.OPEN_POSITIONS[key] = config

                try:
                    save_grid_state(gs_state.OPEN_POSITIONS)
                except Exception as _save_err:
                    logger.warning(f"⚠️ Grid state save failed: {_save_err}")

        except asyncio.CancelledError:
            logger.info("📋 grid_monitor task cancelled")
            break
        except Exception as e:
            logger.error(f"❌ grid_monitor cycle error: {e}", exc_info=True)
            await asyncio.sleep(30)


async def cmd_trade_history(update, context):
    """Display trade history using HTML parse mode."""
    chat_id = update.effective_chat.id
    try:
        from core.trade_ledger import load_history
        history = load_history()

        if not history:
            await context.bot.send_message(chat_id=chat_id, text="📝 No trades recorded yet.")
            return

        lines = ["<b>📝 Trade History (Last 10)</b>", "━━━━━━━━━━━━━━━━━━━━"]

        for trade in history[-10:]:
            t_asset = trade.get("asset", "?")
            t_side = trade.get("side", "?")
            t_size = trade.get("size", 0)
            t_price = trade.get("price", 0)
            t_pnl = trade.get("pnl", 0)
            t_ts = trade.get("timestamp", "")[:19]
            t_strategy = trade.get("strategy", "SIGNAL")

            emoji = "🟢" if t_pnl >= 0 else "🔴"
            lines.append(
                f"{emoji} <b>{t_asset}</b> {t_side} {t_size}\n"
                f"   💲 Price: ${t_price:.4f} | PnL: ${t_pnl:+.4f}\n"
                f"   🏷️ {t_strategy} | ⏰ {t_ts}"
            )
            lines.append("────────────────────")

        message = "\n".join(lines)

        await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Trade history error: {e}", exc_info=True)
        try:
            from core.trade_ledger import load_history as _lh
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Trade history available ({len(_lh())} records). Display error: {str(e)[:100]}"
            )
        except Exception:
            pass
