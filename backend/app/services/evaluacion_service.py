"""Servicios de negocio — evaluación agronómica con clima y persistencia."""

from __future__ import annotations

import logging
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.models.schemas import EvaluacionRequest, EvaluacionResponse
from app.services.clima import evaluar_agronomico
from app.services.evaluacion_repository import guardar_evaluacion, upsert_clima_cache

logger = logging.getLogger(__name__)

UPLOADS_DIR = settings.uploads_path
ALLOWED_AUDIO_TYPES = {
    "audio/webm",
    "audio/ogg",
    "audio/mpeg",
    "audio/mp4",
    "audio/wav",
    "audio/x-wav",
    "audio/aac",
}


def _guardar_audio(audio: UploadFile) -> tuple[str, int, str | None]:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    extension = Path(audio.filename or "nota.webm").suffix or ".webm"
    nombre_guardado = f"{uuid.uuid4().hex}{extension}"
    destino = UPLOADS_DIR / nombre_guardado

    contenido = audio.file.read()
    destino.write_bytes(contenido)

    return nombre_guardado, len(contenido), audio.content_type


def _persistir(
    db: Session | None,
    datos: EvaluacionRequest,
    respuesta: EvaluacionResponse,
    *,
    audio_mime_type: str | None,
    clima_json: dict | None,
) -> int | None:
    if db is None:
        return None
    try:
        evaluacion_id = guardar_evaluacion(
            db,
            datos,
            respuesta,
            audio_mime_type=audio_mime_type,
            clima_json=clima_json,
        )
        if evaluacion_id and datos.latitud is not None and datos.longitud is not None and clima_json:
            upsert_clima_cache(db, datos.latitud, datos.longitud, clima_json)
        return evaluacion_id
    except SQLAlchemyError as exc:
        logger.exception("No se pudo persistir la evaluación: %s", exc)
        db.rollback()
        return None


def procesar_evaluacion(
    datos: EvaluacionRequest,
    audio: UploadFile | None = None,
    db: Session | None = None,
) -> EvaluacionResponse:
    """Procesa evaluación con clima en vivo, reglas agronómicas y persistencia opcional."""
    texto = datos.texto.strip() if datos.texto else None
    audio_recibido = False
    audio_nombre = None
    audio_tamano = None
    audio_mime_type = None

    if audio and audio.filename:
        content_type = audio.content_type or ""
        if content_type and content_type not in ALLOWED_AUDIO_TYPES:
            raise ValueError(
                f"Formato de audio no soportado ({content_type}). "
                "Usá webm, ogg, mp3, wav o m4a."
            )
        audio_nombre, audio_tamano, audio_mime_type = _guardar_audio(audio)
        audio_recibido = True

    agronomia = evaluar_agronomico(
        cultivo=datos.cultivo.value,
        tipo_evaluacion=datos.tipo_evaluacion.value,
        lat=datos.latitud,
        lon=datos.longitud,
        ubicacion_nombre=datos.ubicacion,
        texto=texto,
        db=db,
    )

    clima_completo = agronomia.get("clima_completo")

    mensaje_partes = ["Evaluación procesada correctamente."]
    if texto:
        mensaje_partes.append("Texto incluido.")
    if audio_recibido:
        mensaje_partes.append("Audio incluido.")
    if agronomia.get("semaforo"):
        mensaje_partes.append(f"Semáforo: {agronomia['semaforo']}.")

    respuesta = EvaluacionResponse(
        cultivo=datos.cultivo.value,
        tipo_evaluacion=datos.tipo_evaluacion.value,
        ubicacion=datos.ubicacion,
        latitud=datos.latitud,
        longitud=datos.longitud,
        texto=texto,
        audio_recibido=audio_recibido,
        audio_nombre=audio_nombre,
        audio_tamano_bytes=audio_tamano,
        mensaje=" ".join(mensaje_partes),
        veredicto=agronomia.get("veredicto"),
        semaforo=agronomia.get("semaforo"),
        condiciones_actuales=agronomia.get("condiciones_actuales"),
        advertencias=agronomia.get("advertencias", []),
        recomendacion=agronomia.get("recomendacion"),
        explicacion=agronomia.get("explicacion"),
        fuentes_usadas=agronomia.get("fuentes_usadas", []),
        fuentes_conocimiento=agronomia.get("fuentes_conocimiento", []),
        producto_evaluado=agronomia.get("producto_evaluado"),
    )

    evaluacion_id = _persistir(
        db,
        datos,
        respuesta,
        audio_mime_type=audio_mime_type,
        clima_json=clima_completo,
    )
    respuesta.evaluacion_id = evaluacion_id
    return respuesta
