"""Plagas y enfermedades frecuentes en Santa Cruz (Bolivia) por cultivo."""

PLAGAS_POR_CULTIVO: dict[str, list[dict]] = {
    "soya": [
        {
            "nombre": "Gusano cogollero (Spodoptera frugiperda)",
            "tipo": "insecto",
            "etapas_riesgo": ["V6", "R1", "R2"],
            "sintomas": "Defoliación en cogollo, perforaciones en hojas jóvenes.",
            "monitoreo": "Recorrer lotes al atardecer; umbral: 20% de plantas con daño.",
            "manejo": "Monitoreo semanal; Bt o lambda-cialotrina si supera umbral.",
        },
        {
            "nombre": "Chinche verde / chinche marrón",
            "tipo": "insecto",
            "etapas_riesgo": ["R3", "R5"],
            "sintomas": "Granos chuzos, aborto de vainas, manchas en vainas.",
            "monitoreo": "Muestreo con red entomológica en bordes del lote.",
            "manejo": "Intervenir en R3-R5 si supera umbral económico.",
        },
        {
            "nombre": "Roya asiática (Phakopsora pachyrhizi)",
            "tipo": "enfermedad",
            "etapas_riesgo": ["R1", "R3", "R5"],
            "sintomas": "Pústulas pequeñas en envés de hoja; amarillamiento prematuro.",
            "monitoreo": "Revisar envés de hojas en zonas húmedas del lote.",
            "manejo": "Fungicida preventivo (Elatus, Bumper) con humedad alta y temp 20-28°C.",
        },
        {
            "nombre": "Mancha objetivo (Corynespora cassiicola)",
            "tipo": "enfermedad",
            "etapas_riesgo": ["R1", "R3"],
            "sintomas": "Manchas circulares con halo amarillo en hojas medias y superiores.",
            "monitoreo": "Frecuente en campañas húmedas; revisar tras lluvias prolongadas.",
            "manejo": "Mejorar drenaje; fungicida si afecta >5% del follaje.",
        },
        {
            "nombre": "Trips y pulgón",
            "tipo": "insecto",
            "etapas_riesgo": ["V4", "R1"],
            "sintomas": "Enrollamiento de hojas, honeydew, transmisión de virus.",
            "monitoreo": "Revisar brotes nuevos en etapas vegetativas tempranas.",
            "manejo": "Control cultural; insecticida selectivo si hay colonias activas.",
        },
    ],
    "maiz": [
        {
            "nombre": "Gusano cogollero (Spodoptera frugiperda)",
            "tipo": "insecto",
            "etapas_riesgo": ["V6", "VT", "R1"],
            "sintomas": "Daño en cogollo, plantas con aspecto de 'cogollo quemado'.",
            "monitoreo": "Buscar heces y larvas dentro del cogollo.",
            "manejo": "Aplicación dirigida al cogollo; Bt en presión media.",
        },
        {
            "nombre": "Sigatoka / mancha foliar (Cercospora spp.)",
            "tipo": "enfermedad",
            "etapas_riesgo": ["V8", "VT", "R1"],
            "sintomas": "Estrías grisáceas paralelas a nervaduras; necrosis foliar.",
            "monitoreo": "Hojas del tercio medio en días húmedos.",
            "manejo": "Fox Xpro o Bumper en VT-R1 si hay presión.",
        },
        {
            "nombre": "Chinche barriga-verde",
            "tipo": "insecto",
            "etapas_riesgo": ["R1", "R3"],
            "sintomas": "Granos mal formados, mazorcas chuzas.",
            "monitoreo": "Muestreo en floración y llenado de grano.",
            "manejo": "Tratar si supera umbral en etapa reproductiva.",
        },
        {
            "nombre": "Gorgojo del maíz",
            "tipo": "insecto",
            "etapas_riesgo": ["R3", "R5"],
            "sintomas": "Daño en granos durante llenado y madurez.",
            "monitoreo": "Trampas y revisión de mazorcas en R3.",
            "manejo": "Rotación de cultivos; tratamiento de semilla preventivo.",
        },
        {
            "nombre": "Pudrición de mazorca (Fusarium)",
            "tipo": "enfermedad",
            "etapas_riesgo": ["R3", "R5"],
            "sintomas": "Mazorcas con hongos blancos/rosados, granos abortados.",
            "monitoreo": "Post-lluvia intensa o granizo; revisar base de mazorca.",
            "manejo": "Evitar estrés hídrico; fungicida preventivo en VT si campaña húmeda.",
        },
    ],
}

ZONAS_SANTA_CRUZ: dict[str, str] = {
    "default": "Llanura oriental de Santa Cruz",
    "norte": "Norte integrado (San Julián, Cuatro Cañadas) — presión alta de cogollero en verano",
    "sur": "Sur chaqueño — mayor riesgo de sequía y estrés hídrico",
    "este": "Este integrado (San Ignacio, Pailón) — humedad alta, roya y sigatoka frecuentes",
}
