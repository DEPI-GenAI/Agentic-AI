from __future__ import annotations

from typing import Any, Dict, Optional

from core.agents.analytics_agent import AnalyticsAgent
from core.agents.router_agent import RouterAgent
from core.agents.ticket_agent import TicketAgent


class Orchestrator:
    """
    The "one huge agent": a single entry point that routes to sub-agents/tools.
    """

    def __init__(
        self,
        router: Optional[RouterAgent] = None,
        ticket_agent: Optional[TicketAgent] = None,
        analytics_agent: Optional[AnalyticsAgent] = None,
    ) -> None:
        self.router = router or RouterAgent()
        self.ticket_agent = ticket_agent or TicketAgent()
        self.analytics_agent = analytics_agent or AnalyticsAgent()

    def handle_request(self, user_request: str) -> Dict[str, Any]:
        decision = self.router.route(user_request)

        if decision.route == "TICKET_DECISION":
            out = self.ticket_agent.decide(user_request)
            out["route"] = decision.route
            out["route_reason"] = decision.reason
            return out

        if decision.route == "ANALYTICS":
            out = self.analytics_agent.answer(user_request)
            out["route"] = decision.route
            out["route_reason"] = decision.reason
            return out

        return {
            "action": "ESCALATE_TO_HUMAN",
            "reason": "Router escalated request",
            "route": decision.route,
            "route_reason": decision.reason,
        }

