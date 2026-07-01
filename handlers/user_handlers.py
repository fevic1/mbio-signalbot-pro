"""
handlers/user_handlers.py — Multi-user Telegram commands (ADDITIVE)
Does not modify existing bot behavior. Safe to add/remove.
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from state.user_manager import register_user

logger = logging.getLogger(__name__)

async def cmd_connect(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /connect <private_key> — Register a Hyperliquid wallet for this Telegram user.
    """
    chat_id = update.effective_chat.id
    user = update.effective_user.username or update.effective_user.first_name
    
    if not context.args:
        await update.message.reply_text(
            "❌ Usage: `/connect <your_private_key>`\n"
            "⚠️ Never share your key publicly. This command is processed securely.",
            parse_mode="Markdown"
        )
        return
    
    private_key = context.args[0].strip()
    
    # Basic validation
    if not private_key.startswith("0x") or len(private_key) != 66:
        await update.message.reply_text(
            " Invalid private key format.\n"
            "Must start with `0x` and be exactly 66 characters long."
        )
        return
    
    try:
        # Validate key by deriving public address
        from hyperliquid.utils.signing import Account
        account = Account.from_key(private_key)
        public_key = account.address
        
        # Register user in database
        if register_user(chat_id, public_key, private_key):
            masked_key = f"{public_key[:8]}...{public_key[-6:]}"
            await update.message.reply_text(
                f"✅ *Wallet Connected*\n"
                f"👤 User: `{user}`\n"
                f"🔑 Address: `{masked_key}`\n"
                f"💡 Use `/status` to check balance and `/positions` to manage trades.",
                parse_mode="Markdown"
            )
            logger.info(f"✅ User {chat_id} ({user}) connected wallet {masked_key}")
        else:
            await update.message.reply_text("❌ Registration failed. Please try again or contact support.")
            
    except Exception as e:
        logger.error(f"❌ Connect failed for chat_id={chat_id}: {e}")
        await update.message.reply_text(f" Error: {str(e)}")
