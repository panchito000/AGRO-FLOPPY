import json
import csv
import os
from datetime import datetime

from clima_openmeteo import obtener_clima as obtener_openmeteo, extraer_datos as extraer_openmeteo
from clima_wttr import obtener_clima as obtener_wttr, extraer_datos as extraer_wttr
from clima_foreca import obtener_clima as obtener_foreca, extraer_datos as extraer_foreca
from ubicaciones import UBICACIONES
from datos_agronomicos import evaluar_fumigacion, evaluar_siembra


def consolidar_clima(lat, lon, ubicacion_nombre=None):
    resultado = {
        "lat": lat,
        "lon": lon,
        "nombre": ubicacion_nombre,
        "timestamp": datetime.now().isoformat(),
        "fuentes": {},
        "errores": [],
    }

    try:
        data = obtener_openmeteo(lat, lon)
        resultado["fuentes"]["openmeteo"] = extraer_openmeteo(data)
    except Exception as e:
        resultado["errores"].append({"fuente": "openmeteo", "error": str(e)})

    try:
        data = obtener_wttr(lat, lon)
        resultado["fuentes"]["wttr"] = extraer_wttr(data)
    except Exception as e:
        resultado["errores"].append({"fuente": "wttr", "error": str(e)})

    foreca_id = None
    for ub in UBICACIONES:
        if abs(ub["lat"] - lat) < 0.05 and abs(ub["lon"] - lon) < 0.05:
            if "foreca_location_id" in ub:
                foreca_id = ub["foreca_location_id"]
                foreca_widget = ub["foreca_widget_id"]
                break

    if foreca_id:
        try:
            data = obtener_foreca(foreca_id, foreca_widget)
            resultado["fuentes"]["foreca"] = extraer_foreca(data)
        except Exception as e:
            resultado["errores"].append({"fuente": "foreca", "error": str(e)})

    resultado["condiciones_unificadas"] = _unificar_condiciones(resultado["fuentes"])
    return resultado


def _unificar_condiciones(fuentes):
    temps = []
    humedades = []
    vientos = []
    probs_lluvia = []
    temp_suelo = None
    humedad_suelo = None

    if "openmeteo" in fuentes:
        oc = fuentes["openmeteo"]["condiciones_actuales"]
        if oc.get("temperatura_c") is not None:
            temps.append(oc["temperatura_c"])
        if oc.get("humedad_pct") is not None:
            humedades.append(oc["humedad_pct"])
        if oc.get("viento_kmh") is not None:
            vientos.append(oc["viento_kmh"])
        suelo = fuentes["openmeteo"].get("condiciones_suelo", {})
        if suelo.get("temp_suelo_c") is not None:
            temp_suelo = suelo["temp_suelo_c"]
        if suelo.get("humedad_suelo_pct") is not None:
            humedad_suelo = suelo["humedad_suelo_pct"]

    if "wttr" in fuentes:
        wc = fuentes["wttr"]["condiciones_actuales"]
        if wc.get("temperatura_c"):
            temps.append(wc["temperatura_c"])
        if wc.get("humedad_pct"):
            humedades.append(wc["humedad_pct"])
        if wc.get("viento_kmh"):
            vientos.append(wc["viento_kmh"])
        pronostico = fuentes["wttr"].get("pronostico", [])
        if pronostico:
            probs_lluvia.append(pronostico[0].get("prob_lluvia_pct", 0))

    if "foreca" in fuentes:
        fc = fuentes["foreca"]["condiciones_actuales"]
        if fc.get("temperatura_c") is not None:
            temps.append(fc["temperatura_c"])
        if fc.get("viento_kmh") is not None:
            vientos.append(fc["viento_kmh"])

    promedio = lambda lst: round(sum(lst) / len(lst), 1) if lst else None

    return {
        "temperatura_c": promedio(temps),
        "humedad_pct": promedio(humedades),
        "viento_kmh": promedio(vientos),
        "prob_lluvia_pct": promedio(probs_lluvia) if probs_lluvia else 0,
        "temp_suelo_c": temp_suelo,
        "humedad_suelo_pct": humedad_suelo,
    }


