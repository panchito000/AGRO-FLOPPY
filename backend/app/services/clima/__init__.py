"""Servicio consolidado de clima y evaluación agronómica."""

from __future__ import annotations

from datetime import datetime

from app.data.ubicaciones import UBICACIONES
from app.services.clima import foreca, openmeteo, wttr
from app.services.clima.datos_agronomicos import (
    PRODUCTOS,
    buscar_producto,
    evaluar_fumigacion,
    evaluar_siembra,
)
from app.services.respuestas_agronomicas import detectar_intencion, generar_respuestas


def _promedio(valores: list[float]) -> float | None:
    if not valores:
        return None
    return round(sum(valores) / len(valores), 1)


def _normalizar_humedad_suelo(valor: float | None) -> float | None:
    if valor is None:
        return None
    if valor <= 1:
        return round(valor * 100, 1)
    return valor


def _foreca_cercano(lat: float, lon: float) -> tuple[str | None, str | None]:
    for ubicacion in UBICACIONES:
        if abs(ubicacion["lat"] - lat) < 0.05 and abs(ubicacion["lon"] - lon) < 0.05:
            location_id = ubicacion.get("foreca_location_id")
            widget_id = ubicacion.get("foreca_widget_id")
            if location_id and widget_id:
                return location_id, widget_id
    return None, None


def obtener_clima_consolidado(lat: float, lon: float) -> dict:
    """Consulta fuentes gratuitas y devuelve condiciones unificadas."""
    fuentes: dict = {}
    errores: list[dict] = []

    try:
        data = openmeteo.obtener_clima(lat, lon)
        fuentes["openmeteo"] = openmeteo.extraer_datos(data)
    except Exception as exc:
        errores.append({"fuente": "openmeteo", "error": str(exc)})

    try:
        data = wttr.obtener_clima(lat, lon)
        fuentes["wttr"] = wttr.extraer_datos(data)
    except Exception as exc:
        errores.append({"fuente": "wttr", "error": str(exc)})

    foreca_id, foreca_widget = _foreca_cercano(lat, lon)
    if foreca_id and foreca_widget:
        try:
            data = foreca.obtener_clima(foreca_id, foreca_widget)
            fuentes["foreca"] = foreca.extraer_datos(data)
        except Exception as exc:
            errores.append({"fuente": "foreca", "error": str(exc)})

    condiciones = _unificar_condiciones(fuentes)
    return {
        "timestamp": datetime.now().isoformat(),
        "fuentes": fuentes,
        "errores": errores,
        "condiciones_unificadas": condiciones,
        "fuentes_usadas": list(fuentes.keys()),
    }


def _unificar_condiciones(fuentes: dict) -> dict:
    temps: list[float] = []
    humedades: list[float] = []
    vientos: list[float] = []
    probs_lluvia: list[float] = []
    temp_suelo = None
    humedad_suelo = None

    if "openmeteo" in fuentes:
        actual = fuentes["openmeteo"]["condiciones_actuales"]
        if actual.get("temperatura_c") is not None:
            temps.append(actual["temperatura_c"])
        if actual.get("humedad_pct") is not None:
            humedades.append(actual["humedad_pct"])
        if actual.get("viento_kmh") is not None:
            vientos.append(actual["viento_kmh"])
        suelo = fuentes["openmeteo"].get("condiciones_suelo", {})
        temp_suelo = suelo.get("temp_suelo_c")
        humedad_suelo = _normalizar_humedad_suelo(suelo.get("humedad_suelo_pct"))
        for hora in fuentes["openmeteo"].get("pronostico_6h", []):
            if hora.get("prob_lluvia_pct") is not None:
                probs_lluvia.append(hora["prob_lluvia_pct"])

    if "wttr" in fuentes:
        actual = fuentes["wttr"]["condiciones_actuales"]
        if actual.get("temperatura_c") is not None:
            temps.append(actual["temperatura_c"])
        if actual.get("humedad_pct") is not None:
            humedades.append(actual["humedad_pct"])
        if actual.get("viento_kmh") is not None:
            vientos.append(actual["viento_kmh"])
        pronostico = fuentes["wttr"].get("pronostico", [])
        if pronostico and pronostico[0].get("prob_lluvia_pct") is not None:
            probs_lluvia.append(pronostico[0]["prob_lluvia_pct"])

    if "foreca" in fuentes:
        actual = fuentes["foreca"]["condiciones_actuales"]
        if actual.get("temperatura_c") is not None:
            temps.append(actual["temperatura_c"])
        if actual.get("viento_kmh") is not None:
            vientos.append(actual["viento_kmh"])

    return {
        "temperatura_c": _promedio(temps),
        "humedad_pct": _promedio(humedades),
        "viento_kmh": _promedio(vientos),
        "prob_lluvia_pct": _promedio(probs_lluvia) if probs_lluvia else 0,
        "temp_suelo_c": temp_suelo,
        "humedad_suelo_pct": humedad_suelo,
    }


