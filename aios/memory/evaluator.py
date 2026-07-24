from datetime import datetime


class DecisionEvaluator:

    def evaluate(
        self,
        decision_event,
        outcome=None,
    ):

        metadata = decision_event.metadata

        outcome = outcome or {}

        pnl = outcome.get(
            "pnl",
            0,
        )

        signal = metadata.get(
            "signal",
            "UNKNOWN",
        )

        approved = metadata.get(
            "execution_approval",
            {}
        ).get(
            "approved",
            False,
        )

        confidence = metadata.get(
            "verification",
            {}
        ).get(
            "confidence",
            0,
        )

        if confidence <= 1:
            confidence *= 100

        profitable = pnl > 0

        return {
            "event_type": "decision_evaluation",
            "timestamp": datetime.utcnow().isoformat(),

            "asset": metadata.get(
                "asset"
            ),

            "signal": signal,

            "approved": approved,

            "confidence": confidence,

            "outcome": {
                "pnl": pnl,
                "profitable": profitable,
            },

            "evaluation": {
                "correct_direction": (
                    (signal == "BUY" and profitable)
                    or
                    (signal == "SELL" and not profitable)
                ),
                "decision_quality": (
                    "positive"
                    if approved and profitable
                    else "negative"
                    if approved and not profitable
                    else "blocked"
                ),
            },
        }
