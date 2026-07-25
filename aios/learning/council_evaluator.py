from .decision_feedback import DecisionFeedback


class CouncilEvaluator:


    def evaluate(
        self,
        audit_record,
    ):

        decision = audit_record.get(
            "decision",
            {}
        )


        session = audit_record.get(
            "session",
            {}
        )


        governance = decision.get(
            "governance",
            {}
        )


        failed = []


        for result in governance.get(
            "results",
            []
        ):

            if not result.get(
                "passed",
                False
            ):

                failed.append(
                    result.get(
                        "gate"
                    )
                )


        agents = [

            item.get(
                "agent"
            )

            for item in session.get(
                "responses",
                []
            )

        ]


        return DecisionFeedback(

            decision_id=
                audit_record.get(
                    "id"
                ),

            approved=
                decision.get(
                    "approved",
                    False
                ),

            governance_passed=
                governance.get(
                    "passed",
                    False
                ),

            failed_gates=
                failed,

            agents=
                agents,

        )
