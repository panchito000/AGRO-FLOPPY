"""Búsqueda en base de conocimiento (Supabase + índice JSON local)."""

from __future__ import annotations

import json
import logging
import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

INDEX_PATH = Path(__file__).resolve().parents[1] / "data" / "conocimiento_index.json"

STOPWORDS = {
    "que", "qué", "como", "cómo", "para", "con", "del", "las", "los", "una", "uno",
    "por", "esta", "este", "zona", "puede", "puedo", "decir", "sobre", "hay", "tiene",
}


@dataclass
class FragmentoConocimiento:
    contenido: str
    fuente_cita: str
    documento_titulo: str
    documento_tipo: str
    score: float = 0.0


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9\s]", " ", texto)


def _tokens(texto: str | None) -> set[str]:
    if not texto:
        return set()
    return {t for t in _normalizar(texto).split() if len(t) > 2 and t not in STOPWORDS}


def _score_chunk(
    chunk: dict,
    tokens: set[str],
    cultivo: str,
    tipo_evaluacion: str,
) -> float:
    score = 0.0
    contenido = _normalizar(chunk.get("contenido", ""))
    chunk_tokens = set(contenido.split())

    overlap = tokens & chunk_tokens
    score += len(overlap) * 2.0

    if chunk.get("cultivo") == cultivo:
        score += 4.0
    if chunk.get("tipo_evaluacion") == tipo_evaluacion:
        score += 5.0

    for tag in chunk.get("etiquetas") or []:
        if _normalizar(tag) in tokens:
            score += 1.5

    if tipo_evaluacion == "plagas" and "plaga" in contenido:
        score += 2.0
    if tipo_evaluacion == "siembra" and "siembra" in contenido:
        score += 2.0

    return score


@lru_cache(maxsize=1)
def _cargar_indice_local() -> list[dict]:
    if not INDEX_PATH.exists():
        logger.warning("Índice de conocimiento no encontrado: %s", INDEX_PATH)
        return []
    try:
        data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        return data.get("chunks", [])
    except Exception as exc:
        logger.exception("Error leyendo índice local: %s", exc)
        return []


def _buscar_en_lista(
    chunks: list[dict],
    *,
    cultivo: str,
    tipo_evaluacion: str,
    texto: str | None,
    limit: int,
) -> list[FragmentoConocimiento]:
    tokens = _tokens(texto or "")
    if not tokens:
        tokens = _tokens(f"{cultivo} {tipo_evaluacion}")

    scored: list[tuple[float, dict]] = []
    for ch in chunks:
        s = _score_chunk(ch, tokens, cultivo, tipo_evaluacion)
        if s > 0:
            scored.append((s, ch))

    scored.sort(key=lambda x: x[0], reverse=True)
    if not scored:
        for ch in chunks:
            if ch.get("cultivo") == cultivo and ch.get("tipo_evaluacion") == tipo_evaluacion:
                scored.append((1.0, ch))
            elif ch.get("tipo_evaluacion") == tipo_evaluacion:
                scored.append((0.5, ch))

    result: list[FragmentoConocimiento] = []
    seen: set[str] = set()
    for s, ch in scored[: limit * 2]:
        key = ch.get("contenido", "")[:120]
        if key in seen:
            continue
        seen.add(key)
        meta = ch.get("metadata") or {}
        result.append(
            FragmentoConocimiento(
                contenido=ch["contenido"],
                fuente_cita=ch.get("fuente_cita") or ch.get("documento_titulo", "Fuente interna"),
                documento_titulo=meta.get("documento_titulo") or ch.get("documento_titulo", "Base Zafra"),
                documento_tipo=ch.get("documento_tipo", "codigo"),
                score=s,
            )
        )
        if len(result) >= limit:
            break
    return result


def _buscar_en_db(
    db: Session,
    *,
    cultivo: str,
    tipo_evaluacion: str,
    texto: str | None,
    limit: int,
) -> list[FragmentoConocimiento]:
    from app.models.db_models import Documento, DocumentoChunk

    q = (
        select(DocumentoChunk, Documento)
        .join(Documento, Documento.id == DocumentoChunk.documento_id)
    )
    filtros = [
        or_(DocumentoChunk.cultivo == cultivo, DocumentoChunk.cultivo.is_(None)),
        or_(
            DocumentoChunk.tipo_evaluacion == tipo_evaluacion,
            DocumentoChunk.tipo_evaluacion.is_(None),
        ),
    ]
    rows = db.execute(q.where(*filtros).limit(200)).all()

    chunks = []
    for chunk, doc in rows:
        chunks.append({
            "contenido": chunk.contenido,
            "fuente_cita": chunk.fuente_cita,
            "documento_titulo": doc.titulo,
            "documento_tipo": doc.tipo,
            "cultivo": chunk.cultivo,
            "tipo_evaluacion": chunk.tipo_evaluacion,
            "etiquetas": chunk.etiquetas or [],
        })
    return _buscar_en_lista(chunks, cultivo=cultivo, tipo_evaluacion=tipo_evaluacion, texto=texto, limit=limit)


def buscar_conocimiento(
    *,
    cultivo: str,
    tipo_evaluacion: str,
    texto: str | None = None,
    db: Session | None = None,
    limit: int = 3,
) -> list[FragmentoConocimiento]:
    """Busca fragmentos relevantes en Supabase o índice JSON embebido."""
    if db is not None:
        try:
            from sqlalchemy import func

            from app.models.db_models import DocumentoChunk

            count = db.scalar(select(func.count()).select_from(DocumentoChunk))
            if count and count > 0:
                return _buscar_en_db(
                    db, cultivo=cultivo, tipo_evaluacion=tipo_evaluacion, texto=texto, limit=limit
                )
        except Exception as exc:
            logger.warning("Búsqueda en BD falló, usando índice local: %s", exc)

    return _buscar_en_lista(
        _cargar_indice_local(),
        cultivo=cultivo,
        tipo_evaluacion=tipo_evaluacion,
        texto=texto,
        limit=limit,
    )


def fuentes_clima(nombres: list[str]) -> list[str]:
    mapping = {
        "openmeteo": "Open-Meteo (clima en vivo)",
        "wttr": "wttr.in (clima en vivo)",
        "foreca": "Foreca/ANAPO (clima en vivo)",
    }
    return [mapping.get(n, n) for n in nombres]


def formatear_fuentes(
    *,
    fuentes_clima_list: list[str],
    fragmentos: list[FragmentoConocimiento],
) -> list[str]:
    fuentes: list[str] = []
    for f in fuentes_clima_list:
        if f not in fuentes:
            fuentes.append(f)
    for fr in fragmentos:
        cite = fr.fuente_cita.strip()
        if cite and cite not in fuentes:
            fuentes.append(cite)
    return fuentes[:6]