def _detectar_producto(texto: str | None) -> str | None:
    if texto:
        producto = buscar_producto(texto)
        if producto:
            return producto["nombre"]
        texto_lower = texto.lower()
        for key in PRODUCTOS:
            if key in texto_lower or PRODUCTOS[key]["nombre"].lower() in texto_lower:
                return PRODUCTOS[key]["nombre"]
    return None


def _evaluar_riego(condiciones: dict) -> dict:
    advertencias = []
    humedad_suelo = condiciones.get("humedad_suelo_pct")
    prob_lluvia = condiciones.get("prob_lluvia_pct", 0) or 0

    if prob_lluvia > 50:
        advertencias.append({
            "tipo": "lluvia",
            "severidad": "alta",
            "mensaje": f"Lluvia probable ({prob_lluvia}%) — el riego puede ser innecesario.",
        })
    if humedad_suelo is not None and humedad_suelo >= 65:
        advertencias.append({
            "tipo": "suelo_humedo",
            "severidad": "media",
            "mensaje": f"Suelo con buena humedad ({humedad_suelo}%) — no hace falta regar ahora.",
        })
    if humedad_suelo is not None and humedad_suelo < 45:
        advertencias.append({
            "tipo": "deficit_hidrico",
            "severidad": "alta",
            "mensaje": f"Suelo seco ({humedad_suelo}%) — posible necesidad de riego.",
        })

    if any(a["tipo"] == "lluvia" for a in advertencias):
        return {"veredicto": "ESPERAR", "semaforo": "rojo", "advertencias": advertencias}
    if any(a["tipo"] == "deficit_hidrico" for a in advertencias):
        return {"veredicto": "REGAR", "semaforo": "verde", "advertencias": advertencias}
    if advertencias:
        return {"veredicto": "MONITOREAR", "semaforo": "amarillo", "advertencias": advertencias}
    return {"veredicto": "ESTABLE", "semaforo": "verde", "advertencias": []}


def _evaluar_fertilizacion(condiciones: dict) -> dict:
    advertencias = []
    prob_lluvia = condiciones.get("prob_lluvia_pct", 0) or 0
    viento = condiciones.get("viento_kmh", 0) or 0

    if prob_lluvia > 30:
        advertencias.append({
            "tipo": "lluvia",
            "severidad": "alta",
            "mensaje": f"Lluvia prevista ({prob_lluvia}%) — riesgo de lixiviación del fertilizante.",
        })
    if viento > 18:
        advertencias.append({
            "tipo": "viento",
            "severidad": "media",
            "mensaje": f"Viento {viento} km/h — posible deriva o volatilización.",
        })

    if any(a["severidad"] == "alta" for a in advertencias):
        return {"veredicto": "ESPERAR", "semaforo": "rojo", "advertencias": advertencias}
    if advertencias:
        return {"veredicto": "PRECAUCION", "semaforo": "amarillo", "advertencias": advertencias}
    return {"veredicto": "FAVORABLE", "semaforo": "verde", "advertencias": []}


def _evaluar_cosecha(condiciones: dict) -> dict:
    advertencias = []
    prob_lluvia = condiciones.get("prob_lluvia_pct", 0) or 0
    humedad = condiciones.get("humedad_pct", 0) or 0

    if prob_lluvia > 50:
        advertencias.append({
            "tipo": "lluvia",
            "severidad": "alta",
            "mensaje": f"Lluvia probable ({prob_lluvia}%) — complica secado y calidad de grano.",
        })
    if humedad > 85:
        advertencias.append({
            "tipo": "humedad",
            "severidad": "media",
            "mensaje": f"Humedad ambiental alta ({humedad}%) — verificar humedad de grano en campo.",
        })

    if any(a["severidad"] == "alta" for a in advertencias):
        return {"veredicto": "ESPERAR", "semaforo": "rojo", "advertencias": advertencias}
    if advertencias:
        return {"veredicto": "PRECAUCION", "semaforo": "amarillo", "advertencias": advertencias}
    return {"veredicto": "FAVORABLE", "semaforo": "verde", "advertencias": []}


