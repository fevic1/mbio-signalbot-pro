from datetime import datetime, timezone
import uuid


class IncidentManager:


    def __init__(self):

        self.incidents = []



    def record(
        self,
        error,
        component,
    ):

        incident = {

            "id":
                str(uuid.uuid4()),

            "component":
                component,

            "error":
                str(error),

            "created_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

        }


        self.incidents.append(
            incident
        )


        return incident



    def history(self):

        return self.incidents
