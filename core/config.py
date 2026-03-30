from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


# Load local `.env` if present. Safe no-op if missing.
load_dotenv()


@dataclass(frozen=True)
class Settings:
    # API
    REQUEST_TIMEOUT_SECONDS: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "90.0"))

    # Groq (remote validator / tool calling, etc.)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
    GROQ_VALIDATOR_MODEL: str = os.getenv("GROQ_VALIDATOR_MODEL", "llama-3.3-70b-versatile").strip()

    # Local LLMs
    DECISION_ENGINE_MODEL_NAME: str = os.getenv(
        "DECISION_ENGINE_MODEL_NAME", "microsoft/Phi-3.5-mini-instruct"
    ).strip()
    ANALYTICS_CODE_MODEL_NAME: str = os.getenv(
        "ANALYTICS_CODE_MODEL_NAME", "microsoft/Phi-3.5-mini-instruct"
    ).strip()

    # Local generation params
    DECISION_ENGINE_MAX_NEW_TOKENS: int = int(os.getenv("DECISION_ENGINE_MAX_NEW_TOKENS", "200"))
    ANALYTICS_CODE_MAX_NEW_TOKENS: int = int(os.getenv("ANALYTICS_CODE_MAX_NEW_TOKENS", "256"))

    # Optional dataset wiring
    ANALYTICS_CSV_PATH: Optional[str] = os.getenv("ANALYTICS_CSV_PATH")


settings = Settings()

