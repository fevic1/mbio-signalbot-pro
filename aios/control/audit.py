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
