"""Generación de recomendaciones y explicaciones en lenguaje natural."""

from __future__ import annotations

import re
from datetime import datetime

from app.data.plagas_zona import PLAGAS_POR_CULTIVO, ZONAS_SANTA_CRUZ
from app.services.clima.datos_agronomicos import PRODUCTOS, buscar_producto

TIPOS_EVALUACION = {
    "siembra": "siembra",
    "fertilizacion": "fertilización",
    "riego": "riego",
    "plagas": "manejo de plagas",
    "cosecha": "cosecha",
}

ACCIONES = {
    "siembra": "sembrar",
    "fertilizacion": "fertilizar",
    "riego": "registrar riego o activar el sistema",
    "plagas": "aplicar el producto fitosanitario",
    "cosecha": "iniciar cosecha",
}


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


def _saludo_contexto(cultivo: str, tipo: str, ubicacion: str | None) -> str:
    lugar = f" en {ubicacion}" if ubicacion else " en la zona seleccionada"
    return f"Para {cultivo}{lugar}, revisé el clima y tu consulta de {TIPOS_EVALUACION.get(tipo, tipo)}."


def _ventana_sugerida(semaforo: str, condiciones: dict) -> str:
    viento = condiciones.get("viento_kmh")
    prob_lluvia = condiciones.get("prob_lluvia_pct", 0)
    temp = condiciones.get("temperatura_c")

    if semaforo == "verde":
        return (
            "Podés avanzar hoy, preferentemente en las primeras horas de la mañana "
            "(6:00–10:00) cuando el viento suele ser más estable."
        )
    if semaforo == "amarillo":
        return (
            "Si las condiciones no mejoran, considerá reprogramar para mañana temprano "
            "o cuando baje la probabilidad de lluvia y el viento quede entre 5 y 15 km/h."
        )
    partes = ["Por ahora conviene esperar."]
    if viento and viento > 15:
        partes.append(f"El viento ({viento} km/h) debería bajar por debajo de 15 km/h.")
    if prob_lluvia and prob_lluvia > 30:
        partes.append(f"Esperá a que la probabilidad de lluvia ({prob_lluvia}%) baje de 30%.")
    if temp and temp > 32:
        partes.append("Evitá aplicar en horas de máximo calor; mejor al amanecer o al atardecer.")
    if len(partes) == 1:
        partes.append("Revisá el pronóstico en 24–48 h antes de confirmar la operación.")
    return " ".join(partes)


def _responder_plagas_zona(cultivo: str, ubicacion: str | None, condiciones: dict) -> tuple[str, str]:
    plagas = PLAGAS_POR_CULTIVO.get(cultivo, [])
    zona = ZONAS_SANTA_CRUZ["default"]
    if ubicacion:
        u = ubicacion.lower()
        if any(x in u for x in ("san julián", "cuatro cañadas", "okinawa")):
            zona = ZONAS_SANTA_CRUZ["norte"]
        elif any(x in u for x in ("san ignacio", "pailón", "pailon")):
            zona = ZONAS_SANTA_CRUZ["este"]

    if not plagas:
        rec = "No tengo un catálogo de plagas cargado para este cultivo."
        exp = "Consultá con un agrónomo de la zona para un relevamiento de campo."
        return rec, exp

    nombres = [p["nombre"] for p in plagas[:5]]
    humedad = condiciones.get("humedad_pct")
    temp = condiciones.get("temperatura_c")

    recomendacion = (
        f"En {zona}, para {cultivo} las plagas y enfermedades más frecuentes son: "
        f"{'; '.join(nombres)}. "
        "Te sugiero un monitoreo semanal en el lote antes de aplicar cualquier producto."
    )

    if humedad and humedad > 70 and temp and 20 <= temp <= 28:
        recomendacion += (
            " Con la humedad y temperatura actuales, hay mayor riesgo de enfermedades fúngicas "
            "(roya/sigatoka); priorizá revisar el envés de las hojas."
        )

    detalle = []
    for p in plagas[:4]:
        detalle.append(
            f"• {p['nombre']} ({p['tipo']}): {p['sintomas']} "
            f"Monitoreo: {p['monitoreo']}"
        )

    explicacion = (
        f"Entiendo que querés saber qué plagas podés encontrar en esta zona. "
        f"Según referencias agronómicas de Santa Cruz para {cultivo}, esto es lo más habitual:\n\n"
        + "\n".join(detalle)
        + "\n\nEsta es información orientativa. Confirmá presencia en campo antes de tratar."
    )
    return recomendacion, explicacion


