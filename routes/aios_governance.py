from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/aios/governance")
async def governance_status(request: Request):

    system = request.app.state.aios

    gateway = system.get(
        "governance_gateway"
    )

    if gateway is None:
        return {
            "status": "unavailable"
        }

    return {
        "status": "ready",
        "approvals": gateway.approval_manager.history(),
        "pending": gateway.approval_manager.pending(),
        "audit": gateway.audit_logger.history(),
    }
