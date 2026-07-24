from datetime import datetime


class DecisionEvaluator:

    def evaluate(
        self,
        decision_event,
        outcome=None,
    ):

        metadata = decision_event.metadata

        return {
            "event_type": "decision_evaluation",
            "timestamp": datetime.utcnow().isoformat(),
            "asset": metadata.get("asset"),
            "signal": metadata.get("signal"),
            "approved": metadata.get(
                "execution_approval",
                {}
            ).get(
                "approved",
                False,
            ),
            "confidence": metadata.get(
                "verification",
                {}
            ).get(
                "confidence",
                0,
            ),
            "outcome": outcome or {},
        }
