# Auditoría de base de datos — AGRO-FLOPPY

**Fecha:** 2026-07-25  
**Supabase ref:** `skxgdeogffuaafkdynyk`  
**Estado anterior:** schema `public` vacío  
**Estado objetivo:** 7 tablas + datos semilla + RLS

---

## Hallazgos de la auditoría

### Esquema anterior (`schema.sql` v1)

| Problema | Impacto |
|----------|---------|
| Faltaban campos `texto` y audio | `POST /evaluar` no podía persistir notas ni metadatos de audio |
| `tipo_evaluacion` como VARCHAR suelto | Sin catálogo ni FK; difícil validar y consultar |
| Campo `resultado` genérico | No separaba recomendación, explicación ni clima |
| Sin tabla de lugares demo | 14 fincas de `santa-cruz-data.js` solo en JS, no en BD |
| Sin caché de clima | OpenWeather requeriría llamadas repetidas |
| `SERIAL` en lugar de IDENTITY | Funcional pero menos idiomático en PostgreSQL moderno |
| Sin RLS | Tablas expuestas en Supabase sin protección por defecto |
| Sin `auth_user_id` en usuarios | Bloqueaba integración futura con Supabase Auth |

### Alineación con el código

| Fuente | Campos relevantes |
|--------|---------------------|
| `schemas.py` | cultivo, tipo_evaluacion, ubicacion, lat/lng, texto (5000) |
| `evaluar.py` | multipart + audio UploadFile |
| `evaluacion_service.py` | audio_nombre, audio_tamano_bytes, mensaje |
| `santa-cruz-data.js` | 14 lugares + 3 polígonos |
| `README_AGRONOMIA.md` | 5 tipos de evaluación, variables climáticas |

---

## Esquema nuevo (v2)

### Tablas

| Tabla | PK | Propósito |
|-------|-----|-----------|
| `cultivos` | `INTEGER IDENTITY` | Catálogo soya / maíz |
| `tipos_evaluacion` | `INTEGER IDENTITY` | siembra, fertilización, riego, plagas, cosecha |
| `usuarios` | `INTEGER IDENTITY` | Productores, agrónomos, administradores |
| `lugares` | `INTEGER IDENTITY` | Fincas demo Santa Cruz |
| `campos_poligonos` | `INTEGER IDENTITY` | Polígonos del mapa (JSONB) |
| `evaluaciones` | `INTEGER IDENTITY` | Registro de cada POST /evaluar |
| `clima_cache` | `INTEGER IDENTITY` | Snapshot OpenWeather por coordenadas |

### Tipos de datos clave en `evaluaciones`

| Columna | Tipo | Origen |
|---------|------|--------|
| `texto` | `VARCHAR(5000)` | Formulario |
| `audio_nombre` | `VARCHAR(255)` | Servicio de upload |
| `audio_mime_type` | `VARCHAR(100)` | Content-Type del archivo |
| `audio_tamano_bytes` | `BIGINT` | Tamaño en bytes |
| `audio_storage_path` | `VARCHAR(512)` | Supabase Storage (futuro) |
| `recomendacion` | `TEXT` | Tarjeta Recomendación |
| `explicacion` | `TEXT` | Tarjeta Explicación (IA) |
| `clima_json` | `JSONB` | Tarjeta Clima |
| `estado` | `VARCHAR(30)` | recibida → procesando → completada / error |

### Datos semilla incluidos

- 2 cultivos (soya, maíz)
- 5 tipos de evaluación
- 14 lugares demo Santa Cruz
- 3 polígonos de campos

### Seguridad

- RLS habilitado en las 7 tablas
- Sin políticas públicas (deny-by-default vía Data API)
- Backend FastAPI con `DATABASE_URL` directo bypass RLS (rol postgres)

---

## Cómo aplicar en Supabase

### Opción A — SQL Editor (recomendada si MCP no está conectado)

1. Ir a [Supabase Dashboard → SQL Editor](https://supabase.com/dashboard/project/skxgdeogffuaafkdynyk/sql)
2. Pegar el contenido de `database/schema.sql`
3. Ejecutar

### Opción B — Script Python

```bash
# Crear .env con DATABASE_URL de Supabase (Settings → Database → Connection string)
pip install psycopg2-binary
python database/scripts/apply_schema.py
```

### Opción C — Supabase MCP

```
apply_migration con database/migrations/001_initial_schema.sql
```

### Verificación post-aplicación

```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' ORDER BY table_name;

SELECT COUNT(*) AS cultivos FROM cultivos;        -- 2
SELECT COUNT(*) AS tipos FROM tipos_evaluacion;   -- 5
SELECT COUNT(*) AS lugares FROM lugares;          -- 14
SELECT COUNT(*) AS poligonos FROM campos_poligonos; -- 3
```

---

## Próximo paso en código

Conectar `POST /evaluar` → insert en `evaluaciones` usando los modelos SQLAlchemy actualizados en `backend/app/models/db_models.py`.
