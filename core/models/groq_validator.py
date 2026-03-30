from __future__ import annotations

import json
from typing import Any, Dict

from core.config import settings


DEFAULT_VALIDATION_RESULT = {
    "is_valid": True,
    "reason": "Validator not configured; skipping remote validation.",
    "issues": [],
}


class GroqCodeValidator:
    """
    Optional remote validator using Groq.
    - If GROQ_API_KEY is missing, validation is skipped safely.
    - If groq package is missing, validation is skipped safely.
    """

    def __init__(self, model: str | None = None) -> None:
        self.model = (model or settings.GROQ_VALIDATOR_MODEL).strip()
        self._client = None
        self._enabled = False
        self._init_error = ""
        self._try_init()

    def _try_init(self) -> None:
        if not settings.GROQ_API_KEY:
            self._init_error = "GROQ_API_KEY is not set."
            return

        try:
            from groq import Groq

            self._client = Groq(api_key=settings.GROQ_API_KEY)
            self._enabled = True
        except Exception as exc:
            self._init_error = f"Groq client init failed: {exc}"

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def init_error(self) -> str:
        return self._init_error

    def validate_code(self, question: str, schema: Dict[str, Any], code: str) -> Dict[str, Any]:
        if not self._enabled:
            return {
                **DEFAULT_VALIDATION_RESULT,
                "reason": f"Validation skipped: {self._init_error or 'validator disabled'}",
            }

        prompt = f"""You are an extremely strict pandas code validator.
Your ONLY job is to check whether the generated code fully and correctly answers the question.
Do NOT execute code. Do NOT suggest fixes.

Question:
{question}

DataFrame Schema:
{json.dumps(schema, indent=2)}

Generated Code:
{code}

Return ONLY valid JSON:
{{
  "is_valid": true or false,
  "reason": "short explanation",
  "issues": []
}}"""

        try:
            completion = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.0,
            )
            content = completion.choices[0].message.content.strip()

            if "```json" in content:
                content = content.split("```json", 1)[1].split("```", 1)[0].strip()
            elif "```" in content:
                content = content.split("```", 1)[1].split("```", 1)[0].strip()

            result = json.loads(content)
            result.setdefault("is_valid", False)
            result.setdefault("issues", [])
            result.setdefault("reason", "No reason provided.")
            return result
        except Exception as exc:
            return {
                "is_valid": True,
                "reason": f"Validation failed open due to validator error: {exc}",
                "issues": [],
            }

