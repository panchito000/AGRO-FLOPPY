#!/usr/bin/env python3
"""Configura variables de entorno en Vercel (Production) leyendo .env local.

Uso:
  1. Creá un token en https://vercel.com/account/tokens
  2. set VERCEL_TOKEN=tu_token   (PowerShell: $env:VERCEL_TOKEN="...")
  3. python scripts/configure_vercel_env.py

Opcional: VERCEL_PROJECT_ID=prj_... (default: agro-floppy del equipo)
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECT_ID = os.getenv("VERCEL_PROJECT_ID", "prj_hFklC68kZpJ2Jsew21ZYuVMT4DFM")
API = "https://api.vercel.com"

ENV_KEYS = [
    "DATABASE_URL",
    "SUPABASE_URL",
    "SUPABASE_KEY",
    "APP_ENV",
    "ROOT_PATH",
    "CORS_ORIGINS",
]

DEFAULTS = {
    "APP_ENV": "production",
    "ROOT_PATH": "/api",
    "CORS_ORIGINS": "https://agro-floppy.vercel.app",
    "SUPABASE_URL": "https://skxgdeogffuaafkdynyk.supabase.co",
}


def load_dotenv() -> dict[str, str]:
    env: dict[str, str] = {}
    dotenv = ROOT / ".env"
    if not dotenv.exists():
        return env
    for line in dotenv.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def api_request(method: str, path: str, token: str, body: dict | None = None) -> dict:
    url = f"{API}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def list_env(token: str) -> list[dict]:
    data = api_request("GET", f"/v9/projects/{PROJECT_ID}/env", token)
    return data.get("envs", [])


def upsert_env(token: str, key: str, value: str, existing: dict[str, dict]) -> None:
    payload = {
        "key": key,
        "value": value,
        "type": "encrypted",
        "target": ["production", "preview"],
    }
    if key in existing:
        env_id = existing[key]["id"]
        api_request("PATCH", f"/v9/projects/{PROJECT_ID}/env/{env_id}", token, payload)
        print(f"  actualizado: {key}")
    else:
        api_request("POST", f"/v10/projects/{PROJECT_ID}/env", token, payload)
        print(f"  creado: {key}")


def main() -> int:
    token = os.getenv("VERCEL_TOKEN")
    if not token:
        print("ERROR: Definí VERCEL_TOKEN (token de https://vercel.com/account/tokens)")
        return 1

    local = load_dotenv()
    values: dict[str, str] = {}
    for key in ENV_KEYS:
        val = local.get(key) or DEFAULTS.get(key)
        if val:
            values[key] = val

    if not values.get("DATABASE_URL"):
        print("ERROR: DATABASE_URL no encontrada en .env")
        return 1

    if values.get("SUPABASE_KEY", "").startswith("pega_aqui"):
        print("AVISO: SUPABASE_KEY sigue siendo placeholder; omitiendo.")
        values.pop("SUPABASE_KEY", None)

    print(f"Proyecto Vercel: {PROJECT_ID}")
    try:
        current = {item["key"]: item for item in list_env(token)}
    except urllib.error.HTTPError as exc:
        print(f"ERROR API Vercel ({exc.code}): {exc.read().decode('utf-8', errors='replace')}")
        return 1

    for key, value in values.items():
        upsert_env(token, key, value, current)

    print("\nListo. Redeploy en Vercel → Deployments → Redeploy (Production).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
