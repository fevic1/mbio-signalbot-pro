from datetime import datetime, timezone


class RuntimeMetadata:

    def __init__(self):
        self.name = "AIOS Runtime"
        self.version = None
        self.started_at = None
        self.stopped_at = None
        self.build = None
        self.metadata = {}

    def start(self):
        self.started_at = datetime.now(timezone.utc)

    def stop(self):
        self.stopped_at = datetime.now(timezone.utc)

    def set(self, key, value):
        self.metadata[key] = value
        return value

    def get(self, key, default=None):
        return self.metadata.get(key, default)

    def export(self):
        version = (
            self.version.string
            if hasattr(self.version, "string")
            else self.version
        )

        return {
            "name": self.name,
            "version": version,
            "build": self.build,
            "started_at": self.started_at,
            "stopped_at": self.stopped_at,
            "metadata": dict(self.metadata),
        }
