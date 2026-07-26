"""Generación de recomendaciones y explicaciones en lenguaje natural."""

from __future__ import annotations

import json
import re
from datetime import datetime

from app.data.conocimiento_agronomico import COSECHA, FERTILIZACION, RIEGO, SIEMBRA
from app.data.plagas_zona import PLAGAS_POR_CULTIVO, ZONAS_SANTA_CRUZ
from app.services.clima.datos_agronomicos import PRODUCTOS, buscar_producto
from app.services.conocimiento_service import FragmentoConocimiento

TIPOS_EVALUACION = {
    "siembra": "siembra",
    "fertilizacion": "fertilización",
    "riego": "riego",
    "plagas": "manejo de plagas",
    "cosecha": "cosecha",
}

CULTIVO_NOMBRE = {"soya": "soya", "maiz": "maíz"}


def detectar_intencion(texto: str | None, tipo_evaluacion: str) -> str:
    """Clasifica qué pregunta hace el usuario."""
    if not texto:
        return "evaluacion_clima"

    t = texto.lower().strip()

    if tipo_evaluacion == "plagas" and _coincide(
        t,
        r"qu[eé]\s+plagas?",
        r"plagas?\s+(hay|puedo|encuentro|existen|tengo|encontrar)",
        r"insectos?\s+(hay|puedo|encuentro)",
        r"enfermedades?\s+(hay|puedo|encuentro|comunes?)",
        r"qu[eé]\s+enfermedades?",
        r"lista\s+de\s+plagas",
    ):
        return "consulta_plagas_zona"

    if _coincide(
        t,
        r"cu[aá]ndo\s+(puedo|debo|conviene|ser[ií]a)",
        r"deber[ií]a\s+esperar",
        r"me\s+conviene",
        r"ventana\s+(de|para)",
        r"en\s+cu[aá]nto\s+tiempo",
        r"cu[aá]ndo\s+s[ií]",
    ):
        return "consulta_ventana"

    if buscar_producto(t) or any(k in t for k in PRODUCTOS):
        return "consulta_producto"

    if _coincide(t, r"qu[eé]\s+(producto|fungicida|insecticida|herbicida)", r"con\s+qu[eé]"):
        return "consulta_producto_sugerido"

    return "evaluacion_clima"


def _coincide(texto: str, *patrones: str) -> bool:
    return any(re.search(p, texto) for p in patrones)


def _nombre_cultivo(cultivo: str) -> str:
    return CULTIVO_NOMBRE.get(cultivo, cultivo)


def _zona_descripcion(ubicacion: str | None) -> str:
    if not ubicacion:
        return ZONAS_SANTA_CRUZ["default"]
    u = ubicacion.lower()
    if any(x in u for x in ("san julián", "cuatro cañadas", "okinawa")):
        return ZONAS_SANTA_CRUZ["norte"]
    if any(x in u for x in ("san ignacio", "pailón", "pailon")):
        return ZONAS_SANTA_CRUZ["este"]
    if any(x in u for x in ("charagua", "boyuibe", "camiri")):
        return ZONAS_SANTA_CRUZ["sur"]
    return ZONAS_SANTA_CRUZ["default"]


def _fmt(valor, unidad: str = "", fallback: str = "sin dato") -> str:
    if valor is None:
        return fallback
    return f"{valor}{unidad}"


def _bloque_clima(condiciones: dict) -> list[str]:
    return [
        f"• Temperatura: {_fmt(condiciones.get('temperatura_c'), '°C')}",
        f"• Humedad relativa: {_fmt(condiciones.get('humedad_pct'), '%')}",
        f"• Viento: {_fmt(condiciones.get('viento_kmh'), ' km/h')}",
        f"• Probabilidad de lluvia: {_fmt(condiciones.get('prob_lluvia_pct'), '%')}",
        f"• Temperatura del suelo: {_fmt(condiciones.get('temp_suelo_c'), '°C')}",
        f"• Humedad del suelo: {_fmt(condiciones.get('humedad_suelo_pct'), '%')}",
    ]


