from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes

async def cmd_positions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all open positions"""
    # Import from main module
    from trading_signal_bot import OPEN_POSITIONS, ASSETS, HYPERLIQUID_ASSETS, get_current_price
    
    if not OPEN_POSITIONS:
        await update.message.reply_text("📭 No open positions")
        return
    
    msg = "📊 *Open Positions*\n──────────────────\n"
    
    for asset, pos in OPEN_POSITIONS.items():
        side = pos.get("side", "LONG")
        entry = pos.get("entry", 0)
        size = pos.get("size", 0)
        sl = pos.get("sl", 0)
        tp1 = pos.get("tp1", 0)
        tp2 = pos.get("tp2", 0)
        tp3 = pos.get("tp3", 0)
        
        ticker = ASSETS.get(asset, f"{asset}-USD")
        try:
            current = get_current_price(ticker)
            if side == "BUY":
                pnl = (current - entry) * size
                pnl_pct = ((current - entry) / entry) * 100
            else:
                pnl = (entry - current) * size
                pnl_pct = ((entry - current) / entry) * 100
        except:
            current = 0
            pnl = 0
            pnl_pct = 0
        
        pnl_emoji = "🟢" if pnl > 0 else "🔴"
        
        msg += f"\n*{asset}* {side}\n"
        msg += f"Size: {size} | Entry: ${entry:,.2f}\n"
        msg += f"Current: ${current:,.2f}\n"
        msg += f"{pnl_emoji} PnL: ${pnl:+,.2f} ({pnl_pct:+.2f}%)\n"
        msg += f"SL: ${sl:,.2f} | TP1: ${tp1:,.2f}\n"
        msg += f"TP2: ${tp2:,.2f} | TP3: ${tp3:,.2f}\n"
        msg += "──────────────────\n"
    
    keyboard = []
    for asset in OPEN_POSITIONS.keys():
        keyboard.append([InlineKeyboardButton(f"❌ Close {asset}", callback_data=f"close_{asset}")])
    keyboard.append([InlineKeyboardButton("❌ Close All", callback_data="close_all")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=reply_markup)

async def cmd_close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Close a specific position"""
    from trading_signal_bot import OPEN_POSITIONS, HYPERLIQUID_ASSETS
    from execution.hl_executor import execute_hl_order
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /close <ASSET>\nExample: /close BTC")
        return
    
    asset = context.args[0].upper()
    
    if asset not in OPEN_POSITIONS:
        await update.message.reply_text(f"❌ No open position for {asset}")
        return
    
    pos = OPEN_POSITIONS[asset]
    side = "SELL" if pos["side"] == "BUY" else "BUY"
    
    try:
        order_result = execute_hl_order(
            coin=HYPERLIQUID_ASSETS.get(asset, asset),
            side=side,
            size=pos["size"]
        )
        
        if order_result.get("status") == "success":
            del OPEN_POSITIONS[asset]
            await update.message.reply_text(f"✅ {asset} position closed!")
        else:
            error = order_result.get("reason", "Unknown error")
            await update.message.reply_text(f"❌ Failed: {error}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def cmd_closeall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Close all positions"""
    from trading_signal_bot import OPEN_POSITIONS, HYPERLIQUID_ASSETS
    from execution.hl_executor import execute_hl_order
    
    if not OPEN_POSITIONS:
        await update.message.reply_text("📭 No open positions")
        return
    
    count = len(OPEN_POSITIONS)
    await update.message.reply_text(f"⏳ Closing {count} position(s)...")
    
    closed = 0
    for asset in list(OPEN_POSITIONS.keys()):
        pos = OPEN_POSITIONS[asset]
        side = "SELL" if pos["side"] == "BUY" else "BUY"
        try:
            order_result = execute_hl_order(
                coin=HYPERLIQUID_ASSETS.get(asset, asset),
                side=side,
                size=pos["size"]
            )
            if order_result.get("status") == "success":
                closed += 1
                del OPEN_POSITIONS[asset]
        except:
            pass
    
    await update.message.reply_text(f"✅ Closed {closed}/{count} positions")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button callbacks"""
    from trading_signal_bot import OPEN_POSITIONS, HYPERLIQUID_ASSETS
    from execution.hl_executor import execute_hl_order
    
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "close_all":
        if not OPEN_POSITIONS:
            await query.edit_message_text("📭 No open positions")
            return
        
        count = len(OPEN_POSITIONS)
        closed = 0
        for asset in list(OPEN_POSITIONS.keys()):
            pos = OPEN_POSITIONS[asset]
            side = "SELL" if pos["side"] == "BUY" else "BUY"
            try:
                order_result = execute_hl_order(
                    coin=HYPERLIQUID_ASSETS.get(asset, asset),
                    side=side,
                    size=pos["size"]
                )
                if order_result.get("status") == "success":
                    closed += 1
                    del OPEN_POSITIONS[asset]
            except:
                pass
        
        await query.message.reply_text(f"✅ Closed {closed}/{count} positions")
    
    elif data.startswith("close_"):
        asset = data.replace("close_", "")
        if asset not in OPEN_POSITIONS:
            await query.edit_message_text(f"❌ No position for {asset}")
            return
        
        pos = OPEN_POSITIONS[asset]
        side = "SELL" if pos["side"] == "BUY" else "BUY"
        
        try:
            order_result = execute_hl_order(
                coin=HYPERLIQUID_ASSETS.get(asset, asset),
                side=side,
                size=pos["size"]
            )
            if order_result.get("status") == "success":
                del OPEN_POSITIONS[asset]
                await query.edit_message_text(f"✅ {asset} closed!")
            else:
                await query.edit_message_text(f" Failed: {order_result.get('reason', 'Unknown')}")
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {str(e)}")
