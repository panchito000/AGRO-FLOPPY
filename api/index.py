"""Punto de entrada serverless para Vercel."""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI

from main import app as core_app

# Monta la API bajo /api para convivir con el frontend estático
app = FastAPI(title="AGRO-FLOPPY Gateway", docs_url=None, redoc_url=None)
app.mount("/api", core_app)
