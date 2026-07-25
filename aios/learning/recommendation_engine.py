class RecommendationEngine:


    def generate(
        self,
        patterns,
    ):

        recommendations = []


        for gate, count in patterns.get(
            "gate_failures",
            {}
        ).items():

            if count >= 3:

                recommendations.append(
                    {
                        "type":
                            "governance",

                        "area":
                            gate,

                        "recommendation":
                            (
                                f"Review {gate} "
                                f"gate policy"
                            ),

                    }
                )


        for agent, count in patterns.get(
            "agent_usage",
            {}
        ).items():

            if count == 0:

                recommendations.append(
                    {
                        "type":
                            "routing",

                        "agent":
                            agent,

                        "recommendation":
                            (
                                f"Increase "
                                f"{agent} participation"
                            ),

                    }
                )


        return recommendations
