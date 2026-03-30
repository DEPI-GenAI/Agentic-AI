from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


GuardDecision = Literal["AUTHORIZED", "UNAUTHORIZED", "ASK_FOR_MORE_INFO"]


@dataclass(frozen=True)
class GuardResult:
    decision: GuardDecision
    reason: str


AGGREGATION_KEYWORDS = (
    "average",
    "mean",
    "count",
    "sum",
    "min",
    "max",
    "median",
    "std",
    "group by",
    "groupby",
    "per ",
    "by ",
    "nunique",
)

RAW_DATA_KEYWORDS = (
    "show all rows",
    "show the first",
    "head(",
    "tail(",
    "sample of",
    "list of",
    "return all",
    "display rows",
)


def guard_analytics_question(user_question: str) -> GuardResult:
    """
    Lightweight guard inspired by AUTHORIZED_SYSTEM_PROMPT from the notebook.

    Classifies a question as:
      - AUTHORIZED         → clearly aggregated analytics
      - UNAUTHORIZED       → tries to expose raw data
      - ASK_FOR_MORE_INFO  → too vague / unclear
    """
    text = (user_question or "").lower().strip()

    if any(k in text for k in RAW_DATA_KEYWORDS):
        return GuardResult(
            decision="UNAUTHORIZED",
            reason="Request appears to expose raw rows or detailed records.",
        )

    if any(k in text for k in AGGREGATION_KEYWORDS):
        return GuardResult(
            decision="AUTHORIZED",
            reason="Question looks like an aggregate analytics query.",
        )

    return GuardResult(
        decision="ASK_FOR_MORE_INFO",
        reason="Question is ambiguous; ask for a more specific aggregated query.",
    )

