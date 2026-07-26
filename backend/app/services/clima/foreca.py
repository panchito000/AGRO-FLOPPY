import requests

API_URL = "https://data.forecabox.com/daily/{location_id}.json"


def obtener_clima(location_id, widget_id, lang="es"):
    url = API_URL.format(location_id=location_id)
    params = {"widgetId": widget_id, "lang": lang}
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def extraer_datos(data):
    nowcast = data.get("nowcast", {})
    daily = data.get("daily", [])

    pronostico = []
    for dia in daily[:6]:
        pronostico.append({
            "fecha": dia.get("time", "")[:10],
            "temp_min_c": dia.get("temp_min"),
            "temp_max_c": dia.get("temp_max"),
            "simbolo": dia.get("symb"),
        })

    return {
        "fuente": "foreca",
        "ciudad": data.get("name"),
        "departamento": data.get("adm_name"),
        "pais": data.get("country_name"),
        "timezone": data.get("timezone"),
        "condiciones_actuales": {
            "temperatura_c": nowcast.get("temp"),
            "viento_kmh": nowcast.get("winds"),
            "viento_direccion_grados": nowcast.get("windd"),
            "simbolo_clima": nowcast.get("symb"),
        },
        "pronostico_diario": pronostico,
    }


def buscar_ubicacion(nombre_ciudad):
    url = "https://data.forecabox.com/search/daily"
    params = {"q": nombre_ciudad, "lang": "es"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        resultados = resp.json()
        if resultados:
            return resultados[0].get("locationId")
    except Exception:
        pass
    return None


if __name__ == "__main__":
    from ubicaciones import UBICACIONES

    print("=== ForecaBox Scraper ===\n")
    for ub in UBICACIONES[:5]:
        if "foreca_location_id" not in ub:
            print(f"  {ub['nombre']}: sin location ID de Foreca, saltando")
            continue
        print(f"Consultando: {ub['nombre']}...")
        try:
            data = obtener_clima(ub["foreca_location_id"], ub["foreca_widget_id"])
            datos = extraer_datos(data)
            print(f"  Temp: {datos['condiciones_actuales']['temperatura_c']}°C")
            print(f"  Viento: {datos['condiciones_actuales']['viento_kmh']} km/h")
            print(f"  Condicion: {datos['condiciones_actuales']['simbolo_clima']}")
            print()
        except Exception as e:
            print(f"  Error: {e}\n")
