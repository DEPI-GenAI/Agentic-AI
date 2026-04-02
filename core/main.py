"""
Backward-compatible module.

Use `core/api/app.py` as the main FastAPI entry point:
  uvicorn core.api.app:app --reload
"""

from api.app import app  # re-export