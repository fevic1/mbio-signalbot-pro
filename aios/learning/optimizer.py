class PlannerOptimizer:

    def __init__(self):

        self.history = []
        self.capability_scores = {}
        self.recommendations = []


    def update(
        self,
        feedback,
    ):

        self.history.append(
            feedback
        )

        for observation in feedback.observations:

            if "failed" in observation.lower():

                self.recommendations.append(
                    {
                        "type": "failure",
                        "observation": observation,
                    }
                )


        self.capability_scores[
            feedback.execution_id
        ] = feedback.score


        return feedback


    def get_recommendations(
        self,
    ):

        return self.recommendations
