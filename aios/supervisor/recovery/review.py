class RecoveryReviewAdapter:


    def __init__(
        self,
        review_pipeline,
    ):

        self.review_pipeline = (
            review_pipeline
        )



    def submit(
        self,
        proposal,
    ):

        request = {
            "type":
            "recovery",

            "action":
            proposal.action,

            "reason":
            proposal.reason,

            "priority":
            proposal.priority,

            "metadata":
            proposal.metadata,
        }


        return self.review_pipeline.review(
            request
        )
