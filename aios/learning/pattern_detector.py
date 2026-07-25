from collections import Counter


class PatternDetector:


    def analyze(
        self,
        feedback,
    ):

        failures = []

        agents = []


        for item in feedback:

            failures.extend(
                item.get(
                    "failed_gates",
                    []
                )
            )

            agents.extend(
                item.get(
                    "agents",
                    []
                )
            )


        return {

            "gate_failures":
                dict(
                    Counter(
                        failures
                    )
                ),

            "agent_usage":
                dict(
                    Counter(
                        agents
                    )
                ),

            "total_reviews":
                len(feedback),

        }
