from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from core.guards.ast_sandbox import validate_analytics_code
from core.guards.security_guard import guard_analytics_question
from core.models.groq_validator import GroqCodeValidator
from core.models.llm_analytics import AnalyticsCodeLLM


def escalate_to_human(reason: str, user_question: str) -> Dict[str, str]:
    return {
        "tool": "escalate_to_human",
        "reason": reason,
        "user_question": user_question,
    }


@dataclass
class AnalyticsFlow:
    """
    Extracted from notebook's secure analytics pipeline:
    Guard -> Generate -> Validate -> AST -> Execute
    """

    def run(self, df: Any, user_question: str) -> Dict[str, Any]:
        guard = guard_analytics_question(user_question)
        if guard.decision == "UNAUTHORIZED":
            return {
                "action": "ESCALATE_TO_HUMAN",
                "reason": guard.reason,
                "data": escalate_to_human("unauthorized_data_access", user_question),
            }
        if guard.decision == "ASK_FOR_MORE_INFO":
            return {
                "action": "ASK_FOR_MORE_INFO",
                "reason": "Could you clarify your request? Ask about averages, counts, or grouped comparisons.",
            }

        schema = {
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "rows": len(df),
        }

        llm = AnalyticsCodeLLM()
        validator = GroqCodeValidator()
        code = llm.gen_code(user_question, schema)
        validation = validator.validate_code(user_question, schema, code)
        if not validation.get("is_valid", False):
            return {
                "action": "ASK_FOR_MORE_INFO",
                "reason": validation.get("reason", "Generated code failed validation."),
                "data": {"issues": validation.get("issues", [])},
            }

        validate_analytics_code(code)

        safe_globals = {"__builtins__": {}, "df": df}
        safe_locals: Dict[str, Any] = {}
        exec(code, safe_globals, safe_locals)

        if "result" not in safe_locals:
            return {"action": "ASK_FOR_MORE_INFO", "reason": "Could not compute result safely."}

        return {
            "action": "ANSWER",
            "reason": "Analytics query executed successfully.",
            "data": str(safe_locals["result"]),
            "code": code,
        }

