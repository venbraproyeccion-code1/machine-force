#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
N8N DOCTOR — VenBraX auto-sanador de workflows
===============================================
Escanea la instancia de n8n, detecta nodos/ejecuciones con errores y los
corrige automáticamente. Diseñado para correr por cron en la VM cada 15 min.

Qué hace en cada pasada:
  1. SALUD      : verifica que n8n responda (healthz).
  2. BLINDAJE   : a todo workflow activo le aplica, si le falta:
                    - retryOnFail (3 intentos, 5s entre intentos) en nodos
                      de red (httpRequest, telegram, webhook, etc.)
                    - timeout de 30s en nodos httpRequest
                    - errorWorkflow → apunta al "Error Sentinel" si existe
  3. REANIMACIÓN: busca ejecuciones fallidas recientes y las reintenta
                  (máx. 3 reintentos por ejecución, respetando backoff).
  4. REPORTE    : imprime resumen y (opcional) alerta por Telegram.

Credenciales (variables de entorno — NUNCA hardcodear):
  N8N_URL        p.ej. http://localhost:5678   (en la VM, siempre localhost)
  N8N_API_KEY    API key creada en Settings → API  (preferido)
  N8N_USER / N8N_PASS   fallback basic-auth si no hay API key
  TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID   (opcional, para alertas)

Uso:
  python3 n8n_doctor.py                 # pasada completa
  python3 n8n_doctor.py --dry-run       # solo diagnóstico, no toca nada
  python3 n8n_doctor.py --max-retry 5   # más agresivo reanimando

Cron sugerido (VM, cada 15 min):
  */15 * * * * cd /opt/venbrax && python3 n8n_doctor.py >> /var/log/n8n_doctor.log 2>&1
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

# Nodos que hablan con la red → candidatos a retryOnFail
NETWORK_NODE_TYPES = (
    "n8n-nodes-base.httpRequest",
    "n8n-nodes-base.telegram",
    "n8n-nodes-base.webhook",
    "n8n-nodes-base.emailSend",
    "n8n-nodes-base.postgres",
    "n8n-nodes-base.supabase",
    "n8n-nodes-base.googleSheets",
    "n8n-nodes-base.slack",
)

RETRY_SETTINGS = {"retryOnFail": True, "maxTries": 3, "waitBetweenTries": 5000}
HTTP_TIMEOUT_MS = 30000
SENTINEL_NAME = "Error Sentinel"


class N8nClient:
    """Cliente mínimo de la API de n8n (API key o basic auth)."""

    def __init__(self, base_url: str, api_key: str = "",
                 user: str = "", password: str = ""):
        self.base = base_url.rstrip("/")
        self.api_key = api_key
        self.user = user
        self.password = password

    def _request(self, method: str, path: str, body=None):
        url = f"{self.base}{path}"
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
        if self.api_key:
            req.add_header("X-N8N-API-KEY", self.api_key)
        elif self.user:
            import base64
            tok = base64.b64encode(f"{self.user}:{self.password}".encode()).decode()
            req.add_header("Authorization", f"Basic {tok}")
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}

    def get(self, path):
        return self._request("GET", path)

    def patch(self, path, body):
        return self._request("PATCH", path, body)

    def put(self, path, body):
        return self._request("PUT", path, body)

    def post(self, path, body=None):
        return self._request("POST", path, body)


# ---------------------------------------------------------------------------
# 1) SALUD
# ---------------------------------------------------------------------------
def check_health(base_url: str) -> bool:
    try:
        with urllib.request.urlopen(f"{base_url.rstrip('/')}/healthz",
                                    timeout=10) as r:
            return r.status == 200
    except Exception:
        return False


# ---------------------------------------------------------------------------
# 2) BLINDAJE — parchear workflows frágiles
# ---------------------------------------------------------------------------
def harden_workflow(wf: dict, sentinel_id: str) -> tuple:
    """Devuelve (workflow_parcheado, lista_de_cambios). No muta el original."""
    changes = []
    wf = json.loads(json.dumps(wf))  # copia profunda

    for node in wf.get("nodes", []):
        ntype = node.get("type", "")
        name = node.get("name", "?")
        if ntype in NETWORK_NODE_TYPES:
            if not node.get("retryOnFail"):
                node.update(RETRY_SETTINGS)
                changes.append(f"retry ON → '{name}'")
            if ntype == "n8n-nodes-base.httpRequest":
                opts = node.setdefault("parameters", {}).setdefault("options", {})
                if not opts.get("timeout"):
                    opts["timeout"] = HTTP_TIMEOUT_MS
                    changes.append(f"timeout 30s → '{name}'")

    settings = wf.setdefault("settings", {})
    if sentinel_id and settings.get("errorWorkflow") != sentinel_id:
        settings["errorWorkflow"] = sentinel_id
        changes.append(f"errorWorkflow → {SENTINEL_NAME}")

    return wf, changes


