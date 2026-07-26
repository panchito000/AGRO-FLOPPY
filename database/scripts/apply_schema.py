#!/usr/bin/env python3
"""Aplica database/schema.sql usando DATABASE_URL del entorno o .env."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "database" / "schema.sql"


def load_database_url() -> str:
    env_files = (
        ROOT / ".env",
        ROOT / ".env.local",
        ROOT / "backend" / ".env",
    )
    for env_path in env_files:
        if not env_path.exists():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("DATABASE_URL="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")

    url = os.getenv("DATABASE_URL")
    if not url:
        print("ERROR: Definí DATABASE_URL en .env o como variable de entorno.")
        print("Ejemplo Supabase:")
        print("  DATABASE_URL=postgresql://postgres:[PASSWORD]@db.skxgdeogffuaafkdynyk.supabase.co:5432/postgres")
        sys.exit(1)
    return url


def main() -> None:
    if not SCHEMA.exists():
        print(f"ERROR: No se encontró {SCHEMA}")
        sys.exit(1)

    try:
        import psycopg2
    except ImportError:
        print("ERROR: Instalá psycopg2-binary: pip install psycopg2-binary")
        sys.exit(1)

    sql = SCHEMA.read_text(encoding="utf-8")
    database_url = load_database_url()

    print(f"Aplicando esquema desde {SCHEMA.name}...")
    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        print("Esquema aplicado correctamente.")
    except Exception as exc:
        print(f"ERROR al aplicar esquema: {exc}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
