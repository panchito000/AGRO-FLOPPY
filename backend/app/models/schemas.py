"""Esquemas Pydantic para validación de requests/responses."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CultivoEnum(str, Enum):
    SOYA = "soya"
    MAIZ = "maiz"


class TipoEvaluacionEnum(str, Enum):
    SIEMBRA = "siembra"
    FERTILIZACION = "fertilizacion"
    RIEGO = "riego"
    PLAGAS = "plagas"
    COSECHA = "cosecha"


class EvaluacionRequest(BaseModel):
    cultivo: CultivoEnum
    tipo_evaluacion: TipoEvaluacionEnum
    ubicacion: str = Field(..., min_length=2, max_length=255)
    latitud: float | None = Field(default=None, ge=-90, le=90)
    longitud: float | None = Field(default=None, ge=-180, le=180)
    texto: str | None = Field(default=None, max_length=5000)


class EvaluacionResponse(BaseModel):
    cultivo: str
    tipo_evaluacion: str
    ubicacion: str
    latitud: float | None = None
    longitud: float | None = None
    texto: str | None = None
    audio_recibido: bool = False
    audio_nombre: str | None = None
    audio_tamano_bytes: int | None = None
    mensaje: str = "Evaluación procesada correctamente."
    evaluacion_id: int | None = None
    veredicto: str | None = None
    semaforo: str | None = None
    condiciones_actuales: dict[str, Any] | None = None
    advertencias: list[dict[str, Any]] = Field(default_factory=list)
    recomendacion: str | None = None
    explicacion: str | None = None
    fuentes_usadas: list[str] = Field(default_factory=list)
    producto_evaluado: str | None = None
