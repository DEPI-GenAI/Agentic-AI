"""
Backward-compatible module.

Use `core/api/app.py` as the main FastAPI entry point:
  uvicorn core.api.app:app --reload
"""

from core.api.app import app  # re-export