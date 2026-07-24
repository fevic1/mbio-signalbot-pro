class MemoryClassifier:


    def classify(
        self,
        execution_result,
    ):

        memories = []


        issues = execution_result.get(
            "issues",
            []
        )


        recommendations = execution_result.get(
            "recommendations",
            []
        )


        output = execution_result.get(
            "output",
            {}
        )


        if issues:

            memories.append(
                {
                    "type": "operational",
                    "content": {
                        "issues": issues,
                        "output": output,
                    }
                }
            )


        if recommendations:

            memories.append(
                {
                    "type": "knowledge",
                    "content": {
                        "lessons":
                            recommendations,
                    }
                }
            )


        if output:

            memories.append(
                {
                    "type": "decision",
                    "content": {
                        "execution_pattern":
                            output,
                    }
                }
            )


        return memories
