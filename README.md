# AgroFloppy

Copiloto inteligente para ingenieros agrónomos, administradores agrícolas y productores tecnificados. Analiza cultivos de **soya** y **maíz** en Santa Cruz, Bolivia usando información meteorológica de múltiples fuentes, reglas agronómicas validadas e IA generativa (pendiente).

| Recurso | URL |
|---------|-----|
| **GitHub** | https://github.com/panchito000/AGRO-FLOPPY |
| **Producción** | https://agro-floppy-lilac.vercel.app |
| **App (tras login)** | https://agro-floppy-lilac.vercel.app/app.html |
| **API health** | https://agro-floppy-lilac.vercel.app/api/ |
| **Swagger** | https://agro-floppy-lilac.vercel.app/api/docs |
| **Supabase (proyecto)** | https://supabase.com/dashboard/project/skxgdeogffuaafkdynyk |

---

## Qué hace

1. El usuario **inicia sesión** (Supabase Auth)
2. Selecciona una finca en el mapa, elige cultivo y tipo de evaluación
3. Opcionalmente agrega notas de texto o un audio (grabación + dictado en vivo)
4. El backend consulta el clima en vivo de la ubicación (3 fuentes API gratuitas)
5. Evalúa condiciones contra reglas agronómicas (umbrales de viento, temp, humedad por producto)
6. Devuelve un **semáforo** (verde/amarillo/rojo) con veredicto, advertencias, recomendación y explicación
7. Guarda la evaluación en **Supabase** (PostgreSQL) si `DATABASE_URL` está configurada
8. *(Pendiente)* Generar recomendaciones enriquecidas con OpenAI

---

## Estado actual del MVP

| Funcionalidad | Estado |
|---------------|--------|
| Formulario + mapa Leaflet + audio | ✅ Listo |
| Login / registro (Supabase Auth) | ✅ Listo |
| Clima consolidado (Open-Meteo, wttr, Foreca) | ✅ Integrado en backend |
| Reglas agronómicas + semáforo | ✅ Integrado |
| Persistencia en Supabase | ✅ Código listo (requiere `DATABASE_URL` en local/Vercel) |
| Schema BD v2 (7 tablas + datos semilla) | ✅ Aplicado en Supabase |
| Frontend responsive (celular / pantalla chica) | ✅ Scroll + auto-scroll a resultados |
| Despliegue Vercel | ✅ Frontend + API serverless |
| OpenAI / IA generativa | ⏳ Pendiente |
| Validación JWT en backend + evaluaciones por usuario | ⏳ Pendiente |
| Supabase Storage para audios | ⏳ Pendiente (hoy: `/tmp` en Vercel) |
| n8n workflow | 📄 Listo para importar ([`Saul/scripts/n8n_workflow.json`](Saul/scripts/n8n_workflow.json)) |

---

## Estructura del proyecto

