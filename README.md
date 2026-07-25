# AGRO-FLOPPY (Zafra AI)

Copiloto inteligente para ingenieros agrónomos, administradores agrícolas y productores tecnificados. Analiza cultivos de **soya** y **maíz** usando información meteorológica, reglas agronómicas e IA.

## Estructura del proyecto

```
AGRO-FLOPPY/
├── frontend/          # HTML, CSS, JavaScript vanilla
├── backend/           # API FastAPI
├── database/          # Esquema SQL
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

| Método | Ruta       | Descripción                    |
|--------|------------|--------------------------------|
| GET    | `/`        | Health check de la API         |
| POST   | `/evaluar` | Recibe datos del formulario    |

## Estado actual (v0.1)

- Estructura base frontend y backend
- Conexión PostgreSQL preparada (variables de entorno)
- Esquema de base de datos inicial
- Sin integración de APIs externas ni IA

## Próximos pasos

- OpenWeather API
- OpenAI API
- n8n para automatizaciones
- Lógica agronómica en `docs/README_AGRONOMIA.md`