def _responder_riego(cultivo: str, semaforo: str, condiciones: dict, advertencias: list) -> tuple[str, str]:
    humedad_suelo = condiciones.get("humedad_suelo_pct")
    prob_lluvia = condiciones.get("prob_lluvia_pct", 0)
    temp = condiciones.get("temperatura_c")

    if humedad_suelo is not None and humedad_suelo >= 60:
        rec = (
            f"El suelo muestra buena humedad ({humedad_suelo}%). "
            "No hace falta regar ahora; monitoreá en 2–3 días o si el cultivo muestra estrés."
        )
    elif prob_lluvia and prob_lluvia > 40:
        rec = (
            f"Hay {prob_lluvia}% de probabilidad de lluvia. "
            "Conviene esperar: la lluvia podría cubrir el déficit hídrico sin gastar agua."
        )
    elif semaforo == "verde" or (humedad_suelo is not None and humedad_suelo < 50):
        rec = (
            f"Sí podrías regar {cultivo} en las próximas 24 h, "
            "preferentemente al amanecer o al atardecer para reducir evaporación."
        )
    else:
        rec = (
            "Las condiciones no son claras para un riego urgente. "
            "Revisá el suelo a 15–20 cm de profundidad antes de decidir."
        )

    exp = (
        f"Para riego de {cultivo} analicé humedad de suelo, temperatura y pronóstico. "
        f"Humedad suelo: {humedad_suelo if humedad_suelo is not None else 'sin dato'}%, "
        f"temp {temp}°C, prob. lluvia {prob_lluvia}%. "
    )
    if advertencias:
        exp += "Observaciones: " + "; ".join(a["mensaje"] for a in advertencias[:2]) + "."
    else:
        exp += "No hay alertas críticas de clima para una decisión de riego inmediata."
    return rec, exp


def _responder_fertilizacion(cultivo: str, semaforo: str, condiciones: dict) -> tuple[str, str]:
    prob_lluvia = condiciones.get("prob_lluvia_pct", 0)
    viento = condiciones.get("viento_kmh")
    humedad_suelo = condiciones.get("humedad_suelo_pct")

    if prob_lluvia > 30:
        rec = (
            f"Mejor esperar a fertilizar {cultivo}: hay {prob_lluvia}% de lluvia prevista "
            "y podrías perder nutrientes por lixiviación."
        )
        ventana = "Aplicá cuando pasen 48 h sin lluvias fuertes y el suelo esté en capacidad de campo."
    elif viento and viento > 18:
        rec = (
            f"Podés fertilizar, pero el viento ({viento} km/h) complica granulados volatilizados. "
            "Preferí aplicación al suelo con suelo húmedo o fertirriego."
        )
        ventana = "Ventana más segura: mañana temprano con viento bajo."
    elif semaforo == "verde":
        rec = (
            f"Sí, es un buen momento para fertilizar {cultivo}. "
            "El suelo y el clima están dentro de rangos aceptables."
        )
        ventana = "Aplicá en horas frescas; si usás foliares, evitá mediodía."
    else:
        rec = (
            f"Fertilizar {cultivo} es posible con precaución. "
            "Confirmá humedad de suelo antes de aplicar."
        )
        ventana = _ventana_sugerida(semaforo, condiciones)

    exp = (
        f"Para fertilización de {cultivo} consideré lluvia ({prob_lluvia}%), "
        f"viento ({viento} km/h) y humedad de suelo "
        f"({humedad_suelo if humedad_suelo is not None else 'sin dato'}%). "
        f"{ventana}"
    )
    return rec, exp


def _responder_cosecha(cultivo: str, semaforo: str, condiciones: dict) -> tuple[str, str]:
    prob_lluvia = condiciones.get("prob_lluvia_pct", 0)
    humedad = condiciones.get("humedad_pct")

    if prob_lluvia > 50:
        rec = (
            f"Conviene esperar para cosechar {cultivo}: lluvia probable ({prob_lluvia}%) "
            "sube humedad de grano y complica secado."
        )
    elif semaforo == "verde" and humedad and humedad < 80:
        rec = (
            f"Sí podés avanzar con la cosecha de {cultivo} si el grano en campo "
            "está en 13–14% de humedad (confirmá con medidor)."
        )
    else:
        rec = (
            f"Evaluá cosecha de {cultivo} lote por lote. "
            "Si hay lluvia cercana, priorizá lotes más maduros o con mayor riesgo de pérdida."
        )

    exp = (
        f"Para cosecha de {cultivo} el clima actual muestra humedad relativa {humedad}%, "
        f"prob. lluvia {prob_lluvia}%. "
        "La decisión final depende de humedad de grano en mazorca/vaina y pronóstico de 48 h."
    )
    return rec, exp


def _responder_siembra(cultivo: str, semaforo: str, condiciones: dict, advertencias: list) -> tuple[str, str]:
    temp_suelo = condiciones.get("temp_suelo_c")
    humedad_suelo = condiciones.get("humedad_suelo_pct")

    if semaforo == "verde":
        rec = (
            f"Sí, las condiciones son favorables para sembrar {cultivo}. "
            f"Suelo a {temp_suelo}°C con humedad adecuada."
        )
        ventana = "Podés avanzar en las próximas 24–48 h si el pronóstico se mantiene estable."
    elif semaforo == "amarillo":
        rec = (
            f"Podés sembrar {cultivo} con precaución, pero hay factores marginales. "
            "Asegurate de que no haya heladas en los próximos días."
        )
        ventana = _ventana_sugerida(semaforo, condiciones)
    else:
        principal = advertencias[0]["mensaje"] if advertencias else "condiciones desfavorables"
        rec = f"Por ahora no conviene sembrar {cultivo}. {principal}"
        ventana = _ventana_sugerida(semaforo, condiciones)

    exp = (
        f"Para siembra de {cultivo} el suelo está a {temp_suelo if temp_suelo is not None else '—'}°C "
        f"y {humedad_suelo if humedad_suelo is not None else '—'}% de humedad. "
        f"{ventana}"
    )
    return rec, exp


