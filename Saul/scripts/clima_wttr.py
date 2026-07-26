import requests

API_URL = "https://wttr.in"


def obtener_clima(lat, lon):
    url = f"{API_URL}/{lat},{lon}?format=j1"
    resp = requests.get(url, timeout=15, headers={"Accept": "application/json"})
    resp.raise_for_status()
    return resp.json()


def extraer_datos(data):
    actual = data.get("current_condition", [{}])[0]
    dias = data.get("weather", [])

    pronostico = []
    for dia in dias[:3]:
        for h in dia.get("hourly", []):
            pronostico.append({
                "fecha": dia["date"],
                "hora": h.get("time", "").zfill(4),
                "temp_c": float(h.get("tempC", 0)),
                "humedad_pct": float(h.get("humidity", 0)),
                "viento_kmh": float(h.get("windspeedKmph", 0)),
                "prob_lluvia_pct": float(h.get("chanceofrain", 0)),
                "precipitacion_mm": float(h.get("precipMM", 0)),
                "nubosidad_pct": float(h.get("cloudcover", 0)),
                "uv_index": float(h.get("uvIndex", 0)),
                "punto_rocio_c": float(h.get("DewPointC", 0)),
                "radiacion_solar": float(h.get("shortRad", 0)),
                "prob_trueno_pct": float(h.get("chanceofthunder", 0)),
            })

    return {
        "fuente": "wttr",
        "condiciones_actuales": {
            "temperatura_c": float(actual.get("temp_C", 0)),
            "sensacion_termica_c": float(actual.get("FeelsLikeC", 0)),
            "humedad_pct": float(actual.get("humidity", 0)),
            "viento_kmh": float(actual.get("windspeedKmph", 0)),
            "viento_direccion": actual.get("winddir16Point", ""),
            "viento_direccion_grados": float(actual.get("winddirDegree", 0)),
            "precipitacion_mm": float(actual.get("precipMM", 0)),
            "nubosidad_pct": float(actual.get("cloudcover", 0)),
            "uv_index": float(actual.get("uvIndex", 0)),
            "presion_hpa": float(actual.get("pressure", 0)),
            "visibilidad_km": float(actual.get("visibility", 0)),
            "descripcion": actual.get("weatherDesc", [{}])[0].get("value", ""),
        },
        "pronostico": pronostico,
        "astronomia": {
            "amanecer": dias[0]["astronomy"][0]["sunrise"] if dias else None,
            "atardecer": dias[0]["astronomy"][0]["sunset"] if dias else None,
        },
    }


if __name__ == "__main__":
    from ubicaciones import UBICACIONES

    print("=== wttr.in Scraper ===\n")
    for ub in UBICACIONES[:3]:
        print(f"Consultando: {ub['nombre']} ({ub['lat']}, {ub['lon']})...")
        try:
            data = obtener_clima(ub["lat"], ub["lon"])
            datos = extraer_datos(data)
            print(f"  Temp: {datos['condiciones_actuales']['temperatura_c']}°C")
            print(f"  Humedad: {datos['condiciones_actuales']['humedad_pct']}%")
            print(f"  Viento: {datos['condiciones_actuales']['viento_kmh']} km/h")
            print(f"  UV: {datos['condiciones_actuales']['uv_index']}")
            print(f"  Prob lluvia 3h: {datos['pronostico'][0]['prob_lluvia_pct'] if datos['pronostico'] else 'N/A'}%")
            print()
        except Exception as e:
            print(f"  Error: {e}\n")
