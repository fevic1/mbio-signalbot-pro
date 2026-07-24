from datetime import datetime, timezone


class StrategyVersion:

    def __init__(
        self,
        name,
        version,
        metadata=None,
    ):

        self.name = name
        self.version = version
        self.metadata = metadata or {}
        self.created = datetime.now(
            timezone.utc
        ).isoformat()


    def serialize(self):

        return {
            "name": self.name,
            "version": self.version,
            "metadata": self.metadata,
            "created": self.created,
        }


class StrategyVersionRegistry:

    def __init__(self):

        self.versions = {}


    def register(
        self,
        name,
        version,
        metadata=None,
    ):

        key = f"{name}:{version}"

        strategy = StrategyVersion(
            name,
            version,
            metadata,
        )

        self.versions[key] = strategy

        return strategy


    def get(
        self,
        name,
        version,
    ):

        return self.versions.get(
            f"{name}:{version}"
        )


    def list_versions(
        self,
        name=None,
    ):

        values = list(
            self.versions.values()
        )

        if name:

            values = [
                v for v in values
                if v.name == name
            ]

        return [
            v.serialize()
            for v in values
        ]
