#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
N8N EXPORT — VenBraX respaldo/migración de workflows
=====================================================
Exporta TODOS los workflows de una instancia n8n a archivos JSON, uno por
workflow, con sus nodos y conexiones intactos. Sirve para:
  - Respaldar los nodos de tu PC antes de apagarla
  - Migrar workflows del PC (laboratorio) a la VM (producción)
  - Versionar los workflows en git

Qué exporta y qué NO:
  ✅ nodos, conexiones, settings, nombre, estado activo/inactivo
  ❌ secretos de credenciales (n8n nunca los expone por API; solo quedan
     las REFERENCIAS a la credencial por id/nombre — al importar en otra
     instancia tendrás que re-asignar la credencial una vez)

Uso (en la máquina donde corre esa instancia n8n):
  set N8N_URL / N8N_API_KEY  y luego:
  python n8n_export.py
  python n8n_export.py --out mis_workflows --only-active
  python n8n_export.py --url http://localhost:5678

Al terminar tienes una carpeta con un .json por workflow, listo para
importar en otra instancia (n8n UI → Import from File) o commitear a git.
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path


class N8nClient:
    """Cliente mínimo de la API de n8n (API key o basic auth)."""

    def __init__(self, base_url, api_key="", user="", password=""):
        self.base = base_url.rstrip("/")
        self.api_key = api_key
        self.user = user
        self.password = password

    def get(self, path):
        url = f"{self.base}{path}"
        req = urllib.request.Request(url, method="GET")
        req.add_header("Accept", "application/json")
        if self.api_key:
            req.add_header("X-N8N-API-KEY", self.api_key)
        elif self.user:
            import base64
            tok = base64.b64encode(f"{self.user}:{self.password}".encode()).decode()
            req.add_header("Authorization", f"Basic {tok}")
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}


def safe_filename(name):
    """Convierte el nombre del workflow en un nombre de archivo seguro."""
    s = re.sub(r"[^\w\s-]", "", name, flags=re.UNICODE).strip()
    s = re.sub(r"[-\s]+", "-", s)
    return s[:80] or "workflow"


def export_all(client, out_dir, only_active):
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        listing = client.get("/api/v1/workflows?limit=250")
    except urllib.error.HTTPError as exc:
        print(f"[ERROR] La API respondió {exc.code}. ¿API key correcta y con "
              "permisos? ¿URL bien puesta?")
        return 1
    except Exception as exc:
        print(f"[ERROR] No pude conectar a {client.base}: {exc}")
        return 1

    workflows = listing.get("data", [])
    if not workflows:
        print("[AVISO] La instancia no tiene workflows (o la key no los ve).")
        return 0

    exported, skipped = [], []
    manifest = []

    for wf in workflows:
        wid = wf.get("id")
        wname = wf.get("name", f"workflow-{wid}")
        active = wf.get("active", False)

        if only_active and not active:
            skipped.append(wname)
            continue

        try:
            full = client.get(f"/api/v1/workflows/{wid}")
        except Exception as exc:
            print(f"[ERR] No pude exportar '{wname}': {exc}")
            continue

        # cuerpo limpio, importable en cualquier instancia
        clean = {
            "name": full.get("name", wname),
            "nodes": full.get("nodes", []),
            "connections": full.get("connections", {}),
            "settings": full.get("settings", {}),
            "active": active,
        }
        fname = f"{safe_filename(wname)}.json"
        (out_dir / fname).write_text(
            json.dumps(clean, ensure_ascii=False, indent=2), encoding="utf-8")

        n_nodes = len(clean["nodes"])
        n_conn = len(clean["connections"])
        exported.append(wname)
        manifest.append({
            "name": wname, "file": fname, "active": active,
            "nodes": n_nodes, "connections": n_conn,
        })
        flag = "●activo" if active else "○inactivo"
        print(f"[OK] {flag}  {wname}  ({n_nodes} nodos, {n_conn} conexiones) → {fname}")

    # manifest índice
    (out_dir / "_manifest.json").write_text(json.dumps({
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "source": client.base,
        "total": len(exported),
        "workflows": manifest,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n✅ {len(exported)} workflows exportados a: {out_dir}")
    if skipped:
        print(f"   ({len(skipped)} inactivos omitidos por --only-active)")
    print(f"   Índice: {out_dir / '_manifest.json'}")
    print("\nPara importar en la VM: n8n UI → Workflows → Import from File → "
          "elige cada .json → reasigna credenciales → activa.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Exporta workflows de n8n a JSON")
    ap.add_argument("--url", default=os.environ.get("N8N_URL", "http://localhost:5678"))
    ap.add_argument("--out", type=Path,
                    default=Path("n8n-workflows-export"),
                    help="Carpeta de salida (default: n8n-workflows-export)")
    ap.add_argument("--only-active", action="store_true",
                    help="Exportar solo los workflows activos")
    args = ap.parse_args()

    client = N8nClient(
        args.url,
        api_key=os.environ.get("N8N_API_KEY", ""),
        user=os.environ.get("N8N_USER", ""),
        password=os.environ.get("N8N_PASS", ""),
    )
    print(f"Exportando desde: {args.url}\n")
    return export_all(client, args.out, args.only_active)


if __name__ == "__main__":
    sys.exit(main())
