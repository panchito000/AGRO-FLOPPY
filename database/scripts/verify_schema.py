#!/usr/bin/env python3
"""Verifica tablas y datos semilla en Supabase."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apply_schema import load_database_url

import psycopg2

conn = psycopg2.connect(load_database_url())
cur = conn.cursor()
cur.execute(
    """
    SELECT table_name FROM information_schema.tables
    WHERE table_schema = 'public' ORDER BY table_name
    """
)
tables = [row[0] for row in cur.fetchall()]
print("TABLAS:", ", ".join(tables))
for name, query in [
    ("cultivos", "SELECT COUNT(*) FROM cultivos"),
    ("tipos_evaluacion", "SELECT COUNT(*) FROM tipos_evaluacion"),
    ("lugares", "SELECT COUNT(*) FROM lugares"),
    ("campos_poligonos", "SELECT COUNT(*) FROM campos_poligonos"),
    ("evaluaciones", "SELECT COUNT(*) FROM evaluaciones"),
]:
    cur.execute(query)
    print(f"{name}: {cur.fetchone()[0]}")
conn.close()
