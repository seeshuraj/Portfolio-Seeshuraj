"""
FastAPI entry point for the AI Anime Avatar backend.

Endpoints:
  GET  /health              — Render health check
  POST /api/avatar-chat     — Main chat + TTS endpoint
"""
import base64
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import get_settings
from .rag import retrieve
from .llm import chat
from .tts import synthesise

settings = get_settings()

app = FastAPI(
    title="Seeshuraj Avatar API",
    description="RAG-powered anime avatar for Seeshuraj's portfolio",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


class ChatResponse(BaseModel):
    answer_text: str
    audio_base64: str | None = None
    latency_ms: float


@app.get("/health")
async def health():
    return {"status": "ok", "service": "seeshuraj-avatar-api"}


@app.post("/api/avatar-chat", response_model=ChatResponse)
async def avatar_chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=422, detail="message cannot be empty")
    if len(req.message) > 500:
        raise HTTPException(status_code=422, detail="message too long (max 500 chars)")

    # 1. RAG retrieval
    context = retrieve(req.message)

    # 2. LLM
    try:
        answer, latency_ms = chat(req.message, context, req.history)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}")

    # 3. TTS (optional — won't crash if Azure keys missing)
    audio_b64: str | None = None
    try:
        wav_bytes = synthesise(answer)
        if wav_bytes:
            audio_b64 = base64.b64encode(wav_bytes).decode()
    except Exception:
        pass  # TTS failure is non-fatal

    return ChatResponse(
        answer_text=answer,
        audio_base64=audio_b64,
        latency_ms=latency_ms,
    )