def _bloque_advertencias(advertencias: list[dict]) -> list[str]:
    if not advertencias:
        return ["• No hay alertas críticas según los umbrales configurados."]
    return [f"• {a['mensaje']}" for a in advertencias[:4]]


def _recortar(texto: str, max_len: int = 240) -> str:
    texto = " ".join(texto.split())
    if len(texto) <= max_len:
        return texto
    corto = texto[:max_len].rsplit(" ", 1)[0]
    return corto + "…"


def _bloque_kb(fragmentos: list[FragmentoConocimiento]) -> str:
    if not fragmentos:
        return ""
    lineas = ["\n\nDe nuestra base documental:"]
    for fr in fragmentos[:2]:
        txt = fr.contenido
        if txt.startswith("{"):
            try:
                data = json.loads(txt)
                if isinstance(data, dict):
                    partes = []
                    for k, v in list(data.items())[:3]:
                        if isinstance(v, list):
                            v = ", ".join(str(x) for x in v[:3])
                        partes.append(f"{k}: {v}")
                    txt = "; ".join(partes)
            except json.JSONDecodeError:
                pass
        lineas.append(f"• {_recortar(txt, 200)}")
    return "\n".join(lineas)


def _pie_fuentes(fuentes: list[str]) -> str:
    if not fuentes:
        return ""
    return "\n\nFuentes consultadas:\n" + "\n".join(f"• {f}" for f in fuentes[:5])


def _finalizar(
    rec: str,
    exp: str,
    fragmentos: list[FragmentoConocimiento],
    fuentes: list[str],
) -> tuple[str, str]:
    rec = _recortar(rec, 260)
    if fragmentos and fuentes:
        doc_fuente = next((f for f in fuentes if "clima" not in f.lower()), None)
        if doc_fuente and doc_fuente not in rec:
            rec = _recortar(f"{rec} (Ref: {_recortar(doc_fuente, 80)})", 300)
    if _bloque_kb(fragmentos) not in exp:
        exp += _bloque_kb(fragmentos)
    if _pie_fuentes(fuentes) not in exp:
        exp += _pie_fuentes(fuentes)
    return rec, exp


def _ventana_sugerida(semaforo: str, condiciones: dict, *, accion: str = "avanzar") -> str:
    viento = condiciones.get("viento_kmh")
    prob_lluvia = condiciones.get("prob_lluvia_pct", 0) or 0
    temp = condiciones.get("temperatura_c")

    if semaforo == "verde":
        return (
            f"Podés {accion} hoy, idealmente en la mañana (6:00–10:00) "
            "cuando el clima suele ser más estable."
        )
    if semaforo == "amarillo":
        return (
            f"Si no {accion} hoy, reprogramá para mañana temprano o cuando "
            "baje la lluvia y el viento quede en rango moderado (5–15 km/h)."
        )

    partes = [f"Por ahora conviene esperar antes de {accion}."]
    if viento and viento > 15:
        partes.append(f"Esperá a que el viento baje de {viento} km/h.")
    if prob_lluvia > 30:
        partes.append(f"Esperá a que la probabilidad de lluvia ({prob_lluvia}%) baje.")
    if temp and temp > 32:
        partes.append("Evitá las horas de máximo calor; preferí madrugada o atardecer.")
    if len(partes) == 1:
        partes.append("Revisá el pronóstico en 24–48 h antes de confirmar.")
    return " ".join(partes)


