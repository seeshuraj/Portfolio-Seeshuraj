"""Grok (xAI) LLM wrapper."""
import os
from typing import List, Dict

from app.config import settings
from app.rag import SYSTEM_PROMPT, retrieve

try:
    from openai import OpenAI
    _client = None

    def _get_client():
        global _client
        if _client is None:
            _client = OpenAI(
                api_key=settings.xai_api_key,
                base_url="https://api.x.ai/v1",
            )
        return _client
except ImportError:
    _get_client = None


async def generate_response(message: str, history: List[Dict]) -> str:
    """Generate a response from Grok with RAG context."""
    if not settings.xai_api_key or _get_client is None:
        return "I'm Seeshuraj's anime avatar! My AI backend isn't configured yet, but I can tell you I'm actively looking for Software Engineer roles in Dublin and EU. Email me at bhoopals@tcd.ie!"

    context = retrieve(message)
    system = SYSTEM_PROMPT + f"\n\nRelevant context:\n{context}"

    messages = [{"role": "system", "content": system}]
    for turn in history[-6:]:  # last 3 exchanges
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": message})

    client = _get_client()
    response = client.chat.completions.create(
        model="grok-3-fast-beta",
        messages=messages,
        max_tokens=180,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()
