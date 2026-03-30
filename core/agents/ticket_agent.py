from __future__ import annotations

from typing import Any, Dict, Optional

from core.models.llm_decision_engine import PhiDecisionEngine


class TicketAgent:
    """
    Wraps the legal-contract decision engine into a stable interface.
    """

    def __init__(self, engine: Optional[PhiDecisionEngine] = None) -> None:
        self.engine = engine or PhiDecisionEngine()

    def decide(self, user_request: str) -> Dict[str, Any]:
        result = self.engine.decide(user_request)
        # Normalize/guard output shape
        return {
            "action": str(result.get("action", "FLAG_OUT_OF_SCOPE")),
            "reason": str(result.get("reason", "No reason provided by the model.")),
        }

