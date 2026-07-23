class PlannerOptimizer:

    def __init__(self):

        self.history = []


    def update(
        self,
        feedback,
    ):

        self.history.append(feedback)

        return feedback
