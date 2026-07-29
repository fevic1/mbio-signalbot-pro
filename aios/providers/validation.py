
def valid_secret(value):

    if not value:
        return False

    value = value.strip().lower()

    blocked = {
        "your_key",
        "changeme",
        "example",
        "test",
        "none",
        "null",
    }

    return value not in blocked
