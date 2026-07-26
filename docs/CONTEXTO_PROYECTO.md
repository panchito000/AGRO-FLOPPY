# AgroFloppy — Contexto del proyecto

Documento de handoff para retomar el desarrollo en un chat nuevo o onboarding del equipo.

**Última actualización:** julio 2026

---

## 1. ¿De qué trata?

**AgroFloppy** (repositorio: `AGRO-FLOPPY`) es una plataforma web **B2B agrícola** orientada a Santa Cruz, Bolivia.

**Objetivo:** Copiloto inteligente que ayuda a agrónomos, administradores agrícolas y productores a **prevenir pérdidas económicas** por malas decisiones en el campo (siembra, fertilización, riego, plagas, cosecha) en cultivos de **soya** y **maíz**.

### Flujo principal de la aplicación

1. El usuario **inicia sesión** (Supabase Auth).
2. Elige **cultivo**, **tipo de evaluación** y **ubicación** en mapa (Leaflet).
3. Agrega **notas de texto** y/o **audio** (grabación + dictado en vivo en PC).
4. El backend consulta **clima en vivo** (Open-Meteo, wttr, Foreca).
5. Evalúa **reglas agronómicas** → devuelve **semáforo** (verde/amarillo/rojo), veredicto, advertencias, recomendación y explicación.
6. **Persiste** la evaluación en Supabase PostgreSQL (si `DATABASE_URL` está configurada).

### Pendiente / roadmap

- OpenAI para recomendaciones generativas enriquecidas.
- Validación JWT en backend y vínculo `evaluaciones.usuario_id`.
- Trigger Supabase: auto-crear fila en `usuarios` al registrarse.
- Supabase Storage para audios (hoy en Vercel se usa `/tmp`, efímero).
- Script automático de sincronización `frontend/` → `public/`.

---

## 2. URLs y recursos

| Recurso | URL |
|---------|-----|
| **Producción (Vercel)** | https://agro-floppy-lilac.vercel.app/ |
| **App (tras login)** | `/app.html` |
| **API health** | https://agro-floppy-lilac.vercel.app/api/ |
| **Swagger** | https://agro-floppy-lilac.vercel.app/api/docs |
| **GitHub** | https://github.com/panchito000/AGRO-FLOPPY |
| **Supabase Dashboard** | https://supabase.com/dashboard/project/skxgdeogffuaafkdynyk |

---

## 3. Arquitectura

```
┌─────────────────┐     POST /evaluar      ┌──────────────────┐
│  Frontend       │ ─────────────────────► │  FastAPI         │
│  (HTML/JS)      │     Bearer JWT         │  (Python)        │
│  index.html     │                        │  backend/        │
│  app.html       │ ◄───────────────────── │                  │
└────────┬────────┘     JSON semáforo     └────────┬─────────┘
         │                                          │
         │ Supabase Auth                            │ SQLAlchemy
         ▼                                          ▼
┌─────────────────┐                        ┌──────────────────┐
│  Supabase Auth  │                        │  Supabase        │
│  (login/registro)│                        │  PostgreSQL      │
└─────────────────┘                        └──────────────────┘
```

### Stack tecnológico

| Capa | Tecnología |
|------|------------|
| Frontend | HTML, CSS, JavaScript vanilla, Leaflet, Supabase JS (CDN) |
| Backend | FastAPI, SQLAlchemy, Pydantic, psycopg2 |
| Base de datos | Supabase (PostgreSQL 14+) |
| Auth | Supabase Auth (email + contraseña) |
| Deploy | Vercel (frontend estático + API Python serverless) |
| Clima | Open-Meteo, wttr.in, Foreca (APIs gratuitas) |

---

## 4. Estructura del repositorio

```
AGRO-FLOPPY/
├── api/
│   └── index.py                 # Gateway serverless Vercel → monta /api
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── app/
│       ├── config/settings.py   # Variables de entorno
│       ├── database/connection.py
│       ├── routes/              # health, evaluar
│       ├── services/
│       │   ├── evaluacion_service.py
│       │   ├── evaluacion_repository.py
│       │   ├── respuestas_agronomicas.py
│       │   ├── conocimiento_service.py
│       │   └── clima/            # Clima + reglas agronómicas
│       ├── data/                 # ubicaciones, FAQ, conocimiento
│       └── models/               # Pydantic + SQLAlchemy
├── frontend/                    # Fuente para desarrollo local
│   ├── index.html               # LOGIN (página inicial)
│   ├── app.html                 # App principal (protegida)
│   ├── assets/logo.png          # Logo AgroFloppy
│   ├── css/styles.css
│   └── js/
│       ├── app.js
│       ├── auth.js              # Login/registro Supabase
│       ├── supabase-config.js   # URL + publishable key
│       ├── audio-recorder.js    # Grabación + dictado
│       ├── config.js            # URL API (local vs Vercel)
│       ├── map-picker.js
│       └── santa-cruz-data.js
├── public/                      # ⚠️ Copia servida por Vercel — mantener sincronizada
├── database/
│   ├── schema.sql
│   ├── supabase_er_v2.sql
│   └── scripts/                 # apply_schema, test_connection, verify_schema
├── docs/
│   ├── README_AGRONOMIA.md
│   ├── VERCEL_ENV.md
│   └── CONTEXTO_PROYECTO.md     # ← este documento
├── Saul/                        # Scripts y datos de referencia del equipo
├── vercel.json
├── .env.example
├── AGENTS.md
└── IMPLEMENTACION.md
```

