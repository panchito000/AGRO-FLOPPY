"""Punto de entrada serverless para Vercel."""

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

backend_dir = Path(__file__).resolve().parent.parent / "backend"
public_dir = Path(__file__).resolve().parent.parent / "public"
sys.path.insert(0, str(backend_dir))

from main import app as core_app

app = FastAPI(title="AGRO-FLOPPY Gateway", docs_url=None, redoc_url=None)
app.mount("/api", core_app)

if public_dir.exists():
    app.mount("/css", StaticFiles(directory=str(public_dir / "css")), name="css")
    app.mount("/js", StaticFiles(directory=str(public_dir / "js")), name="js")
    app.mount("/assets", StaticFiles(directory=str(public_dir / "assets")), name="assets")

    @app.get("/")
    async def serve_index():
        return FileResponse(public_dir / "index.html")

    @app.get("/index.html")
    async def serve_index_html():
        return FileResponse(public_dir / "index.html")
