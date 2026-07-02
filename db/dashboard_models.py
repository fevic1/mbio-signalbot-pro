"""
Institutional-grade dashboard authentication models.
SQLite schema for users, sessions, and audit log.
Includes CLI tool for creating/managing users securely.
"""
import sqlite3
import os
import sys
import uuid
import hashlib
import secrets
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "dashboard.db")


def get_dashboard_db() -> sqlite3.Connection:
    """Get connection to dashboard database. Creates tables if missing."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    _ensure_tables(conn)
    return conn


def _ensure_tables(conn: sqlite3.Connection):
    """Create tables if they don't exist."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS dashboard_users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            role TEXT NOT NULL DEFAULT 'VIEWER',
            telegram_chat_id TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS dashboard_sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            expires_at TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES dashboard_users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS dashboard_audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            action TEXT NOT NULL,
            resource TEXT,
            details TEXT,
            ip_address TEXT,
            otp_verified INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES dashboard_users(id)
        );

        CREATE INDEX IF NOT EXISTS idx_sessions_user ON dashboard_sessions(user_id);
        CREATE INDEX IF NOT EXISTS idx_sessions_expires ON dashboard_sessions(expires_at);
        CREATE INDEX IF NOT EXISTS idx_audit_user ON dashboard_audit_log(user_id);
        CREATE INDEX IF NOT EXISTS idx_audit_created ON dashboard_audit_log(created_at);
    """)
    conn.commit()


# --- Password Hashing ---

def hash_password(password: str) -> str:
    """Hash password with bcrypt. Falls back to SHA-256+salt if bcrypt unavailable."""
    try:
        import bcrypt
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()
    except ImportError:
        salt = secrets.token_hex(16)
        h = hashlib.sha256((salt + password).encode()).hexdigest()
        return f"sha256${salt}${h}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    try:
        import bcrypt
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ImportError:
        if not hashed.startswith("sha256$"):
            return False
        parts = hashed.split("$")
        if len(parts) != 3:
            return False
        salt, expected = parts[1], parts[2]
        actual = hashlib.sha256((salt + password).encode()).hexdigest()
        return secrets.compare_digest(actual, expected)


# --- User CRUD ---

def create_user(email: str, password: str, first_name: str = "",
                last_name: str = "", role: str = "VIEWER",
                telegram_chat_id: str = "") -> dict:
    """Create a new dashboard user. Returns user dict (no password)."""
    conn = get_dashboard_db()
    try:
        user_id = str(uuid.uuid4())
        pw_hash = hash_password(password)
        conn.execute(
            "INSERT INTO dashboard_users (id, email, password_hash, first_name, last_name, role, telegram_chat_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, email.lower().strip(), pw_hash, first_name, last_name, role.upper(), telegram_chat_id)
        )
        conn.commit()
        logger.info(f"Dashboard user created: {email} (role={role})")
        return {"id": user_id, "email": email, "role": role, "first_name": first_name, "last_name": last_name}
    except sqlite3.IntegrityError:
        raise ValueError(f"User with email {email} already exists")
    finally:
        conn.close()


def get_user_by_email(email: str) -> Optional[dict]:
    """Lookup user by email. Returns None if not found or inactive."""
    conn = get_dashboard_db()
    try:
        row = conn.execute(
            "SELECT * FROM dashboard_users WHERE email = ? AND is_active = 1",
            (email.lower().strip(),)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def authenticate_user(email: str, password: str) -> Optional[dict]:
    """Authenticate user. Returns user dict (without password_hash) or None."""
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    safe = {k: v for k, v in user.items() if k != "password_hash"}
    return safe


# --- Session Management ---

def create_session(user_id: str, ip_address: str = "", user_agent: str = "",
                   ttl_hours: int = 8) -> str:
    """Create server-side session. Returns session token."""
    session_id = secrets.token_urlsafe(64)
    expires = (datetime.now(timezone.utc) + timedelta(hours=ttl_hours)).isoformat()
    conn = get_dashboard_db()
    try:
        conn.execute(
            "INSERT INTO dashboard_sessions (session_id, user_id, ip_address, user_agent, expires_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (session_id, user_id, ip_address, user_agent, expires)
        )
        conn.commit()
        return session_id
    finally:
        conn.close()


def validate_session(session_id: str) -> Optional[dict]:
    """Validate session. Returns user dict or None if expired/invalid."""
    conn = get_dashboard_db()
    try:
        row = conn.execute("""
            SELECT u.* FROM dashboard_users u
            JOIN dashboard_sessions s ON s.user_id = u.id
            WHERE s.session_id = ? AND s.expires_at > datetime('now') AND u.is_active = 1
        """, (session_id,)).fetchone()
        if not row:
            return None
        user = dict(row)
        return {k: v for k, v in user.items() if k != "password_hash"}
    finally:
        conn.close()


def destroy_session(session_id: str):
    """Delete session (logout)."""
    conn = get_dashboard_db()
    try:
        conn.execute("DELETE FROM dashboard_sessions WHERE session_id = ?", (session_id,))
        conn.commit()
    finally:
        conn.close()


def cleanup_expired_sessions():
    """Remove expired sessions. Call periodically."""
    conn = get_dashboard_db()
    try:
        conn.execute("DELETE FROM dashboard_sessions WHERE expires_at < datetime('now')")
        conn.commit()
    finally:
        conn.close()


# --- Audit Logging ---

def log_audit(user_id: str, action: str, resource: str = "",
              details: str = "", ip_address: str = "", otp_verified: bool = False):
    """Log an auditable action."""
    conn = get_dashboard_db()
    try:
        conn.execute(
            "INSERT INTO dashboard_audit_log (user_id, action, resource, details, ip_address, otp_verified) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, action, resource, details, ip_address, 1 if otp_verified else 0)
        )
        conn.commit()
    finally:
        conn.close()




def log_trade_action(user_id: str, action: str, asset: str = "",
                     params: dict = None, ip_address: str = "",
                     otp_verified: bool = False, error: str = ""):
    """Convenience wrapper for logging trade-related audit events.
    Automatically serializes params to JSON. Never raises."""
    import json as _json
    details = ""
    if error:
        details = _json.dumps({"error": error[:500]})
    elif params:
        try:
            details = _json.dumps(params, default=str)[:1000]
        except Exception:
            details = str(params)[:500]
    try:
        log_audit(
            user_id=user_id,
            action=action,
            resource=asset,
            details=details,
            ip_address=ip_address,
            otp_verified=otp_verified,
        )
    except Exception as e:
        logger.error(f"Audit log failed for {action}/{asset}: {e}")



def query_audit_log(limit: int = 100, offset: int = 0, action: str = "",
                    user_id: str = "", search: str = "", days: int = 90) -> tuple:
    """Query audit log with filters. Returns (entries, total_count). Never raises."""
    try:
        conn = get_dashboard_db()
        conditions = [f"created_at > datetime('now', '-{days} days')"]
        params = []
        if action:
            conditions.append("action LIKE ?")
            params.append(f"%{action}%")
        if user_id:
            conditions.append("user_id = ?")
            params.append(user_id)
        if search:
            conditions.append("(resource LIKE ? OR details LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])
        where = " AND ".join(conditions)
        rows = conn.execute(
            f"SELECT * FROM dashboard_audit_log WHERE {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
            params + [limit, offset]
        ).fetchall()
        total = conn.execute(
            f"SELECT COUNT(*) as cnt FROM dashboard_audit_log WHERE {where}", params
        ).fetchone()["cnt"]
        conn.close()
        return [dict(r) for r in rows], total
    except Exception as e:
        logger.error(f"Audit query failed: {e}")
        return [], 0

# --- CLI Tool ---

def cli_main():
    """Command-line interface for user management."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m db.dashboard_models create <email> <role> [first_name] [last_name] [telegram_chat_id]")
        print("  python -m db.dashboard_models list")
        print("  python -m db.dashboard_models deactivate <email>")
        print("  python -m db.dashboard_models set-password <email>")
        print("  python -m db.dashboard_models set-role <email> <role>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "create":
        if len(sys.argv) < 4:
            print("Usage: create <email> <role> [first_name] [last_name] [telegram_chat_id]")
            sys.exit(1)
        email = sys.argv[2]
        role = sys.argv[3].upper()
        first_name = sys.argv[4] if len(sys.argv) > 4 else ""
        last_name = sys.argv[5] if len(sys.argv) > 5 else ""
        tg_chat = sys.argv[6] if len(sys.argv) > 6 else ""

        import getpass
        password = getpass.getpass(f"Password for {email}: ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Passwords do not match")
            sys.exit(1)
        if len(password) < 12:
            print("Password must be at least 12 characters")
            sys.exit(1)

        try:
            user = create_user(email, password, first_name, last_name, role, tg_chat)
            print(f"User created: {user['email']} (role={user['role']}, id={user['id']})")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif cmd == "list":
        conn = get_dashboard_db()
        rows = conn.execute(
            "SELECT id, email, first_name, last_name, role, is_active, created_at "
            "FROM dashboard_users ORDER BY created_at"
        ).fetchall()
        conn.close()
        if not rows:
            print("No users found.")
        else:
            print(f"{'Email':<30} {'Name':<20} {'Role':<10} {'Active':<7} {'Created'}")
            print("-" * 90)
            for r in rows:
                name = f"{r['first_name']} {r['last_name']}".strip() or "-"
                active = "Yes" if r["is_active"] else "No"
                print(f"{r['email']:<30} {name:<20} {r['role']:<10} {active:<7} {r['created_at']}")

    elif cmd == "set-password":
        if len(sys.argv) < 3:
            print("Usage: set-password <email>")
            sys.exit(1)
        email = sys.argv[2]
        user = get_user_by_email(email)
        if not user:
            print(f"User {email} not found")
            sys.exit(1)
        import getpass
        password = getpass.getpass(f"New password for {email}: ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Passwords do not match")
            sys.exit(1)
        if len(password) < 12:
            print("Password must be at least 12 characters")
            sys.exit(1)
        conn = get_dashboard_db()
        conn.execute(
            "UPDATE dashboard_users SET password_hash = ?, updated_at = datetime('now') WHERE email = ?",
            (hash_password(password), email.lower().strip())
        )
        conn.commit()
        conn.close()
        print(f"Password updated for {email}")

    elif cmd == "deactivate":
        if len(sys.argv) < 3:
            print("Usage: deactivate <email>")
            sys.exit(1)
        email = sys.argv[2]
        conn = get_dashboard_db()
        conn.execute(
            "UPDATE dashboard_users SET is_active = 0, updated_at = datetime('now') WHERE email = ?",
            (email.lower().strip(),)
        )
        conn.commit()
        conn.close()
        print(f"User {email} deactivated")

    elif cmd == "set-role":
        if len(sys.argv) < 4:
            print("Usage: set-role <email> <role>")
            sys.exit(1)
        email = sys.argv[2]
        role = sys.argv[3].upper()
        if role not in ("ADMIN", "OPERATOR", "VIEWER"):
            print(f"Invalid role: {role}. Must be ADMIN, OPERATOR, or VIEWER")
            sys.exit(1)
        conn = get_dashboard_db()
        conn.execute(
            "UPDATE dashboard_users SET role = ?, updated_at = datetime('now') WHERE email = ?",
            (role, email.lower().strip())
        )
        conn.commit()
        conn.close()
        print(f"Role updated for {email}: {role}")

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
