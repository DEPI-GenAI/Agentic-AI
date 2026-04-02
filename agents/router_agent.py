from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional
from models.llm_decision_engine import PhiDecisionEngine

Route = Literal["TICKET_DECISION", "ANALYTICS", "ESCALATE"]

@dataclass(frozen=True)
class RouterResult:
    route: Route
    reason: str

class RouterAgent:
    def __init__(self, engine: Optional[PhiDecisionEngine] = None) -> None:
        self.engine = engine or PhiDecisionEngine()

    def route(self, user_request: str) -> RouterResult:
        routing_prompt = f"""
        Analyze the user request and categorize it:
        1. ANALYTICS: Calculating, counting, or averaging data.
        2. TICKET_DECISION: Legal issues or contract disputes.
        3. ESCALATE: Harmful or nonsensical requests.
        Request: "{user_request}"
        Return ONLY JSON: {{ "route": "ANALYTICS" | "TICKET_DECISION" | "ESCALATE", "reason": "string" }}
        """
        original_prompt = self.engine.system_prompt
        self.engine.system_prompt = routing_prompt.strip()
        
        try:
            decision = self.engine.decide(user_request)
            self.engine.system_prompt = original_prompt
            return RouterResult(
                route=decision.get("route", "TICKET_DECISION"), 
                reason=decision.get("reason", "LLM decision")
            )
        except:
            self.engine.system_prompt = original_prompt
            return RouterResult(route="TICKET_DECISION", reason="Fallback to default")