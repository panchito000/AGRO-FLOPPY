# Variables de entorno — Vercel (producción)

Configurá en **Vercel → Project agro-floppy → Settings → Environment Variables**  
(entorno **Production**, y opcionalmente Preview/Development).

| Variable | Valor |
|----------|--------|
| `DATABASE_URL` | Copiar de tu `.env` local (pooler us-east-1) |
| `SUPABASE_URL` | `https://skxgdeogffuaafkdynyk.supabase.co` |
| `SUPABASE_KEY` | Clave **anon** de Supabase → Settings → API |
| `APP_ENV` | `production` |
| `ROOT_PATH` | `/api` |
| `CORS_ORIGINS` | `https://agro-floppy.vercel.app` |

Después: **Deployments → Redeploy** el último deploy (o `vercel deploy --prod`).

## Nota sobre Supabase

Supabase **es** un servidor PostgreSQL en la nube. El backend en Vercel se conecta con `DATABASE_URL` (no hace falta otro “servidor” aparte).  
Usá la URL **pooler** `aws-0-us-east-1.pooler.supabase.com` (región del proyecto).

## Verificar producción

```bash
curl https://agro-floppy.vercel.app/api/
```

Tras analizar desde el celular, revisá filas nuevas en Supabase → Table Editor → `evaluaciones`.