def _aplicar_evaluacion(resultado: dict, evaluacion: dict, *, error_tipo: str = "general") -> None:
    if evaluacion.get("error"):
        resultado["advertencias"] = [{
            "tipo": error_tipo,
            "severidad": "alta",
            "mensaje": evaluacion["error"],
        }]
        resultado["veredicto"] = "NO_APLICA"
        resultado["semaforo"] = "rojo"
    else:
        resultado["veredicto"] = evaluacion["veredicto"]
        resultado["semaforo"] = evaluacion["semaforo"]
        resultado["advertencias"] = evaluacion.get("advertencias", [])
        if evaluacion.get("producto"):
            resultado["producto_evaluado"] = evaluacion["producto"]


def evaluar_agronomico(
    *,
    cultivo: str,
    tipo_evaluacion: str,
    lat: float,
    lon: float,
    ubicacion_nombre: str | None = None,
    texto: str | None = None,
) -> dict:
    """Combina clima en vivo con reglas agronómicas de Saul."""
    clima = obtener_clima_consolidado(lat, lon)
    condiciones = clima["condiciones_unificadas"]
    intencion = detectar_intencion(texto, tipo_evaluacion)

    resultado = {
        "condiciones_actuales": condiciones,
        "fuentes_usadas": clima["fuentes_usadas"],
        "errores_fuentes": clima["errores"],
        "veredicto": "SIN_DATOS",
        "semaforo": "amarillo",
        "advertencias": [],
        "recomendacion": None,
        "explicacion": None,
        "intencion_detectada": intencion,
    }

    if not clima["fuentes_usadas"]:
        resultado["advertencias"] = [{
            "tipo": "clima",
            "severidad": "alta",
            "mensaje": "No se pudo obtener clima de ninguna fuente disponible.",
        }]
        resultado["recomendacion"] = (
            "No tengo datos climáticos confiables en este momento. "
            "Reintentá en unos minutos o consultá el pronóstico local."
        )
        resultado["explicacion"] = (
            "Todas las fuentes de clima fallaron en esta consulta. "
            "Sin esos datos no puedo darte una recomendación segura."
        )
        return resultado

    producto = None
    if intencion == "consulta_plagas_zona":
        resultado["veredicto"] = "INFORMATIVO"
        resultado["semaforo"] = "amarillo"
        resultado["advertencias"] = []
    elif tipo_evaluacion == "plagas":
        producto = _detectar_producto(texto)
        if producto:
            _aplicar_evaluacion(resultado, evaluar_fumigacion(producto, condiciones), error_tipo="producto")
        else:
            intencion = "consulta_plagas_zona"
            resultado["intencion_detectada"] = intencion
            resultado["veredicto"] = "INFORMATIVO"
            resultado["semaforo"] = "amarillo"
            resultado["advertencias"] = []
    elif tipo_evaluacion == "siembra":
        _aplicar_evaluacion(resultado, evaluar_siembra(cultivo, condiciones), error_tipo="cultivo")
    elif tipo_evaluacion == "riego":
        _aplicar_evaluacion(resultado, _evaluar_riego(condiciones))
    elif tipo_evaluacion == "fertilizacion":
        _aplicar_evaluacion(resultado, _evaluar_fertilizacion(condiciones))
    elif tipo_evaluacion == "cosecha":
        _aplicar_evaluacion(resultado, _evaluar_cosecha(condiciones))
    else:
        _aplicar_evaluacion(resultado, evaluar_siembra(cultivo, condiciones), error_tipo="cultivo")

    resultado["recomendacion"], resultado["explicacion"] = generar_respuestas(
        cultivo=cultivo,
        tipo_evaluacion=tipo_evaluacion,
        semaforo=resultado["semaforo"],
        veredicto=resultado["veredicto"],
        condiciones=condiciones,
        advertencias=resultado["advertencias"],
        fuentes=clima["fuentes_usadas"],
        ubicacion=ubicacion_nombre,
        texto=texto,
        producto=resultado.get("producto_evaluado") or producto,
        intencion=resultado.get("intencion_detectada"),
    )
    resultado["clima_completo"] = clima
    return resultado
