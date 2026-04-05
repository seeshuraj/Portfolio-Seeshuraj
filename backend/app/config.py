from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # NVIDIA NIM (via OpenAI-compatible API)
    nvidia_api_key: str = ""
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_model: str = "deepseek-ai/deepseek-r1-0528-qwen3-8b"

    # Azure Neural TTS
    speech_key: str = ""
    speech_region: str = "westeurope"
    speech_voice: str = "en-US-AriaNeural"

    # CORS
    allowed_origins: list[str] = [
        "https://seeshuraj.github.io",
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache
def get_settings() -> Settings:
    return Settings()
