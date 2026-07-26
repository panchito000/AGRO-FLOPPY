# Parámetros agronómicos validados y estimados
# Fuente: Cosecha_Parametros.xlsx + investigación agronómica

PRODUCTOS = {
    "glifosato": {
        "nombre": "Glifosato",
        "tipo": "herbicida",
        "modo_accion": "sistémico no selectivo",
        "ingrediente_activo": "glifosato",
        "viento_max_kmh": 16,
        "temp_min_c": 10,
        "temp_max_c": 30,
        "humedad_min_pct": 55,
        "rainfast_horas": 2,
        "reingreso_horas": 4,
        "riesgo_deriva": "medio",
        "etapas_permitidas": ["pre-siembra", "barbecho", "sobre_cultivo_RR"],
        "fuente": "Iowa State/GPCAH - Pesticide Drift Prevention Poster (2025)",
        "estado": "VALIDADO",
        "notas": "Etiqueta real permite hasta 16 km/h. Valor conservador aplicado.",
    },
    "2,4-D": {
        "nombre": "2,4-D",
        "tipo": "herbicida",
        "modo_accion": "hormonal sintético",
        "ingrediente_activo": "2,4-D",
        "viento_max_kmh": 15,
        "temp_min_c": 10,
        "temp_max_c": 25,
        "humedad_min_pct": 55,
        "rainfast_horas": 1,
        "reingreso_horas": 24,
        "riesgo_deriva": "alto",
        "etapas_permitidas": ["pre-siembra"],
        "fuente": "UNL CropWatch - How Temperature and Rain Can Affect Burndown Herbicides",
        "estado": "VALIDADO",
        "notas": "Etiqueta real permite hasta 24 km/h. Alto riesgo de deriva por volatilidad.",
    },
    "dicamba": {
        "nombre": "Dicamba",
        "tipo": "herbicida",
        "modo_accion": "hormonal sintético",
        "ingrediente_activo": "dicamba",
        "viento_max_kmh": 12,
        "temp_min_c": 10,
        "temp_max_c": 29,
        "humedad_min_pct": 55,
        "rainfast_horas": 3,
        "reingreso_horas": 24,
        "riesgo_deriva": "muy_alto",
        "etapas_permitidas": ["pre-siembra", "sobre_cultivo_Xtend"],
        "fuente": "Estimado razonable - muy volátil",
        "estado": "PENDIENTE",
        "notas": "Solo variedades Xtend. Muy volátil, restricciones estrictas.",
    },
    "fomesafen": {
        "nombre": "Fomesafén",
        "tipo": "herbicida",
        "modo_accion": "inhibidor de protoporfirinógeno oxidasa (PPO)",
        "ingrediente_activo": "fomesafen",
        "viento_max_kmh": 16,
        "temp_min_c": 15,
        "temp_max_c": 30,
        "humedad_min_pct": 60,
        "rainfast_horas": 2,
        "reingreso_horas": 12,
        "riesgo_deriva": "medio",
        "etapas_permitidas": ["pre-emergente", "post-emergente_temprano"],
        "fuente": "Estimado razonable",
        "estado": "PENDIENTE",
        "notas": "Pre-emergente en soya. Aplicar antes de emergencia de malezas.",
    },
    "elatus": {
        "nombre": "Elatus (Solatenol + Azoxystrobin)",
        "tipo": "fungicida",
        "modo_accion": "sistémico preventivo",
        "ingrediente_activo": "solatenol + azoxystrobin",
        "viento_max_kmh": 15,
        "temp_min_c": 15,
        "temp_max_c": 30,
        "humedad_min_pct": 60,
        "rainfast_horas": 2,
        "reingreso_horas": 12,
        "aplicaciones_ciclo": 3,
        "intervalo_dias": 21,
        "riesgo_deriva": "bajo",
        "target": "roya_asiatica_soya",
        "etapas_permitidas": ["V4", "R1", "R3"],
        "fuente": "Portal Syngenta Brasil - Fungicida Elatus",
        "estado": "PENDIENTE",
        "notas": "Intervalo 12-14 días entre aplicaciones. Sin umbral de viento público.",
    },
    "fox_xpro": {
        "nombre": "Fox Xpro (Protioconazol)",
        "tipo": "fungicida",
        "modo_accion": " sistémico curativo",
        "ingrediente_activo": "protioconazol",
        "viento_max_kmh": 15,
        "temp_min_c": 10,
        "temp_max_c": 30,
        "humedad_min_pct": 55,
        "rainfast_horas": 2,
        "reingreso_horas": 12,
        "riesgo_deriva": "bajo",
        "target": "sigatoka_maiz",
        "etapas_permitidas": ["V6", "VT", "R1"],
        "fuente": "Estimado razonable",
        "estado": "PENDIENTE",
        "notas": "Fungicida para maíz. Usado en zonas de alta presión de Sigatoka.",
    },
    "bumper": {
        "nombre": "Bumper (Propiconazol)",
        "tipo": "fungicida",
        "modo_accion": "sistémico preventivo/curativo",
        "ingrediente_activo": "propiconazol",
        "viento_max_kmh": 15,
        "temp_min_c": 10,
        "temp_max_c": 30,
        "humedad_min_pct": 55,
        "rainfast_horas": 2,
        "reingreso_horas": 12,
        "riesgo_deriva": "bajo",
        "target": "roya_soya_sigatoka_maiz",
        "etapas_permitidas": ["V4", "R1", "R3", "V6", "VT"],
        "fuente": "Estimado razonable",
        "estado": "PENDIENTE",
        "notas": "Fungicida genérico amplio espectro.",
    },
    "lambda_cialotrina": {
        "nombre": "Lambda-cialotrina",
        "tipo": "insecticida",
        "modo_accion": "piretroide sintético",
        "ingrediente_activo": "lambda-cialotrina",
        "viento_max_kmh": 24,
        "temp_min_c": 10,
        "temp_max_c": 32,
        "humedad_min_pct": 50,
        "rainfast_horas": 2,
        "reingreso_horas": 12,
        "riesgo_deriva": "medio",
        "target": "gusano_cogollero_soya_maiz",
        "etapas_permitidas": ["V6", "R1", "VT"],
        "fuente": "Etiquetas EPA - Nufarm Lambda-Cyhalothrin 1 EC; POMAIS Agriculture",
        "estado": "VALIDADO",
        "notas": "Restricción explícita: NO aplicar durante inversiones térmicas.",
        "restriccion_inversion_termica": True,
    },
    "metomil": {
        "nombre": "Metomil",
        "tipo": "insecticida",
        "modo_accion": "carbamato",
        "ingrediente_activo": "metomil",
        "viento_max_kmh": 16,
        "temp_min_c": 15,
        "temp_max_c": 32,
        "humedad_min_pct": 50,
        "rainfast_horas": 4,
        "reingreso_horas": 48,
        "riesgo_deriva": "medio",
        "target": "chinche_norte_soya",
        "etapas_permitidas": ["R1", "R3", "R5"],
        "restringido_bolivia": True,
        "cultivos_permitidos": ["soya", "maiz", "trigo"],
        "requiere_receta_senasag": True,
        "fuente": "Fundación Solón - Regulación de plaguicidas en Bolivia",
        "estado": "VALIDADO",
        "notas": "Plaguicida de uso RESTRINGIDO en Bolivia. Solo con receta SENASAG.",
    },
    "bt": {
        "nombre": "Bacillus thuringiensis (Bt)",
        "tipo": "insecticida",
        "modo_accion": "biológico - toxina cristalina",
        "ingrediente_activo": "Bacillus thuringiensis",
        "viento_max_kmh": 15,
        "temp_min_c": 15,
        "temp_max_c": 30,
        "humedad_min_pct": 60,
        "rainfast_horas": 4,
        "reingreso_horas": 0,
        "riesgo_deriva": "bajo",
        "target": "gusano_cogollero_soya_maiz",
        "etapas_permitidas": ["V6", "R1", "VT"],
        "fuente": "Estimado razonable - biológico",
        "estado": "PENDIENTE",
        "notas": "Producto biológico. Sin período de reingreso. Menor persistencia.",
    },
}

