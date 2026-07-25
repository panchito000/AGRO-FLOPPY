"""Servicios de negocio (lógica futura)."""

import uuid
from pathlib import Path

from fastapi import UploadFile

from app.models.schemas import EvaluacionRequest, EvaluacionResponse

UPLOADS_DIR = Path(__file__).resolve().parents[2] / "uploads" / "audio"
ALLOWED_AUDIO_TYPES = {
    "audio/webm",
    "audio/ogg",
    "audio/mpeg",
    "audio/mp4",
    "audio/wav",
    "audio/x-wav",
    "audio/aac",
}


def _guardar_audio(audio: UploadFile) -> tuple[str, int]:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    extension = Path(audio.filename or "nota.webm").suffix or ".webm"
    nombre_guardado = f"{uuid.uuid4().hex}{extension}"
    destino = UPLOADS_DIR / nombre_guardado

    contenido = audio.file.read()
    destino.write_bytes(contenido)

    return nombre_guardado, len(contenido)


def procesar_evaluacion(
    datos: EvaluacionRequest,
    audio: UploadFile | None = None,
) -> EvaluacionResponse:
    """
    Procesa una evaluación agronómica con texto y/o audio opcionales.
    Por ahora devuelve los datos recibidos sin lógica adicional.
    """
    texto = datos.texto.strip() if datos.texto else None
    audio_recibido = False
    audio_nombre = None
    audio_tamano = None

    if audio and audio.filename:
        content_type = audio.content_type or ""
        if content_type and content_type not in ALLOWED_AUDIO_TYPES:
            raise ValueError(
                f"Formato de audio no soportado ({content_type}). "
                "Usá webm, ogg, mp3, wav o m4a."
            )

        audio_nombre, audio_tamano = _guardar_audio(audio)
        audio_recibido = True

    partes_mensaje = ["Datos recibidos correctamente."]
    if texto:
        partes_mensaje.append("Texto incluido.")
    if audio_recibido:
        partes_mensaje.append("Audio incluido.")
    partes_mensaje.append("Lógica de evaluación pendiente.")

    return EvaluacionResponse(
        cultivo=datos.cultivo.value,
        tipo_evaluacion=datos.tipo_evaluacion.value,
        ubicacion=datos.ubicacion,
        texto=texto,
        audio_recibido=audio_recibido,
        audio_nombre=audio_nombre,
        audio_tamano_bytes=audio_tamano,
        mensaje=" ".join(partes_mensaje),
    )
