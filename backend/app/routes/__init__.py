"""Rutas de la API."""

from app.routes.evaluar import router as evaluar_router
from app.routes.health import router as health_router

__all__ = ["health_router", "evaluar_router"]
