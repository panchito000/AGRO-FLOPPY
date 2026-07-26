import requests

API_URL = "https://api.open-meteo.com/v1/forecast"


def obtener_clima(lat, lon, forecast_days=7):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,precipitation,rain,weather_code,cloud_cover,uv_index",
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation_probability,precipitation,soil_temperature_0cm,soil_moisture_0_to_1cm",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max,uv_index_max,et0_fao_evapotranspiration,sunrise,sunset,daylight_duration",
        "timezone": "America/La_Paz",
        "forecast_days": forecast_days,
    }
    resp = requests.get(API_URL, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def extraer_datos(data):
    current = data.get("current", {})
    hourly = data.get("hourly", {})
    daily = data.get("daily", {})

    pronostico_6h = []
    horas = hourly.get("time", [])[:6]
    for i, hora in enumerate(horas):
        pronostico_6h.append({
            "hora": hora,
            "temp_c": hourly.get("temperature_2m", [None])[i],
            "humedad_pct": hourly.get("relative_humidity_2m", [None])[i],
            "viento_kmh": hourly.get("wind_speed_10m", [None])[i],
            "prob_lluvia_pct": hourly.get("precipitation_probability", [None])[i],
            "precipitacion_mm": hourly.get("precipitation", [None])[i],
        })

    return {
        "fuente": "openmeteo",
        "condiciones_actuales": {
            "temperatura_c": current.get("temperature_2m"),
            "humedad_pct": current.get("relative_humidity_2m"),
            "viento_kmh": current.get("wind_speed_10m"),
            "viento_direccion_grados": current.get("wind_direction_10m"),
            "precipitacion_mm": current.get("precipitation"),
            "lluvia_mm": current.get("rain"),
            "codigo_clima": current.get("weather_code"),
            "nubosidad_pct": current.get("cloud_cover"),
            "uv_index": current.get("uv_index"),
        },
        "condiciones_suelo": {
            "temp_suelo_c": hourly.get("soil_temperature_0cm", [None])[0],
            "humedad_suelo_pct": hourly.get("soil_moisture_0_to_1cm", [None])[0],
        },
        "pronostico_6h": pronostico_6h,
        "pronostico_diario": {
            "fechas": daily.get("time", []),
            "temp_max": daily.get("temperature_2m_max", []),
            "temp_min": daily.get("temperature_2m_min", []),
            "precipitacion_mm": daily.get("precipitation_sum", []),
            "prob_lluvia_max_pct": daily.get("precipitation_probability_max", []),
            "viento_max_kmh": daily.get("wind_speed_10m_max", []),
            "uv_max": daily.get("uv_index_max", []),
            "et0_mm": daily.get("et0_fao_evapotranspiration", []),
            "amanecer": daily.get("sunrise", []),
            "atardecer": daily.get("sunset", []),
            "dias_segundos": daily.get("daylight_duration", []),
        },
    }


if __name__ == "__main__":
    from ubicaciones import UBICACIONES
    import json

    print("=== Open-Meteo Scraper ===\n")
    for ub in UBICACIONES[:3]:
        print(f"Consultando: {ub['nombre']} ({ub['lat']}, {ub['lon']})...")
        try:
            data = obtener_clima(ub["lat"], ub["lon"])
            datos = extraer_datos(data)
            print(f"  Temp: {datos['condiciones_actuales']['temperatura_c']}°C")
            print(f"  Humedad: {datos['condiciones_actuales']['humedad_pct']}%")
            print(f"  Viento: {datos['condiciones_actuales']['viento_kmh']} km/h")
            print(f"  Suelo temp: {datos['condiciones_suelo']['temp_suelo_c']}°C")
            print(f"  Suelo humedad: {datos['condiciones_suelo']['humedad_suelo_pct']} m³/m³")
            print()
        except Exception as e:
            print(f"  Error: {e}\n")
