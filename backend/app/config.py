from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    nvidia_api_key: str = ""          # NVIDIA NIM API key — set in Render env vars
    speech_key: str = ""
    speech_region: str = "westeurope"
    speech_voice: str = "en-US-AriaNeural"
    allowed_origins: List[str] = [
        "https://seeshuraj.github.io",
        "http://localhost:3000",
        "http://localhost:5500",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