```
AGRO-FLOPPY/
├── api/
│   └── index.py                    # Gateway serverless Vercel (monta /api)
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── app/
│       ├── config/settings.py      # Variables de entorno (Pydantic Settings)
│       ├── database/connection.py  # SQLAlchemy + PostgreSQL
│       ├── routes/                 # GET /, POST /evaluar
│       ├── services/
│       │   ├── evaluacion_service.py
│       │   ├── evaluacion_repository.py   # Persistencia en Supabase
│       │   └── clima/              # Clima + reglas (integrado desde Saul)
│       │       ├── __init__.py     # Consolidador + evaluar_agronomico()
│       │       ├── openmeteo.py
│       │       ├── wttr.py
│       │       ├── foreca.py
│       │       └── datos_agronomicos.py   # 10 productos + umbrales
│       ├── data/
│       │   └── ubicaciones.py      # 15 ubicaciones Santa Cruz
│       └── models/
│           ├── schemas.py          # Pydantic (request/response)
│           └── db_models.py        # SQLAlchemy (7 tablas)
├── frontend/                       # Fuente del frontend (desarrollo local)
│   ├── index.html                  # Login y registro
│   ├── app.html                    # App principal (protegida)
│   ├── assets/logo.png
│   ├── css/styles.css
│   └── js/
│       ├── app.js                  # Formulario + resultados + semáforo
│       ├── auth.js                 # Login/registro Supabase
│       ├── supabase-config.js      # URL + anon key (no commitear secretos)
│       ├── audio-recorder.js       # Grabación + dictado
│       ├── config.js               # URL API (local vs Vercel)
│       ├── map-picker.js
│       ├── map-config.js
│       └── santa-cruz-data.js      # 14 fincas demo + polígonos
├── public/                         # Copia servida por Vercel — mantener sincronizada
├── database/
│   ├── schema.sql                  # Schema principal (usar este)
│   ├── supabase_er_v2.sql          # Mismo modelo, formato ER
│   ├── migrations/001_initial_schema.sql
│   ├── AUDITORIA.md
│   └── scripts/
│       ├── apply_schema.py         # Aplica schema.sql vía DATABASE_URL
│       ├── test_connection.py
│       └── verify_schema.py
├── docs/
│   ├── CONTEXTO_PROYECTO.md        # Handoff / contexto completo del equipo
│   ├── README_AGRONOMIA.md
│   ├── VERCEL_ENV.md               # Guía de variables en producción
│   └── CONOCIMIENTO.md
├── scripts/
│   └── configure_vercel_env.py     # Configura env vars en Vercel vía API
├── Saul/                           # Contribución original de Saul (referencia)
│   ├── scripts/                    # Scripts standalone de clima + n8n
│   ├── Data/                       # PDFs y XLSX de ANAPO
│   └── clima_anapo_datos.json
├── vercel.json
├── requirements.txt                # Dependencias Python para Vercel
├── .env.example
├── AGENTS.md                       # Contexto para agentes de Cursor
└── IMPLEMENTACION.md               # Plan de implementación por fases
```

> **Importante:** Vercel sirve `public/`, no `frontend/`. Si editás el frontend, copiá los cambios a `public/` (o automatizá la sincronización).

---

## Modelo de Base de Datos (Supabase ER v2)

PostgreSQL en **Supabase** — proyecto `skxgdeogffuaafkdynyk` (región **us-east-1**).

### Tablas

| Tabla | Propósito |
|-------|-----------|
| `cultivos` | Catálogo: soya, maíz |
| `tipos_evaluacion` | siembra, fertilización, riego, plagas, cosecha |
| `usuarios` | Productores, agrónomos, administradores (`auth_user_id` para Supabase Auth) |
| `lugares` | 14 fincas demo de Santa Cruz |
| `campos_poligonos` | Polígonos de potreros/lotes para el mapa |
| `evaluaciones` | Registro de cada evaluación (núcleo del negocio) |
| `clima_cache` | Caché de clima por coordenadas (TTL 30 min) |

### Configurar Supabase