def _responder_plagas_zona(cultivo: str, ubicacion: str | None, condiciones: dict) -> tuple[str, str]:
    plagas = PLAGAS_POR_CULTIVO.get(cultivo, [])
    zona = _zona_descripcion(ubicacion)
    nombre = _nombre_cultivo(cultivo)

    if not plagas:
        return (
            "No tengo un catálogo de plagas para este cultivo.",
            "Consultá con un agrónomo local para un relevamiento en campo.",
        )

    nombres = [p["nombre"] for p in plagas[:5]]
    humedad = condiciones.get("humedad_pct")
    temp = condiciones.get("temperatura_c")

    recomendacion = (
        f"En {zona}, para {nombre} las plagas más frecuentes son: "
        f"{'; '.join(nombres)}. "
        "Te recomiendo un monitoreo semanal en el lote antes de aplicar cualquier producto."
    )
    if humedad and humedad > 70 and temp and 20 <= temp <= 28:
        recomendacion += (
            " Con la humedad actual hay mayor riesgo de enfermedades fúngicas; "
            "revisá el envés de las hojas."
        )

    detalle = [
        f"• {p['nombre']} ({p['tipo']}): {p['sintomas']} Monitoreo: {p['monitoreo']}"
        for p in plagas[:4]
    ]

    explicacion = (
        f"Entiendo que querés saber qué plagas podés encontrar en esta zona.\n\n"
        f"Para {nombre} en Santa Cruz, lo más habitual es:\n\n"
        + "\n".join(detalle)
        + "\n\nConfirmá presencia en campo antes de tratar. Zafra AI complementa, no reemplaza, al agrónomo."
    )
    return recomendacion, explicacion


def _responder_siembra(
    cultivo: str,
    semaforo: str,
    condiciones: dict,
    advertencias: list,
    ubicacion: str | None,
    texto: str | None,
) -> tuple[str, str]:
    info = SIEMBRA.get(cultivo, SIEMBRA["soya"])
    nombre = _nombre_cultivo(cultivo)
    zona = _zona_descripcion(ubicacion)
    temp_suelo = condiciones.get("temp_suelo_c")
    humedad_suelo = condiciones.get("humedad_suelo_pct")

    if semaforo == "verde":
        recomendacion = (
            f"Sí, es buen momento para sembrar {nombre}. "
            f"El suelo está a {_fmt(temp_suelo, '°C')} con {_fmt(humedad_suelo, '%')} de humedad. "
            "Podés avanzar en las próximas 24–48 h si el pronóstico se mantiene."
        )
    elif semaforo == "amarillo":
        recomendacion = (
            f"Podés sembrar {nombre} con precaución. Hay condiciones marginales — "
            "confirmá que no haya heladas ni lluvias intensas en los próximos días."
        )
    else:
        principal = advertencias[0]["mensaje"] if advertencias else "condiciones desfavorables"
        recomendacion = f"Por ahora no conviene sembrar {nombre}. {principal}"

    intro = (
        f"Revisé las condiciones de siembra para {nombre} en {zona}."
        if not texto
        else f"Entiendo tu consulta sobre siembra de {nombre}. Revisé el clima del lote en {zona}."
    )

    explicacion = (
        f"{intro}\n\n"
        f"Lo que dice el clima ahora:\n"
        + "\n".join(_bloque_clima(condiciones))
        + f"\n\nReferencia agronómica para {nombre}:\n"
        f"• Ventana habitual: {info['ventana']}\n"
        f"• Profundidad recomendada: {info['profundidad_cm']} cm\n"
        f"• Temp. suelo ideal: {info['temp_suelo_ideal_c']}\n"
        f"• Humedad suelo ideal: {info['humedad_suelo_ideal_pct']}\n"
        f"• Densidad referencia: {info['densidad']}\n\n"
        f"Puntos clave:\n"
        + "\n".join(f"• {p}" for p in info["puntos_clave"])
        + "\n\n"
        f"Alertas del momento:\n"
        + "\n".join(_bloque_advertencias(advertencias))
        + f"\n\n{_ventana_sugerida(semaforo, condiciones, accion='sembrar')}"
    )
    return recomendacion, explicacion


