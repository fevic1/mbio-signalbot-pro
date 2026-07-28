from aios.core.factory import Factory

from datetime import datetime, timezone
import uuid


class ChangeManager:


    def __init__(self):

        self.changes = []



    def create(
        self,
        component,
        reason,
        rollback_available,
    ):

        change = {

            "change_id":
                str(uuid.uuid4()),

            "component":
                component,

            "reason":
                reason,

            "rollback_available":
                rollback_available,

            "approved":
                False,

            "created_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

        }


        self.changes.append(
            change
        )


        return change



    def approve(
        self,
        change_id,
    ):

        for change in self.changes:

            if change["change_id"] == change_id:

                change["approved"] = True

                return change


        return None



    def history(self):

        return self.changes
