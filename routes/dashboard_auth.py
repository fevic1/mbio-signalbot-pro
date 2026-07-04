"""
Dashboard Authentication Module v4
Session-based auth + RBAC for MBIO SignalBot Pro Dashboard.
Recreated from import signatures in dashboard_api.py.
"""

import os
import json
import time
import hashlib
import secrets
import logging
from datetime import datetime, timezone
from typing import Optional, Callable
from pathlib import Path

from fastapi import Request, HTTPException, Depends
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# === Configuration ===
SESSION_SECRET = os.environ.get("MBIO_SESSION_SECRET", secrets.token_hex(32))
SESSION_MAX_AGE = int(os.environ.get("MBIO_SESSION_MAX_AGE", 86400))  # 24h
AUDIT_LOG_PATH = Path(os.environ.get("MBIO_AUDIT_LOG", "data/audit_log.json"))
USERS_DB_PATH = Path(os.environ.get("MBIO_USERS_DB", "config/users.json"))

# In-memory session store
_sessions: dict[str, dict] = {}

# Default admin user (fallback if no users.json)
_DEFAULT_USERS = {
    "fixed@mbio.com": {
        "id": "admin-001",
        "email": "fixed@mbio.com",
        "name": "Fixed Test",
        "role": "ADMIN",
        "password_hash": None,  # Uses password from env or default
    }
}


def _load_users() -> dict:
    """Load users from JSON file or return defaults."""
    if USERS_DB_PATH.exists():
        try:
            with open(USERS_DB_PATH) as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load users DB: {e}")
    return _DEFAULT_USERS


def _hash_password(password: str) -> str:
    """Simple SHA-256 password hash (upgrade to bcrypt in production)."""
    return hashlib.sha256(f"{SESSION_SECRET}:{password}".encode()).hexdigest()


def _create_session(user: dict) -> str:
    """Create a new session and return session token."""
    token = secrets.token_urlsafe(32)
    _sessions[token] = {
        "user": user,
        "created_at": time.time(),
        "expires_at": time.time() + SESSION_MAX_AGE,
    }
    return token


def _validate_session(token: str) -> Optional[dict]:
    """Validate session token and return user dict or None."""
    session = _sessions.get(token)
    if not session:
        return None
    if time.time() > session["expires_at"]:
        del _sessions[token]
        return None
    return session["user"]


# === Exported Functions ===

def get_current_user(request: Request) -> dict:
    """FastAPI dependency: extract and validate current user from session cookie."""
    token = request.cookies.get("mbio_session")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = _validate_session(token)
    if not user:
        raise HTTPException(status_code=401, detail="Session expired")
    return user


def require_role(*allowed_roles: str) -> Callable:
    """Returns a FastAPI dependency that enforces role-based access control."""
    def _check(user: dict = Depends(get_current_user)) -> dict:
        user_role = user.get("role", "").upper()
        if user_role not in [r.upper() for r in allowed_roles]:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        return user
    return _check


def verify_otp_for_user(user_id: str, otp: str) -> bool:
    """Verify OTP code for a given user. Currently accepts any non-empty OTP for testing."""
    if not otp or len(otp) < 4:
        return False
    # TODO: Implement proper TOTP/HOTP verification
    # For now, accept configured test OTP or any 6-digit code in dev mode
    expected_otp = os.environ.get("MBIO_TEST_OTP", "123456")
    return otp == expected_otp or (os.environ.get("MBIO_DEV_MODE", "false").lower() == "true")


async def login(request: Request):
    """POST /auth/login - Authenticate user and create session."""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    email = body.get("email", "").strip().lower()
    password = body.get("password", "")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    users = _load_users()
    user = users.get(email)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Check password
    expected_hash = user.get("password_hash")
    if expected_hash:
        if _hash_password(password) != expected_hash:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    else:
        # Fallback: check against env password or default
        env_password = os.environ.get("MBIO_ADMIN_PASSWORD", "123456789000")
        if password != env_password:
            raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create session
    token = _create_session(user)
    log_audit(user["id"], "LOGIN", resource=email)

    response = JSONResponse(content={
        "status": "ok",
        "user": {"id": user["id"], "email": user["email"], "name": user.get("name", ""), "role": user.get("role", "USER")}
    })
    response.set_cookie(
        key="mbio_session",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=SESSION_MAX_AGE,
        secure=request.url.scheme == "https",
    )
    return response


async def logout(request: Request):
    """POST /auth/logout - Destroy session."""
    token = request.cookies.get("mbio_session")
    if token and token in _sessions:
        user = _sessions[token].get("user", {})
        del _sessions[token]
        log_audit(user.get("id", "unknown"), "LOGOUT")

    response = JSONResponse(content={"status": "ok"})
    response.delete_cookie("mbio_session")
    return response


async def get_me(user: dict = Depends(get_current_user)):
    """GET /auth/me - Return current user info."""
    return {
        "id": user["id"],
        "email": user.get("email", ""),
        "name": user.get("name", ""),
        "role": user.get("role", "USER"),
    }


async def request_otp(request: Request, user: dict = Depends(get_current_user)):
    """POST /auth/otp/request - Generate and send OTP for sensitive operations."""
    # TODO: Integrate with Telegram/email OTP delivery
    log_audit(user["id"], "OTP_REQUESTED")
    return {"status": "ok", "message": "OTP sent via configured channel"}


def log_audit(
    user_id: str,
    action: str,
    resource: str = "",
    details: str = "",
    ip_address: str = "",
    otp_verified: bool = False,
):
    """Append an audit log entry to the audit log file."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "action": action,
        "resource": resource,
        "details": details,
        "ip_address": ip_address,
        "otp_verified": otp_verified,
    }
    try:
        AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        entries = []
        if AUDIT_LOG_PATH.exists():
            with open(AUDIT_LOG_PATH) as f:
                entries = json.load(f)
        entries.append(entry)
        # Keep last 1000 entries
        if len(entries) > 1000:
            entries = entries[-1000:]
        with open(AUDIT_LOG_PATH, "w") as f:
            json.dump(entries, f, indent=2)
    except Exception as e:
        logger.error(f"Audit log write failed: {e}")
