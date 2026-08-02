\
import asyncio
import io
import os
import re
from contextlib import asynccontextmanager
from time import perf_counter

import soundfile as sf
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from kokoro_onnx import Kokoro
from pydantic import BaseModel, Field


MODEL_PATH = os.getenv(
    "KOKORO_MODEL_PATH",
    "/models/kokoro-v1.0.int8.onnx",
)
VOICES_PATH = os.getenv(
    "KOKORO_VOICES_PATH",
    "/models/voices-v1.0.bin",
)
DEFAULT_VOICE = os.getenv("KOKORO_VOICE", "af_sarah")
MAX_CHARS = max(
    100,
    min(2000, int(os.getenv("KOKORO_MAX_CHARS", "900"))),
)

VOICE_PATTERN = re.compile(r"^[a-z]{2}_[a-z0-9_]+$")
synthesis_lock = asyncio.Lock()
engine = None


class SynthesisRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    voice: str | None = None
    speed: float = Field(default=1.0, ge=0.75, le=1.35)
    lang: str = Field(default="en-us", pattern=r"^[a-z]{2}(?:-[a-z]{2})?$")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine
    engine = await asyncio.to_thread(
        Kokoro,
        MODEL_PATH,
        VOICES_PATH,
    )
    yield
    engine = None


api = FastAPI(
    title="AIOS Kokoro TTS",
    version="1.0.0",
    lifespan=lifespan,
)


@api.get("/health")
async def health():
    return {
        "status": "ok" if engine is not None else "starting",
        "provider": "kokoro-onnx",
        "model": os.path.basename(MODEL_PATH),
        "voice": DEFAULT_VOICE,
        "max_chars": MAX_CHARS,
    }


@api.post("/synthesize")
async def synthesize(request: SynthesisRequest):
    if engine is None:
        raise HTTPException(503, "Kokoro model is not ready")

    text = " ".join(request.text.split()).strip()

    if not text:
        raise HTTPException(400, "Text is empty")

    if len(text) > MAX_CHARS:
        raise HTTPException(
            413,
            f"Text exceeds the {MAX_CHARS}-character alert limit",
        )

    voice = request.voice or DEFAULT_VOICE

    if not VOICE_PATTERN.fullmatch(voice):
        raise HTTPException(400, "Invalid voice identifier")

    started = perf_counter()

    async with synthesis_lock:
        try:
            samples, sample_rate = await asyncio.to_thread(
                engine.create,
                text,
                voice,
                request.speed,
                request.lang,
            )
        except Exception as error:
            raise HTTPException(
                500,
                f"Speech synthesis failed: {type(error).__name__}",
            ) from error

    output = io.BytesIO()
    sf.write(output, samples, sample_rate, format="WAV")

    return Response(
        output.getvalue(),
        media_type="audio/wav",
        headers={
            "X-TTS-Provider": "kokoro-onnx",
            "X-TTS-Voice": voice,
            "X-TTS-Latency": f"{perf_counter() - started:.3f}",
            "Cache-Control": "no-store",
        },
    )
