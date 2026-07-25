"""Rutas de evaluación agronómica."""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.models.schemas import CultivoEnum, EvaluacionRequest, EvaluacionResponse, TipoEvaluacionEnum
from app.services.evaluacion_service import procesar_evaluacion

router = APIRouter(prefix="/evaluar", tags=["Evaluación"])


@router.post("", response_model=EvaluacionResponse)
async def evaluar(
    cultivo: CultivoEnum = Form(...),
    tipo_evaluacion: TipoEvaluacionEnum = Form(...),
    ubicacion: str = Form(..., min_length=2, max_length=255),
    texto: str | None = Form(default=None, max_length=5000),
    audio: UploadFile | None = File(default=None),
):
    """Recibe datos del formulario con texto y/o audio opcionales."""
    texto_limpio = texto.strip() if texto else None

    if not texto_limpio and (not audio or not audio.filename):
        raise HTTPException(
            status_code=422,
            detail="Incluí al menos una nota de texto o un archivo de audio.",
        )

    datos = EvaluacionRequest(
        cultivo=cultivo,
        tipo_evaluacion=tipo_evaluacion,
        ubicacion=ubicacion.strip(),
        texto=texto_limpio,
    )

    try:
        return procesar_evaluacion(datos, audio=audio)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