CALENDARIO_FENOLOGICO = {
    "soya": {
        "verano": {
            "siembra_meses": ["diciembre", "enero"],
            "duracion_ciclo_dias": 100,
            "lluvia_total_mm": {"min": 450, "max": 700},
            "fotoperiodo_min_horas": 13,
            "etapas": [
                {"codigo": "VE", "nombre": "Emergencia", "dias_inicio": 0, "dias_fin": 7,
                 "temp_min": 10, "temp_max": 40, "temp_optima_min": 25, "temp_optima_max": 30,
                 "humedad_suelo_min": 60},
                {"codigo": "V1", "nombre": "Primera hoja", "dias_inicio": 8, "dias_fin": 14,
                 "temp_min": 10, "temp_max": 35, "temp_optima_min": 25, "temp_optima_max": 30,
                 "humedad_suelo_min": 55},
                {"codigo": "V3", "nombre": "Tercera hoja trifoliada", "dias_inicio": 15, "dias_fin": 22,
                 "temp_min": 12, "temp_max": 35, "temp_optima_min": 25, "temp_optima_max": 30,
                 "humedad_suelo_min": 55},
                {"codigo": "V6", "nombre": "Sexta hoja", "dias_inicio": 23, "dias_fin": 35,
                 "temp_min": 15, "temp_max": 35, "temp_optima_min": 25, "temp_optima_max": 30,
                 "humedad_suelo_min": 50},
                {"codigo": "R1", "nombre": "Floración", "dias_inicio": 36, "dias_fin": 45,
                 "temp_min": 15, "temp_max": 33, "temp_optima_min": 23, "temp_optima_max": 28,
                 "humedad_suelo_min": 60},
                {"codigo": "R3", "nombre": "Inicio de vaina", "dias_inicio": 46, "dias_fin": 55,
                 "temp_min": 15, "temp_max": 33, "temp_optima_min": 23, "temp_optima_max": 28,
                 "humedad_suelo_min": 60},
                {"codigo": "R5", "nombre": "Llenado de grano", "dias_inicio": 56, "dias_fin": 70,
                 "temp_min": 15, "temp_max": 33, "temp_optima_min": 23, "temp_optima_max": 28,
                 "humedad_suelo_min": 55},
                {"codigo": "R7", "nombre": "Madurez fisiológica", "dias_inicio": 71, "dias_fin": 85,
                 "temp_min": 10, "temp_max": 35, "temp_optima_min": 20, "temp_optima_max": 25,
                 "humedad_suelo_min": 45},
                {"codigo": "R8", "nombre": "Cosecha", "dias_inicio": 86, "dias_fin": 100,
                 "temp_min": 5, "temp_max": 38, "temp_optima_min": 18, "temp_optima_max": 25,
                 "humedad_suelo_min": 40},
            ],
        }
    },
    "maiz": {
        "verano": {
            "siembra_meses": ["noviembre", "diciembre"],
            "duracion_ciclo_dias": 120,
            "lluvia_total_mm": {"min": 500, "max": 800},
            "fotoperiodo_min_horas": 12,
            "etapas": [
                {"codigo": "VE", "nombre": "Emergencia", "dias_inicio": 0, "dias_fin": 7,
                 "temp_min": 10, "temp_max": 42, "temp_optima_min": 25, "temp_optima_max": 30,
                 "humedad_suelo_min": 60},
                {"codigo": "V6", "nombre": "Macollaje", "dias_inicio": 25, "dias_fin": 35,
                 "temp_min": 12, "temp_max": 38, "temp_optima_min": 25, "temp_optima_max": 30,
                 "humedad_suelo_min": 55},
                {"codigo": "VT", "nombre": "Floración", "dias_inicio": 55, "dias_fin": 65,
                 "temp_min": 15, "temp_max": 35, "temp_optima_min": 25, "temp_optima_max": 30,
                 "humedad_suelo_min": 65},
                {"codigo": "R1", "nombre": "Granos sedosos", "dias_inicio": 65, "dias_fin": 70,
                 "temp_min": 15, "temp_max": 35, "temp_optima_min": 25, "temp_optima_max": 30,
                 "humedad_suelo_min": 60},
                {"codigo": "R3", "nombre": "Llenado de grano", "dias_inicio": 75, "dias_fin": 80,
                 "temp_min": 15, "temp_max": 35, "temp_optima_min": 25, "temp_optima_max": 30,
                 "humedad_suelo_min": 55},
                {"codigo": "R6", "nombre": "Madurez", "dias_inicio": 110, "dias_fin": 120,
                 "temp_min": 10, "temp_max": 38, "temp_optima_min": 20, "temp_optima_max": 25,
                 "humedad_suelo_min": 45},
            ],
        }
    },
}

