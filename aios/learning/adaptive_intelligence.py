class AdaptiveCouncilIntelligence:


    def __init__(
        self,
        learning,
        detector,
        recommender,
    ):

        self.learning = learning

        self.detector = detector

        self.recommender = recommender



    def analyze(
        self,
    ):

        feedback = (
            self.learning.analyze_history()
        )


        patterns = (
            self.detector.analyze(
                feedback
            )
        )


        recommendations = (
            self.recommender.generate(
                patterns
            )
        )


        return {

            "feedback":
                feedback,

            "patterns":
                patterns,

            "recommendations":
                recommendations,

        }
