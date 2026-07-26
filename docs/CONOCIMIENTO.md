# Base de conocimiento agronómico

## Qué incluye

- **Excel:** `Saul/Data/Cosecha_Parametros.xlsx` (parámetros validados por Saul)
- **PDFs:** Fichas Municipales, Santa Cruz (Riquezas de Bolivia), CIPCA frontera soyera, ANAPO 2025, soya tecnológica
- **Markdown:** versiones texto de Santa Cruz y CIPCA (mejor calidad de búsqueda)
- **FAQ:** `backend/app/data/faq_agronomico.py` — respuestas curadas a preguntas frecuentes
- **Código:** catálogo de plagas y guías por tipo de evaluación

Manifiesto de documentos: `Saul/Data/documentos_manifest.json`

## Clima vs. agronomía (de dónde salen los datos)

| Tipo | Fuente | ¿En vivo? | Cómo se usa |
|------|--------|-----------|-------------|
| Clima | Open-Meteo, wttr, Foreca | Sí | APIs gratuitas en cada consulta |
| Plagas, siembra, riego, etc. | Excel, PDFs, guías en código | No | Se indexan y se buscan por palabras clave |

No existe una API pública gratuita equivalente al clima para “plagas en vivo” o “épocas de siembra por municipio”. Para esos temas hay que **agregar documentos** (PDF, Excel, fichas técnicas) y volver a correr la ingesta.

### PDFs y datos recomendados para Santa Cruz / soya

- Fichas municipales del departamento (ya parcialmente ingestadas)
- Estadísticas ANAPO (verificar que el PDF no esté vacío)
- Guías INTA / EMBRAPA de soya y maíz
- Boletines fitosanitarios SENASAG / INIAF
- Manuales de manejo integrado de plagas por cultivo
- Tablas de ventanas de siembra por zona (Excel o PDF con texto seleccionable)

**Importante:** los PDF escaneados (solo imagen) no sirven sin OCR. Preferí PDFs con texto copiable.

## Ingestar / actualizar

1. Colocá PDFs en `Saul/Data/` y actualizá `Saul/Data/documentos_manifest.json` si agregás archivos nuevos
2. Ejecutá:

```bash
pip install openpyxl pypdf psycopg2-binary
python scripts/ingest_conocimiento.py
```

Genera:
- `backend/app/data/conocimiento_index.json` — fallback para Vercel (sin depender de re-ingestar)
- Tablas `documentos` + `documento_chunks` en Supabase (migración `002_knowledge_base.sql`)

Después de ingesta, las respuestas pueden citar esos documentos en **Fuentes consultadas**.

## Cómo responde la app

1. Clima en vivo (Open-Meteo, wttr, Foreca)
2. Reglas agronómicas (semáforo)
3. Búsqueda en chunks de Excel/PDF/código (por uno o **varios temas** si la pregunta lo pide)
4. Recomendación corta + explicación con **Fuentes consultadas**

### Consultas con varios temas

Si preguntás algo como *“plagas de soya y peores épocas para sembrar”*, el sistema detecta **plagas + siembra** y responde una sección por cada tema.
