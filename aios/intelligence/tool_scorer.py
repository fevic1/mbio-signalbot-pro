class ToolScorer:

    def score(self, tool_results):

        scores = {}

        for item in tool_results:

            key = (
                item["server"],
                item["tool"],
            )

            score = 1.0 if item.get("success") else 0.0

            scores[key] = {
                "score": score,
                "success": item.get("success"),
            }

        return scores
