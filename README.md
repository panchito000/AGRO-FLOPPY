# AGRO-FLOPPY (Zafra AI)

Copiloto inteligente para ingenieros agrónomos, administradores agrícolas y productores tecnificados. Analiza cultivos de **soya** y **maíz** en Santa Cruz, Bolivia usando información meteorológica de múltiples fuentes, reglas agronómicas validadas e IA.

## Qué hace

1. El usuario selecciona una finca en el mapa, elige cultivo y tipo de evaluación
2. El sistema consulta el clima actual de la ubicación (3 fuentes API gratuitas)
3. Evalúa condiciones contra reglas agronómicas (umbrales de viento, temp, humedad por producto)
4. Devuelve un **semáforo** (verde/amarillo/rojo) con veredicto y advertencias
5. Opcionalmente genera recomendación e explicación con IA

## Estructura del proyecto

```
AGRO-FLOPPY/
├── api/                    # Entry point serverless (Vercel)
│   └── index.py
├── backend/                # API FastAPI
│   ├── main.py
│   ├── requirements.txt
│   └── app/
│       ├── config/         # Variables de entorno
│       ├── routes/         # Endpoints (/evaluar, /health)
│       ├── services/       # Lógica de negocio
│       │   ├── evaluacion_service.py
│       │   └── clima/      # ← Servicios climáticos (de Saul)
│       │       ├── __init__.py
│       │       ├── openmeteo.py
│       │       ├── wttr.py
│       │       ├── foreca.py
│       │       └── datos_agronomicos.py
│       ├── data/           # Datos estáticos
│       │   └── ubicaciones.py
│       └── models/         # Pydantic schemas + SQLAlchemy
├── frontend/               # HTML, CSS, JavaScript vanilla
│   ├── index.html
│   └── js/
│       ├── app.js
│       ├── config.js
│       ├── map-picker.js
│       └── santa-cruz-data.js
├── database/
│   └── supabase_er_v2.sql  # ← Modelo entidad-relación completo
├── Saul/                   # ← Contribución de Saul
│   ├── scripts/            # Scripts de recolección de datos
│   ├── Data/               # PDFs y XLSX de ANAPO
│   └── clima_anapo_datos.json
├── docs/
│   └── README_AGRONOMIA.md
├── vercel.json
├── requirements.txt        # Dependencias Python (Vercel)
└── .env.example
```

---

## Modelo de Base de Datos (Supabase ER v2)

El proyecto usa **Supabase** (PostgreSQL) con el siguiente modelo:

### Tablas principales

| Tabla | Propósito |
|-------|-----------|
| `cultivos` | Catálogo: soya, maíz |
| `tipos_evaluacion` | siembra, fertilización, riego, plagas, cosecha |
| `usuarios` | Productores, agrónomos, administradores |
| `lugares` | 14 fincas demo de Santa Cruz |
| `campos_poligonos` | Polígonos de potreros/lotes para el mapa |
| `evaluaciones` | Registro de cada evaluación (núcleo del negocio) |
| `clima_cache` | Caché de clima por coordenadas |

### Configurar Supabase

