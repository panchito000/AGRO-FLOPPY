# Plan de Implementación — AGRO-FLOPPY MVP

## Estado actual
- Frontend funcional (formulario + mapa + grabación de audio)
- Backend FastAPI con endpoint `/evaluar` que solo hace eco
- Scripts de Saul listos (clima + reglas agronómicas)
- Modelo ER v2 definido pero NO creado en Supabase
- n8n workflow listo para importar

---

## FASE 1 — Base de datos (15 min)

### Archivo: `database/supabase_er_v2.sql`

Crear el SQL completo con:
- 7 tablas: cultivos, tipos_evaluacion, usuarios, lugares, campos_poligonos, evaluaciones, clima_cache
- Datos semilla: 2 cultivos, 5 tipos evaluación, 14 lugares demo
- Índices y constraints

### Pasos:
1. Ir a supabase.com → crear proyecto `agro_floppy`
2. SQL Editor → pegar contenido del .sql
3. Copiar DATABASE_URL, SUPABASE_URL, SUPABASE_KEY
4. Crear `.env` con esas credenciales

---

## FASE 2 — Mover scripts de Saul al backend (10 min)

### Mover archivos:

```
Saul/scripts/clima_openmeteo.py    → backend/app/services/clima/openmeteo.py
Saul/scripts/clima_wttr.py         → backend/app/services/clima/wttr.py
Saul/scripts/clima_foreca.py       → backend/app/services/clima/foreca.py
Saul/scripts/datos_agronomicos.py  → backend/app/services/clima/datos_agronomicos.py
Saul/scripts/ubicaciones.py        → backend/app/data/ubicaciones.py
```

### Crear:
- `backend/app/services/clima/__init__.py` → consolidador
- `backend/app/data/__init__.py`

### Modificar:
- `backend/requirements.txt` → agregar `requests>=2.31.0`

---

## FASE 3 — Servicio de clima consolidado (15 min)

### Archivo: `backend/app/services/clima/__init__.py`

Función `obtener_clima_consolidado(lat, lon)`:
1. Llama a openmeteo.obtener_clima(lat, lon)
2. Llama a wttr.obtener_clima(lat, lon)
3. Llama a foreca.obtener_clima(foreca_id, widget_id) si hay ID
4. Promedia temp, humedad, viento
5. Extrae temp_suelo y humedad_suelo de Open-Meteo
6. Retorna dict estandarizado:
```python
{
    "temperatura_c": float,
    "humedad_pct": float,
    "viento_kmh": float,
    "prob_lluvia_pct": float,
    "temp_suelo_c": float | None,
    "humedad_suelo_pct": float | None,
}
```

---

## FASE 4 — Actualizar schemas Pydantic (5 min)

### Archivo: `backend/app/models/schemas.py`

Agregar a `EvaluacionResponse`:
- veredicto: str
- semaforo: str ("verde" | "amarillo" | "rojo")
- condiciones_actuales: dict
- advertencias: list[dict]
- recomendacion: str | None
- explicacion: str | None
- fuentes_usadas: list[str]

---

## FASE 5 — Actualizar endpoint /evaluar (20 min)

### Archivo: `backend/app/services/evaluacion_service.py`

Reemplazar `procesar_evaluacion()` para que:

1. Llame a `obtener_clima_consolidado(lat, lon)`
2. Importe `evaluar_fumigacion` o `evaluar_siembra` de datos_agronomicos.py
3. Evalúe según tipo_evaluacion
4. Genere recomendacion y explicacion basadas en veredicto
5. Retorne EvaluacionResponse con todos los campos

### Lógica:
```
SI tipo_evaluacion == "siembra" o "fertilizacion" o "riego" o "cosecha":
  → evaluar_siembra(cultivo, condiciones_clima)
SI tipo_evaluacion == "plagas":
  → evaluar_fumigacion(producto_seleccionado, condiciones_clima)
```

---

## FASE 6 — Actualizar frontend (20 min)

### Archivo: `frontend/js/app.js`

Modificar `showPlaceholderResults(data)` para renderizar:

1. **Semáforo visual**: div con fondo verde/amarillo/rojo según data.semaforo
2. **Tarjeta Clima**: mostrar temp, humedad, viento, prob lluvia
3. **Tarjeta Recomendación**: texto de data.recomendacion
4. **Tarjeta Explicación**: texto de data.explicacion
5. **Lista advertencias**: items con icono de severidad

### Agregar CSS para:
- .semaforo-verde (fondo verde)
- .semaforo-amarillo (fondo amarillo)
- .semaforo-rojo (fondo rojo)
- .advertencia-item (lista de advertencias)

---

## FASE 7 — n8n Cloud (10 min)

1. Crear cuenta en n8n.cloud
2. Importar `Saul/scripts/n8n_workflow.json`
3. Activar workflow
4. Copiar URL del webhook
5. Probar con curl

---

## FASE 8 — Deploy Vercel (10 min)

1. git add . && git commit && git push
2. Importar en Vercel
3. Configurar variables de entorno
4. Verificar frontend + API + Swagger

---

## Orden de ejecución

| # | Fase | Tiempo | Dependencia |
|---|------|--------|-------------|
| 1 | Supabase + SQL | 15 min | Ninguna |
| 2 | Mover scripts Saul | 10 min | Ninguna |
| 3 | Servicio clima | 15 min | Fase 2 |
| 4 | Schemas Pydantic | 5 min | Ninguna |
| 5 | Endpoint /evaluar | 20 min | Fase 1, 3, 4 |
| 6 | Frontend | 20 min | Fase 5 |
| 7 | n8n cloud | 10 min | Ninguna |
| 8 | Deploy Vercel | 10 min | Todo |
| **Total** | | **~105 min** | |

---

## Archivos a crear/modificar

### Crear:
- `database/supabase_er_v2.sql`
- `backend/app/services/clima/__init__.py`
- `backend/app/data/__init__.py`

### Mover (copiar de Saul/):
- `clima_openmeteo.py` → `backend/app/services/clima/`
- `clima_wttr.py` → `backend/app/services/clima/`
- `clima_foreca.py` → `backend/app/services/clima/`
- `datos_agronomicos.py` → `backend/app/services/clima/`
- `ubicaciones.py` → `backend/app/data/`

### Modificar:
- `backend/requirements.txt` (agregar requests)
- `backend/app/models/schemas.py` (campos nuevos response)
- `backend/app/services/evaluacion_service.py` (lógica real)
- `frontend/js/app.js` (renderizar resultados)
- `frontend/css/` (estilos semáforo)
