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


def detectar_temas(texto: str | None, tipo_evaluacion: str) -> list[str]:
    """Detecta uno o más temas en la pregunta del usuario."""
    temas: list[str] = []
    if not texto:
        return [tipo_evaluacion]

    t = texto.lower().strip()

    if _coincide(
        t,
        r"plagas?",
        r"insectos?",
        r"enfermedades?",
        r"roya",
        r"cogollero",
        r"chinche",
        r"fumig",
        r"fitosanit",
        r"sufrir",
        r"prevenir",
        r"prevenci",
    ):
        temas.append("plagas")

    if _coincide(
        t,
        r"siembra",
        r"sembrar",
        r"sembr",
        r"plantar",
        r"epocas?",
        r"épocas?",
        r"germin",
        r"peor(es)?\s+(epocas?|momentos?)",
        r"mal[a]?\s+epoca",
        r"cu[aá]ndo\s+(sembr|siembra|plant)",
        r"ventana\s+de\s+siembra",
    ):
        temas.append("siembra")

    if _coincide(t, r"riego", r"regar", r"agua", r"h[ií]dric", r"sequ[ií]a"):
        temas.append("riego")

    if _coincide(t, r"fertiliz", r"\bnpk\b", r"urea", r"nutriente"):
        temas.append("fertilizacion")

    if _coincide(t, r"cosecha", r"cosechar", r"grano", r"madurez"):
        temas.append("cosecha")

    if not temas:
        return [tipo_evaluacion]

    if tipo_evaluacion in temas:
        temas.remove(tipo_evaluacion)
        temas.insert(0, tipo_evaluacion)
    else:
        temas.insert(0, tipo_evaluacion)

    return list(dict.fromkeys(temas))


def _es_consulta_evitar(texto: str) -> bool:
    """Detecta preguntas sobre cuándo NO hacer algo o peores prácticas."""
    return _coincide(
        texto,
        r"peor(es)?\s+(formas?|maneras?|momentos?|epocas?|practicas?)",
        r"mal[a]?\s+(forma|manera|epoca|practica)",
        r"cu[aá]ndo\s+no",
        r"no\s+(deber[ií]a|conviene|fertiliz|sembr|regar|cosech)",
        r"no\s+deber[ií]a\s+hacer",
        r"cosas?\s+no\s+deber[ií]a",
        r"qu[eé]\s+cosas?\s+no",
        r"qu[eé]\s+evitar",
        r"formas?\s+incorrectas?",
        r"errores?\s+(comunes?|frecuentes?|al|de)",
        r"mal\s+fertiliz",
        r"evitar.*fertiliz",
        r"evitar.*siembra",
    )


def _es_consulta_evitar_riego(texto: str) -> bool:
    return _coincide(
        texto,
        r"cosas?\s+no\s+deber[ií]a",
        r"no\s+deber[ií]a\s+hacer",
        r"qu[eé]\s+cosas?\s+no",
        r"evitar.*regar",
        r"evitar.*riego",
        r"errores?\s+.*regar",
        r"mal\s+regar",
        r"peor(es)?\s+.*regar",
        r"a la hora de regar",
        r"al regar",
        r"no\s+deber[ií]a\s+.*regar",
    ) or (_es_consulta_evitar(texto) and _coincide(texto, r"regar", r"riego"))


def _es_consulta_ventana(texto: str) -> bool:
    return _coincide(
        texto,
        r"cu[aá]ndo\s+(puedo|debo|conviene|ser[ií]a)",
        r"deber[ií]a\s+esperar",
        r"me\s+conviene",
        r"ventana\s+(de|para)",
        r"en\s+cu[aá]nto\s+tiempo",
        r"cu[aá]ndo\s+s[ií]",
        r"es\s+buen\s+momento",
        r"hoy\s+puedo",
        r"hoy\s+a\s+esta\s+hora",
        r"a\s+esta\s+hora",
        r"conviene\s+regar",
    )


