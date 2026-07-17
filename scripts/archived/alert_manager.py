import os
import logging
from telegram import Bot
import asyncio

logger = logging.getLogger(__name__)

_bot = None

def _get_bot():
    global _bot
    if _bot is None:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            logger.warning("TELEGRAM_BOT_TOKEN not set")
            return None
        _bot = Bot(token=token)
    return _bot

async def send_trade_alert(symbol: str, side: str, entry: float, size: float, order_id: str = None):
    """Send Telegram alert when a trade is executed."""
    bot = _get_bot()
    if not bot:
        return
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not chat_id:
        logger.warning("TELEGRAM_CHAT_ID not set")
        return
    notional = entry * size
    msg = (
        f"🟢 *TRADE EXECUTED*\n"
        f"Symbol: {symbol}\n"
        f"Side: {side}\n"
        f"Entry: ${entry:.4f}\n"
        f"Size: {size:.4f}\n"
        f"Notional: ${notional:.2f}"
    )
    if order_id:
        msg += f"\nOrder ID: {order_id}"
    await bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")

# Keep existing functions from the original alert_manager.py if any
# (e.g., send_alert, etc.) – but we'll just add the trade alert.
