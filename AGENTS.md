# AGRO-FLOPPY — Contexto para agentes

> Copiloto web para ingenieros agrónomos y productores (también **Zafra AI**).  
> MVP / hackathon base: estructura completa, **sin IA ni APIs externas conectadas aún**.

## Repositorio y despliegue

| Recurso | Valor |
|---------|-------|
| **Local** | `C:\Users\cesit\OneDrive\Escritorio\PRUEBA DE BUILD\AGRO-FLOPPY` |
| **GitHub** | https://github.com/panchito000/AGRO-FLOPPY |
| **Rama** | `main` (sincronizada con remoto) |
| **Último commit conocido** | `ba315bc` — "Redirect raiz a index.html en Vercel" |
| **GitHub CLI** | Autenticado como `cesitarah`; remote apunta a `panchito000` |
| **Producción** | https://agro-floppy.vercel.app → redirige a `/index.html` |
| **API health** | https://agro-floppy.vercel.app/api/ |
| **Swagger** | https://agro-floppy.vercel.app/api/docs |
| **Vercel project** | `floppy3/agro-floppy` |
| **Vercel CLI** | Cuenta `cesitarah-3671` |
| **Deploy** | Manual: `vercel deploy --prod --yes` (Git auto-deploy no conectado entre cuentas distintas) |

## Supabase

| Recurso | Valor |
|---------|-------|
| **Project ref** | `skxgdeogffuaafkdynyk` |
| **URL** | https://skxgdeogffuaafkdynyk.supabase.co |
| **MCP** | `project-0-PRUEBA DE BUILD-supabase` |
| **BD** | Schema `public` vacío — **aún no se aplicó** `database/schema.sql` |

## Historial del proyecto

| Fase | Qué se hizo |
|------|-------------|
| Creación inicial | Proyecto `zafra-ai` con FastAPI + frontend vanilla + PostgreSQL |
| Supabase MCP | MCP + Agent Skills de Supabase en `.cursor/` |
| Consolidación | Todo migrado a **AGRO-FLOPPY** (prioridad Zafra). Carpeta `zafra-ai` eliminada |
| Mapa | Selector de ubicación con Leaflet + coordenadas lat/lng |
| Datos demo | 14 fincas/campos sintéticos de Santa Cruz de la Sierra |
| Audio + texto | Formulario con notas de texto y grabación/subida de audio |
| Vercel | Proyecto desplegado en producción |
| GitHub | Código pusheado a `panchito000/AGRO-FLOPPY` |

## Estructura del proyecto

```
AGRO-FLOPPY/
├── api/
│   └── index.py              # Gateway serverless Vercel (monta /api)
├── backend/
│   ├── main.py               # FastAPI app
│   ├── requirements.txt
│   └── app/
│       ├── config/settings.py
│       ├── database/connection.py
│       ├── models/           # Pydantic + SQLAlchemy
│       ├── routes/           # GET /, POST /evaluar
│       └── services/         # evaluacion_service.py (stub)
├── frontend/                 # Fuente del frontend (desarrollo local)
├── public/                   # Copia para Vercel (mantener sincronizada)
├── database/schema.sql
├── docs/README_AGRONOMIA.md
├── vercel.json
├── requirements.txt          # Para Vercel Python
├── .env.example
├── .cursor/
│   ├── mcp.json              # Supabase MCP
│   └── skills/               # supabase + postgres-best-practices
└── README.md
```

**Importante:** Hay duplicación `frontend/` y `public/`. En Vercel se sirve `public/`. Si editás el frontend, actualizá también `public/` o automatizá la copia.

## Stack

| Capa | Tecnología |
|------|------------|
| Frontend | HTML5, CSS3, JavaScript vanilla |
| Mapa | Leaflet + OpenStreetMap (sin API key) |
| Backend | Python, FastAPI |
| BD | PostgreSQL / Supabase (preparado, no usado en runtime aún) |
| Deploy | Vercel (frontend estático + Python serverless) |
| Tools | GitHub CLI, Vercel CLI, Supabase MCP |

## Funcionalidades implementadas