> **CRÍTICO:** Vercel sirve la carpeta `public/`, NO `frontend/`. Después de editar el frontend, copiar cambios a `public/` antes de desplegar.

---

## 5. Páginas web y autenticación

| Ruta / archivo | Función |
|----------------|---------|
| `index.html` | Login y registro (página inicial en `/`) |
| `app.html` | Formulario de evaluación, mapa, resultados |

### Flujo de auth

1. Usuario abre `/` → formulario de login.
2. Puede **registrarse** con email + contraseña nueva (no la del correo Gmail/Outlook).
3. Tras registro exitoso → aviso verde: *"¡Cuenta creada correctamente! Ahora iniciá sesión..."* y cambio automático a modo login.
4. Tras login → redirect a `app.html`.
5. Si accede a `app.html` sin sesión → redirect a `/`.
6. Botón **Salir** → cierra sesión y vuelve a `/`.

### Archivos de auth

| Archivo | Descripción |
|---------|-------------|
| `frontend/js/auth.js` | Lógica login, registro, logout, protección de páginas |
| `frontend/js/supabase-config.js` | Credenciales Supabase para el navegador |

**Configuración Supabase (frontend):**

```javascript
window.SUPABASE_CONFIG = {
  url: "https://skxgdeogffuaafkdynyk.supabase.co",
  anonKey: "sb_publishable_...",  // Publishable key (Settings → API)
};
```

> Usar `window.SUPABASE_CONFIG`, NO `const SUPABASE_CONFIG` (bug corregido: el navegador no lo encontraba).

### Configuración Supabase Dashboard

- **Authentication → Providers:** Email **Enabled**
- **Confirm email:** ON (puede bloquear registro web por rate limit de emails)
- **URL Configuration:**
  - Site URL: `https://agro-floppy-lilac.vercel.app`
  - Redirect URLs:
    - `http://localhost:8080/**`
    - `http://localhost:5500/**`
    - `https://agro-floppy-lilac.vercel.app/**`

**Alternativa para pruebas:** crear usuarios con **Authentication → Users → Add user** (marcar Auto Confirm).

---

## 6. Backend — API

### Endpoints

| Método | Local | Vercel | Descripción |
|--------|-------|--------|-------------|
| GET | `/` | `/api/` | Health check |
| POST | `/evaluar` | `/api/evaluar` | Evaluación agronómica (multipart: form + audio) |
| GET | `/docs` | `/api/docs` | Swagger |

### Servicios principales

- `services/clima/__init__.py` → `obtener_clima_consolidado()` + `evaluar_agronomico()`
- `services/evaluacion_service.py` → orquesta clima, reglas, persistencia, audio
- `services/evaluacion_repository.py` → guarda en tablas Supabase
- `services/respuestas_agronomicas.py` → respuestas humanas por tipo de evaluación

---

## 7. Base de datos (Supabase)

- **Proyecto:** `skxgdeogffuaafkdynyk`
- **Región:** us-east-1
- **Schema:** `database/schema.sql`

### Tablas

| Tabla | Propósito |
|-------|-----------|
| `cultivos` | soya, maíz |
| `tipos_evaluacion` | siembra, fertilización, riego, plagas, cosecha |
| `usuarios` | productores, agrónomos (`auth_user_id` para Supabase Auth) |
| `lugares` | 14 fincas demo Santa Cruz |
| `campos_poligonos` | Polígonos para el mapa |
| `evaluaciones` | Registro de cada análisis |
| `clima_cache` | Caché de clima por coordenadas |

### Conexión recomendada (pooler)

```
postgresql://postgres.skxgdeogffuaafkdynyk:PASSWORD@aws-0-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require
```

---

## 8. Variables de entorno

Copiar `.env.example` → `.env` en la raíz del proyecto.

| Variable | Uso |
|----------|-----|
| `DATABASE_URL` | PostgreSQL/Supabase (backend) |
| `SUPABASE_URL` | URL del proyecto |
| `SUPABASE_KEY` | Clave anon (backend, futuro) |
| `CORS_ORIGINS` | Orígenes permitidos (incluir localhost:8080) |
| `ROOT_PATH` | Vacío en local; `/api` en Vercel |
| `APP_ENV` | `development` / `production` |

Ver también: `docs/VERCEL_ENV.md`

---

## 9. Desarrollo local