CONDICIONES_SIEMBRA = {
    "soya": {
        "temp_suelo_min_c": 10,
        "temp_suelo_ideal_min_c": 13,
        "temp_aire_min_c": 10,
        "temp_aire_ideal_min_c": 25,
        "temp_aire_ideal_max_c": 30,
        "humedad_suelo_min_pct": 50,
        "humedad_suelo_ideal_min_pct": 60,
        "helada_tolerada": False,
        "fotoperiodo_min_horas": 13,
        "lluvia_min_7dias_mm": 10,
        "lluvia_total_ciclo_mm": {"min": 450, "max": 700},
    },
    "maiz": {
        "temp_suelo_min_c": 10,
        "temp_suelo_ideal_min_c": 15,
        "temp_aire_min_c": 10,
        "temp_aire_ideal_min_c": 25,
        "temp_aire_ideal_max_c": 30,
        "humedad_suelo_min_pct": 50,
        "humedad_suelo_ideal_min_pct": 60,
        "helada_tolerada": False,
        "fotoperiodo_min_horas": 12,
        "lluvia_min_7dias_mm": 15,
        "lluvia_total_ciclo_mm": {"min": 500, "max": 800},
    },
}

REGLAS_CLIMA = {
    "inversion_termica": {
        "viento_calmo_max_kmh": 3,
        "hora_inicio": "17:00",
        "hora_fin": "07:00",
        "nubosidad_max_pct": 30,
        "descripcion": "Viento calmo (<3 km/h) entre 17:00-07:00 con cielo despejado. Las gotas quedan suspendidas y se desplazan km en dirección impredecible.",
    },
    "surazo": {
        "viento_sur_min_kmh": 40,
        "caida_temp_min_c": 10,
        "anticipacion_horas": 48,
        "descripcion": "Frente frío del sur con vientos >40 km/h y caída brusca de temperatura. Predecible con días de anticipación.",
    },
    "semáforo_fumigacion": {
        "verde": {"viento_min": 5, "viento_max": 15, "temp_min": 18, "temp_max": 30, "humedad_min": 55, "humedad_max": 85, "prob_lluvia_max": 10},
        "amarillo": {"viento_min": 3, "viento_max": 20, "temp_min": 10, "temp_max": 35, "humedad_min": 45, "humedad_max": 90, "prob_lluvia_max": 30},
        "rojo": "fuera de rango amarillo",
    },
    "semáforo_siembra": {
        "verde": {"temp_suelo_min": 15, "humedad_suelo_min": 60, "helada": False, "lluvia_7dias_min": 10},
        "amarillo": {"temp_suelo_min": 10, "humedad_suelo_min": 50, "helada": False, "lluvia_7dias_min": 5},
        "rojo": "fuera de rango amarillo",
    },
}


