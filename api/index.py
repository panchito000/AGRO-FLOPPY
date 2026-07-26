"""Punto de entrada serverless para Vercel."""

import sys
from pathlib import Path

from fastapi import FastAPI

backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from main import app as core_app

app = FastAPI(title="AgroFloppy Gateway", docs_url=None, redoc_url=None)
app.mount("/api", core_app)
