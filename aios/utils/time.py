from datetime import datetime, timezone


def utc_now():
    return datetime.now(timezone.utc)


def utc_iso():
    return utc_now().isoformat()