def buscar_producto(nombre):
    nombre_lower = nombre.lower().strip()
    for key, prod in PRODUCTOS.items():
        if nombre_lower in key or nombre_lower in prod["nombre"].lower():
            return prod
    return None


def buscar_etapa(cultivo, dia_desde_siembra):
    calendario = CALENDARIO_FENOLOGICO.get(cultivo, {}).get("verano", {})
    for etapa in calendario.get("etapas", []):
        if etapa["dias_inicio"] <= dia_desde_siembra <= etapa["dias_fin"]:
            return etapa
    return None


def evaluar_fumigacion(producto_nombre, condiciones_clima):
    producto = buscar_producto(producto_nombre)
    if not producto:
        return {"error": f"Producto '{producto_nombre}' no encontrado"}

    advertencias = []
    viento = condiciones_clima.get("viento_kmh", 0)
    temp = condiciones_clima.get("temperatura_c", 0)
    humedad = condiciones_clima.get("humedad_pct", 0)
    prob_lluvia = condiciones_clima.get("prob_lluvia_pct", 0)

    if viento > producto["viento_max_kmh"]:
        advertencias.append({
            "tipo": "viento",
            "severidad": "alta",
            "mensaje": f"Viento {viento} km/h excede máximo {producto['viento_max_kmh']} km/h para {producto['nombre']}",
        })

    if temp < producto["temp_min_c"]:
        advertencias.append({
            "tipo": "temperatura_baja",
            "severidad": "alta",
            "mensaje": f"Temperatura {temp}°C por debajo del mínimo {producto['temp_min_c']}°C",
        })

    if temp > producto["temp_max_c"]:
        advertencias.append({
            "tipo": "temperatura_alta",
            "severidad": "alta",
            "mensaje": f"Temperatura {temp}°C excede máximo {producto['temp_max_c']}°C",
        })

    if humedad < producto["humedad_min_pct"]:
        advertencias.append({
            "tipo": "humedad_baja",
            "severidad": "media",
            "mensaje": f"Humedad {humedad}% por debajo del mínimo {producto['humedad_min_pct']}%",
        })

    if prob_lluvia > 30:
        advertencias.append({
            "tipo": "lluvia",
            "severidad": "alta",
            "mensaje": f"Probabilidad de lluvia {prob_lluvia}% - producto puede ser lavado antes de absorberse",
        })

    if viento < REGLAS_CLIMA["inversion_termica"]["viento_calmo_max_kmh"]:
        advertencias.append({
            "tipo": "inversion_termica",
            "severidad": "alta",
            "mensaje": f"Viento muy calmo ({viento} km/h) - riesgo de inversión térmica",
        })

    if producto.get("restriccion_inversion_termica"):
        advertencias.append({
            "tipo": "restriccion_producto",
            "severidad": "critica",
            "mensaje": f"{producto['nombre']} tiene restricción explícita: NO aplicar durante inversiones térmicas",
        })

    if producto.get("restringido_bolivia"):
        advertencias.append({
            "tipo": "restriccion_legal",
            "severidad": "critica",
            "mensaje": f"{producto['nombre']} es de uso RESTRINGIDO en Bolivia. Requiere receta SENASAG.",
        })

    criticas = [a for a in advertencias if a["severidad"] in ("alta", "critica")]
    if len(criticas) > 0:
        veredicto = "NO_SEGURO"
        semaforo = "rojo"
    elif len(advertencias) > 0:
        veredicto = "PRECAUCION"
        semaforo = "amarillo"
    else:
        veredicto = "SEGURO"
        semaforo = "verde"

    return {
        "veredicto": veredicto,
        "semaforo": semaforo,
        "producto": producto["nombre"],
        "advertencias": advertencias,
        "umbrales": {
            "viento_max_kmh": producto["viento_max_kmh"],
            "temp_min_c": producto["temp_min_c"],
            "temp_max_c": producto["temp_max_c"],
            "humedad_min_pct": producto["humedad_min_pct"],
            "rainfast_horas": producto["rainfast_horas"],
        },
    }


