"""Conocimiento agronómico por cultivo y tipo de evaluación (Santa Cruz, Bolivia)."""

SIEMBRA = {
    "soya": {
        "ventana": "Diciembre–enero (verano)",
        "profundidad_cm": "3–5",
        "temp_suelo_ideal_c": "≥ 15 (óptimo 18–25)",
        "humedad_suelo_ideal_pct": "≥ 60",
        "densidad": "250.000–350.000 plantas/ha según variedad",
        "puntos_clave": [
            "Sembrá con suelo en capacidad de campo, no saturado ni polvo.",
            "Evitá siembra 48 h antes de lluvias intensas (>30 mm).",
            "Profundidad uniforme para emergencia pareja.",
            "Inoculá semilla si es primera siembra de soya en el lote.",
        ],
    },
    "maiz": {
        "ventana": "Noviembre–diciembre (verano)",
        "profundidad_cm": "4–6",
        "temp_suelo_ideal_c": "≥ 15 (óptimo 18–28)",
        "humedad_suelo_ideal_pct": "≥ 60",
        "densidad": "55.000–70.000 plantas/ha según híbrido",
        "puntos_clave": [
            "Maíz es sensible a heladas en emergencia — confirmá pronóstico 7 días.",
            "Suelo con buena estructura y sin encharcamiento.",
            "Asegurá buen contacto semilla-suelo para absorción de agua.",
            "Considerá tratamiento de semilla ante presión de cogollero.",
        ],
    },
}

RIEGO = {
    "soya": {
        "critico_etapas": ["R1 (floración)", "R3–R5 (llenado de vaina y grano)"],
        "signos_estres": [
            "Hojas trifoliadas con aspecto azulado o enrolladas al mediodía.",
            "Suelo seco a 15–20 cm de profundidad.",
            "Aborto de flores o vainas pequeñas en R1–R3.",
        ],
        "frecuencia_referencia": "Cada 7–10 días en floración/llenado si no hay lluvia.",
        "mejor_horario": "Madrugada (4:00–8:00) o atardecer (17:00–19:00).",
    },
    "maiz": {
        "critico_etapas": ["VT–R1 (floración)", "R2–R3 (llenado de grano)"],
        "signos_estres": [
            "Hojas enrolladas en 'pipa' antes de las 11:00.",
            "Péndulos de hojas sin recuperarse al atardecer.",
            "Suelo seco en zona radicular (15–25 cm).",
        ],
        "frecuencia_referencia": "Cada 5–8 días en VT–R3 con déficit hídrico.",
        "mejor_horario": "Madrugada o noche para reducir evaporación.",
    },
}

FERTILIZACION = {
    "soya": {
        "momentos": [
            "Pre-siembra: fósforo (P) y en suelos ácidos, encalado previo.",
            "V4–V6: refuerzo foliar si hay deficiencias visibles.",
            "Post-R1: evitar N excesivo — favorece vegetativo sobre grano.",
        ],
        "productos_referencia": "MAP/DAP al surco; micronutrientes (Mo, B) según análisis.",
        "evitar": "Fertilizar justo antes de lluvia fuerte (>25 mm) — lixiviación.",
        "peores_practicas": [
            "Fertilizar justo antes de lluvia fuerte (>25 mm): se pierde N y P por lixiviación.",
            "Aplicar urea foliar en mediodía con >32°C: quemaduras foliares y volatilización de N.",
            "Abonar sin análisis de suelo: exceso de N genera vegetativo sin rendimiento.",
            "Mezclar productos incompatibles en tanque: precipitación o pérdida de eficacia.",
            "Fertilizar con suelo encharcado: raíces asfixiadas y menor absorción.",
            "Aplicar N en exceso post-R1: más hojas, menos grano en vaina.",
        ],
        "cuando_no": [
            "48 h antes de lluvias intensas previstas.",
            "Con viento >20 km/h (deriva en aplicaciones foliares).",
            "Suelo saturado o encharcado.",
            "Horas de máximo calor si usás productos foliares o urea.",
        ],
    },
    "maiz": {
        "momentos": [
            "Siembra: fracción de N + todo el P en banda.",
            "V6: primera dosis de N (30–40% del total).",
            "VT: segunda dosis de N (40–50%) antes de floración.",
        ],
        "productos_referencia": "Urea granulada, MAP, KCl según análisis de suelo.",
        "evitar": "Aplicación foliar de urea en horas de calor (>32°C).",
        "peores_practicas": [
            "Aplicar urea foliar en horas de calor (>32°C): quemaduras y volatilización.",
            "Fertilizar justo antes de lluvia fuerte: lixiviación de N.",
            "Una sola dosis de N al inicio: estrés en VT y menor rendimiento.",
            "Abonar sin análisis: desbalance N-P-K y encarecimiento sin beneficio.",
            "Aplicar sobre suelo seco sin incorporar: N volatiliza antes de absorberse.",
        ],
        "cuando_no": [
            "Antes de lluvias fuertes (>25 mm en pronóstico).",
            "Con viento alto en aplicaciones foliares.",
            "Suelo muy seco sin fertirriego o incorporación.",
        ],
    },
}

COSECHA = {
    "soya": {
        "humedad_grano_objetivo_pct": "13–14",
        "indicadores": [
            "Hojas amarillas y caída de vainas secas.",
            "Grano duro, no se marca con uña.",
            "Vainas marrones, semillas separadas del pericarpio.",
        ],
        "riesgos": [
            "Lluvia en cosecha: sube humedad de grano y riesgo de hongos.",
            "Demora en cosecha: pérdida por dehisencia de vainas.",
        ],
        "equipo": "Cosechadora con ajuste de cilindro y zaranda para soya.",
    },
    "maiz": {
        "humedad_grano_objetivo_pct": "13–15",
        "indicadores": [
            "Capa negra (black layer) visible en grano.",
            "Hojas y tallo secos, mazorca con humedad ~30% en campo.",
            "Granos duros al morder.",
        ],
        "riesgos": [
            "Lluvia post-madurez: pudrición en mazorca.",
            "Grano >18% humedad: requiere secado — costo extra.",
        ],
        "equipo": "Ajustar concavidad y velocidad de cosechadora según humedad.",
    },
}
