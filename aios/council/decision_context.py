class DecisionContext:


    def __init__(
        self,
        decisions=None,
    ):

        self.decisions = decisions or []



    def add(
        self,
        decision,
    ):

        self.decisions.append(
            decision
        )



    def build(
        self,
    ):

        return {
            "previous_decisions":
                self.decisions,
            "count":
                len(self.decisions),
        }
