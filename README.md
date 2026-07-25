# AGRO-FLOPPY (Zafra AI)

Copiloto inteligente para ingenieros agrónomos, administradores agrícolas y productores tecnificados. Analiza cultivos de **soya** y **maíz** usando información meteorológica, reglas agronómicas e IA.

## Estructura del proyecto

```
AGRO-FLOPPY/
├── api/               # Entry point serverless (Vercel)
├── frontend/          # HTML, CSS, JavaScript vanilla
├── backend/           # API FastAPI
├── database/          # Esquema SQL
├── vercel.json        # Configuración de despliegue
├── requirements.txt   # Dependencias Python (Vercel)
└── docs/              # Documentación agronómica
```

## Requisitos

- Python 3.11+
- PostgreSQL 14+ (o Supabase)
- Navegador moderno

## Configuración

1. Clonar el repositorio.
2. Copiar variables de entorno:

```bash
cp .env.example .env
```

3. Editar `.env` con tus credenciales de PostgreSQL.

4. Instalar dependencias del backend:

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

5. Crear la base de datos y ejecutar el esquema:

```bash
psql -U postgres -d zafra_ai -f ../database/schema.sql
```

## Ejecutar

**Backend:**

```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Frontend:** abrir `frontend/index.html` con Live Server o un servidor estático en el puerto 5500.

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Endpoints

| Método | Ruta (local)   | Ruta (Vercel)      | Descripción                 |
|--------|----------------|--------------------|-----------------------------|
| GET    | `/`            | `/api/`            | Health check de la API      |
| POST   | `/evaluar`     | `/api/evaluar`     | Recibe datos del formulario |
| GET    | `/docs`        | `/api/docs`        | Documentación Swagger       |

---

## Despliegue en Vercel

El proyecto está configurado para desplegarse en **un solo proyecto Vercel**:

- **Frontend** → carpeta `frontend/` (sitio estático)
- **Backend** → `api/index.py` (FastAPI serverless bajo `/api`)

### Paso 1 — Subir a GitHub

```bash
git add .
git commit -m "Configurar despliegue en Vercel"
git push origin main
```

### Paso 2 — Importar en Vercel

1. Entrá a [vercel.com/new](https://vercel.com/new)
2. Importá el repositorio **AGRO-FLOPPY** desde GitHub
3. Vercel detectará `vercel.json` automáticamente
4. **No cambies** el Output Directory (ya está en `frontend`)
5. Clic en **Deploy**

### Paso 3 — Variables de entorno en Vercel

En **Project → Settings → Environment Variables**, agregá:

| Variable | Valor | Entorno |
|----------|-------|---------|
| `DATABASE_URL` | URL de PostgreSQL/Supabase | Production |
| `SUPABASE_URL` | `https://xxx.supabase.co` | Production |
| `SUPABASE_KEY` | Clave anon de Supabase | Production |
| `ROOT_PATH` | `/api` | Production |
| `APP_ENV` | `production` | Production |

> `ROOT_PATH` y `APP_ENV` ya están en `vercel.json`, pero conviene repetirlos en el dashboard.

### Paso 4 — Verificar

- Frontend: `https://tu-proyecto.vercel.app`
- API health: `https://tu-proyecto.vercel.app/api/`
- Swagger: `https://tu-proyecto.vercel.app/api/docs`

### Notas importantes

- El frontend detecta automáticamente si está en local (`localhost:8000`) o en Vercel (`/api`).
- Los audios subidos en Vercel se guardan en `/tmp` (temporal en serverless). Para persistencia usá Supabase Storage más adelante.
- Límite de body en plan Hobby: ~4.5 MB por request (considerá esto para audios largos).

---

- Estructura base frontend y backend
- Conexión PostgreSQL preparada (variables de entorno)
- Esquema de base de datos inicial
- Sin integración de APIs externas ni IA

## Próximos pasos

- OpenWeather API
- OpenAI API
- n8n para automatizaciones
- Lógica agronómica en `docs/README_AGRONOMIA.md`
