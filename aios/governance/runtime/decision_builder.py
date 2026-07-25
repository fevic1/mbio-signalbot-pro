from .decision_record import DecisionRecord


class DecisionRecordBuilder:


    def build(
        self,
        decision,
        session,
        governance,
    ):

        policies = {}

        evidence = []


        for result in governance.get(
            "results",
            []
        ):

            policy = result.get(
                "policy"
            )

            if policy:

                policies[
                    result["gate"]
                ] = policy


            if result["gate"] == "evidence":

                evidence.append(
                    result
                )


        record = DecisionRecord(

            decision=decision,

            session_id=session.id,

            policies=policies,

            evidence=evidence,

        )


        return record.describe()
