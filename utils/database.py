import sqlite3
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def init_db():
    """Create the open_positions table"""
    try:
        conn = sqlite3.connect('signals.db')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS open_positions (
                asset TEXT PRIMARY KEY,
                side TEXT NOT NULL,
                entry REAL NOT NULL,
                size REAL NOT NULL,
                sl REAL NOT NULL,
                tp1 REAL NOT NULL,
                tp2 REAL NOT NULL,
                tp3 REAL NOT NULL,
                order_id TEXT,
                opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ DB init failed: {e}")

def save_position_to_db(asset: str, position: Dict[str, Any]):
    try:
        conn = sqlite3.connect('signals.db')
        conn.execute("""
            INSERT OR REPLACE INTO open_positions 
            (asset, side, entry, size, sl, tp1, tp2, tp3, order_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            asset, position['side'], position['entry'], position['size'],
            position['sl'], position['tp1'], position['tp2'], position['tp3'],
            position.get('order_id', '')
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"❌ DB save failed: {e}")

def restore_open_positions() -> Dict[str, Dict[str, Any]]:
    positions = {}
    try:
        conn = sqlite3.connect('signals.db')
        rows = conn.execute("""
            SELECT asset, side, entry, size, sl, tp1, tp2, tp3, order_id
            FROM open_positions
        """).fetchall()
        conn.close()
        
        for row in rows:
            asset, side, entry, size, sl, tp1, tp2, tp3, order_id = row
            positions[asset] = {
                "side": side, "entry": entry, "size": size,
                "sl": sl, "tp1": tp1, "tp2": tp2, "tp3": tp3,
                "order_id": order_id, "tp1_hit": False, "tp2_hit": False
            }
        if positions:
            logger.info(f"🔄 Restored {len(positions)} positions from DB")
    except Exception as e:
        logger.error(f"❌ DB restore failed: {e}")
    return positions

def mark_position_closed(asset: str):
    try:
        conn = sqlite3.connect('signals.db')
        conn.execute("DELETE FROM open_positions WHERE asset=?", (asset,))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"❌ DB close failed: {e}")
