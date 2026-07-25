"""Esquemas Pydantic para validación de requests/responses."""

from enum import Enum

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
    texto: str | None = Field(default=None, max_length=5000)


class EvaluacionResponse(BaseModel):
    cultivo: str
    tipo_evaluacion: str
    ubicacion: str
    texto: str | None = None
    audio_recibido: bool = False
    audio_nombre: str | None = None
    audio_tamano_bytes: int | None = None
    mensaje: str = "Datos recibidos correctamente. Lógica de evaluación pendiente."
