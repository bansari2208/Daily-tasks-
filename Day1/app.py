"""AI Career Mentor Agent entrypoint.

Re-exports FastAPI app from the modular app package.
"""
from app.main import app

__all__ = ["app"]