def evaluar_completo(lat, lon, accion, producto=None, cultivo=None, ubicacion_nombre=None):
    datos_clima = consolidar_clima(lat, lon, ubicacion_nombre)
    condiciones = datos_clima["condiciones_unificadas"]

    resultado = {
        "ubicacion": {
            "lat": lat,
            "lon": lon,
            "nombre": ubicacion_nombre,
        },
        "timestamp": datetime.now().isoformat(),
        "condiciones_actuales": condiciones,
        "fuentes_usadas": list(datos_clima["fuentes"].keys()),
        "errores_fuentes": datos_clima["errores"],
    }

    if accion == "fumigar" and producto:
        ev = evaluar_fumigacion(producto, condiciones)
        resultado["accion_evaluada"] = "fumigar"
        resultado["producto_evaluado"] = producto
        resultado["veredicto"] = ev.get("veredicto")
        resultado["semaforo"] = ev.get("semaforo")
        resultado["advertencias"] = ev.get("advertencias", [])
        resultado["umbrales_aplicados"] = ev.get("umbrales", {})

    elif accion == "sembrar" and cultivo:
        ev = evaluar_siembra(cultivo, condiciones)
        resultado["accion_evaluada"] = "sembrar"
        resultado["cultivo_evaluado"] = cultivo
        resultado["veredicto"] = ev.get("veredicto")
        resultado["semaforo"] = ev.get("semaforo")
        resultado["advertencias"] = ev.get("advertencias", [])
        resultado["condiciones_evaluadas"] = ev.get("condiciones_evaluadas", {})

    return resultado


def exportar_json(datos, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    print(f"Exportado: {filepath}")


def exportar_csv(datos, filepath):
    if isinstance(datos, dict) and "ubicaciones" in datos:
        registros = datos["ubicaciones"]
    elif isinstance(datos, list):
        registros = datos
    else:
        registros = [datos]

    if not registros:
        print("No hay datos para exportar")
        return

    flat = []
    for reg in registros:
        row = {
            "lat": reg.get("lat", ""),
            "lon": reg.get("lon", ""),
            "nombre": reg.get("nombre", ""),
            "timestamp": reg.get("timestamp", ""),
        }
        cu = reg.get("condiciones_unificadas", {})
        row["temp_c"] = cu.get("temperatura_c", "")
        row["humedad_pct"] = cu.get("humedad_pct", "")
        row["viento_kmh"] = cu.get("viento_kmh", "")
        row["prob_lluvia_pct"] = cu.get("prob_lluvia_pct", "")
        row["temp_suelo_c"] = cu.get("temp_suelo_c", "")
        row["humedad_suelo_pct"] = cu.get("humedad_suelo_pct", "")
        row["fuentes"] = ",".join(reg.get("fuentes_usadas", []))
        row["errores"] = len(reg.get("errores_fuentes", []))
        flat.append(row)

    if flat:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=flat[0].keys())
            writer.writeheader()
            writer.writerows(flat)
        print(f"Exportado: {filepath}")


def ejecutar_todas_ubicaciones():
    print("=== Zafra - Recopilación de datos climáticos ===\n")
    resultados = {"ubicaciones": [], "timestamp": datetime.now().isoformat()}

    for ub in UBICACIONES:
        print(f"Consultando: {ub['nombre']} ({ub['lat']}, {ub['lon']})...")
        try:
            datos = consolidar_clima(ub["lat"], ub["lon"], ub["nombre"])
            resultados["ubicaciones"].append(datos)
            cu = datos["condiciones_unificadas"]
            print(f"  Temp: {cu['temperatura_c']}°C | Humedad: {cu['humedad_pct']}% | Viento: {cu['viento_kmh']} km/h")
        except Exception as e:
            print(f"  Error: {e}")
            resultados["ubicaciones"].append({
                "lat": ub["lat"], "lon": ub["lon"], "nombre": ub["nombre"],
                "error": str(e), "timestamp": datetime.now().isoformat(),
            })

    exportar_json(resultados, "datos_clima_agricultura.json")
    exportar_csv(resultados, "datos_clima_agricultura.csv")

    print("\n=== Resumen ===")
    print(f"Total ubicaciones: {len(resultados['ubicaciones'])}")
    print(f"Archivos generados: datos_clima_agricultura.json, datos_clima_agricultura.csv")


if __name__ == "__main__":
    ejecutar_todas_ubicaciones()
