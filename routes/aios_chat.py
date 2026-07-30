from fastapi import APIRouter, Request
from pydantic import BaseModel


router = APIRouter(
    prefix="/api/chat",
    tags=["AIOS Chat"],
)


class ChatRequest(BaseModel):
    session_id: str | None = None
    agent: str | None = None
    message: str


@router.get("/status")
async def chat_status():

    return {
        "service": "AIOS Chat",
        "status": "online",
        "transport": "http",
        "websocket": "/ws/chat/{session_id}",
    }


@router.post("")
async def chat(
    payload: ChatRequest,
    request: Request,
):

    runtime = getattr(
        request.app.state,
        "aios_runtime",
        None,
    )

    return {
        "status": "received",
        "session_id": payload.session_id,
        "agent": payload.agent,
        "message": payload.message,
        "runtime_available": runtime is not None,
    }
