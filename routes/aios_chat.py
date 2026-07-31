from fastapi import APIRouter, Request
from aios.capabilities.executor import CapabilityExecutor
from aios.capabilities.request import CapabilityRequest

router = APIRouter()


@router.post("/aios/chat")
async def aios_chat(request: Request, payload: dict):
    system = request.app.state.aios

    executor = CapabilityExecutor(system)

    chat_request = CapabilityRequest(
        capability="reasoning",
        context={
            "message": payload.get("message", "")
        },
    )

    result = await executor.execute(chat_request)

    content = result.get("content")

    if isinstance(content, dict):
        content = (
            content.get("summary")
            or content.get("reasoning")
            or str(content)
        )

    return {
        "success": result.get("success"),
        "capability": result.get("capability"),
        "provider": result.get("provider"),
        "model": result.get("model"),
        "content": content,
        "latency": result.get("latency"),
        "cost": result.get("cost"),
        "attempt": result.get("attempt"),
    }
