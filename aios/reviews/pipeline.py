class ReviewPipeline:


    def __init__(
        self,
    ):

        self.reviewers = []



    def register(
        self,
        reviewer,
    ):

        self.reviewers.append(
            reviewer
        )



    def run(
        self,
        objective_analysis,
    ):

        results = []


        for reviewer in self.reviewers:

            results.append(
                reviewer.review(
                    objective_analysis
                )
            )


        approved = all(
            result.approved()
            for result in results
        )


        return {
            "approved": approved,
            "reviews": results,
        }
