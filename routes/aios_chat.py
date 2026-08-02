import json
import logging

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from aios.api.chat.stream import stream_response
from aios.dispatcher import AIOSDispatcher


router = APIRouter()
logger = logging.getLogger(__name__)


MAX_ATTACHMENTS = 5
MAX_ATTACHMENT_CHARS = 100000
MAX_TOTAL_ATTACHMENT_CHARS = 300000


def normalize_attachments(payload: dict) -> list[dict]:
    raw = payload.get("attachments") or []

    if not isinstance(raw, list):
        raise HTTPException(
            status_code=400,
            detail="attachments must be a list",
        )

    if len(raw) > MAX_ATTACHMENTS:
        raise HTTPException(
            status_code=413,
            detail=f"Maximum {MAX_ATTACHMENTS} attachments per message",
        )

    normalized = []
    total = 0

    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise HTTPException(
                status_code=400,
                detail=f"Attachment {index + 1} is invalid",
            )

        content = str(item.get("content", ""))

        content = "".join(
            character
            for character in content
            if character in "\t\n\r" or ord(character) >= 32
        )

        if len(content) > MAX_ATTACHMENT_CHARS:
            raise HTTPException(
                status_code=413,
                detail=(
                    f"Attachment {index + 1} exceeds "
                    f"{MAX_ATTACHMENT_CHARS} characters"
                ),
            )

        if not content.strip():
            continue

        total += len(content)

        if total > MAX_TOTAL_ATTACHMENT_CHARS:
            raise HTTPException(
                status_code=413,
                detail=(
                    "Combined attachment text exceeds "
                    f"{MAX_TOTAL_ATTACHMENT_CHARS} characters"
                ),
            )

        normalized.append({
            "id": str(item.get("id") or f"attachment-{index + 1}")[:100],
            "name": str(
                item.get("name") or f"Pasted text {index + 1}"
            )[:160],
            "type": "text/plain",
            "content": content,
            "characters": len(content),
            "lines": content.count("\n") + 1,
        })

    return normalized


@router.post("/aios/chat")
async def aios_chat(request: Request, payload: dict):
    payload = dict(payload)
    payload["attachments"] = normalize_attachments(payload)

    system = request.app.state.aios
    dispatcher = AIOSDispatcher(system)

    async def events():
        try:
            _, predicted_capability = dispatcher._classify_task(
                str(payload.get("message", ""))
            )
            if predicted_capability == "research":
                initial_activity = [
                    "Understanding the request",
                    "Searching current sources",
                    "Inspecting selected sources",
                ]

                progress_event = json.dumps({
                    "metadata": {
                        "capability": predicted_capability,
                        "activity": initial_activity,
                        "in_progress": True,
                    }
                })
                yield f"data: {progress_event}\n\n"

            result = await dispatcher.dispatch(payload)
            content = str(result.get("content", ""))

            evidence = result.get("execution_evidence") or {}
            research = evidence.get("research_context") or {}
            research_results = research.get("results") or []
            verified_count = sum(
                1
                for item in research_results
                if isinstance(item, dict)
                and item.get("verified_by") == "firecrawl"
            )
            tools_called = evidence.get("tools_called") or []

            activity = []
            if result.get("capability") == "research":
                activity.append("Request classified as current research")
            if "tavily__search_web" in tools_called:
                activity.append(
                    f"Search completed: {len(research_results)} sources selected"
                )
            if "firecrawl__scrape_url" in tools_called:
                activity.append(
                    f"Source inspection completed: {verified_count} sources verified"
                )
            if result.get("provider") and (
                activity
                or tools_called
                or evidence.get("fallback_used")
            ):
                activity.append(
                    "Synthesis completed with "
                    f"{result.get('provider')} / {result.get('model')}"
                )

            metadata_event = json.dumps({
                "metadata": {
                    "provider": result.get("provider"),
                    "model": result.get("model"),
                    "latency": result.get("latency"),
                    "capability": result.get("capability"),
                    "activity": activity,
                    "source_count": len(research_results),
                    "verified_source_count": verified_count,
                    "fallback_used": bool(evidence.get("fallback_used")),
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
