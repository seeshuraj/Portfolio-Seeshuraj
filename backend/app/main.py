"""FastAPI app — Seeshuraj Anime Avatar API."""
import time
from typing import List, Dict, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from app.llm import generate_response
from app.tts import synthesize

app = FastAPI(
    title="Seeshuraj Avatar API",
    description="AI avatar backend: RAG + Grok LLM + Azure TTS",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict]] = []


class ChatResponse(BaseModel):
    answer_text: str
    audio_base64: Optional[str] = None
    latency_ms: int


@app.get("/health")
async def health():
    return {"status": "ok", "model": "grok-3-fast-beta", "tts": bool(settings.speech_key)}


@app.post("/api/avatar-chat", response_model=ChatResponse)
async def avatar_chat(req: ChatRequest):
    t0 = time.monotonic()
    answer = await generate_response(req.message, req.history or [])
    audio = await synthesize(answer)
    latency = int((time.monotonic() - t0) * 1000)
    return ChatResponse(answer_text=answer, audio_base64=audio, latency_ms=latency)