def detectar_sub_intenciones(texto: str | None, tema: str) -> list[str]:
    """Detecta una o más sub-intenciones dentro del mismo tema."""
    if not texto:
        return ["evaluacion_clima"]

    t = texto.lower().strip()
    subs: list[str] = []

    if tema == "plagas":
        if _coincide(t, r"prevenir", r"prevenci", r"como\s+evitar", r"c[oó]mo\s+prevenir", r"evitar.*plagas?"):
            subs.append("consulta_plagas_prevencion")
        elif _coincide(
            t,
            r"qu[eé]\s+plagas?",
            r"plagas?\s+(hay|puedo|encuentro|existen|tengo|encontrar|para|que\s+puedo)",
            r"sobre\s+las\s+plagas",
            r"plagas?\s+.*sufrir",
        ):
            subs.append("consulta_plagas_zona")

    if tema == "siembra" and _coincide(
        t, r"peor(es)?\s+(epocas?|momentos?)", r"mal[a]?\s+epoca", r"cu[aá]ndo\s+no\s+sembr", r"evitar.*siembra"
    ):
        subs.append("consulta_epocas_siembra")

    if tema == "fertilizacion" and (
        _es_consulta_evitar(t) or _coincide(t, r"peor.*fertiliz", r"mal.*fertiliz", r"evitar.*fertiliz")
    ):
        subs.append("consulta_evitar_fertilizacion")

    if tema == "riego" and _es_consulta_evitar_riego(t):
        subs.append("consulta_evitar_riego")

    if _es_consulta_ventana(t):
        subs.append("consulta_ventana")

    if buscar_producto(t) or any(k in t for k in PRODUCTOS):
        subs.append("consulta_producto")

    if _coincide(t, r"qu[eé]\s+(producto|fungicida|insecticida|herbicida)", r"con\s+qu[eé]"):
        subs.append("consulta_producto_sugerido")

    if not subs:
        subs.append("evaluacion_clima")

    orden = [
        "consulta_ventana",
        "evaluacion_clima",
        "consulta_epocas_siembra",
        "consulta_evitar_fertilizacion",
        "consulta_evitar_riego",
        "consulta_plagas_zona",
        "consulta_plagas_prevencion",
        "consulta_producto",
        "consulta_producto_sugerido",
    ]
    subs.sort(key=lambda s: orden.index(s) if s in orden else 99)
    return list(dict.fromkeys(subs))


def detectar_sub_intencion(texto: str | None, tema: str) -> str:
    """Sub-intención por tema: educativa (cuándo no) vs evaluación climática (¿hoy?)."""
    if not texto:
        return "evaluacion_clima"

    t = texto.lower().strip()

    if tema == "plagas":
        if _coincide(
            t,
            r"prevenir",
            r"prevenci",
            r"como\s+evitar",
            r"c[oó]mo\s+prevenir",
            r"evitar.*plagas?",
        ):
            return "consulta_plagas_prevencion"
        if _coincide(
            t,
            r"qu[eé]\s+plagas?",
            r"plagas?\s+(hay|puedo|encuentro|existen|tengo|encontrar|para|que\s+puedo)",
            r"plagas?\s+que\s+puedo",
            r"insectos?\s+(hay|puedo|encuentro)",
            r"enfermedades?\s+(hay|puedo|encuentro|comunes?)",
            r"qu[eé]\s+enfermedades?",
            r"lista\s+de\s+plagas",
            r"sobre\s+las\s+plagas",
            r"saber\s+sobre.*plagas",
            r"plagas?\s+.*sufrir",
            r"hablar.*plagas",
            r"habl[eé].*plagas",
        ):
            return "consulta_plagas_prevencion" if _coincide(t, r"prevenir", r"prevenci") else "consulta_plagas_zona"

    if tema == "siembra" and _coincide(
        t,
        r"peor(es)?\s+(epocas?|momentos?)",
        r"mal[a]?\s+epoca",
        r"cu[aá]ndo\s+no\s+sembr",
        r"evitar.*siembra",
    ):
        return "consulta_epocas_siembra"

    if tema == "fertilizacion" and (
        _es_consulta_evitar(t) or _coincide(t, r"peor.*fertiliz", r"mal.*fertiliz", r"evitar.*fertiliz")
    ):
        return "consulta_evitar_fertilizacion"

    if tema == "riego" and _es_consulta_evitar_riego(t):
        return "consulta_evitar_riego"

    if _es_consulta_ventana(t):
        return "consulta_ventana"

    if buscar_producto(t) or any(k in t for k in PRODUCTOS):
        return "consulta_producto"

    if _coincide(t, r"qu[eé]\s+(producto|fungicida|insecticida|herbicida)", r"con\s+qu[eé]"):
        return "consulta_producto_sugerido"

    return "evaluacion_clima"


