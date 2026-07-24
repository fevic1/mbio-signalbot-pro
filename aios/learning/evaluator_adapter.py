from .feedback import ExecutionFeedback


def evaluation_to_feedback(
    evaluation: dict,
) -> ExecutionFeedback:

    pnl = (
        evaluation
        .get("outcome", {})
        .get("pnl", 0)
    )

    quality = (
        evaluation
        .get("evaluation", {})
        .get("decision_quality")
    )

    return ExecutionFeedback(
        execution_id=evaluation.get(
            "timestamp",
            "",
        ),
        success=quality == "positive",
        score=(
            1.0
            if quality == "positive"
            else 0.0
        ),

        asset=evaluation.get(
            "asset",
            "",
        ),

        signal=evaluation.get(
            "signal",
            "",
        ),

        pnl=pnl,

        confidence=evaluation.get(
            "confidence",
            0,
        ),

        observations=[
            f"asset={evaluation.get('asset')}",
            f"signal={evaluation.get('signal')}",
            f"pnl={pnl}",
            f"quality={quality}",
        ],
    )
