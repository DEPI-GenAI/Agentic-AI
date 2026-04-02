from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Route = Literal["TICKET_DECISION", "ANALYTICS", "ESCALATE"]


@dataclass(frozen=True)
class RouterResult:
    route: Route
    reason: str


class RouterAgent:
    """
    Very small router for now.

    You can later swap this to an LLM-based router (like the notebooks' workflow router).
    """

    def route(self, user_request: str) -> RouterResult:
        text = (user_request or "").lower()

        analytics_keywords = (
            "average",
            "mean",
            "count",
            "sum",
            "median",
            "std",
            "group by",
            "groupby",
            "dataset",
            "dataframe",
            "df",
            "csv",
            "tickets data",
        )
        ticket_keywords = (
            "contract",
            "agreement",
            "breach",
            "supplier",
            "deliver",
            "deliveries",
            "payment",
            "invoice dispute",
            "legal",
            "clause",
        )

        if any(k in text for k in analytics_keywords):
            return RouterResult(route="ANALYTICS", reason="Matched analytics keywords")
        if any(k in text for k in ticket_keywords):
            return RouterResult(route="TICKET_DECISION", reason="Matched contract/ticket keywords")

        # Default to ticket decision engine (safe decision-only behavior)
        return RouterResult(route="TICKET_DECISION", reason="Default route")

