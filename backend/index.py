"""Vercel ASGI entrypoint for the FastAPI backend.

The Vercel project root is configured as `backend/`, so this module exposes
`app` at the root expected by the Python runtime.
"""

from app.main import app

__all__ = ["app"]
