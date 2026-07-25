class CouncilLearning:


    def __init__(
        self,
        audit_query,
        evaluator,
    ):

        self.audit_query = audit_query

        self.evaluator = evaluator



    def analyze_history(
        self,
    ):

        decisions = (
            self.audit_query.all_decisions()
        )


        results = []


        for decision in decisions:

            feedback = (
                self.evaluator.evaluate(
                    decision
                )
            )

            results.append(
                feedback.describe()
            )


        return results
