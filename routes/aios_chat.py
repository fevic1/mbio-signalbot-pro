import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from aios.api.chat.stream import stream_response
from aios.dispatcher import AIOSDispatcher


router = APIRouter()


@router.post("/aios/chat")
async def aios_chat(request: Request, payload: dict):
    system = request.app.state.aios
    dispatcher = AIOSDispatcher(system)

    async def events():
        result = await dispatcher.dispatch(payload)
        content = str(result.get("content", ""))

        async for chunk in stream_response(content):
            event = json.dumps({"content": chunk})
            yield f"data: {event}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
