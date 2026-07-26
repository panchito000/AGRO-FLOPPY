"""Preguntas frecuentes y respuestas curadas (Santa Cruz, soya/maíz).

Extraídas y resumidas de: Riquezas de Bolivia (Santa Cruz), CIPCA frontera soyera,
ANAPO, CIAT/CETABOL y guías del equipo Zafra.
"""

FAQ_AGRONOMICO: list[dict] = [
    {
        "pregunta_patrones": ["zona este", "zona norte", "norte integrado", "donde se siembra", "region soya"],
        "cultivo": "soya",
        "tipo_evaluacion": "siembra",
        "respuesta": (
            "En Santa Cruz la soya se concentra en dos grandes zonas: la Zona Este (Subregión Chiquitana, "
            "suelos más fértiles — Pailón, Cuatro Cañadas, San Julián, Guarayos) con ~70% de la siembra "
            "de verano; y el Norte Integrado (Warnes, Montero, Okinawa, Yapacaní) con fuerte componente "
            "de siembra de invierno. Evitá sembrar en suelos marginales reconocidos por baja productividad "
            "(ej. zonas de Pailón Centro/Sur tras compactación)."
        ),
        "fuente": "CIPCA (2020) + ANAPO — frontera agrícola soyera Santa Cruz",
    },
    {
        "pregunta_patrones": ["siembra directa", "labranza", "compactacion", "suelo compactado"],
        "cultivo": "soya",
        "tipo_evaluacion": "siembra",
        "respuesta": (
            "La siembra directa en Santa Cruz (≈85% de la superficie según ANAPO) evita remoción del suelo, "
            "mantiene cobertura con rastrojo y usa rotación con maíz/sorgo. Surgió ante suelos compactados "
            "y baja de rendimientos en la Zona Este. No conviene volver a labranza convencional sin diagnóstico: "
            "aumenta erosión y pérdida de materia orgánica."
        ),
        "fuente": "CIPCA / Díaz (2001) citado en Mundos Rurales 2020",
    },
    {
        "pregunta_patrones": ["peores epocas", "cuando no sembrar", "mal epoca", "no deberia sembrar"],
        "cultivo": "soya",
        "tipo_evaluacion": "siembra",
        "respuesta": (
            "Peores momentos para sembrar soya en Santa Cruz: suelo frío o compactado, sequía fuerte antes "
            "de emergencia, justo antes de lluvias que encharquen, y en zonas ya marginales por años de "
            "monocultivo sin rotación (Pailón Centro/Sur históricamente). Preferí ventana verano cuando el "
            "suelo tenga humedad y temperatura adecuada."
        ),
        "fuente": "CIPCA + guía siembra Zafra AI",
    },
    {
        "pregunta_patrones": ["maleza", "herbicida", "glifosato", "resistencia", "hoja ancha"],
        "cultivo": "soya",
        "tipo_evaluacion": "plagas",
        "respuesta": (
            "Con siembra directa aumentaron malezas de hoja ancha; el CIAT estima 30–50% de pérdida de "
            "rendimiento por malezas si no se controlan. Evitá aplicaciones indiscriminadas de herbicidas "
            "ni repetir siempre el mismo principio activo (riesgo de resistencia al glifosato). "
            "Usá manejo integrado: rotación, dosis recomendadas y monitoreo previo."
        ),
        "fuente": "CIAT (2019) citado en CIPCA 2020",
    },
    {
        "pregunta_patrones": ["plagas", "prevenir", "prevencion", "sufrir", "enfermedades soya"],
        "cultivo": "soya",
        "tipo_evaluacion": "plagas",
        "respuesta": (
            "Prevención de plagas en soya (Santa Cruz): monitoreo semanal, manejo integrado (MIP), "
            "rotación con maíz/sorgo, no tratar por calendario fijo. CIPCA y CIAT recomiendan frenar "
            "degradación del suelo y diversificar — monocultivo mecanizado sin rotación aumenta presión "
            "de malezas, compactación y pérdida de fertilidad."
        ),
        "fuente": "CIPCA 2020 + catálogo plagas Zafra",
    },
    {
        "pregunta_patrones": ["peores formas", "no deberia fertilizar", "cuando no fertilizar", "evitar fertiliz"],
        "cultivo": "soya",
        "tipo_evaluacion": "fertilizacion",
        "respuesta": (
            "No fertilizar soya: justo antes de lluvia fuerte (lixiviación), con suelo encharcado, "
            "sin análisis de suelo (exceso de N genera vegetativo), en pleno calor con urea foliar, "
            "ni en suelos frágiles sin plan de recuperación. CETABOL/CIAT enfatizan mantener fertilidad "
            "con rotaciones y técnicas conservacionistas antes de abonar a ciegas."
        ),
        "fuente": "CETABOL/CIAT — Riquezas de Bolivia + guía Zafra",
    },
    {
        "pregunta_patrones": ["me conviene regar", "puedo regar", "hora regar", "cuando regar"],
        "cultivo": "soya",
        "tipo_evaluacion": "riego",
        "respuesta": (
            "Para regar soya en Santa Cruz: preferí madrugada (4:00–8:00) o atardecer; evitá mediodía "
            "con calor fuerte. Revisá si ya hay lluvia prevista o suelo húmedo. En el Norte Integrado "
            "hay mayor precipitación (~1.347 mm/año) — muchas veces el riego supplemental solo se justifica "
            "en floración/llenado (R1–R5) con déficit real."
        ),
        "fuente": "Guía riego Zafra + CIPCA (Norte Integrado)",
    },
    {
        "pregunta_patrones": ["no deberia hacer", "que no hacer", "evitar regar", "peores formas regar", "a la hora de regar"],
        "cultivo": "soya",
        "tipo_evaluacion": "riego",
        "respuesta": (
            "Errores al regar: riego superficial frecuente, regar al mediodía con evaporación alta, "
            "regar con suelo encharcado, regar antes de lluvia fuerte, mojar follaje al atardecer sin secado. "
            "En suelos frágiles del oriente (capa fértil delgada), el exceso de agua sin drenaje empeora "
            "compactación y pérdida de raíces."
        ),
        "fuente": "CIAT suelos + guía riego Zafra AI",
    },
    {
        "pregunta_patrones": ["suelo apto", "fertilidad suelo", "8 por ciento", "uso agropecuario"],
        "cultivo": "soya",
        "tipo_evaluacion": "siembra",
        "respuesta": (
            "Según el Plan de Uso de Suelo de Santa Cruz, solo ~8% del departamento es Uso Agropecuario "
            "Intensivo (mejores tierras para agricultura comercial). El 73% del suelo intensivo del Norte "
            "Integrado ya estaba en uso hacia 2001 — expandir sin criterio lleva a zonas forestales o "
            "suelos frágiles con bajo retorno."
        ),
        "fuente": "GASC Plan Uso de Suelo 2009 — CIPCA 2020",
    },
    {
        "pregunta_patrones": ["anapo", "asistencia tecnica", "semilla", "manual siembra"],
        "cultivo": "soya",
        "tipo_evaluacion": "siembra",
        "respuesta": (
            "ANAPO brinda a productores: planificación de semilla por campaña, manual de siembra directa, "
            "boletines técnicos, análisis de calidad de grano, pesaje en acopios, asistencia técnica y "
            "representación gremial. Publica informes de campaña y datos de superficie por zona (Este/Norte)."
        ),
        "fuente": "Riquezas de Bolivia — ANAPO (2020)",
    },
    {
        "pregunta_patrones": ["fumigacion aerea", "avion", "aplicar producto", "viento aplicar"],
        "cultivo": "soya",
        "tipo_evaluacion": "plagas",
        "respuesta": (
            "En Santa Cruz la fumigación aérea es común en extensas áreas de soya, maíz y girasol por "
            "eficiencia en grandes lotes. A nivel de lote, igual aplica: no aplicar con viento alto, "
            "lluvia inminente ni horas de calor extremo; respetar dosis y MIP antes de entrar con avión o terrestre."
        ),
        "fuente": "Riquezas de Bolivia — Fumigación aérea Santa Cruz",
    },
    {
        "pregunta_patrones": ["okinawa", "colonias", "cetabol", "jica"],
        "cultivo": "soya",
        "tipo_evaluacion": "fertilizacion",
        "respuesta": (
            "CETABOL (JICA) en colonias Okinawa y San Juan difunde técnicas de fertilidad de suelos, "
            "agricultura conservacionista y manejo bovino. Objetivo: agricultura sostenible como modelo "
            "para el oriente — rotación, materia orgánica y evitar degradación por monocultivo intensivo."
        ),
        "fuente": "Riquezas de Bolivia — CETABOL/JICA",
    },
]
