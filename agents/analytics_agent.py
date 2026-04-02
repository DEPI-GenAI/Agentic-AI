from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from core.guards.ast_sandbox import validate_analytics_code
from core.guards.security_guard import guard_analytics_question
from core.models.groq_validator import GroqCodeValidator
from core.models.llm_analytics import AnalyticsCodeLLM


@dataclass(frozen=True)
class AnalyticsResult:
    action: str
    reason: str
    data: Optional[Any] = None


class AnalyticsAgent:
    """
    Productionized analytics agent:
      1) Guard question (AUTHORIZED / UNAUTHORIZED / ASK_FOR_MORE_INFO)
      2) If authorized → generate pandas code with LLM
      3) Run AST sandbox checks
      4) Execute safely against a configured DataFrame
    """

    def __init__(self, df: Optional[Any] = None) -> None:
        # df can be injected from outside; if not available, we degrade gracefully.
        self._df = df
        self._llm = AnalyticsCodeLLM()
        self._validator = GroqCodeValidator()

    def _ensure_df(self) -> Optional[Any]:
        # In your own project you can load a real CSV here (e.g. from memory/).
        return self._df

    def answer(self, user_request: str) -> Dict[str, Any]:
        df = self._ensure_df()
        guard = guard_analytics_question(user_request)

        if guard.decision == "UNAUTHORIZED":
            return AnalyticsResult(
                action="ESCALATE_TO_HUMAN",
                reason=guard.reason,
                data={"tool": "escalate_to_human", "user_question": user_request},
            ).__dict__

        if guard.decision == "ASK_FOR_MORE_INFO":
            return AnalyticsResult(
                action="ASK_FOR_MORE_INFO",
                reason=guard.reason,
                data=None,
            ).__dict__

        # AUTHORIZED case
        if df is None:
            return AnalyticsResult(
                action="ASK_FOR_MORE_INFO",
                reason="Analytics dataframe is not configured on the server yet.",
                data=None,
            ).__dict__

        schema = {
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "rows": len(df),
        }

        try:
            code = self._llm.gen_code(user_request, schema)
            validation = self._validator.validate_code(user_request, schema, code)
            if not validation.get("is_valid", False):
                return AnalyticsResult(
                    action="ASK_FOR_MORE_INFO",
                    reason=f"Validator rejected generated code: {validation.get('reason', 'unknown issue')}",
                    data={"issues": validation.get("issues", [])},
                ).__dict__
            validate_analytics_code(code)

            safe_globals = {
                "__builtins__": {},
                "df": df,
            }
            # Add pandas if available without crashing import-time.
            try:
                import pandas as pd
                safe_globals["pd"] = pd
            except Exception:
                pass
            safe_locals: Dict[str, Any] = {}

            exec(code, safe_globals, safe_locals)
            if "result" not in safe_locals:
                raise ValueError("Generated code did not assign to 'result'.")

            result_value = safe_locals["result"]
            return AnalyticsResult(
                action="ANSWER",
                reason="Analytics query executed successfully.",
                data=str(result_value),
            ).__dict__

        except Exception as exc:
            return AnalyticsResult(
                action="ASK_FOR_MORE_INFO",
                reason=f"Analytics agent failed to answer safely: {exc}",
                data=None,
            ).__dict__
