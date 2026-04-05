"""NVIDIA NIM LLM wrapper — meta/llama-3.3-70b-instruct via OpenAI-compat API."""
import logging
from typing import List, Dict

from app.config import settings
from app.rag import SYSTEM_PROMPT, retrieve

logger = logging.getLogger(__name__)

FALLBACK = (
    "Hi! I'm Seeshuraj's anime avatar. My AI backbone is warming up — "
    "ask me again in a moment, or email bhoopals@tcd.ie directly!"
)

try:
    from openai import OpenAI
    _client: OpenAI | None = None

    def _get_client() -> OpenAI:
        global _client
        if _client is None:
            _client = OpenAI(
                api_key=settings.nvidia_api_key,
                base_url="https://integrate.api.nvidia.com/v1",
            )
        return _client
except ImportError:
    _get_client = None  # type: ignore


async def generate_response(message: str, history: List[Dict]) -> str:
    """Generate a response using NVIDIA NIM with RAG context."""
    if not settings.nvidia_api_key or _get_client is None:
        logger.warning("[llm] NVIDIA_API_KEY not set or openai not installed")
        return FALLBACK

    context = retrieve(message)
    logger.info("[llm] context len=%d", len(context))

    # Keep system + context short so the model stays within max_tokens
    system = SYSTEM_PROMPT + f"\n\n# Context\n{context}"

    messages: List[Dict] = [{"role": "system", "content": system}]
    for turn in history[-4:]:          # last 2 exchanges only
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": message})

    try:
        client = _get_client()
        resp = client.chat.completions.create(
            model="meta/llama-3.3-70b-instruct",
            messages=messages,
            max_tokens=200,
            temperature=0.65,
            top_p=0.9,
            stream=False,
        )

        choice = resp.choices[0]
        text: str | None = None

        # NVIDIA NIM sometimes returns content in message.content
        # and sometimes in delta.content (even on non-streaming)
        if choice.message and choice.message.content:
            text = choice.message.content.strip()
        elif hasattr(choice, "delta") and choice.delta and choice.delta.content:
            text = choice.delta.content.strip()

        logger.info(
            "[llm] finish_reason=%s text_len=%s preview=%s",
            choice.finish_reason,
            len(text) if text else 0,
            (text[:60] + "…") if text and len(text) > 60 else text,
        )

        if not text:
            logger.warning("[llm] empty response — returning fallback")
            return FALLBACK

        return text

    except Exception as exc:
        logger.error("[llm] exception: %s", exc, exc_info=True)
        return FALLBACK
