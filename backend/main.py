"""Punto de entrada de la API Zafra AI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import evaluar_router, health_router

app = FastAPI(
    title="Zafra AI API",
    description="Copiloto inteligente para decisiones agronómicas en soya y maíz.",
    version="0.1.0",
    root_path=settings.root_path,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(evaluar_router)
