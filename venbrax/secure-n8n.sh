#!/bin/bash
# VenBraTech — Blindaje de seguridad de n8n (ejecutar EN LA VM via SSH)
# ======================================================================
# Qué hace:
#   1. Rota el password de basic-auth de n8n (genera uno aleatorio de 24
#      chars o usa el que pases: N8N_PASSWORD=... ./secure-n8n.sh)
#   2. Lo persiste en /opt/n8n/.env (chmod 600) — nunca en git
#   3. Reescribe docker-compose para leer credenciales desde .env
#   4. Reinicia n8n con las credenciales nuevas
#   5. Imprime los comandos de gcloud para restringir el firewall a tu IP
#
# Uso en la VM:
#   curl -fsSL https://raw.githubusercontent.com/venbraproyeccion-code1/machine-force/main/venbrax/secure-n8n.sh | sudo bash
#   (o: sudo bash secure-n8n.sh)
set -e

ENV_FILE=/opt/n8n/.env
COMPOSE=/opt/n8n/docker-compose.yml

if [ ! -f "$COMPOSE" ]; then
  echo "[ERROR] No existe $COMPOSE — ¿n8n está instalado en esta máquina?"
  exit 1
fi

# ── 1. Generar/rotar password ────────────────────────────────────────
NEW_PASS="${N8N_PASSWORD:-$(tr -dc 'A-Za-z0-9' </dev/urandom | head -c 24)}"

touch "$ENV_FILE"
chmod 600 "$ENV_FILE"
# eliminar entradas viejas y escribir las nuevas
grep -v '^N8N_BASIC_AUTH_' "$ENV_FILE" > "${ENV_FILE}.tmp" || true
{
  cat "${ENV_FILE}.tmp"
  echo "N8N_BASIC_AUTH_USER=admin"
  echo "N8N_BASIC_AUTH_PASSWORD=$NEW_PASS"
} > "$ENV_FILE"
rm -f "${ENV_FILE}.tmp"
chmod 600 "$ENV_FILE"
echo "[OK] Password rotado y guardado en $ENV_FILE"

# ── 2. Purgar password hardcodeado del docker-compose ────────────────
if grep -q 'N8N_BASIC_AUTH_PASSWORD=[^$]' "$COMPOSE"; then
  # reemplazar valor literal por interpolación desde .env
  sed -i 's|N8N_BASIC_AUTH_USER=.*|N8N_BASIC_AUTH_USER=${N8N_BASIC_AUTH_USER}|' "$COMPOSE"
  sed -i 's|N8N_BASIC_AUTH_PASSWORD=.*|N8N_BASIC_AUTH_PASSWORD=${N8N_BASIC_AUTH_PASSWORD}|' "$COMPOSE"
  echo "[OK] docker-compose.yml ya no contiene el password literal"
fi

# asegurar que compose cargue el .env como env_file para el contenedor n8n
if ! grep -q 'env_file' "$COMPOSE"; then
  echo "[WARN] docker-compose.yml no tiene env_file — docker compose"
  echo "       interpola \${VARS} desde el .env del mismo directorio,"
  echo "       así que la interpolación de arriba es suficiente."
fi

# ── 3. Reiniciar n8n ─────────────────────────────────────────────────
cd /opt/n8n
if docker compose version >/dev/null 2>&1; then
  docker compose up -d --force-recreate n8n
else
  docker-compose up -d --force-recreate n8n
fi
echo "[OK] n8n reiniciado con credenciales nuevas"

# ── 4. Resumen + firewall ────────────────────────────────────────────
PUBLIC_IP=$(curl -s ifconfig.me || echo "IP_PUBLICA")
echo ""
echo "======================================================"
echo "  🛡️  n8n BLINDADO"
echo "  URL:      http://${PUBLIC_IP}:5678"
echo "  Usuario:  admin"
echo "  Password: (nuevo) → sudo cat /opt/n8n/.env"
echo "======================================================"
echo ""
echo "SIGUIENTE PASO — restringir firewall (correr en Cloud Shell):"
echo ""
echo "  # 1. Ver tu IP actual: https://ifconfig.me"
echo "  # 2. Reemplazar TU_IP y ejecutar:"
echo "  gcloud compute firewall-rules list --project=venbrax"
echo "  gcloud compute firewall-rules update REGLA_PUERTO_5678 \\"
echo "      --source-ranges=TU_IP/32 --project=venbrax"
echo ""
echo "RECORDATORIO: actualizar el password en los clientes que llaman"
echo "a n8n (n8n_doctor.py usa N8N_API_KEY, no le afecta; cualquier"
echo "webhook externo con basic-auth sí)."
