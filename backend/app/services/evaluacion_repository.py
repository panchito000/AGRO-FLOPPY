"""Persistencia de evaluaciones en Supabase/PostgreSQL."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.db_models import ClimaCache, Cultivo, Evaluacion, TipoEvaluacion
from app.models.schemas import EvaluacionRequest, EvaluacionResponse

logger = logging.getLogger(__name__)

CACHE_TTL_MINUTES = 30


def _get_cultivo_id(db: Session, nombre: str) -> int | None:
    cultivo = db.scalar(select(Cultivo).where(Cultivo.nombre == nombre))
    return cultivo.id if cultivo else None


def _get_tipo_evaluacion_id(db: Session, codigo: str) -> int | None:
    tipo = db.scalar(select(TipoEvaluacion).where(TipoEvaluacion.codigo == codigo))
    return tipo.id if tipo else None


def guardar_evaluacion(
    db: Session,
    datos: EvaluacionRequest,
    respuesta: EvaluacionResponse,
    *,
    audio_mime_type: str | None = None,
    audio_storage_path: str | None = None,
    clima_json: dict | None = None,
) -> int | None:
    cultivo_id = _get_cultivo_id(db, datos.cultivo.value)
    tipo_id = _get_tipo_evaluacion_id(db, datos.tipo_evaluacion.value)

    if not cultivo_id or not tipo_id:
        logger.warning("Catálogos no encontrados en BD. ¿Aplicaste database/schema.sql?")
        return None

    evaluacion = Evaluacion(
        cultivo_id=cultivo_id,
        tipo_evaluacion_id=tipo_id,
        ubicacion=datos.ubicacion,
        latitud=datos.latitud,
        longitud=datos.longitud,
        texto=datos.texto,
        audio_nombre=respuesta.audio_nombre,
        audio_mime_type=audio_mime_type,
        audio_tamano_bytes=respuesta.audio_tamano_bytes,
        audio_storage_path=audio_storage_path,
        recomendacion=respuesta.recomendacion,
        explicacion=respuesta.explicacion,
        clima_json=clima_json,
        estado="completada",
        mensaje=respuesta.mensaje,
    )
    db.add(evaluacion)
    db.commit()
    db.refresh(evaluacion)
    return evaluacion.id


def upsert_clima_cache(db: Session, lat: float, lon: float, datos: dict) -> None:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=CACHE_TTL_MINUTES)
    existente = db.scalar(
        select(ClimaCache).where(ClimaCache.latitud == lat, ClimaCache.longitud == lon)
    )
    if existente:
        existente.datos = datos
        existente.fetched_at = datetime.now(timezone.utc)
        existente.expires_at = expires_at
    else:
        db.add(ClimaCache(latitud=lat, longitud=lon, datos=datos, expires_at=expires_at))
    db.commit()
