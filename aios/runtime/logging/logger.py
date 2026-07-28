from datetime import datetime, timezone


class RuntimeLogger:

    def __init__(self):
        self._entries = []

    def log(self, level: str, message: str, metadata=None):
        entry = {
            "level": level,
            "message": message,
            "metadata": metadata or {},
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        self._entries.append(entry)
        return entry

    def info(self, message, metadata=None):
        return self.log(
            "info",
            message,
            metadata,
        )

    def warning(self, message, metadata=None):
        return self.log(
            "warning",
            message,
            metadata,
        )

    def error(self, message, metadata=None):
        return self.log(
            "error",
            message,
            metadata,
        )

    def entries(self):
        return tuple(self._entries)

    def clear(self):
        self._entries.clear()

    def __len__(self):
        return len(self._entries)
