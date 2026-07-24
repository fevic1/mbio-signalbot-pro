from datetime import datetime, timezone


class SystemHealth:

    def __init__(self):

        self.records = {}


    def update(
        self,
        system_name,
        status,
        details=None,
    ):

        self.records[system_name] = {
            "status": status,
            "details": details or {},
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        }


    def get(
        self,
        system_name,
    ):

        return self.records.get(
            system_name,
            {
                "status": "unknown"
            },
        )