### Frontend
- Formulario: cultivo, tipo evaluación, ubicación (mapa), notas texto, audio
- Mapa modal con selección de punto, geolocalización, geocodificación inversa
- 14 marcadores + 3 polígonos sintéticos de Santa Cruz (demo)
- Tarjetas: Clima, Recomendación, Explicación (Clima/Explicación vacías)
- Diseño responsive verde/blanco/gris

### Backend
- `GET /` → health check
- `POST /evaluar` → multipart (cultivo, tipo, ubicación, lat, lng, texto, audio)
- Validación Pydantic
- Audio guardado en `/tmp` en Vercel, `backend/uploads/` en local
- Sin lógica agronómica ni IA

### Base de datos (preparada, no activa)
- Tablas: `usuarios`, `cultivos`, `evaluaciones`
- Campos geo: `latitud`, `longitud` en evaluaciones
- Script: `database/schema.sql`

## Configuración de entorno

Variables (`.env.example`):
- `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_KEY`
- `APP_ENV=development|production`
- `CORS_ORIGINS=...`
- `ROOT_PATH=/api` (en Vercel)

Mapa (`frontend/js/map-config.js`):
- Provider: `leaflet` (listo para cambiar a Google/Mapbox)
- Centro default: Santa Cruz de la Sierra `[-17.78, -63.18]`
- Datos demo: `frontend/js/santa-cruz-data.js`

API URL frontend (`frontend/js/config.js`):
- Local: `http://localhost:8000`
- Producción: `/api`

## Ejecución local

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend: abrir frontend/index.html con Live Server (puerto 5500)
```

## Pendientes / próximos pasos

### Alta prioridad
1. Aplicar `schema.sql` en Supabase (vía MCP `apply_migration` o SQL editor)
2. Configurar env vars en Vercel: `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_KEY`
3. Persistir evaluaciones en BD desde `POST /evaluar`
4. Sincronizar `frontend/` ↔ `public/` (script de build o eliminar duplicación)

### Media prioridad
- Conectar OpenWeather → tarjeta Clima
- Implementar reglas agronómicas en `evaluacion_service.py` (ver `docs/README_AGRONOMIA.md`)
- Integrar OpenAI → tarjeta Explicación
- Supabase Storage para audios (actualmente `/tmp` en serverless, no persiste)
- Conectar GitHub auto-deploy en Vercel (cuentas `panchito000` vs `cesitarah`)

### Baja prioridad
- Auth de usuarios (tabla usuarios + Supabase Auth)
- n8n para automatizaciones
- Tests con pytest + TestClient
- Fix: `/` en Vercel usa redirect 307 a `/index.html` (funciona, se puede pulir)

## Decisiones de arquitectura

- Capas: `routes` → `services` → `models` (Pydantic + SQLAlchemy separados)
- Vercel: gateway en `api/index.py` monta FastAPI bajo `/api`; estáticos en `public/`
- CORS: automático same-origin en Vercel; configurable vía `CORS_ORIGINS`
- Proyecto unificado: solo existe AGRO-FLOPPY, `zafra-ai` fue eliminado

## Herramientas en la máquina del usuario

- **GitHub CLI (`gh`)** — autenticado como `cesitarah`
- **Node.js LTS + Vercel CLI** — autenticado como `cesitarah-3671`
- Proyecto Vercel linkeado en `.vercel/project.json`

## Comandos útiles

```bash
# Deploy
cd AGRO-FLOPPY
vercel deploy --prod --yes

# Push
git add .
git commit -m "mensaje"
git push origin main

# Health check producción
curl https://agro-floppy.vercel.app/api/
```

## Supabase MCP (si está conectado)

- `list_tables`, `apply_migration`, `execute_sql`, `get_project_url`

## Instrucciones para continuar

Continuá el proyecto AGRO-FLOPPY (Zafra AI). Repo: `panchito000/AGRO-FLOPPY`. Producción: https://agro-floppy.vercel.app. Supabase project ref: `skxgdeogffuaafkdynyk` (BD vacía). **Prioridad:** aplicar schema SQL, configurar env vars en Vercel, persistir evaluaciones, conectar OpenWeather. Frontend en `frontend/` + copia en `public/`. Backend FastAPI en `backend/`. **No reimplementar lo ya hecho.**
