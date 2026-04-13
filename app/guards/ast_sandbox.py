import ast
from typing import Iterable, Set

ALLOWED_FUNCTIONS: Set[str] = {
    "mean", "count", "max", "sum", "min", "median", "std", 
    "groupby", "agg", "nunique", "value_counts",
    "to_datetime", "dt", "year", "month", "days" 
}

FORBIDDEN_ATTRIBUTES: Set[str] = {"head", "tail", "iloc", "loc", "sample", "to_csv"}

def validate_analytics_code(code: str) -> None:
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef)):
            raise ValueError("Forbidden syntax.")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr not in ALLOWED_FUNCTIONS:
                raise ValueError(f"Forbidden function: {node.func.attr}")