1. Crear cuenta en [supabase.com](https://supabase.com)
2. Crear proyecto nuevo: nombre `agro_floppy`, contraseña segura
3. Ir a **SQL Editor** → pegar el contenido de `database/supabase_er_v2.sql`
4. Copiar credenciales de **Settings → Database**:
   - `DATABASE_URL`: `postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres`
   - `SUPABASE_URL`: `https://[PROJECT].supabase.co`
   - `SUPABASE_KEY`: clave anon de **Settings → API**

---

## Variables de entorno

Copiar `.env.example` a `.env` y completar:

```bash
cp .env.example .env
```

```env
# PostgreSQL / Supabase
DATABASE_URL=postgresql://postgres:tu_password@db.tu_proyecto.supabase.co:5432/postgres

# Supabase
SUPABASE_URL=https://tu_proyecto.supabase.co
SUPABASE_KEY=tu_clave_anon

# App
APP_ENV=development
CORS_ORIGINS=http://localhost:5500,http://127.0.0.1:5500,http://localhost:8000
ROOT_PATH=
```

---

## Setup local

### 1. Instalar dependencias del backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Dependencias: `fastapi`, `uvicorn`, `sqlalchemy`, `psycopg2-binary`, `pydantic-settings`, `python-dotenv`, `python-multipart`, `requests`.

### 2. Correr el backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Verificar: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger)

### 3. Correr el frontend

Abrir `frontend/index.html` con Live Server (VS Code) o cualquier servidor estático en puerto 5500.

El frontend detecta automáticamente:
- **Local**: apunta a `http://localhost:8000`
- **Vercel**: apunta a `/api`

---

## Cómo funciona el clima (scripts de Saul)

### Fuentes de datos

| Fuente | API | Costo | Datos |
|--------|-----|-------|-------|
| **Open-Meteo** | `api.open-meteo.com` | Gratis (sin key) | Temp, humedad, viento, suelo, UV, pronóstico 7 días |
| **wttr.in** | `wttr.in/{lat},{lon}` | Gratis (sin key) | Temp, humedad, viento, lluvia, pronóstico 3 días |
| **ForecaBox/ANAPO** | `data.forecabox.com` | Gratis (widget ID) | Temp, viento, pronóstico 6 días |

### Ubicaciones soportadas

5 ubicaciones principales del depto. Santa Cruz con IDs de Foreca:

| Ubicación | Coordenadas | Foreca ID |
|-----------|-------------|-----------|
| Santa Cruz de la Sierra | -17.78, -63.18 | 103904906 |
| Cuatro Cañadas | -17.40, -62.35 | 108335389 |
| San Julián | -17.78, -62.83 | 103905453 |
| San Ignacio de Velasco | -16.37, -60.96 | 103905658 |
| Okinawa Número Uno | -17.23, -62.68 | 103909360 |

### Cómo usar los scripts de Saul

```bash
cd Saul/scripts
pip install -r requirements.txt   # solo requests

# Probar una fuente individual
python clima_openmeteo.py
python clima_wttr.py
python clima_foreca.py

# Correr el consolidador (consulta las 3 fuentes para todas las ubicaciones)
python clima_agricultura.py

# Consulta ANAPO específica
python clima_anapo.py
```

Archivos generados: `datos_clima_agricultura.json` y `.csv`.

### Consolidación de clima

El consolidador (`clima_agricultura.py`) hace:
1. Consulta Open-Meteo, wttr y Foreca para cada ubicación
2. Promedia temperatura, humedad y viento de las fuentes disponibles
3. Extrae datos de suelo (temp y humedad) de Open-Meteo
4. Exporta JSON y CSV con los resultados

---

## Evaluación agronómica

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
- **Surazo**: vientos >40°C con caída brusca de temperatura
- **Metomil**: RESTRINGIDO en Bolivia, requiere receta SENASAG
- **Lambda-cialotrina**: NO aplicar durante inversiones térmicas

---

## n8n (Automatización)

### Opción A: n8n Cloud (recomendada para hackathon)

1. Crear cuenta gratis en [n8n.cloud](https://n8n.cloud)
2. Crear workspace nuevo
3. Importar workflow: copiar el contenido de `Saul/scripts/n8n_workflow.json`
4. Activar el workflow
5. El webhook queda en: `https://tu-workspace.n8n.cloud/webhook/zafra-check`

**Probar:**
```bash
curl -X POST https://tu-workspace.n8n.cloud/webhook/zafra-check \
  -H "Content-Type: application/json" \
  -d '{"latitude": -17.78, "longitude": -63.18}'
```

**Qué hace el workflow:**
1. Recibe POST con `{latitude, longitude}`
2. Consulta Open-Meteo y wttr.in en paralelo
3. Mergea los datos
4. Evalúa contra umbrales de 10 productos
5. Responde con JSON: veredicto, semáforo, advertencias

### Opción B: n8n local (Docker)

```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  n8nio/n8n
```

Abrir [http://localhost:5678](http://localhost:5678) → importar workflow.

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
| cultivo | string | Si | `soya` o `maiz` |
| tipo_evaluacion | string | Si | `siembra`, `fertilizacion`, `riego`, `plagas`, `cosecha` |
| ubicacion | string | Si | Nombre de la ubicación |
| latitud | float | Si | Latitud (-90 a 90) |
| longitud | float | Si | Longitud (-180 a 180) |
| texto | string | No | Notas del usuario (max 5000 chars) |
| audio | file | No | Audio (webm, ogg, mp3, wav, m4a) |

**Response** (JSON):

```json
{
  "veredicto": "SEGURO",
  "semaforo": "verde",
  "condiciones_actuales": {
    "temperatura_c": 24.5,
    "humedad_pct": 72,
    "viento_kmh": 8.3,
    "prob_lluvia_pct": 15,
    "temp_suelo_c": 18.2,
    "humedad_suelo_pct": 0.21
  },
  "advertencias": [],
  "recomendacion": "Condiciones favorables para aplicar glifosato.",
  "explicacion": "Viento 8.3 km/h dentro del rango máximo (16 km/h). Temperatura 24.5°C en rango óptimo (10-30°C). Humedad 72% adecuada (mín 55%).",
  "fuentes_usadas": ["openmeteo", "wttr", "foreca"]
}
```

---

## Despliegue en Vercel

### Paso 1 — Subir a GitHub

```bash
git add .
git commit -m " MVP con evaluación climática "
git push origin main
```

### Paso 2 — Importar en Vercel

1. Ir a [vercel.com/new](https://vercel.com/new)
2. Importar repositorio **AGRO-FLOPPY** desde GitHub
3. Vercel detecta `vercel.json` automáticamente
4. **No cambiar** Output Directory (ya está en `frontend`)
5. Clic en **Deploy**

### Paso 3 — Variables de entorno en Vercel

En **Project → Settings → Environment Variables**:

| Variable | Valor | Entorno |
|----------|-------|---------|
| `DATABASE_URL` | URL de Supabase | Production |
| `SUPABASE_URL` | `https://xxx.supabase.co` | Production |
| `SUPABASE_KEY` | Clave anon de Supabase | Production |
| `ROOT_PATH` | `/api` | Production |
| `APP_ENV` | `production` | Production |

### Paso 4 — Verificar

- Frontend: `https://tu-proyecto.vercel.app`
- API health: `https://tu-proyecto.vercel.app/api/`
- Swagger: `https://tu-proyecto.vercel.app/api/docs`

---

## Datos de Saul

### Contenido

| Archivo | Descripción |
|---------|-------------|
| `Saul/scripts/clima_openmeteo.py` | Scraper Open-Meteo API |
| `Saul/scripts/clima_wttr.py` | Scraper wttr.in API |
| `Saul/scripts/clima_foreca.py` | Scraper ForecaBox/ANAPO |
| `Saul/scripts/clima_anapo.py` | Consulta ANAPO específica |
| `Saul/scripts/clima_agricultura.py` | Consolidador principal |
| `Saul/scripts/datos_agronomicos.py` | Reglas + 10 productos + calendario fenológico |
| `Saul/scripts/ubicaciones.py` | 15 ubicaciones (5 agrícolas + 10 capitales) |
| `Saul/scripts/n8n_workflow.json` | Workflow n8n completo |
| `Saul/Data/Cosecha_Parametros.xlsx` | Parámetros de cosecha |
| `Saul/Data/ESTADISTICAS-ANAPO-2025.pdf` | Estadísticas ANAPO |
| `Saul/Data/2025-3107d-9-1-Fichas-Municipales-Dpto-Santa-Cruz-2024V2.pdf` | Fichas municipales |
| `Saul/clima_anapo_datos.json` | Datos climáticos ANAPO pre-colectados |

### Integración en el backend

Los scripts de Saul se movieron a:
- `backend/app/services/clima/` → servicios de clima
- `backend/app/data/ubicaciones.py` → ubicaciones
- `backend/app/data/productos.py` → reglas agronómicas

---

## Próximos pasos

- [ ] Integrar OpenAI para recomendaciones con IA
- [ ] Persistir evaluaciones en Supabase
- [ ] Autenticación con Supabase Auth
- [ ] Supabase Storage para audios
- [ ] Historial de evaluaciones por usuario
- [ ] Alertas automáticas por WhatsApp/Telegram (via n8n)
- [ ] Dashboard de monitoreo de cultivos