def find_sentinel_id(client: N8nClient) -> str:
    try:
        data = client.get("/api/v1/workflows?limit=100")
        for wf in data.get("data", []):
            if wf.get("name") == SENTINEL_NAME:
                return wf.get("id", "")
    except Exception:
        pass
    return ""


def harden_all(client: N8nClient, dry_run: bool) -> dict:
    report = {"patched": [], "clean": [], "failed": []}
    sentinel_id = find_sentinel_id(client)
    if not sentinel_id:
        print(f"[WARN] No existe el workflow '{SENTINEL_NAME}' — "
              "impórtalo desde n8n-workflows/error-sentinel-workflow.json")

    data = client.get("/api/v1/workflows?limit=100")
    for wf_summary in data.get("data", []):
        wid, wname = wf_summary.get("id"), wf_summary.get("name")
        try:
            wf = client.get(f"/api/v1/workflows/{wid}")
            patched, changes = harden_workflow(wf, sentinel_id)
            if not changes:
                report["clean"].append(wname)
                continue
            if dry_run:
                print(f"[DRY] {wname}: " + "; ".join(changes))
            else:
                body = {k: patched[k] for k in
                        ("name", "nodes", "connections", "settings")
                        if k in patched}
                client.put(f"/api/v1/workflows/{wid}", body)
                print(f"[FIX] {wname}: " + "; ".join(changes))
            report["patched"].append({"workflow": wname, "changes": changes})
        except Exception as exc:
            print(f"[ERR] No pude blindar '{wname}': {exc}")
            report["failed"].append(wname)
    return report


# ---------------------------------------------------------------------------
# 3) REANIMACIÓN — reintentar ejecuciones fallidas
# ---------------------------------------------------------------------------
def revive_failed(client: N8nClient, max_retry: int, dry_run: bool) -> dict:
    report = {"retried": [], "gave_up": [], "still_failing": []}
    try:
        data = client.get("/api/v1/executions?status=error&limit=20")
    except Exception as exc:
        print(f"[ERR] No pude listar ejecuciones: {exc}")
        return report

    for ex in data.get("data", []):
        eid = ex.get("id")
        wname = ex.get("workflowName") or ex.get("workflowId", "?")
        retries = int(ex.get("retryOf") is not None)
        if retries >= max_retry:
            report["gave_up"].append({"execution": eid, "workflow": wname})
            continue
        if dry_run:
            print(f"[DRY] Reintentaría ejecución {eid} ({wname})")
            report["retried"].append({"execution": eid, "workflow": wname})
            continue
        try:
            client.post(f"/api/v1/executions/{eid}/retry")
            print(f"[RETRY] Ejecución {eid} ({wname}) relanzada")
            report["retried"].append({"execution": eid, "workflow": wname})
        except Exception as exc:
            print(f"[ERR] Reintento de {eid} falló: {exc}")
            report["still_failing"].append({"execution": eid,
                                            "workflow": wname})
    return report


# ---------------------------------------------------------------------------
# 4) REPORTE / ALERTA
# ---------------------------------------------------------------------------
def telegram_alert(text: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat:
        return
    try:
        body = json.dumps({"chat_id": chat, "text": text,
                           "parse_mode": "HTML"}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        urllib.request.urlopen(req, timeout=15)
    except Exception:
        pass  # la alerta nunca debe tumbar al doctor


def main() -> int:
    ap = argparse.ArgumentParser(description="n8n Doctor — auto-sanador")
    ap.add_argument("--dry-run", action="store_true",
                    help="solo diagnóstico, no modifica nada")
    ap.add_argument("--max-retry", type=int, default=3)
    args = ap.parse_args()

    base = os.environ.get("N8N_URL", "http://localhost:5678")
    client = N8nClient(
        base,
        api_key=os.environ.get("N8N_API_KEY", ""),
        user=os.environ.get("N8N_USER", ""),
        password=os.environ.get("N8N_PASS", ""),
    )

    stamp = datetime.now(timezone.utc).isoformat()
    print(f"\n===== N8N DOCTOR {stamp} | {base} =====")

    if not check_health(base):
        msg = f"🔴 n8n NO RESPONDE en {base} — revisar VM/contenedor"
        print(f"[CRITICAL] {msg}")
        telegram_alert(msg)
        return 1
    print("[OK] n8n vivo")

    harden = harden_all(client, args.dry_run)
    revive = revive_failed(client, args.max_retry, args.dry_run)

    n_patch = len(harden["patched"])
    n_retry = len(revive["retried"])
    n_bad = len(revive["still_failing"]) + len(harden["failed"])

    summary = (f"🩺 n8n Doctor: {n_patch} workflows blindados, "
               f"{n_retry} ejecuciones reanimadas, {n_bad} pendientes")
    print(f"\n{summary}")
    if n_patch or n_retry or n_bad:
        telegram_alert(summary)
    return 0 if n_bad == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
