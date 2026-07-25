class AuditReplay:


    def replay(
        self,
        records,
    ):

        return [

            {

                "change_id":
                    record.get(
                        "change_id"
                    ),

                "component":
                    record.get(
                        "component"
                    ),

                "reason":
                    record.get(
                        "reason"
                    ),

                "approved":
                    record.get(
                        "approved",
                        False,
                    ),

                "rollback_available":
                    record.get(
                        "rollback_available",
                        False,
                    ),

                "governance":
                    record.get(
                        "governance",
                        {},
                    ),

                "policy_version_used":
                    record.get(
                        "policy_version_used"
                    ),

                "decision_id":
                    record.get(
                        "decision_id"
                    ),

                "proposal_id":
                    record.get(
                        "proposal_id"
                    ),

                "council_session":
                    record.get(
                        "council_session"
                    ),

            }

            for record in records

        ]
