from datetime import datetime
import uuid


class Event:

    def __init__(
        self,
        event_type,
        source="system",
        payload=None,
    ):

        self.id = str(uuid.uuid4())

        self.type = event_type

        self.source = source

        self.payload = payload or {}

        self.time = datetime.utcnow().isoformat()


    def to_dict(self):

        return {
            "id": self.id,
            "event": self.type,
            "source": self.source,
            "payload": self.payload,
            "time": self.time,
        }
