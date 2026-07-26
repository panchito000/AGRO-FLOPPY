# Base de conocimiento agronómico

## Qué incluye

- **Excel:** `Saul/Data/Cosecha_Parametros.xlsx` (parámetros validados por Saul)
- **PDF:** Fichas Municipales Santa Cruz 2024
- **Código:** catálogo de plagas y guías por tipo de evaluación

## Ingestar / actualizar

```bash
pip install openpyxl pypdf psycopg2-binary
python scripts/ingest_conocimiento.py
```

Genera:
- `backend/app/data/conocimiento_index.json` — fallback para Vercel (sin depender de re-ingestar)
- Tablas `documentos` + `documento_chunks` en Supabase (migración `002_knowledge_base.sql`)

## Cómo responde la app

1. Clima en vivo (Open-Meteo, wttr, Foreca)
2. Reglas agronómicas (semáforo)
3. Búsqueda en chunks de Excel/PDF/código
4. Recomendación corta + explicación con **Fuentes consultadas**