1. Crear cuenta en [supabase.com](https://supabase.com) (o usar el proyecto existente del equipo)
2. Copiar `.env.example` → `.env` y completar credenciales
3. Aplicar el schema:

```bash
# Desde la raíz del proyecto (con .env configurado)
pip install psycopg2-binary
python database/scripts/apply_schema.py
```

4. Verificar conexión y tablas:

```bash
python database/scripts/test_connection.py
python database/scripts/verify_schema.py
```

**Alternativa manual:** Supabase → **SQL Editor** → pegar `database/schema.sql` o `database/supabase_er_v2.sql`.

### URL de conexión (pooler recomendado)

En muchas redes la URL directa `db.*.supabase.co` no resuelve (IPv6). Usá el **pooler** de la región del proyecto:

```
postgresql://postgres.skxgdeogffuaafkdynyk:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require
```

Si la contraseña tiene caracteres especiales (ej. `!`), codificarlos en la URL (`!` → `%21`).

Credenciales en Supabase → **Settings → Database** y **Settings → API** (clave anon).

---

## Variables de entorno

Copiar `.env.example` a `.env`:

```bash
cp .env.example .env        # Linux/macOS
copy .env.example .env        # Windows
```

```env
# PostgreSQL / Supabase (preferir pooler us-east-1)
DATABASE_URL=postgresql://postgres.skxgdeogffuaafkdynyk:TU_PASSWORD@aws-0-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require

SUPABASE_URL=https://skxgdeogffuaafkdynyk.supabase.co
SUPABASE_KEY=tu-clave-anon

APP_ENV=development
CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080,http://localhost:8000
ROOT_PATH=
```

| Variable | Local | Vercel (Production) |
|----------|-------|---------------------|
| `DATABASE_URL` | Pooler Supabase | Igual que local |
| `SUPABASE_URL` | URL del proyecto | Igual |
| `SUPABASE_KEY` | Clave anon | Igual |
| `APP_ENV` | `development` | `production` |
| `ROOT_PATH` | *(vacío)* | `/api` |
| `CORS_ORIGINS` | localhost:8080 | `https://agro-floppy-lilac.vercel.app` |

Guía detallada de producción: [`docs/VERCEL_ENV.md`](docs/VERCEL_ENV.md)

Script automático (requiere token de [vercel.com/account/tokens](https://vercel.com/account/tokens)):

```bash
# PowerShell
$env:VERCEL_TOKEN = "tu_token"
python scripts/configure_vercel_env.py
```

---

## Setup local

### 1. Clonar e instalar dependencias

```bash
git clone https://github.com/panchito000/AGRO-FLOPPY.git
cd AGRO-FLOPPY
copy .env.example .env    # Completar DATABASE_URL y demás
```

```bash
cd backend
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

Dependencias: `fastapi`, `uvicorn`, `sqlalchemy`, `psycopg2-binary`, `pydantic-settings`, `python-dotenv`, `python-multipart`, `requests`.

### 2. Aplicar schema (primera vez)

```bash
cd ..
pip install psycopg2-binary
python database/scripts/apply_schema.py
```

### 3. Correr el backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Verificar: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Correr el frontend

```bash
cd frontend
python -m http.server 8080
```

| Página | URL local |
|--------|-----------|
| Login | http://localhost:8080/ |
| App | http://localhost:8080/app.html |

> En Windows el puerto 5500 suele estar bloqueado; usar **8080**. También podés usar Live Server apuntando a `frontend/`.

Copiá `frontend/js/supabase-config.example.js` → `supabase-config.js` y completá la anon key de Supabase.

El frontend detecta el entorno en [`frontend/js/config.js`](frontend/js/config.js):
- **Local** → `http://localhost:8000`
- **Vercel** → `/api`

### 5. Probar una evaluación

1. Iniciar sesión en http://localhost:8080/
2. Elegir cultivo y tipo de evaluación
3. Marcar ubicación en el mapa (lat/lng obligatorios)
4. Agregar texto o audio
5. Clic en **Analizar** → semáforo + clima + recomendación
6. Verificar en [Supabase → Table Editor → evaluaciones](https://supabase.com/dashboard/project/skxgdeogffuaafkdynyk/editor)

---

## Cómo funciona el clima

### Fuentes de datos

| Fuente | API | Costo | Datos |
|--------|-----|-------|-------|
| **Open-Meteo** | `api.open-meteo.com` | Gratis (sin key) | Temp, humedad, viento, suelo, UV, pronóstico 7 días |
| **wttr.in** | `wttr.in/{lat},{lon}` | Gratis (sin key) | Temp, humedad, viento, lluvia, pronóstico 3 días |
| **ForecaBox/ANAPO** | `data.forecabox.com` | Gratis (widget ID) | Temp, viento, pronóstico 6 días |

El consolidador en `backend/app/services/clima/__init__.py`:
1. Consulta las fuentes disponibles para las coordenadas
2. Promedia temperatura, humedad y viento
3. Extrae datos de suelo de Open-Meteo
4. Evalúa reglas agronómicas y devuelve semáforo + veredicto

### Ubicaciones con Foreca ID

| Ubicación | Coordenadas | Foreca ID |
|-----------|-------------|-----------|
| Santa Cruz de la Sierra | -17.78, -63.18 | 103904906 |
| Cuatro Cañadas | -17.40, -62.35 | 108335389 |
| San Julián | -17.78, -62.83 | 103905453 |
| San Ignacio de Velasco | -16.37, -60.96 | 103905658 |
| Okinawa Número Uno | -17.23, -62.68 | 103909360 |

### Scripts standalone de Saul (referencia / pruebas)

Los scripts originales siguen en `Saul/scripts/` para pruebas independientes. La lógica de producción está en `backend/app/services/clima/`.

```bash
cd Saul/scripts
pip install -r requirements.txt

python clima_openmeteo.py
python clima_wttr.py
python clima_foreca.py
python clima_agricultura.py    # Consolidador standalone → JSON/CSV
```

---

## Evaluación agronómica

Reglas en `backend/app/services/clima/datos_agronomicos.py`.

### Productos evaluados (10)

| Producto | Tipo | Viento max | Temp (min-max) | Humedad min | Riesgo deriva |
|----------|------|------------|-----------------|-------------|---------------|
| Glifosato | Herbicida | 16 km/h | 10-30°C | 55% | Medio |
| 2,4-D | Herbicida | 15 km/h | 10-25°C | 55% | Alto |
| Dicamba | Herbicida | 12 km/h | 10-29°C | 55% | Muy alto |
| Fomesafén | Herbicida | 16 km/h | 15-30°C | 60% | Medio |
| Elatus | Fungicida | 15 km/h | 15-30°C | 60% | Bajo |
| Fox Xpro | Fungicida | 15 km/h | 10-30°C | 55% | Bajo |
| Bumper | Fungicida | 15 km/h | 10-30°C | 55% | Bajo |
| Lambda-cialotrina | Insecticida | 24 km/h | 10-32°C | 50% | Medio |
| Metomil | Insecticida | 16 km/h | 15-32°C | 50% | Medio |
| Bt | Insecticida | 15 km/h | 15-30°C | 60% | Bajo |

### Reglas de semáforo

**Fumigación:**
- **Verde**: viento 5-15, temp 18-30, humedad 55-85, prob lluvia <10%
- **Amarillo**: viento 3-20, temp 10-35, humedad 45-90, prob lluvia <30%
- **Rojo**: fuera de rango amarillo

**Siembra:**
- **Verde**: temp suelo ≥15°C, humedad suelo ≥60%, sin helada, lluvia 7d ≥10mm
- **Amarillo**: temp suelo ≥10°C, humedad suelo ≥50%, sin helada, lluvia 7d ≥5mm
- **Rojo**: fuera de rango amarillo

### Condiciones especiales

- **Inversión térmica**: viento <3 km/h entre 17:00-07:00 con cielo despejado
- **Surazo**: vientos >40 km/h con caída brusca de temperatura
- **Metomil**: RESTRINGIDO en Bolivia, requiere receta SENASAG
- **Lambda-cialotrina**: NO aplicar durante inversiones térmicas

---

## Endpoints

| Método | Ruta (local) | Ruta (Vercel) | Descripción |
|--------|-------------|---------------|-------------|
| GET | `/` | `/api/` | Health check |
| POST | `/evaluar` | `/api/evaluar` | Evaluación agronómica |
| GET | `/docs` | `/api/docs` | Swagger UI |

### POST /evaluar

**Request** (multipart/form-data):

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| cultivo | string | Sí | `soya` o `maiz` |
| tipo_evaluacion | string | Sí | `siembra`, `fertilizacion`, `riego`, `plagas`, `cosecha` |
| ubicacion | string | Sí | Nombre de la ubicación |
| latitud | float | Sí | Latitud (-90 a 90) |
| longitud | float | Sí | Longitud (-180 a 180) |
| texto | string | No* | Notas del usuario (max 5000 chars) |
| audio | file | No* | Audio (webm, ogg, mp3, wav, m4a) |

\* Al menos uno de `texto` o `audio` es obligatorio.

**Response** (JSON):

```json
{
  "cultivo": "soya",
  "tipo_evaluacion": "siembra",
  "ubicacion": "Finca demo",
  "latitud": -17.78,
  "longitud": -63.18,
  "texto": "Notas del agrónomo",
  "audio_recibido": false,
  "mensaje": "Evaluación procesada correctamente. Texto incluido. Semáforo: verde.",
  "evaluacion_id": 1,
  "veredicto": "SEGURO",
  "semaforo": "verde",
  "condiciones_actuales": {
    "temperatura_c": 24.5,
    "humedad_pct": 72,
    "viento_kmh": 8.3,
    "prob_lluvia_pct": 15,
    "temp_suelo_c": 18.2,
    "humedad_suelo_pct": 65.0
  },
  "advertencias": [],
  "recomendacion": "Condiciones favorables para la operación.",
  "explicacion": "Viento 8.3 km/h dentro del rango. Temperatura 24.5°C en rango óptimo.",
  "fuentes_usadas": ["openmeteo", "wttr"],
  "producto_evaluado": "glifosato"
}
```

---

## Frontend

### Páginas

| Archivo | Ruta | Función |
|---------|------|---------|
| [`frontend/index.html`](frontend/index.html) | `/` | Login y registro |
| [`frontend/app.html`](frontend/app.html) | `/app.html` | Formulario de evaluación (requiere sesión) |

### Características

- Login/registro con Supabase Auth
- Formulario con cultivo, tipo, mapa, texto y audio (grabar + dictado en vivo)
- Mapa modal Leaflet con geolocalización y 14 fincas demo de Santa Cruz
- Tarjetas de resultados: **Clima**, **Recomendación**, **Explicación**
- Semáforo visual (verde / amarillo / rojo) con veredicto y advertencias
- **Responsive**: en celular y pantallas chicas el formulario deja de ser sticky, se puede scrollear y tras analizar la página baja automáticamente a los resultados

### Sincronizar frontend → public (antes de deploy)

```powershell
# PowerShell, desde la raíz del proyecto
Copy-Item frontend\index.html public\index.html -Force
Copy-Item frontend\app.html public\app.html -Force
Copy-Item frontend\css\styles.css public\css\styles.css -Force
Copy-Item frontend\js\*.js public\js\ -Force
Copy-Item frontend\assets\logo.png public\assets\logo.png -Force
```

---

## Despliegue en Vercel

Arquitectura: **Vercel** (frontend estático + API Python serverless) + **Supabase** (PostgreSQL).

```
Usuario → agro-floppy-lilac.vercel.app → FastAPI (/api) → Supabase PostgreSQL
```

### Paso 1 — Código en GitHub

```bash
git add .
git commit -m "descripción del cambio"
git push origin main
```

### Paso 2 — Importar / conectar en Vercel

1. [vercel.com/new](https://vercel.com/new) → importar **AGRO-FLOPPY**
2. Vercel detecta `vercel.json` automáticamente
3. Deploy

### Paso 3 — Variables de entorno

En **Project → Settings → Environment Variables** (Production):

| Variable | Valor |
|----------|-------|
| `DATABASE_URL` | Pooler Supabase (ver `.env.example`) |
| `SUPABASE_URL` | `https://skxgdeogffuaafkdynyk.supabase.co` |
| `SUPABASE_KEY` | Clave anon de Supabase |
| `ROOT_PATH` | `/api` |
| `APP_ENV` | `production` |
| `CORS_ORIGINS` | `https://agro-floppy-lilac.vercel.app` |

Ver [`docs/VERCEL_ENV.md`](docs/VERCEL_ENV.md) o ejecutar [`scripts/configure_vercel_env.py`](scripts/configure_vercel_env.py).

### Paso 4 — Redeploy y verificar

```bash
curl https://agro-floppy-lilac.vercel.app/api/
```

Tras analizar desde la app, revisar filas en [Supabase → evaluaciones](https://supabase.com/dashboard/project/skxgdeogffuaafkdynyk/editor).

---

## n8n (Automatización opcional)

Workflow listo en `Saul/scripts/n8n_workflow.json`.

### Opción A: n8n Cloud

1. Crear cuenta en [n8n.cloud](https://n8n.cloud)
2. Importar `Saul/scripts/n8n_workflow.json`
3. Activar el workflow

**Probar:**
```bash
curl -X POST https://tu-workspace.n8n.cloud/webhook/zafra-check \
  -H "Content-Type: application/json" \
  -d '{"latitude": -17.78, "longitude": -63.18}'
```

### Opción B: n8n local (Docker)

```bash
docker run -it --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n
```

---

## Datos de Saul

| Archivo | Descripción |
|---------|-------------|
| `Saul/scripts/clima_*.py` | Scrapers individuales + consolidador standalone |
| `Saul/scripts/datos_agronomicos.py` | Reglas + 10 productos + calendario fenológico |
| `Saul/scripts/ubicaciones.py` | 15 ubicaciones (5 agrícolas + 10 capitales) |
| `Saul/scripts/n8n_workflow.json` | Workflow n8n completo |
| `Saul/Data/Cosecha_Parametros.xlsx` | Parámetros de cosecha |
| `Saul/clima_anapo_datos.json` | Datos climáticos ANAPO pre-colectados |

### Integración en el backend (ya hecha)

| Origen (Saul) | Destino (backend) |
|---------------|-------------------|
| `clima_openmeteo.py` | `backend/app/services/clima/openmeteo.py` |
| `clima_wttr.py` | `backend/app/services/clima/wttr.py` |
| `clima_foreca.py` | `backend/app/services/clima/foreca.py` |
| `datos_agronomicos.py` | `backend/app/services/clima/datos_agronomicos.py` |
| `ubicaciones.py` | `backend/app/data/ubicaciones.py` |
| `clima_agricultura.py` | Lógica en `backend/app/services/clima/__init__.py` |

---

## Próximos pasos

- [x] Integrar clima (Open-Meteo, wttr, Foreca) en el backend
- [x] Reglas agronómicas + semáforo en `/evaluar`
- [x] Schema Supabase v2 + scripts de aplicación/verificación
- [x] Persistir evaluaciones en Supabase
- [x] Frontend responsive (móvil / pantalla chica)
- [x] Autenticación con Supabase Auth (login/registro)
- [ ] Validación JWT en backend + historial de evaluaciones por usuario
- [ ] Integrar OpenAI para recomendaciones con IA
- [ ] Supabase Storage para audios persistentes
- [ ] Alertas automáticas por WhatsApp/Telegram (vía n8n)
- [ ] Dashboard de monitoreo de cultivos
- [ ] Tests con pytest + TestClient

---

## Documentación adicional

| Archivo | Contenido |
|---------|-----------|
| [`docs/CONTEXTO_PROYECTO.md`](docs/CONTEXTO_PROYECTO.md) | Handoff completo del proyecto (URLs, auth, deploy) |
| [`AGENTS.md`](AGENTS.md) | Contexto para agentes de Cursor |
| [`IMPLEMENTACION.md`](IMPLEMENTACION.md) | Plan de implementación por fases |
| [`docs/README_AGRONOMIA.md`](docs/README_AGRONOMIA.md) | Detalle agronómico |
| [`docs/VERCEL_ENV.md`](docs/VERCEL_ENV.md) | Variables de entorno en producción |
| [`docs/CONOCIMIENTO.md`](docs/CONOCIMIENTO.md) | Base de conocimiento |
| [`database/AUDITORIA.md`](database/AUDITORIA.md) | Auditoría del modelo de datos |

---

## Equipo

Proyecto hackathon **AgroFloppy** — Santa Cruz, Bolivia.

Repositorio: [github.com/panchito000/AGRO-FLOPPY](https://github.com/panchito000/AGRO-FLOPPY)
