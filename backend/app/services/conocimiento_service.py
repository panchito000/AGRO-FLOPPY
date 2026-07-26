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
    "quiero", "saber", "hablar", "hablame", "cosas", "hora", "hoy", "esta",
}

SINONIMOS_BUSQUEDA = {
    "regar": "riego",
    "regando": "riego",
    "sembrar": "siembra",
    "sembrando": "siembra",
    "plantar": "siembra",
    "fertilizar": "fertilizacion",
    "abonar": "fertilizacion",
    "cosechar": "cosecha",
    "plaga": "plagas",
    "plagas": "plagas",
    "prevenir": "plagas",
    "prevencion": "plagas",
    "insectos": "plagas",
    "enfermedades": "plagas",
    "epocas": "siembra",
    "epoca": "siembra",
    "evitar": "evitar",
    "anapo": "anapo",
    "suelo": "suelo",
    "directa": "siembra",
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
    base = {t for t in _normalizar(texto).split() if len(t) > 2 and t not in STOPWORDS}
    extra: set[str] = set()
    for t in base:
        if t in SINONIMOS_BUSQUEDA:
            extra.add(SINONIMOS_BUSQUEDA[t])
    return base | extra


def _coincide(texto: str, *patrones: str) -> bool:
    return any(re.search(p, texto) for p in patrones)


def _texto_pide_evitar(texto: str | None, tipo_evaluacion: str) -> bool:
    """True solo si el usuario pregunta explícitamente qué NO hacer o peores prácticas."""
    if not texto:
        return False
    t = _normalizar(texto)
    comunes = (
        r"peor(es)?\s+(formas?|maneras?|momentos?|epocas?|practicas?)",
        r"no\s+deber[ií]a\s+hacer",
        r"cosas?\s+no\s+deber[ií]a",
        r"qu[eé]\s+cosas?\s+no",
        r"qu[eé]\s+evitar",
        r"cu[aá]ndo\s+no",
        r"errores?\s+",
    )
    if any(re.search(p, t) for p in comunes):
        return True
    if tipo_evaluacion == "riego":
        return _coincide(t, r"evitar.*regar", r"peor.*regar", r"mal.*regar", r"a la hora de regar")
    if tipo_evaluacion == "fertilizacion":
        return _coincide(t, r"evitar.*fertiliz", r"peor.*fertiliz", r"mal.*fertiliz", r"no.*fertiliz")
    if tipo_evaluacion == "siembra":
        return _coincide(t, r"peor.*sembr", r"cu[aá]ndo\s+no\s+sembr", r"evitar.*siembra", r"mal.*epoca")
    return False


def _texto_pide_prevencion(texto: str | None) -> bool:
    if not texto:
        return False
    t = _normalizar(texto)
    return _coincide(t, r"prevenir", r"prevenci", r"como\s+evitar", r"sufrir", r"manejo\s+integrado")


def _faq_categoria(chunk: dict) -> str:
    meta = chunk.get("metadata") or {}
    cat = meta.get("categoria")
    if cat:
        return cat
    patrones = " ".join(meta.get("patrones") or chunk.get("etiquetas") or [])
    pn = _normalizar(patrones)
    if _coincide(pn, r"que no hacer", r"peores formas", r"cuando no", r"evitar regar", r"no deberia"):
        return "evitar"
    if _coincide(pn, r"prevenir", r"prevencion", r"sufrir"):
        return "prevencion"
    if _coincide(pn, r"me conviene", r"conviene regar", r"ahorita"):
        return "ventana"
    return "informativo"


def _faq_permitido(chunk: dict, texto: str | None, tipo_evaluacion: str) -> bool:
    if chunk.get("documento_tipo") != "faq":
        return True
    cat = _faq_categoria(chunk)
    if cat == "evitar":
        return _texto_pide_evitar(texto, tipo_evaluacion)
    if cat == "prevencion":
        return _texto_pide_prevencion(texto)
    return True


def _score_faq(chunk: dict, texto: str | None, cultivo: str, tipo_evaluacion: str) -> float:
    if chunk.get("documento_tipo") != "faq":
        return 0.0
    if not _faq_permitido(chunk, texto, tipo_evaluacion):
        return 0.0
    meta = chunk.get("metadata") or {}
    patrones = meta.get("patrones") or chunk.get("etiquetas") or []
    if not texto:
        return 0.0
    t = _normalizar(texto)
    score = 0.0
    for p in patrones:
        if not p or p == "faq":
            continue
        pn = _normalizar(p)
        if pn in t:
            score += 10.0
            continue
        partes = [part for part in pn.split() if len(part) > 3]
        if len(partes) >= 2 and sum(1 for part in partes if part in t) >= 2:
            score += 7.0
    if score == 0.0:
        return 0.0
    if chunk.get("cultivo") == cultivo:
        score += 3.0
    if chunk.get("tipo_evaluacion") == tipo_evaluacion:
        score += 4.0
    return score


def _score_chunk(
    chunk: dict,
    tokens: set[str],
    cultivo: str,
    tipo_evaluacion: str,
    texto_original: str | None = None,
) -> float:
    score = 0.0
    if chunk.get("documento_tipo") == "faq":
        faq_score = _score_faq(chunk, texto_original, cultivo, tipo_evaluacion)
        if faq_score > 0:
            return faq_score

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
        if not _faq_permitido(ch, texto, tipo_evaluacion):
            continue
        s = _score_chunk(ch, tokens, cultivo, tipo_evaluacion, texto)
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
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except json.JSONDecodeError:
                meta = {}
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
            "metadata": chunk.metadata or {},
        })
    return _buscar_en_lista(chunks, cultivo=cultivo, tipo_evaluacion=tipo_evaluacion, texto=texto, limit=limit)


def buscar_conocimiento_multi(
    *,
    cultivo: str,
    tipos_evaluacion: list[str],
    texto: str | None = None,
    db: Session | None = None,
    limit_por_tipo: int = 2,
) -> list[FragmentoConocimiento]:
    """Busca fragmentos para varios temas en una misma consulta."""
    vistos: set[str] = set()
    resultados: list[FragmentoConocimiento] = []
    for tipo in tipos_evaluacion:
        for fr in buscar_conocimiento(
            cultivo=cultivo,
            tipo_evaluacion=tipo,
            texto=texto,
            db=db,
            limit=limit_por_tipo,
        ):
            clave = fr.contenido[:100]
            if clave in vistos:
                continue
            vistos.add(clave)
            resultados.append(fr)
    return resultados[:8]


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
