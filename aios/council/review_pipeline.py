class CouncilReviewPipeline:


    def __init__(
        self,
        quality_gate,
        council_manager,
    ):

        self.quality_gate = quality_gate

        self.council = council_manager



    def review(
        self,
        proposal,
    ):

        gate_result = (
            self.quality_gate
            .evaluate(
                proposal
            )
        )


        if not gate_result["passed"]:

            return {
                "approved": False,
                "stage": "quality_gate",
                "report": gate_result,
            }


        session = (
            self.council
            .create_session(
                proposal.get(
                    "question",
                    "Review proposal"
                )
            )
        )


        return {
            "approved": None,
            "stage": "council",
            "session": session,
            "quality_gate": gate_result,
        }
