class PatternDetector:


    def detect(
        self,
        events,
    ):

        patterns = []


        for event in events:

            if event.get(
                "severity"
            ) == "warning":

                patterns.append(
                    {
                        "type":
                            "warning_pattern",

                        "source":
                            event.get(
                                "component"
                            ),

                        "message":
                            event.get(
                                "message"
                            ),
                    }
                )


        return patterns
