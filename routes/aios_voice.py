import json
import logging
import os
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import Response

from aios.capabilities.executor import CapabilityExecutor
from aios.capabilities.request import CapabilityRequest


logger = logging.getLogger(__name__)
router = APIRouter()

KOKORO_URL = os.getenv(
    "AIOS_TTS_URL",
    "http://kokoro-tts:8000",
).rstrip("/")

MAX_SPEECH_CHARS = 900


def _services(request: Request):
    system = request.app.state.aios
    return getattr(system, "services", {})


def _safe_speech_text(value):
    text = " ".join(str(value or "").split())
    return text[:MAX_SPEECH_CHARS]


def _event_alert(event, recent_events):
    event_type = str(event.get("event_type", ""))
    payload = event.get("payload") or {}
    event_id = str(event.get("id", ""))

    if event_type in {"council.review.created", "council.review.updated"}:
        status = str(payload.get("status", ""))
        severity = str(payload.get("severity", "medium")).lower()

        if status != "awaiting_human" and event_type.endswith("updated"):
            return None

        title = _safe_speech_text(
            payload.get("title") or "Council review"
        )

        return {
            "id": event_id,
            "kind": "council",
            "severity": severity,
            "text": (
                f"AIOS Council requires your attention. {title}. "
                "Human review is awaiting."
            ),
        }

    emergency_types = {
        "risk.emergency",
        "position.critical",
        "system.critical",
        "execution.emergency",
    }

    if event_type in emergency_types:
        message = _safe_speech_text(
            payload.get("message")
            or payload.get("summary")
            or payload.get("title")
            or "A critical AIOS event requires attention."
        )

        return {
            "id": event_id,
            "kind": "emergency",
            "severity": "critical",
            "text": f"Urgent AIOS alert. {message}",
        }

    if event_type == "execution.completed" and payload.get("notify_user") is True:
        capability = _safe_speech_text(
            payload.get("capability") or "requested task"
        )

        return {
            "id": event_id,
            "kind": "completion",
            "severity": "info",
            "text": f"AIOS completed the {capability} task.",
        }

    if event_type == "provider_execution.failed":
        provider = str(payload.get("provider") or "language model")
        matching = [
            item
            for item in recent_events[-30:]
            if item.get("event_type") == "provider_execution.failed"
            and str((item.get("payload") or {}).get("provider") or "") == provider
        ]

        if len(matching) >= 3 and matching[-1].get("id") == event_id:
            return {
                "id": event_id,
                "kind": "provider",
                "severity": "high",
                "text": (
                    f"AIOS alert. The {provider} provider has failed "
                    "repeatedly. Fallback providers may be in use."
                ),
            }

    return None


@router.get("/aios/voice/health")
async def voice_health():
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(f"{KOKORO_URL}/health")
            response.raise_for_status()
            return {
                "success": True,
                "tts": response.json(),
            }
    except Exception as error:
        logger.warning("Kokoro health check failed: %s", error)
        raise HTTPException(
            status_code=503,
            detail="AIOS voice synthesis is unavailable",
        )


@router.post("/aios/voice/synthesize")
async def synthesize_voice(payload: dict):
    text = _safe_speech_text(payload.get("text"))

    if not text:
        raise HTTPException(status_code=400, detail="Speech text is required")

    request_payload = {
        "text": text,
        "voice": str(payload.get("voice") or "af_sarah"),
        "speed": float(payload.get("speed") or 1.0),
        "lang": str(payload.get("lang") or "en-us"),
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{KOKORO_URL}/synthesize",
                json=request_payload,
            )
            response.raise_for_status()
    except Exception as error:
        logger.exception("Kokoro synthesis failed")
        raise HTTPException(
            status_code=503,
            detail="AIOS voice synthesis failed",
        ) from error

    return Response(
        content=response.content,
        media_type="audio/wav",
        headers={
            "Cache-Control": "no-store",
            "Content-Disposition": 'inline; filename="aios-speech.wav"',
        },
    )


@router.get("/aios/voice/alerts")
async def voice_alerts(request: Request, cursor: int = -1):
    persistence = _services(request).get("event_persistence")
    events = persistence.load() if persistence is not None else []

    if not isinstance(events, list):
        events = []

    current_cursor = len(events)

    if cursor < 0:
        return {
            "cursor": current_cursor,
            "alerts": [],
        }

    cursor = min(max(cursor, 0), current_cursor)
    alerts = []

    for index in range(cursor, current_cursor):
        alert = _event_alert(
            events[index],
            events[: index + 1],
        )
        if alert:
            alerts.append(alert)

    return {
        "cursor": current_cursor,
        "alerts": alerts[-10:],
    }


@router.websocket("/ws/aios/voice")
async def aios_voice(websocket: WebSocket):
    await websocket.accept()

    system = websocket.app.state.aios
    executor = CapabilityExecutor(system)

    try:
        while True:
            message = await websocket.receive_text()

            request = CapabilityRequest(
                capability="reasoning",
                context={
                    "message": message,
                    "source": "voice",
                },
            )

            result = await executor.execute(request)
            await websocket.send_json(result)

    except WebSocketDisconnect:
        pass