def detectar_intencion(texto: str | None, tipo_evaluacion: str) -> str:
    """Clasifica la intención principal (compatibilidad)."""
    temas = detectar_temas(texto, tipo_evaluacion)
    if len(temas) > 1:
        return "consulta_multiple"

    if not texto:
        return "evaluacion_clima"

    subs = detectar_sub_intenciones(texto, temas[0])
    if len(subs) > 1:
        return "consulta_multiple"
    if subs[0] != "evaluacion_clima":
        return subs[0]

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


def _responder_peores_epocas_siembra(
    cultivo: str,
    condiciones: dict,
    advertencias: list,
    ubicacion: str | None,
) -> tuple[str, str]:
    info = SIEMBRA.get(cultivo, SIEMBRA["soya"])
    nombre = _nombre_cultivo(cultivo)
    zona = _zona_descripcion(ubicacion)
    prob_lluvia = condiciones.get("prob_lluvia_pct", 0) or 0
    temp_suelo = condiciones.get("temp_suelo_c")

    recomendacion = (
        f"Peores momentos para sembrar {nombre} en {zona}: suelo frío (<10°C), sequía fuerte, "
        f"justo antes de lluvias intensas o con heladas en pronóstico. "
        f"Ventana favorable habitual: {info['ventana']}."
    )
    if temp_suelo is not None and temp_suelo < 10:
        recomendacion += f" Hoy el suelo ({temp_suelo}°C) está en zona de riesgo."

    explicacion = (
        f"Sobre épocas de siembra de {nombre}:\n\n"
        f"• Evitá sembrar: suelo <10°C, humedad muy baja, heladas cercanas o encharcamiento.\n"
        f"• Ventana recomendada en Santa Cruz: {info['ventana']}.\n"
        f"• Profundidad: {info['profundidad_cm']} cm | Temp. suelo ideal: {info['temp_suelo_ideal_c']}.\n"
        f"• Clima hoy: suelo {_fmt(temp_suelo, '°C')}, prob. lluvia {_fmt(prob_lluvia, '%')}.\n\n"
        "Puntos clave:\n"
        + "\n".join(f"• {p}" for p in info["puntos_clave"][:3])
    )
    if advertencias:
        explicacion += "\n\nAlertas actuales:\n" + "\n".join(_bloque_advertencias(advertencias))
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