def _responder_riego(
    cultivo: str,
    semaforo: str,
    condiciones: dict,
    advertencias: list,
    ubicacion: str | None,
    texto: str | None,
) -> tuple[str, str]:
    info = RIEGO.get(cultivo, RIEGO["soya"])
    nombre = _nombre_cultivo(cultivo)
    humedad_suelo = condiciones.get("humedad_suelo_pct")
    prob_lluvia = condiciones.get("prob_lluvia_pct", 0) or 0

    if humedad_suelo is not None and humedad_suelo >= 65:
        recomendacion = (
            f"No hace falta regar {nombre} ahora: el suelo tiene buena humedad ({humedad_suelo}%). "
            "Monitoreá en 2–3 días o si ves signos de estrés en las hojas."
        )
    elif prob_lluvia > 40:
        recomendacion = (
            f"Conviene esperar antes de regar: hay {prob_lluvia}% de probabilidad de lluvia. "
            "La precipitación podría cubrir el déficit sin gastar agua."
        )
    elif semaforo == "verde" or (humedad_suelo is not None and humedad_suelo < 50):
        recomendacion = (
            f"Sí, podrías regar {nombre} en las próximas 24 h. "
            f"Mejor horario: {info['mejor_horario']}."
        )
    else:
        recomendacion = (
            f"Antes de regar {nombre}, revisá el suelo a 15–20 cm. "
            "Si está seco y el cultivo muestra estrés, podés regar al amanecer."
        )

    intro = (
        f"Analicé si conviene regar {nombre} según el clima actual."
        if not texto
        else f"Entiendo tu consulta sobre riego de {nombre}. Cruzé el clima con referencias de manejo hídrico."
    )

    explicacion = (
        f"{intro}\n\n"
        f"Condiciones actuales:\n"
        + "\n".join(_bloque_clima(condiciones))
        + f"\n\nEtapas críticas de {nombre} para riego:\n"
        + "\n".join(f"• {e}" for e in info["critico_etapas"])
        + "\n\nSignos de que el cultivo necesita agua:\n"
        + "\n".join(f"• {s}" for s in info["signos_estres"])
        + f"\n\nReferencia de frecuencia: {info['frecuencia_referencia']}\n\n"
        f"Observaciones:\n"
        + "\n".join(_bloque_advertencias(advertencias))
        + f"\n\n{_ventana_sugerida(semaforo, condiciones, accion='regar')}"
    )
    return recomendacion, explicacion


def _responder_fertilizacion(
    cultivo: str,
    semaforo: str,
    condiciones: dict,
    advertencias: list,
    ubicacion: str | None,
    texto: str | None,
) -> tuple[str, str]:
    info = FERTILIZACION.get(cultivo, FERTILIZACION["soya"])
    nombre = _nombre_cultivo(cultivo)
    prob_lluvia = condiciones.get("prob_lluvia_pct", 0) or 0
    viento = condiciones.get("viento_kmh")

    if prob_lluvia > 30:
        recomendacion = (
            f"Mejor esperar para fertilizar {nombre}: hay {prob_lluvia}% de lluvia prevista "
            "y podrías perder nutrientes por lixiviación. "
            "Aplicá cuando pasen 48 h sin lluvias fuertes."
        )
    elif viento and viento > 18:
        recomendacion = (
            f"Podés fertilizar {nombre}, pero con viento de {viento} km/h conviene "
            "aplicación al suelo con humedad o fertirriego, preferentemente mañana temprano."
        )
    elif semaforo == "verde":
        recomendacion = (
            f"Sí, es buen momento para fertilizar {nombre}. "
            "Clima y suelo están en rangos aceptables. Aplicá en horas frescas."
        )
    else:
        recomendacion = (
            f"Podés fertilizar {nombre} con precaución. "
            "Confirmá humedad de suelo y evitá mediodía si usás productos foliares."
        )

    intro = (
        f"Evalué si las condiciones climáticas favorecen una fertilización de {nombre}."
        if not texto
        else f"Entiendo tu consulta sobre fertilización de {nombre}. Revisé lluvia, viento y suelo."
    )

    explicacion = (
        f"{intro}\n\n"
        f"Clima ahora:\n"
        + "\n".join(_bloque_clima(condiciones))
        + f"\n\nMomentos clave de fertilización en {nombre}:\n"
        + "\n".join(f"• {m}" for m in info["momentos"])
        + f"\n\nProductos de referencia: {info['productos_referencia']}\n"
        f"Evitar: {info['evitar']}\n\n"
        f"Alertas:\n"
        + "\n".join(_bloque_advertencias(advertencias))
        + f"\n\n{_ventana_sugerida(semaforo, condiciones, accion='fertilizar')}"
    )
    return recomendacion, explicacion


