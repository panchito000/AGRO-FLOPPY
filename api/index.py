"""Punto de entrada serverless para Vercel."""

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

backend_dir = Path(__file__).resolve().parent.parent / "backend"
public_dir = Path(__file__).resolve().parent.parent / "public"
sys.path.insert(0, str(backend_dir))

from main import app as core_app

app = FastAPI(title="AGRO-FLOPPY Gateway", docs_url=None, redoc_url=None)
app.mount("/api", core_app)

if public_dir.exists():
    app.mount("/", StaticFiles(directory=str(public_dir), html=True), name="frontend")
