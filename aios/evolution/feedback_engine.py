class FeedbackEngine:


    def __init__(
        self,
        detector,
    ):

        self.detector = detector



    def analyze(
        self,
        events,
    ):

        return self.detector.detect(
            events
        )