def _responder_riego_evitar(
    cultivo: str,
    condiciones: dict,
    ubicacion: str | None,
) -> tuple[str, str]:
    """Qué NO hacer al regar y peores prácticas."""
    info = RIEGO.get(cultivo, RIEGO["soya"])
    nombre = _nombre_cultivo(cultivo)
    zona = _zona_descripcion(ubicacion)
    peores = info.get("peores_practicas", [])
    cuando_no = info.get("cuando_no", [])
    prob_lluvia = condiciones.get("prob_lluvia_pct", 0) or 0
    humedad_suelo = condiciones.get("humedad_suelo_pct")
    temp = condiciones.get("temperatura_c")
    hora = datetime.now().hour

    recomendacion = (
        f"Al regar {nombre} en {zona}, evitá: regar al mediodía con calor, "
        f"riego superficial frecuente, regar con suelo encharcado o justo antes de lluvia fuerte. "
        f"Mejor horario: {info['mejor_horario']}."
    )

    alertas_hoy: list[str] = []
    if 11 <= hora <= 15:
        alertas_hoy.append("Estás en horario de mediodía — no es ideal para regar salvo emergencia.")
    if prob_lluvia > 40:
        alertas_hoy.append(f"Hay {prob_lluvia}% de lluvia prevista — regar ahora sería un error.")
    if humedad_suelo is not None and humedad_suelo >= 65:
        alertas_hoy.append(f"El suelo ya tiene {humedad_suelo}% de humedad — regar ahora no conviene.")
    if temp and temp > 32:
        alertas_hoy.append(f"Con {temp}°C, evitá regar en pleno calor.")

    explicacion = (
        f"Cosas que NO deberías hacer a la hora de regar {nombre}:\n\n"
        f"Errores frecuentes:\n"
        + "\n".join(f"• {p}" for p in peores)
        + "\n\nCuándo NO regar:\n"
        + "\n".join(f"• {c}" for c in cuando_no)
        + f"\n\nHorario recomendado: {info['mejor_horario']}\n"
        f"Frecuencia referencia: {info['frecuencia_referencia']}\n\n"
        f"Clima hoy:\n"
        + "\n".join(_bloque_clima(condiciones))
    )
    if alertas_hoy:
        explicacion += "\n\nAlertas para este momento:\n" + "\n".join(f"• {a}" for a in alertas_hoy)
        recomendacion += " " + alertas_hoy[0]

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


def _responder_fertilizacion_evitar(
    cultivo: str,
    condiciones: dict,
    ubicacion: str | None,
) -> tuple[str, str]:
    """Responde cuándo NO fertilizar y peores prácticas (consulta educativa)."""
    info = FERTILIZACION.get(cultivo, FERTILIZACION["soya"])
    nombre = _nombre_cultivo(cultivo)
    zona = _zona_descripcion(ubicacion)
    prob_lluvia = condiciones.get("prob_lluvia_pct", 0) or 0
    viento = condiciones.get("viento_kmh")
    temp = condiciones.get("temperatura_c")

    peores = info.get("peores_practicas", [info["evitar"]])
    cuando_no = info.get("cuando_no", [])

    recomendacion = (
        f"Peores formas de fertilizar {nombre}: abonar sin análisis de suelo, "
        f"justo antes de lluvia fuerte, con suelo encharcado o urea foliar en pleno calor. "
        f"En {zona}, evitá especialmente: {peores[0].lower()}"
    )

    alertas_hoy: list[str] = []
    if prob_lluvia > 30:
        alertas_hoy.append(f"Hoy hay {prob_lluvia}% de lluvia prevista — no es buen día para fertilizar.")
    if viento and viento > 18:
        alertas_hoy.append(f"Viento de {viento} km/h — riesgo de deriva en aplicaciones foliares.")
    if temp and temp > 32:
        alertas_hoy.append(f"Temperatura alta ({temp}°C) — evitá urea foliar o aplicaciones al mediodía.")

    explicacion = (
        f"Entiendo que querés saber cuándo NO fertilizar y qué errores evitar en {nombre}.\n\n"
        f"Peores prácticas (qué NO hacer):\n"
        + "\n".join(f"• {p}" for p in peores)
        + "\n\nCuándo NO fertilizar:\n"
        + "\n".join(f"• {c}" for c in cuando_no)
        + f"\n\nReferencia agronómica — momentos correctos:\n"
        + "\n".join(f"• {m}" for m in info["momentos"])
        + f"\n\nProductos de referencia: {info['productos_referencia']}\n\n"
        f"Clima hoy (para decidir si aplicar o esperar):\n"
        + "\n".join(_bloque_clima(condiciones))
    )
    if alertas_hoy:
        explicacion += "\n\nSeñales de alerta para hoy:\n" + "\n".join(f"• {a}" for a in alertas_hoy)
        recomendacion += " " + alertas_hoy[0]

    return recomendacion, explicacion


