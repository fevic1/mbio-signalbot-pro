import logging
import sqlite3
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
_DB_PATH = "signals.db"

def init_db() -> None:
    conn = sqlite3.connect(_DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, asset TEXT,
        signal TEXT, entry_price REAL, sl_price REAL, tp1_price REAL,
        tp2_price REAL, tp3_price REAL, status TEXT, exit_price REAL,
        closed_at TEXT, tp_hit TEXT
    )""")
    conn.commit()
    conn.close()
    logger.info("✅ Database initialised")

def save_signal(asset: str, signal: str, entry: float, sl: float, tp1: float, tp2: float, tp3: float) -> None:
    try:
        conn = sqlite3.connect(_DB_PATH)
        conn.execute("INSERT INTO signals (timestamp,asset,signal,entry_price,sl_price,tp1_price,tp2_price,tp3_price,status) VALUES (?,?,?,?,?,?,?,?,?)",
            (datetime.now(timezone.utc).isoformat(), asset, signal, entry, sl, tp1, tp2, tp3, "open"))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"DB save failed: {e}")
