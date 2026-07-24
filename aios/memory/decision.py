from .events import MemoryEvent


def create_decision_event(
    asset,
    signal,
    market_analysis,
    risk_analysis,
    verification,
    approval,
    executed=False,
):
    return MemoryEvent(
        event_type="trading_decision",
        action=(
            "execution_approved"
            if approval.get("approved")
            else "execution_rejected"
        ),
        source="hunter",
        metadata={
            "asset": asset,
            "signal": signal,
            "market_analysis": market_analysis,
            "risk_analysis": risk_analysis,
            "verification": verification,
            "execution_approval": approval,
            "executed": executed,
        },
    )
