from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict

from core.config import settings


@dataclass(frozen=True)
class AnalyticsConfig:
    model_name: str = settings.ANALYTICS_CODE_MODEL_NAME
    torch_dtype: str = "float16"
    max_new_tokens: int = settings.ANALYTICS_CODE_MAX_NEW_TOKENS


def _clean_llm_code(text: str) -> str:
    """
    Clean LLM output and ensure it assigns to `result`.
    """
    text = text.strip()

    # Extract code from markdown blocks
    if "```python" in text:
        text = text.split("```python", 1)[1].split("```", 1)[0].strip()
    elif "```" in text:
        text = text.split("```", 1)[1].split("```", 1)[0].strip()

    # Remove remaining backticks
    text = text.replace("```", "").strip()

    # Ensure assignment to result
    if "result =" not in text and "result=" not in text:
        # Heuristic: single expression → wrap into result =
        if text.endswith((")", "]")):
            text = f"result = {text}"

    return text


def _build_prompt(question: str, schema: Dict[str, Any]) -> str:
    return f"""
You are a pandas data analyst.

Write executable pandas code to answer the question.

Rules:
- Use ONLY existing dataframe columns.
- The dataframe is named: df
- No explanations.
- No markdown.
- No imports.
- No loops.
- Must assign final answer to variable: result.

Schema:
{schema}

Question:
{question}
""".strip()


class AnalyticsCodeLLM:
    """
    Local HuggingFace LLM that generates pandas code for analytics queries.

    This mirrors the pattern from `2)self_correction (2).py` but is packaged
    for reuse by the AnalyticsAgent.
    """

    def __init__(self, config: AnalyticsConfig | None = None) -> None:
        self.config = config or AnalyticsConfig()
        self._tokenizer = None
        self._model = None
        self._device = None

    def _ensure_loaded(self) -> None:
        if self._tokenizer is not None and self._model is not None:
            return

        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except Exception as exc:
            raise RuntimeError(
                "Missing local model dependencies. Install `transformers` and `torch`."
            ) from exc

        self._tokenizer = AutoTokenizer.from_pretrained(
            self.config.model_name,
            trust_remote_code=True,
        )

        dtype = torch.float16 if self.config.torch_dtype == "float16" else torch.float32
        self._model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            device_map="auto",
            torch_dtype=dtype,
            trust_remote_code=True,
        )

        self._device = "cuda" if torch.cuda.is_available() else "cpu"

    def _generate(self, prompt: str, max_tokens: int = 256) -> str:
        try:
            import torch
        except Exception as exc:
            raise RuntimeError("Torch runtime is unavailable.") from exc

        self._ensure_loaded()
        tokenizer = self._tokenizer
        model = self._model

        inputs = tokenizer(prompt, return_tensors="pt").to(self._device)
        input_token_num = inputs["input_ids"].shape[1]

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )

        gen_tokens = outputs[0][input_token_num:]
        return tokenizer.decode(gen_tokens, skip_special_tokens=True)

    def gen_code(self, question: str, schema: Dict[str, Any]) -> str:
        prompt = _build_prompt(question, schema)
        raw = self._generate(prompt, max_tokens=self.config.max_new_tokens)
        return _clean_llm_code(raw)