def _responder_fumigacion(
    *,
    cultivo: str,
    semaforo: str,
    veredicto: str,
    condiciones: dict,
    advertencias: list,
    producto: str | None,
    ubicacion: str | None,
    texto: str | None,
) -> tuple[str, str]:
    accion = ACCIONES["plagas"]
    lugar = f" en {ubicacion}" if ubicacion else ""
    producto_txt = producto or "el producto seleccionado"

    if semaforo == "verde":
        rec = (
            f"Sí podés {accion} ({producto_txt}){lugar}. "
            f"Clima favorable: {condiciones.get('temperatura_c')}°C, "
            f"viento {condiciones.get('viento_kmh')} km/h, "
            f"humedad {condiciones.get('humedad_pct')}%."
        )
        ventana = "Ventana ideal: mañana temprano (6:00–10:00) con viento entre 5 y 15 km/h."
    elif semaforo == "amarillo":
        rec = (
            f"Podés {accion} con precaución. Hay condiciones marginales para {producto_txt}{lugar}. "
            + (advertencias[0]["mensaje"] if advertencias else "")
        )
        ventana = _ventana_sugerida(semaforo, condiciones)
    else:
        principal = advertencias[0]["mensaje"] if advertencias else "condiciones desfavorables"
        rec = f"No conviene {accion} hoy. {principal}"
        ventana = _ventana_sugerida(semaforo, condiciones)

    exp_partes = [
        f"Evalué si es buen momento para aplicar {producto_txt} en {cultivo}{lugar}.",
        (
            f"Ahora hay {condiciones.get('temperatura_c')}°C, "
            f"viento {condiciones.get('viento_kmh')} km/h, "
            f"humedad {condiciones.get('humedad_pct')}% "
            f"y {condiciones.get('prob_lluvia_pct')}% de probabilidad de lluvia."
        ),
        ventana,
    ]
    if advertencias:
        exp_partes.append(
            "Detalle técnico: " + "; ".join(a["mensaje"] for a in advertencias[:3]) + "."
        )
    if texto and "?" in texto:
        exp_partes.insert(1, "Respondiendo a tu consulta: el clima de hoy " +
                         ("permite" if semaforo == "verde" else "no favorece" if semaforo == "rojo" else "permite con cuidado") +
                         " una aplicación.")
    return rec, " ".join(exp_partes)


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
) -> tuple[str, str]:
    """Devuelve (recomendacion, explicacion) según tipo e intención del usuario."""
    if intencion is None:
        intencion = detectar_intencion(texto, tipo_evaluacion)

    if intencion == "consulta_plagas_zona":
        return _responder_plagas_zona(cultivo, ubicacion, condiciones)

    if tipo_evaluacion == "riego":
        return _responder_riego(cultivo, semaforo, condiciones, advertencias)

    if tipo_evaluacion == "fertilizacion":
        return _responder_fertilizacion(cultivo, semaforo, condiciones)

    if tipo_evaluacion == "cosecha":
        return _responder_cosecha(cultivo, semaforo, condiciones)

    if tipo_evaluacion == "plagas":
        return _responder_fumigacion(
            cultivo=cultivo,
            semaforo=semaforo,
            veredicto=veredicto,
            condiciones=condiciones,
            advertencias=advertencias,
            producto=producto,
            ubicacion=ubicacion,
            texto=texto,
        )

    if tipo_evaluacion == "siembra":
        return _responder_siembra(cultivo, semaforo, condiciones, advertencias)

    # Fallback genérico
    accion = ACCIONES.get(tipo_evaluacion, tipo_evaluacion)
    if semaforo == "verde":
        rec = f"Sí podés {accion} {cultivo} en las condiciones actuales."
    elif semaforo == "amarillo":
        rec = f"Podés {accion} con precaución. " + _ventana_sugerida(semaforo, condiciones)
    else:
        rec = f"Mejor esperar para {accion}. " + _ventana_sugerida(semaforo, condiciones)

    hora = datetime.now().strftime("%H:%M")
    exp = (
        f"{_saludo_contexto(cultivo, tipo_evaluacion, ubicacion)} "
        f"Consulta realizada a las {hora}. "
        f"Datos de: {', '.join(fuentes) if fuentes else 'sin fuentes'}. "
        f"Condiciones: {condiciones.get('temperatura_c')}°C, "
        f"humedad {condiciones.get('humedad_pct')}%, viento {condiciones.get('viento_kmh')} km/h."
    )
    return rec, exp