def _responder_cosecha(
    cultivo: str,
    semaforo: str,
    condiciones: dict,
    advertencias: list,
    ubicacion: str | None,
    texto: str | None,
) -> tuple[str, str]:
    info = COSECHA.get(cultivo, COSECHA["soya"])
    nombre = _nombre_cultivo(cultivo)
    prob_lluvia = condiciones.get("prob_lluvia_pct", 0) or 0
    humedad = condiciones.get("humedad_pct")

    if prob_lluvia > 50:
        recomendacion = (
            f"Conviene esperar para cosechar {nombre}: lluvia probable ({prob_lluvia}%) "
            "sube humedad de grano y complica secado. "
            "Priorizá lotes más maduros si la ventana se achica."
        )
    elif semaforo == "verde":
        recomendacion = (
            f"Sí podés avanzar con la cosecha de {nombre} si el grano en campo "
            f"está cerca de {info['humedad_grano_objetivo_pct']}% de humedad. "
            "Confirmá con medidor de humedad antes de entrar."
        )
    else:
        recomendacion = (
            f"Evaluá la cosecha de {nombre} lote por lote. "
            "Si no llueve en 48 h y el grano está en punto, podés avanzar con precaución."
        )

    intro = (
        f"Revisé las condiciones climáticas para decidir cosecha de {nombre}."
        if not texto
        else f"Entiendo tu consulta sobre cuándo cosechar {nombre}. Analicé clima y referencias de punto de corte."
    )

    explicacion = (
        f"{intro}\n\n"
        f"Clima actual:\n"
        + "\n".join(_bloque_clima(condiciones))
        + f"\n\nSeñales de que el {nombre} está listo:\n"
        + "\n".join(f"• {i}" for i in info["indicadores"])
        + f"\n\nHumedad objetivo de grano: {info['humedad_grano_objetivo_pct']}%\n\n"
        f"Riesgos a considerar:\n"
        + "\n".join(f"• {r}" for r in info["riesgos"])
        + f"\n\nEquipo: {info['equipo']}\n\n"
        f"Alertas del momento:\n"
        + "\n".join(_bloque_advertencias(advertencias))
        + f"\n\n{_ventana_sugerida(semaforo, condiciones, accion='cosechar')}"
    )
    return recomendacion, explicacion


