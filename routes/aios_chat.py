import json
import logging

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from aios.api.chat.stream import stream_response
from aios.dispatcher import AIOSDispatcher


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/aios/chat")
async def aios_chat(request: Request, payload: dict):
    system = request.app.state.aios
    dispatcher = AIOSDispatcher(system)

    async def events():
        try:
            result = await dispatcher.dispatch(payload)
            content = str(result.get("content", ""))

            metadata_event = json.dumps({
                "metadata": {
                    "provider": result.get("provider"),
                    "model": result.get("model"),
                    "latency": result.get("latency"),
                }
            })
            yield f"data: {metadata_event}\n\n"

            async for chunk in stream_response(content):
                event = json.dumps({"content": chunk})
                yield f"data: {event}\n\n"

        except Exception as error:
            logger.exception("AIOS chat stream failed")
            event = json.dumps({
                "content": (
                    "AIOS could not complete this response because its "
                    "language-model providers are temporarily unavailable."
                ),
                "error": True,
            })
            yield f"data: {event}\n\n"

        finally:
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
