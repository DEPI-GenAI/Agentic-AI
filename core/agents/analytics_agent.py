from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional, List
import pandas as pd

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
    def __init__(self, df: Any = None, max_retries: int = 3) -> None:
        self._df = df
        self._llm = AnalyticsCodeLLM()
        self._validator = GroqCodeValidator()
        self.max_retries = max_retries

    def _infer_schema_mapping(self, user_request: str, columns: list) -> dict:
        mapping_prompt = f"""
        You are a data schema mapper. Compare the user's question to the available columns.
        Columns: {columns}
        Question: "{user_request}"
        Rules:
        1. Identify synonyms (e.g., "pay" -> "salary", "dept" -> "department").
        2. If a term matches multiple columns, set is_ambiguous to true.
        Return ONLY JSON:
        {{ "mapped_query": "translated question", "is_ambiguous": false, "suggestions": [] }}
        """
        raw_result = self._llm.gen_code(mapping_prompt, {"task": "mapping"})
        try:
            return json.loads(raw_result) if isinstance(raw_result, str) else raw_result
        except:
            return {"mapped_query": user_request, "is_ambiguous": False, "suggestions": []}

    def _repair_logic(self, question: str, schema: dict, code: str, error: str) -> str:
        repair_prompt = f"Fix this pandas code.\nQuestion: {question}\nError: {error}\nBroken Code: {code}\nReturn ONLY fixed code."
        return self._llm.gen_code(repair_prompt, schema)

    def answer(self, user_request: str) -> Dict[str, Any]:
        df = self._df
        if df is None:
            return AnalyticsResult(action="ASK_FOR_MORE_INFO", reason="Dataframe not configured.").__dict__

        guard = guard_analytics_question(user_request)
        if guard.decision != "AUTHORIZED":
            return AnalyticsResult(action=guard.decision, reason=guard.reason).__dict__

        mapping = self._infer_schema_mapping(user_request, list(df.columns))
        if mapping.get("is_ambiguous"):
            return AnalyticsResult(action="CLARIFY", reason="Ambiguous columns.", data=mapping.get("suggestions")).__dict__

        effective_query = mapping.get("mapped_query", user_request)
        schema = {"columns": list(df.columns), "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}, "rows": len(df)}

        code = self._llm.gen_code(effective_query, schema)
        
        for attempt in range(self.max_retries):
            try:
                validation = self._validator.validate_code(effective_query, schema, code)
                if not validation.get("is_valid", False):
                    raise ValueError(f"Logic Error: {validation.get('reason')}")

                validate_analytics_code(code)

                safe_globals = {"__builtins__": {}, "df": df, "pd": pd}
                safe_locals = {}
                exec(code, safe_globals, safe_locals)
                
                if "result" not in safe_locals:
                    raise ValueError("Code did not assign to 'result'.")

                return AnalyticsResult(action="ANSWER", reason="Success", data=str(safe_locals["result"])).__dict__

            except Exception as exc:
                if attempt == self.max_retries - 1:
                    return AnalyticsResult(action="ASK_FOR_MORE_INFO", reason=f"Failed after retries: {exc}").__dict__
                code = self._repair_logic(effective_query, schema, code, str(exc))