def _responder_fumigacion(
    *,
    cultivo: str,
    semaforo: str,
    condiciones: dict,
    advertencias: list,
    producto: str | None,
    ubicacion: str | None,
    texto: str | None,
) -> tuple[str, str]:
    nombre = _nombre_cultivo(cultivo)
    lugar = f" en {ubicacion}" if ubicacion else ""
    producto_txt = producto or "el producto fitosanitario"

    if semaforo == "verde":
        recomendacion = (
            f"Sí podés aplicar {producto_txt} en {nombre}{lugar}. "
            f"Clima favorable: {_fmt(condiciones.get('temperatura_c'), '°C')}, "
            f"viento {_fmt(condiciones.get('viento_kmh'), ' km/h')}, "
            f"humedad {_fmt(condiciones.get('humedad_pct'), '%')}. "
            "Ventana ideal: mañana 6:00–10:00."
        )
    elif semaforo == "amarillo":
        detalle = advertencias[0]["mensaje"] if advertencias else "condiciones marginales"
        recomendacion = (
            f"Podés aplicar {producto_txt} con precaución en {nombre}{lugar}. {detalle} "
            "Si podés, reprogramá para mañana temprano."
        )
    else:
        principal = advertencias[0]["mensaje"] if advertencias else "condiciones desfavorables"
        recomendacion = (
            f"No conviene aplicar {producto_txt} hoy en {nombre}{lugar}. {principal} "
            + _ventana_sugerida(semaforo, condiciones, accion="aplicar")
        )

    intro = (
        f"Evalué si es buen momento para aplicar {producto_txt} en {nombre}{lugar}."
        if not texto
        else f"Entiendo tu consulta sobre aplicación de {producto_txt} en {nombre}. Revisé el clima del lote."
    )

    explicacion = (
        f"{intro}\n\n"
        f"Condiciones actuales:\n"
        + "\n".join(_bloque_clima(condiciones))
        + "\n\nUmbrales para una buena aplicación:\n"
        "• Viento ideal: 5–15 km/h\n"
        "• Humedad relativa: 55–85%\n"
        "• Prob. lluvia: menor a 30% en las próximas horas\n"
        "• Evitar: horas de calor (>32°C) e inversiones térmicas (viento <3 km/h al anochecer)\n\n"
        f"Detalle de la evaluación:\n"
        + "\n".join(_bloque_advertencias(advertencias))
        + f"\n\n{_ventana_sugerida(semaforo, condiciones, accion='aplicar')}"
    )
    return recomendacion, explicacion


def generar_respuestas(
    *,
    cultivo: str,
    tipo_evaluacion: str,
    semaforo: str,
    veredicto: str,
    condiciones: dict,
    advertencias: list[dict],
    fuentes: list[str],
    ubicacion: str | None = None,
    texto: str | None = None,
    producto: str | None = None,
    intencion: str | None = None,
    fragmentos: list[FragmentoConocimiento] | None = None,
    fuentes_conocimiento: list[str] | None = None,
) -> tuple[str, str]:
    """Devuelve (recomendacion, explicacion) según tipo e intención del usuario."""
    if intencion is None:
        intencion = detectar_intencion(texto, tipo_evaluacion)

    frags = fragmentos or []
    cites = fuentes_conocimiento or []

    if intencion == "consulta_plagas_zona":
        rec, exp = _responder_plagas_zona(cultivo, ubicacion, condiciones)
        return _finalizar(rec, exp, frags, cites)

    if tipo_evaluacion == "siembra":
        rec, exp = _responder_siembra(cultivo, semaforo, condiciones, advertencias, ubicacion, texto)
    elif tipo_evaluacion == "riego":
        rec, exp = _responder_riego(cultivo, semaforo, condiciones, advertencias, ubicacion, texto)
    elif tipo_evaluacion == "fertilizacion":
        rec, exp = _responder_fertilizacion(cultivo, semaforo, condiciones, advertencias, ubicacion, texto)
    elif tipo_evaluacion == "cosecha":
        rec, exp = _responder_cosecha(cultivo, semaforo, condiciones, advertencias, ubicacion, texto)
    elif tipo_evaluacion == "plagas":
        rec, exp = _responder_fumigacion(
            cultivo=cultivo,
            semaforo=semaforo,
            condiciones=condiciones,
            advertencias=advertencias,
            producto=producto,
            ubicacion=ubicacion,
            texto=texto,
        )
    else:
        nombre = _nombre_cultivo(cultivo)
        accion = tipo_evaluacion
        if semaforo == "verde":
            rec = f"Sí podés {accion} {nombre} en las condiciones actuales."
        elif semaforo == "amarillo":
            rec = f"Podés {accion} {nombre} con precaución."
        else:
            rec = f"Mejor esperar para {accion} {nombre}."
        hora = datetime.now().strftime("%H:%M")
        exp = (
            f"Consulta de {TIPOS_EVALUACION.get(tipo_evaluacion, tipo_evaluacion)} "
            f"({hora}).\n\nClima:\n" + "\n".join(_bloque_clima(condiciones))
        )

    return _finalizar(rec, exp, frags, cites)
