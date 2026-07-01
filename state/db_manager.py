import psycopg2, os, json
from state.state_manager import state

def get_db_url():
    return os.getenv("DATABASE_URL", "")

def _connect():
    url = get_db_url()
    if not url:
        raise psycopg2.OperationalError("DATABASE_URL not set")
    return psycopg2.connect(url)

def init_db():
    try:
        conn = _connect()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS agent_state (
                key TEXT PRIMARY KEY,
                value JSONB NOT NULL
            );
            CREATE TABLE IF NOT EXISTS trade_log (
                id SERIAL PRIMARY KEY,
                coin TEXT,
                side TEXT,
                size FLOAT,
                price FLOAT,
                pnl FLOAT,
                reason TEXT,
                ts TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        conn.commit()
        conn.close()
        return True
    except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
        print(f"⚠️ Database unavailable – using JSON state. ({e})")
        return False

def save_state():
    try:
        conn = _connect()
        cur = conn.cursor()
        for key, value in state.data.items():
            if key == "state_file": continue
            cur.execute(
                "INSERT INTO agent_state (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
                (key, json.dumps(value, default=str))
            )
        conn.commit()
        conn.close()
    except (psycopg2.OperationalError, psycopg2.InterfaceError):
        # silently fallback to JSON save
        pass

def load_state():
    try:
        conn = _connect()
        cur = conn.cursor()
        cur.execute("SELECT key, value FROM agent_state")
        for key, value in cur.fetchall():
            if key in state.data:
                try:
                    state.data[key] = json.loads(value)
                except:
                    pass
        conn.close()
    except (psycopg2.OperationalError, psycopg2.InterfaceError):
        # fallback to JSON load
        pass

def log_trade(coin, side, size, price, pnl, reason):
    try:
        conn = _connect()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO trade_log (coin, side, size, price, pnl, reason) VALUES (%s,%s,%s,%s,%s,%s)",
            (coin, side, size, price, pnl, reason)
        )
        conn.commit()
        conn.close()
    except (psycopg2.OperationalError, psycopg2.InterfaceError):
        pass
