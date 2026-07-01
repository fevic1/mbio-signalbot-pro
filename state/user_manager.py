"""
state/user_manager.py — Multi-user credential management (ADDITIVE MODULE)
Does not modify or depend on existing db_manager.py or single-user flow.
"""
import os
import sqlite3
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# Encryption: Load key from env (generate once with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
_ENCRYPTION_KEY = os.getenv("USER_DATA_ENCRYPTION_KEY", "").encode()
_cipher = None
if _ENCRYPTION_KEY and len(_ENCRYPTION_KEY) == 44:  # Fernet key length
    try:
        from cryptography.fernet import Fernet
        _cipher = Fernet(_ENCRYPTION_KEY)
        logger.info("✅ User data encryption enabled")
    except ImportError:
        logger.warning("⚠️ cryptography library not installed — user keys will be stored in plaintext (NOT RECOMMENDED FOR PRODUCTION)")
        _cipher = None
elif _ENCRYPTION_KEY:
    logger.error("❌ Invalid USER_DATA_ENCRYPTION_KEY format — encryption disabled")
    _cipher = None
else:
    logger.warning("⚠️ USER_DATA_ENCRYPTION_KEY not set — user keys will be stored in plaintext (NOT RECOMMENDED FOR PRODUCTION)")

_DB_PATH = os.getenv("USER_DB_PATH", "data/users.db")

def _get_conn() -> sqlite3.Connection:
    """Get SQLite connection for user data."""
    return sqlite3.connect(_DB_PATH)

def init_user_db() -> bool:
    """Create users table if not exists. Safe to call multiple times."""
    try:
        conn = _get_conn()
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                chat_id INTEGER PRIMARY KEY,
                hl_public_key TEXT NOT NULL,
                hl_encrypted_private_key TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("✅ User database initialized")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to init user DB: {e}")
        return False

def register_user(chat_id: int, public_key: str, private_key: str) -> bool:
    """
    Register a new user with encrypted Hyperliquid keys.
    
    Args:
        chat_id: Telegram chat ID (unique user identifier)
        public_key: Hyperliquid public address (for display)
        private_key: Hyperliquid private key (will be encrypted before storage)
    
    Returns:
        bool: True if registration succeeded, False otherwise
    """
    if not _cipher:
        # Fallback: store plaintext (WARNING: not secure)
        encrypted_key = private_key
        logger.warning(f"⚠️ Storing private key in plaintext for chat_id={chat_id} (encryption disabled)")
    else:
        try:
            encrypted_key = _cipher.encrypt(private_key.encode()).decode()
        except Exception as e:
            logger.error(f"❌ Encryption failed for chat_id={chat_id}: {e}")
            return False
    
    conn = _get_conn()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT OR REPLACE INTO users (chat_id, hl_public_key, hl_encrypted_private_key, status, last_active) VALUES (?, ?, ?, 'active', CURRENT_TIMESTAMP)",
            (chat_id, public_key, encrypted_key)
        )
        conn.commit()
        logger.info(f"✅ User registered: chat_id={chat_id}, public_key={public_key[:10]}...")
        return True
    except Exception as e:
        logger.error(f"❌ Registration failed for chat_id={chat_id}: {e}")
        return False
    finally:
        conn.close()

def get_user_keys(chat_id: int) -> Optional[Dict[str, str]]:
    """
    Retrieve and decrypt a user's Hyperliquid keys.
    
    Args:
        chat_id: Telegram chat ID
    
    Returns:
        dict with 'public_key' and 'private_key' if found and active, None otherwise
    """
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT hl_public_key, hl_encrypted_private_key, status FROM users WHERE chat_id = ?", (chat_id,))
    row = c.fetchone()
    conn.close()
    
    if not row or row[2] != 'active':
        return None
    
    public_key = row[0]
    encrypted_key = row[1]
    
    if not _cipher:
        # Fallback: key is stored plaintext
        private_key = encrypted_key
        logger.warning(f"⚠️ Retrieving plaintext private key for chat_id={chat_id} (encryption disabled)")
    else:
        try:
            private_key = _cipher.decrypt(encrypted_key.encode()).decode()
        except Exception as e:
            logger.error(f"❌ Decryption failed for chat_id={chat_id}: {e}")
            return None
    
    return {
        "public_key": public_key,
        "private_key": private_key
    }

def update_user_activity(chat_id: int) -> bool:
    """Update last_active timestamp for a user."""
    conn = _get_conn()
    c = conn.cursor()
    try:
        c.execute("UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE chat_id = ?", (chat_id,))
        conn.commit()
        return c.rowcount > 0
    except Exception as e:
        logger.error(f"❌ Failed to update activity for chat_id={chat_id}: {e}")
        return False
    finally:
        conn.close()

def deactivate_user(chat_id: int) -> bool:
    """Deactivate a user (soft delete)."""
    conn = _get_conn()
    c = conn.cursor()
    try:
        c.execute("UPDATE users SET status = 'inactive', last_active = CURRENT_TIMESTAMP WHERE chat_id = ?", (chat_id,))
        conn.commit()
        return c.rowcount > 0
    except Exception as e:
        logger.error(f"❌ Failed to deactivate chat_id={chat_id}: {e}")
        return False
    finally:
        conn.close()
