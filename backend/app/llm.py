"""
NVIDIA NIM chat via OpenAI-compatible SDK.
Persona: Seeshuraj's anime avatar — first-person, concise, warm.
"""
import time
from openai import OpenAI
from .config import get_settings

SYSTEM_PROMPT = """
You are the AI avatar of Seeshuraj Bhoopalan — an MSc HPC graduate from Trinity College Dublin
and an AI & Software Engineer based in Dublin, Ireland.

Personality:
- Speak in first person as Seeshuraj ("I built...", "My experience is...")
- Warm, confident, technically sharp — like a senior engineer in a friendly 1-on-1
- Keep answers concise (2–4 sentences max) unless asked for detail
- If asked something outside your knowledge base, say "That's not in my CV, but feel free to email me at bhoopals@tcd.ie!"
- Never make up facts. Only answer from the provided context.

You are currently running as an animated anime avatar on Seeshuraj's portfolio website.
Answer questions about his background, skills, projects, experience, and career goals.
""".strip()


def chat(user_message: str, context: str, history: list[dict]) -> tuple[str, float]:
    """
    Returns (reply_text, latency_ms).
    history: list of {role: 'user'|'assistant', content: str}
    """
    settings = get_settings()
    client = OpenAI(
        api_key=settings.nvidia_api_key,
        base_url=settings.nvidia_base_url,
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"Relevant context from Seeshuraj's CV:\n{context}"},
    ]
    # Append last 4 turns of history to maintain short-term memory
    for turn in history[-4:]:
        messages.append(turn)
    messages.append({"role": "user", "content": user_message})

    t0 = time.perf_counter()
    response = client.chat.completions.create(
        model=settings.nvidia_model,
        messages=messages,
        max_tokens=256,
        temperature=0.7,
    )
    latency_ms = (time.perf_counter() - t0) * 1000
    reply = response.choices[0].message.content.strip()
    return reply, round(latency_ms, 1)