def evaluar_siembra(cultivo, condiciones_clima):
    params = CONDICIONES_SIEMBRA.get(cultivo)
    if not params:
        return {"error": f"Cultivo '{cultivo}' no encontrado"}

    advertencias = []
    temp_suelo = condiciones_clima.get("temp_suelo_c", 0)
    humedad_suelo = condiciones_clima.get("humedad_suelo_pct", 0)
    helada = condiciones_clima.get("helada_7_dias", False)
    lluvia_7dias = condiciones_clima.get("lluvia_7dias_mm", 0)

    if temp_suelo < params["temp_suelo_min_c"]:
        advertencias.append({
            "tipo": "temp_suelo_baja",
            "severidad": "alta",
            "mensaje": f"Temperatura suelo {temp_suelo}°C por debajo del mínimo {params['temp_suelo_min_c']}°C",
        })

    if humedad_suelo < params["humedad_suelo_min_pct"]:
        advertencias.append({
            "tipo": "humedad_suelo_baja",
            "severidad": "alta",
            "mensaje": f"Humedad suelo {humedad_suelo}% por debajo del mínimo {params['humedad_suelo_min_pct']}%",
        })

    if helada:
        advertencias.append({
            "tipo": "helada",
            "severidad": "critica",
            "mensaje": "Se pronostica helada en los próximos 7 días. NO sembrar.",
        })

    criticas = [a for a in advertencias if a["severidad"] in ("alta", "critica")]
    if len(criticas) > 0:
        veredicto = "DESFAVORABLE"
        semaforo = "rojo"
    elif len(advertencias) > 0:
        veredicto = "MARGINAL"
        semaforo = "amarillo"
    else:
        veredicto = "FAVORABLE"
        semaforo = "verde"

    return {
        "veredicto": veredicto,
        "semaforo": semaforo,
        "cultivo": cultivo,
        "advertencias": advertencias,
        "condiciones_evaluadas": {
            "temp_suelo_c": temp_suelo,
            "temp_suelo_min_requerida": params["temp_suelo_min_c"],
            "humedad_suelo_pct": humedad_suelo,
            "humedad_suelo_min_requerida": params["humedad_suelo_min_pct"],
            "helada_detectada": helada,
            "lluvia_7dias_mm": lluvia_7dias,
        },
    }
