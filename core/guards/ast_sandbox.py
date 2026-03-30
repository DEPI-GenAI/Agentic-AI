from __future__ import annotations

import ast
from typing import Iterable, Set


ALLOWED_FUNCTIONS: Set[str] = {
    "mean",
    "count",
    "max",
    "sum",
    "min",
    "median",
    "std",
    "groupby",
    "agg",
    "nunique",
    "value_counts",
}

FORBIDDEN_ATTRIBUTES: Set[str] = {
    "head",
    "tail",
    "iloc",
    "loc",
    "sample",
    "values",
    "tolist",
    "to_dict",
    "to_csv",
    "plot",
}


FORBIDDEN_NODES: Iterable[type] = (
    ast.Import,
    ast.ImportFrom,
    ast.With,
    ast.Try,
    ast.FunctionDef,
    ast.ClassDef,
)


def validate_analytics_code(code: str) -> None:
    """
    Static safety checks for pandas analytics code.

    Raises ValueError if something unsafe or disallowed is detected.
    """
    tree = ast.parse(code)

    for node in ast.walk(tree):
        if isinstance(node, FORBIDDEN_NODES):
            raise ValueError("Forbidden syntax detected in generated code.")

        if isinstance(node, ast.Call):
            # df.some_func(...)
            if isinstance(node.func, ast.Attribute):
                attr = node.func.attr
                if attr in FORBIDDEN_ATTRIBUTES:
                    raise ValueError(f"Forbidden operation '{attr}' is not allowed.")
                if attr not in ALLOWED_FUNCTIONS:
                    raise ValueError(f"The function '{attr}' is not in the allowed functions list.")

        # direct attribute access like df.values
        if isinstance(node, ast.Attribute):
            if node.attr in FORBIDDEN_ATTRIBUTES:
                raise ValueError(f"Forbidden attribute access '{node.attr}' is not allowed.")

