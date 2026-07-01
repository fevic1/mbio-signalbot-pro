"""
Telegram Command Handlers - FIXED: Authorization checks
"""
import logging
import asyncio
import os
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# FIXED: Authorization guard
ALLOWED_CHAT_IDS = {int(os.getenv("TELEGRAM_CHAT_ID", "0"))}

def authorized(func):
    """Decorator to check if user is authorized"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.id not in ALLOWED_CHAT_IDS:
            logger.warning(f"🚫 Unauthorized access attempt from chat {update.effective_chat.id}")
            return  # Silent reject
        return await func(update, context)
    return wrapper

@authorized
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 *MBIO SignalBot v9.0 Active*\n\n"
        "Use /positions to view open trades.\n"
        "Use /stats to view performance.\n"
        "Use /close <ASSET> to close a position.\n"
        "Use /closeall to emergency close all.", 
        parse_mode='Markdown'
    )

@authorized
async def positions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.application.bot_data.get('bot')
    if not bot:
        await update.message.reply_text("❌ Bot instance not linked.")
        return
    
    tracker = bot.position_tracker
    positions = tracker.open_positions
    
    if not positions:
        await update.message.reply_text("📊 No open positions currently.")
        return

    msg = "📊 *Open Positions:*\n\n"
    for asset, pos in positions.items():
        msg += (f"• *{asset}* ({pos['side']})\n"
                f"  Entry: ${pos['entry']:,.4f} | Size: {pos['size']}\n"
                f"  SL: ${pos['sl']:,.4f} | TP1: ${pos['tp1']:,.4f}\n\n")
    
    await update.message.reply_text(msg, parse_mode='Markdown')

@authorized
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.application.bot_data.get('bot')
    if not bot: return
    
    risk = bot.risk_manager
    tracker = bot.position_tracker
    
    msg = (f"📊 *Performance Stats*\n\n"
           f"📈 Daily PnL: {risk.daily_pnl:+.2f}%\n"
           f"🔓 Open Positions: {len(tracker.open_positions)}/{risk.max_positions}\n"
           f"🛡️ Daily Limit: {risk.daily_loss_limit}%")
    
    await update.message.reply_text(msg, parse_mode='Markdown')

@authorized
async def close_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.application.bot_data.get('bot')
    if not bot or not context.args:
        await update.message.reply_text("Usage: /close <ASSET> (e.g., /close BTC)")
        return
    
    asset = context.args[0].upper()
    tracker = bot.position_tracker
    
    if asset not in tracker.open_positions:
        await update.message.reply_text(f"❌ No open position for {asset}")
        return
    
    pos = tracker.open_positions[asset]
    
    try:
        success = await asyncio.to_thread(
            bot.executor.close_position, asset, pos['side'], pos['size']
        )
        
        if success:
            await update.message.reply_text(f"✅ Successfully closed {asset}")
            tracker.remove_position(asset)
        else:
            await update.message.reply_text(f"❌ Failed to close {asset}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error closing {asset}: {e}")

@authorized
async def closeall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.application.bot_data.get('bot')
    if not bot: return
    
    tracker = bot.position_tracker
    if not tracker.open_positions:
        await update.message.reply_text("📊 No open positions to close.")
        return
    
    await update.message.reply_text(f"🚨 Closing all {len(tracker.open_positions)} positions...")
    
    for asset in list(tracker.open_positions.keys()):
        pos = tracker.open_positions[asset]
        try:
            await asyncio.to_thread(bot.executor.close_position, asset, pos['side'], pos['size'])
            tracker.remove_position(asset)
        except Exception as e:
            logger.error(f"Failed to close {asset}: {e}")
    
    await update.message.reply_text("✅ All positions closed.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"Action processed: {query.data}")
