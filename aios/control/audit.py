class ControlAudit:


    def __init__(
        self,
        audit_logger,
    ):

        self.audit = audit_logger



    def record_change(
        self,
        change,
        decision,
    ):

        data = {

            "change_id":
                change["change_id"],

            "component":
                change["component"],

            "reason":
                change["reason"],

            "approved":
                decision.get(
                    "approved",
                    False,
                ),

            "rollback_available":
                change.get(
                    "rollback_available",
                    False,
                ),

            "proposal_id":
                change.get(
                    "proposal_id"
                ),

            "governance":
                decision.get(
                    "governance",
                    {},
                ),

            "policy_version_used":
                decision.get(
                    "policy_version_used"
                ),

            "decision_id":
                decision.get(
                    "decision_id"
                ),

            "council_session":
                decision.get(
                    "council_session"
                ),

        }


        self.audit.storage.append(
            "changes",
            data,
        )


        return data


from datetime import datetime, timezone


class RuntimeAudit:

    def __init__(self):
        self._records = []

    def record(
        self,
        action: str,
        actor="runtime",
        metadata=None,
    ):
        event = {
            "action": action,
            "actor": actor,
            "metadata": metadata or {},
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        self._records.append(event)

        return event

    def all(self):
        return tuple(self._records)

    def filter(self, action: str):
        return [
            event
            for event in self._records
            if event["action"] == action
        ]

    def clear(self):
        self._records.clear()

    def __len__(self):
        return len(self._records)
