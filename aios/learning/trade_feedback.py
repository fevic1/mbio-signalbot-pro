from .feedback import ExecutionFeedback


def trade_to_feedback(record: dict):

    pnl = record.get(
        "pnl",
        0
    )

    strategy = record.get(
        "strategy",
        "UNKNOWN"
    )

    asset = record.get(
        "asset",
        "UNKNOWN"
    )

    signal = record.get(
        "side",
        "UNKNOWN"
    )

    score = 1.0 if pnl >= 0 else 0.0

    return ExecutionFeedback(
        execution_id=record.get(
            "order_id",
            ""
        ),
        success=pnl >= 0,
        score=score,
        observations=[
            f"asset={asset}",
            f"strategy={strategy}",
            f"signal={signal}",
            f"pnl={pnl}",
        ],
        asset=asset,
        strategy=strategy,
        signal=signal,
        pnl=pnl,
    )
