class DeliberationEngine:

    def __init__(
        self,
        evaluator=None,
    ):

        self.evaluator = evaluator

        self.history = []


    def evaluate(
        self,
        proposal,
    ):

        opinions = proposal.opinions


        if not opinions:

            return {

                "status": "no_opinions",

                "confidence": 0,

                "agreement": False,

            }


        evaluation = None


        if self.evaluator:

            evaluation = self.evaluator.evaluate(
                proposal
            )


        confidences = [

            opinion.get(
                "confidence",
                0
            )

            for opinion in opinions

        ]


        average = round(
            sum(confidences) / len(confidences),
            2,
        )


        agents = [

            opinion["agent"]

            for opinion in opinions

        ]


        result = {

            "proposal": proposal.title,

            "agents": agents,

            "confidence": average,

            "agreement": average >= 0.75,

            "evaluation": evaluation,

        }


        # reduce confidence when evaluator finds issues

        if evaluation:

            if not evaluation["valid"]:

                result["confidence"] = round(
                    average * evaluation["score"],
                    2,
                )


                result["agreement"] = False



        self.history.append(
            result
        )


        return result



    def history(self):

        return self.history
