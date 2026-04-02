from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

from modesls.llm_decision_engine import DEFAULT_SYSTEM_PROMPT, PhiDecisionEngine


_JSON_PATTERN = re.compile(r"\{[\s\S]*?\}")


def extract_json(text: str) -> Optional[Dict[str, Any]]:
    match = _JSON_PATTERN.search(text or "")
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except Exception:
        return None


def run_decision_flow(user_question: str) -> Dict[str, Any]:
    """
    Notebook Part: decision system.
    Uses the same system prompt and returns action + reason JSON.
    """
    engine = PhiDecisionEngine(system_prompt=DEFAULT_SYSTEM_PROMPT)
    return engine.decide(user_question)

