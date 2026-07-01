"""
Telegram Bot Setup
"""
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from .commands import (
    start_command, positions_command, stats_command,
    close_command, closeall_command, button_callback
)

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str, chat_id: str, bot_instance=None):
        self.token = token
        self.chat_id = chat_id
        self.bot_instance = bot_instance  # Store reference to the main SignalBot
        self.application = None
    
    async def initialize(self):
        """Initialize Telegram bot"""
        self.application = Application.builder().token(self.token).build()
        
        # Link the main bot instance to the application data
        self.application.bot_data['bot'] = self.bot_instance
        
        # Register commands
        self.application.add_handler(CommandHandler("start", start_command))
        self.application.add_handler(CommandHandler("positions", positions_command))
        self.application.add_handler(CommandHandler("stats", stats_command))
        self.application.add_handler(CommandHandler("close", close_command))
        self.application.add_handler(CommandHandler("closeall", closeall_command))
        self.application.add_handler(CallbackQueryHandler(button_callback))
        
        # Clear webhook
        await self.application.bot.delete_webhook(drop_pending_updates=True)
        
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(drop_pending_updates=True)
        
        logger.info(" Telegram bot started and polling.")
    
    async def shutdown(self):
        """Shutdown Telegram bot"""
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info("📱 Telegram bot stopped.")
    
    async def send_message(self, text: str, parse_mode: str = 'Markdown'):
        if self.application and self.chat_id:
            try:
                await self.application.bot.send_message(
                    chat_id=self.chat_id, text=text, parse_mode=parse_mode
                )
            except Exception as e:
                # Handle Telegram rate limits (429)
                if "RetryAfter" in str(e):
                    import re
                    match = re.search(r'RetryAfter\((\d+)\)', str(e))
                    if match:
                        wait = int(match.group(1))
                        logger.warning(f"⏳ Telegram rate limited. Waiting {wait}s...")
                        import asyncio
                        await asyncio.sleep(wait)
                        # Retry once
                        await self.application.bot.send_message(
                            chat_id=self.chat_id, text=text, parse_mode=parse_mode
                        )
                else:
                    logger.error(f"Failed to send Telegram message: {e}")
