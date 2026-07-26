import requests
import json

UBICACIONES = [
    {"location_id": "103904906", "widget_id": "8ufE7r9n6t", "lang": "es"},
    {"location_id": "108335389", "widget_id": "Y86MxJHLT7", "lang": "es"},
    {"location_id": "103905453", "widget_id": "uCN1yIUhQQ", "lang": "en"},
    {"location_id": "103905658", "widget_id": "s1ZeNoWIw5", "lang": "es"},
    {"location_id": "103909360", "widget_id": "12D68Zxu2K", "lang": "es"},
]

API_URL = "https://data.forecabox.com/daily/{location_id}.json"


def obtener_clima(location_id, widget_id, lang):
    url = API_URL.format(location_id=location_id)
    params = {"widgetId": widget_id, "lang": lang}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def mostrar_clima(data):
    print(f"\n{'='*50}")
    print(f"Ciudad: {data['name']}")
    print(f"Departamento: {data['adm_name']}")
    print(f"Pais: {data['country_name']}")
    print(f"Zona horaria: {data['timezone']}")
    print(f"{'-'*50}")

    now = data.get("nowcast", {})
    print("  ACTUAL:")
    print(f"  Temperatura: {now.get('temp')} C")
    print(f"  Condicion: {now.get('symb')}")
    print(f"  Viento: {now.get('winds')} km/h (rafaga {now.get('winds_max')} km/h)")
    print(f"  Direccion viento: {now.get('windd')} grados")

    print("  PRONOSTICO DIARIO:")
    for dia in data.get("daily", []):
        fecha = dia["time"][:10]
        print(f"    {fecha}: min {dia['temp_min']}C / max {dia['temp_max']}C  ({dia['symb']})")


def main():
    print("Obteniendo datos del clima de ANAPO Bolivia (Foreca)...")
    todos_los_datos = []

    for ubic in UBICACIONES:
        try:
            data = obtener_clima(
                ubic["location_id"],
                ubic["widget_id"],
                ubic["lang"],
            )
            mostrar_clima(data)
            todos_los_datos.append(data)
        except Exception as e:
            print(f"Error con location {ubic['location_id']}: {e}")

    with open("clima_anapo_datos.json", "w", encoding="utf-8") as f:
        json.dump(todos_los_datos, f, ensure_ascii=False, indent=2)
    print(f"\nDatos guardados en clima_anapo_datos.json")


if __name__ == "__main__":
    main()
