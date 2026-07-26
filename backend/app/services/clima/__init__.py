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


def _detectar_producto(texto: str | None) -> str:
    if texto:
        producto = buscar_producto(texto)
        if producto:
            return producto["nombre"]
        texto_lower = texto.lower()
        for key in PRODUCTOS:
            if key in texto_lower or PRODUCTOS[key]["nombre"].lower() in texto_lower:
                return PRODUCTOS[key]["nombre"]
    return "Glifosato"


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

    resultado = {
        "condiciones_actuales": condiciones,
        "fuentes_usadas": clima["fuentes_usadas"],
        "errores_fuentes": clima["errores"],
        "veredicto": "SIN_DATOS",
        "semaforo": "amarillo",
        "advertencias": [],
        "recomendacion": None,
        "explicacion": None,
    }

    if not clima["fuentes_usadas"]:
        resultado["advertencias"] = [{
            "tipo": "clima",
            "severidad": "alta",
            "mensaje": "No se pudo obtener clima de ninguna fuente disponible.",
        }]
        resultado["recomendacion"] = "Reintentá en unos minutos. No hay datos climáticos confiables."
        resultado["explicacion"] = "Todas las fuentes de clima fallaron en esta consulta."
        return resultado

    if tipo_evaluacion == "plagas":
        producto = _detectar_producto(texto)
        evaluacion = evaluar_fumigacion(producto, condiciones)
        if evaluacion.get("error"):
            resultado["advertencias"] = [{
                "tipo": "producto",
                "severidad": "alta",
                "mensaje": evaluacion["error"],
            }]
            resultado["veredicto"] = "NO_SEGURO"
            resultado["semaforo"] = "rojo"
        else:
            resultado["veredicto"] = evaluacion["veredicto"]
            resultado["semaforo"] = evaluacion["semaforo"]
            resultado["advertencias"] = evaluacion.get("advertencias", [])
            resultado["producto_evaluado"] = evaluacion.get("producto")
    else:
        evaluacion = evaluar_siembra(cultivo, condiciones)
        if evaluacion.get("error"):
            resultado["advertencias"] = [{
                "tipo": "cultivo",
                "severidad": "alta",
                "mensaje": evaluacion["error"],
            }]
            resultado["veredicto"] = "DESFAVORABLE"
            resultado["semaforo"] = "rojo"
        else:
            resultado["veredicto"] = evaluacion["veredicto"]
            resultado["semaforo"] = evaluacion["semaforo"]
            resultado["advertencias"] = evaluacion.get("advertencias", [])

    resultado["recomendacion"] = _generar_recomendacion(
        tipo_evaluacion=tipo_evaluacion,
        cultivo=cultivo,
        veredicto=resultado["veredicto"],
        semaforo=resultado["semaforo"],
        condiciones=condiciones,
        advertencias=resultado["advertencias"],
        ubicacion=ubicacion_nombre,
    )
    resultado["explicacion"] = _generar_explicacion(
        tipo_evaluacion=tipo_evaluacion,
        cultivo=cultivo,
        condiciones=condiciones,
        advertencias=resultado["advertencias"],
        fuentes=clima["fuentes_usadas"],
    )
    resultado["clima_completo"] = clima
    return resultado


def _generar_recomendacion(
    *,
    tipo_evaluacion: str,
    cultivo: str,
    veredicto: str,
    semaforo: str,
    condiciones: dict,
    advertencias: list[dict],
    ubicacion: str | None,
) -> str:
    accion = "fumigar" if tipo_evaluacion == "plagas" else tipo_evaluacion
    lugar = f" en {ubicacion}" if ubicacion else ""

    if semaforo == "rojo":
        principal = advertencias[0]["mensaje"] if advertencias else "Condiciones desfavorables."
        return f"No se recomienda {accion}{lugar} hoy. {principal}"

    if semaforo == "amarillo":
        detalle = "; ".join(a["mensaje"] for a in advertencias[:2]) if advertencias else "Condiciones marginales."
        return f"Precaución al {accion}{lugar}. {detalle}"

    temp = condiciones.get("temperatura_c")
    viento = condiciones.get("viento_kmh")
    humedad = condiciones.get("humedad_pct")
    return (
        f"Condiciones favorables para {accion} de {cultivo}{lugar}. "
        f"Temp {temp}°C, viento {viento} km/h, humedad {humedad}%."
    )


def _generar_explicacion(
    *,
    tipo_evaluacion: str,
    cultivo: str,
    condiciones: dict,
    advertencias: list[dict],
    fuentes: list[str],
) -> str:
    partes = [
        f"Evaluación de {tipo_evaluacion} para {cultivo}.",
        f"Clima consolidado desde: {', '.join(fuentes)}.",
        (
            f"Condiciones actuales: {condiciones.get('temperatura_c')}°C, "
            f"humedad {condiciones.get('humedad_pct')}%, "
            f"viento {condiciones.get('viento_kmh')} km/h, "
            f"prob. lluvia {condiciones.get('prob_lluvia_pct')}%."
        ),
    ]
    if condiciones.get("temp_suelo_c") is not None:
        partes.append(
            f"Suelo: {condiciones.get('temp_suelo_c')}°C, "
            f"humedad {condiciones.get('humedad_suelo_pct')}%."
        )
    if advertencias:
        partes.append(f"Advertencias ({len(advertencias)}): " + "; ".join(a["mensaje"] for a in advertencias))
    else:
        partes.append("No se detectaron advertencias críticas según umbrales agronómicos.")
    return " ".join(partes)