### Requisitos

- Python 3.11+
- Git Bash o PowerShell
- Navegador moderno

### Levantar el proyecto

**Terminal 1 — Backend:**

```bash
cd ~/Desktop/AGRO-FLOPPY/backend
source venv/Scripts/activate        # PowerShell: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Terminal 2 — Frontend:**

```bash
cd ~/Desktop/AGRO-FLOPPY/frontend
python -m http.server 8080
```

### URLs locales

| Qué | URL |
|-----|-----|
| Login | http://localhost:8080/ |
| App | http://localhost:8080/app.html |
| API docs | http://localhost:8000/docs |

> El puerto **5500** suele estar bloqueado en Windows. Usar **8080**.

---

## 10. Despliegue (Vercel)

1. Cambios en `frontend/` → copiar a `public/`
2. Commit + push a `main`
3. Vercel redeploya automáticamente (~1–2 min)

### Sincronizar frontend → public

```powershell
Copy-Item frontend\index.html public\index.html -Force
Copy-Item frontend\app.html public\app.html -Force
Copy-Item frontend\css\styles.css public\css\styles.css -Force
Copy-Item frontend\js\*.js public\js\ -Force
Copy-Item frontend\assets\logo.png public\assets\logo.png -Force
```

### vercel.json (importante)

```json
"redirects": [
  { "source": "/", "destination": "/index.html", "permanent": false },
  { "source": "/app", "destination": "/app.html", "permanent": false }
]
```

Sin el redirect de `/` → `/index.html`, la raíz devuelve `{"detail":"Not Found"}` de FastAPI.

---

## 11. Git — flujo del equipo

El equipo sube cambios en paralelo. **Siempre** antes de push:

```bash
git pull --rebase origin main
git push origin main
```

### Problemas frecuentes

| Error | Solución |
|-------|----------|
| `fetch first` / push rejected | `git pull --rebase origin main` y reintentar push |
| `unrelated histories` / `(forced update)` | Alguien hizo force push → `git fetch origin && git reset --hard origin/main` (⚠️ pierde cambios locales no commiteados) |
| `RPC failed` / red lenta | `git config --global http.version HTTP/1.1` y reintentar |
| Puerto 5500 bloqueado | Usar puerto 8080 para frontend |

---

## 12. Marca e identidad visual

| Elemento | Valor actual |
|----------|--------------|
| Nombre | **AgroFloppy** |
| Logo | `frontend/assets/logo.png` (Floppa + hojas verdes) |
| Favicon | `assets/logo.png` |
| Nombre anterior | Zafra AI (reemplazado en UI) |

Variables JS internas (`ZafraAuth`, `ZafraAudioRecorder`) conservan el nombre antiguo — no visible al usuario.

---

## 13. Problemas conocidos y soluciones

| Problema | Causa | Solución |
|----------|-------|----------|
| Registro web falla | Rate limit emails Supabase + Confirm email ON | Desactivar Confirm email o usar Add user |
| "Falta configurar supabase-config.js" | Config no en `window` | Usar `window.SUPABASE_CONFIG` |
| Vercel muestra JSON en `/` | Falta redirect | Ver `vercel.json` |
| Análisis no guarda en BD | `DATABASE_URL` no configurada | Configurar `.env` y Vercel env vars |
| Dictado no funciona en PC | Speech API | Ver commits recientes de `audio-recorder.js` |

---

## 14. Commits relevantes (sesión julio 2026)

```
28f2a13 fix: actualizar logo AgroFloppy
dcf8bf1 chore: renombrar marca visible a AgroFloppy
6d093ac feat: aviso de cuenta creada y mejor manejo de errores en registro
95d55b0 feat: login con Supabase como pagina inicial
8d727b1 fix: redirigir raiz a index.html en Vercel
```

---

## 15. Prompt sugerido para nuevo chat en Cursor

```
Continúo el proyecto AgroFloppy (repo AGRO-FLOPPY).
Lee docs/CONTEXTO_PROYECTO.md para contexto completo.

Resumen rápido:
- Producción: https://agro-floppy-lilac.vercel.app
- Supabase project: skxgdeogffuaafkdynyk
- Frontend en frontend/ (copia en public/ para Vercel)
- Login: index.html | App: app.html
- Backend FastAPI en backend/
- Auth con Supabase Auth implementado
- Marca: AgroFloppy, logo en assets/logo.png

[Tu tarea aquí]
```

---

## 16. Documentación adicional

| Archivo | Contenido |
|---------|-----------|
| `README.md` | Documentación general (puede estar desactualizado en auth/marca) |
| `AGENTS.md` | Contexto para agentes Cursor |
| `IMPLEMENTACION.md` | Plan por fases |
| `docs/README_AGRONOMIA.md` | Reglas agronómicas |
| `docs/VERCEL_ENV.md` | Variables de entorno en producción |
| `database/AUDITORIA.md` | Auditoría del schema |