def _responder_plagas_prevencion(
    cultivo: str,
    ubicacion: str | None,
    condiciones: dict,
) -> tuple[str, str]:
    """Plagas frecuentes + cómo prevenirlas."""
    plagas = PLAGAS_POR_CULTIVO.get(cultivo, [])
    zona = _zona_descripcion(ubicacion)
    nombre = _nombre_cultivo(cultivo)
    humedad = condiciones.get("humedad_pct")
    temp = condiciones.get("temperatura_c")

    if not plagas:
        return (
            "No tengo un catálogo de plagas para este cultivo.",
            "Consultá con un agrónomo local para un plan de prevención en campo.",
        )

    nombres = [p["nombre"] for p in plagas[:4]]
    recomendacion = (
        f"Plagas frecuentes de {nombre} en {zona}: {', '.join(nombres)}. "
        "Prevención clave: monitoreo semanal, rotación de cultivos y tratamiento "
        "solo cuando superás el umbral económico en campo."
    )
    if humedad and humedad > 70 and temp and 20 <= temp <= 28:
        recomendacion += (
            " Con humedad y temperatura actuales, reforzá monitoreo de enfermedades fúngicas."
        )

    detalle = []
    for p in plagas[:4]:
        prevencion = p.get("manejo", p.get("monitoreo", ""))
        detalle.append(
            f"• {p['nombre']} ({p['tipo']}): {p['sintomas']}\n"
            f"  Prevención/manejo: {prevencion}\n"
            f"  Monitoreo: {p['monitoreo']}"
        )

    explicacion = (
        f"Plagas que podés sufrir con {nombre} en {zona} y cómo prevenirlas:\n\n"
        + "\n\n".join(detalle)
        + "\n\nPrácticas generales de prevención:\n"
        "• Recorrido semanal del lote (bordes y zonas húmedas primero).\n"
        "• Confirmar presencia antes de aplicar — no tratar por calendario fijo.\n"
        "• Registrar fecha, etapa fenológica y producto usado.\n"
        "• Alternar mecanismos de acción para evitar resistencia.\n\n"
        f"Clima hoy: humedad {_fmt(humedad, '%')}, temp {_fmt(temp, '°C')}."
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


SUB_INTENCION_TITULOS: dict[str, str] = {
    "consulta_ventana": "¿Conviene hoy?",
    "evaluacion_clima": "Evaluación actual",
    "consulta_evitar_riego": "Qué NO hacer al regar",
    "consulta_evitar_fertilizacion": "Qué NO hacer al fertilizar",
    "consulta_epocas_siembra": "Peores épocas de siembra",
    "consulta_plagas_zona": "Plagas en la zona",
    "consulta_plagas_prevencion": "Plagas y prevención",
}


def _titulo_sub_intencion(tema: str, sub: str) -> str:
    if sub in SUB_INTENCION_TITULOS:
        return SUB_INTENCION_TITULOS[sub]
    return TIPOS_EVALUACION.get(tema, tema).capitalize()


def _generar_seccion_sub(
    tema: str,
    sub: str,
    *,
    cultivo: str,
    semaforo: str,
    condiciones: dict,
    advertencias: list,
    ubicacion: str | None,
    texto: str | None,
    producto: str | None,
) -> tuple[str, str]:
    if sub == "consulta_evitar_riego":
        return _responder_riego_evitar(cultivo, condiciones, ubicacion)
    if sub == "consulta_evitar_fertilizacion":
        return _responder_fertilizacion_evitar(cultivo, condiciones, ubicacion)
    if sub == "consulta_plagas_prevencion":
        return _responder_plagas_prevencion(cultivo, ubicacion, condiciones)
    if sub == "consulta_plagas_zona":
        return _responder_plagas_zona(cultivo, ubicacion, condiciones)
    if sub == "consulta_epocas_siembra":
        return _responder_peores_epocas_siembra(cultivo, condiciones, advertencias, ubicacion)
    if sub in ("consulta_ventana", "evaluacion_clima") and tema == "riego":
        return _responder_riego(cultivo, semaforo, condiciones, advertencias, ubicacion, texto)
    if sub in ("consulta_ventana", "evaluacion_clima") and tema == "fertilizacion":
        return _responder_fertilizacion(cultivo, semaforo, condiciones, advertencias, ubicacion, texto)
    if sub in ("consulta_ventana", "evaluacion_clima") and tema == "siembra":
        return _responder_siembra(cultivo, semaforo, condiciones, advertencias, ubicacion, texto)
    if sub in ("consulta_ventana", "evaluacion_clima") and tema == "cosecha":
        return _responder_cosecha(cultivo, semaforo, condiciones, advertencias, ubicacion, texto)
    return _generar_seccion_tema(
        tema,
        cultivo=cultivo,
        semaforo=semaforo,
        condiciones=condiciones,
        advertencias=advertencias,
        ubicacion=ubicacion,
        texto=texto,
        producto=producto,
        intencion=sub,
    )


def _generar_seccion_tema(
    tema: str,
    *,
    cultivo: str,
    semaforo: str,
    condiciones: dict,
    advertencias: list,
    ubicacion: str | None,
    texto: str | None,
    producto: str | None,
    intencion: str,
) -> tuple[str, str]:
    """Genera recomendación y explicación para un solo tema."""
    sub = intencion
    if intencion in ("evaluacion_clima", "consulta_multiple") and texto:
        sub = detectar_sub_intencion(texto, tema)

    if tema == "plagas" and sub in ("consulta_plagas_zona", "consulta_plagas_prevencion"):
        if sub == "consulta_plagas_prevencion":
            return _responder_plagas_prevencion(cultivo, ubicacion, condiciones)
        return _responder_plagas_zona(cultivo, ubicacion, condiciones)
    if tema == "plagas" and _coincide((texto or "").lower(), r"prevenir", r"prevenci", r"sufrir"):
        return _responder_plagas_prevencion(cultivo, ubicacion, condiciones)

    if tema == "fertilizacion" and sub == "consulta_evitar_fertilizacion":
        return _responder_fertilizacion_evitar(cultivo, condiciones, ubicacion)

    if tema == "riego" and sub == "consulta_evitar_riego":
        return _responder_riego_evitar(cultivo, condiciones, ubicacion)

    if tema == "siembra" and sub == "consulta_epocas_siembra":
        return _responder_peores_epocas_siembra(cultivo, condiciones, advertencias, ubicacion)

    if tema == "siembra":
        return _responder_siembra(cultivo, semaforo, condiciones, advertencias, ubicacion, texto)
    if tema == "riego":
        return _responder_riego(cultivo, semaforo, condiciones, advertencias, ubicacion, texto)
    if tema == "fertilizacion":
        return _responder_fertilizacion(cultivo, semaforo, condiciones, advertencias, ubicacion, texto)
    if tema == "cosecha":
        return _responder_cosecha(cultivo, semaforo, condiciones, advertencias, ubicacion, texto)
    if tema == "plagas":
        return _responder_fumigacion(
            cultivo=cultivo,
            semaforo=semaforo,
            condiciones=condiciones,
            advertencias=advertencias,
            producto=producto,
            ubicacion=ubicacion,
            texto=texto,
        )

    nombre = _nombre_cultivo(cultivo)
    if semaforo == "verde":
        rec = f"Sí podés avanzar con {tema} en {nombre}."
    elif semaforo == "amarillo":
        rec = f"Podés {tema} en {nombre} con precaución."
    else:
        rec = f"Mejor esperar para {tema} en {nombre}."
    exp = f"Clima actual:\n" + "\n".join(_bloque_clima(condiciones))
    return rec, exp


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
    temas: list[str] | None = None,
    evaluaciones_por_tema: dict[str, dict] | None = None,
) -> tuple[str, str]:
    """Devuelve (recomendacion, explicacion) según tipo e intención del usuario."""
    if intencion is None:
        intencion = detectar_intencion(texto, tipo_evaluacion)

    temas_consulta = temas or detectar_temas(texto, tipo_evaluacion)
    frags = fragmentos or []
    cites = fuentes_conocimiento or []
    ev_por_tema = evaluaciones_por_tema or {}

    # Mismo tema, varias sub-intenciones (ej. ¿conviene regar hoy? + qué NO hacer al regar)
    if texto and len(temas_consulta) == 1:
        tema = temas_consulta[0]
        subs = detectar_sub_intenciones(texto, tema)
        if len(subs) > 1:
            ev = ev_por_tema.get(tema, {})
            partes_rec: list[str] = []
            partes_exp: list[str] = ["Tu consulta tiene más de un enfoque. Te respondo cada parte:\n"]
            for sub in subs:
                rec_t, exp_t = _generar_seccion_sub(
                    tema,
                    sub,
                    cultivo=cultivo,
                    semaforo=ev.get("semaforo", semaforo),
                    condiciones=condiciones,
                    advertencias=ev.get("advertencias", advertencias),
                    ubicacion=ubicacion,
                    texto=texto,
                    producto=producto,
                )
                titulo = _titulo_sub_intencion(tema, sub)
                partes_rec.append(f"{titulo}: {_recortar(rec_t, 200)}")
                partes_exp.append(f"—— {titulo} ——\n{exp_t}")
            return _finalizar(" ".join(partes_rec), "\n\n".join(partes_exp), frags, cites)

    # Consulta con varios temas (ej. plagas + siembra)
    if len(temas_consulta) > 1 or intencion == "consulta_multiple":
        partes_rec: list[str] = []
        partes_exp: list[str] = []
        partes_exp.append("Tu consulta incluye varios temas. Te respondo cada uno:\n")

        for tema in temas_consulta:
            ev = ev_por_tema.get(tema, {})
            sub_intencion = detectar_sub_intencion(texto, tema)

            rec_t, exp_t = _generar_seccion_tema(
                tema,
                cultivo=cultivo,
                semaforo=ev.get("semaforo", semaforo),
                condiciones=condiciones,
                advertencias=ev.get("advertencias", advertencias),
                ubicacion=ubicacion,
                texto=texto,
                producto=producto if tema == "plagas" else None,
                intencion=sub_intencion,
            )
            titulo = TIPOS_EVALUACION.get(tema, tema).capitalize()
            partes_rec.append(f"{titulo}: {_recortar(rec_t, 200)}")
            partes_exp.append(f"—— {titulo} ——\n{exp_t}")

        rec = " ".join(partes_rec)
        exp = "\n\n".join(partes_exp)
        return _finalizar(rec, exp, frags, cites)

    if intencion == "consulta_plagas_zona":
        rec, exp = _responder_plagas_zona(cultivo, ubicacion, condiciones)
        return _finalizar(rec, exp, frags, cites)

    if intencion == "consulta_plagas_prevencion":
        rec, exp = _responder_plagas_prevencion(cultivo, ubicacion, condiciones)
        return _finalizar(rec, exp, frags, cites)

    if intencion == "consulta_epocas_siembra":
        rec, exp = _responder_peores_epocas_siembra(cultivo, condiciones, advertencias, ubicacion)
        return _finalizar(rec, exp, frags, cites)

    if intencion == "consulta_evitar_fertilizacion":
        rec, exp = _responder_fertilizacion_evitar(cultivo, condiciones, ubicacion)
        return _finalizar(rec, exp, frags, cites)

    if intencion == "consulta_evitar_riego":
        rec, exp = _responder_riego_evitar(cultivo, condiciones, ubicacion)
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
