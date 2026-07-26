#!/usr/bin/env python3
"""Prueba conexión a Supabase usando DATABASE_URL del .env."""

from apply_schema import load_database_url

try:
    import psycopg2
except ImportError:
    print("Instalá psycopg2-binary: pip install psycopg2-binary")
    raise SystemExit(1)


def main() -> None:
    url = load_database_url()
    print("Probando conexión...")
    conn = psycopg2.connect(url, connect_timeout=12)
    cur = conn.cursor()
    cur.execute("SELECT current_database(), current_user")
    db, user = cur.fetchone()
    cur.execute(
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"
    )
    tables = cur.fetchone()[0]
    print(f"Conectado: db={db}, user={user}, tablas public={tables}")
    conn.close()


if __name__ == "__main__":
    main()
