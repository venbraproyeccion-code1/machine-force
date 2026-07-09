#!/bin/bash
# VenBraTech — Instalador MINIMO de n8n para e2-micro (1GB RAM)
# Solo Docker + n8n. Sin pip, sin git, sin paquetes dev.
# El content engine se instala DESPUES con install-content-engine.sh
set -e

echo "[VenBraTech] Instalador minimo iniciando..."

# Recuperar dpkg si quedo interrumpido por un reinicio
dpkg --configure -a 2>/dev/null || true

# Solo lo esencial
apt-get update -y
apt-get install -y --no-install-recommends docker.io curl

systemctl enable docker
systemctl start docker

mkdir -p /opt/n8n
PUBLIC_IP=$(curl -s ifconfig.me)

cat > /opt/n8n/docker-compose.yml <<DCEOF
version: '3.8'
services:
  n8n:
    image: n8nio/n8n:latest
    restart: always
    ports:
      - "5678:5678"
    volumes:
      - n8n_data:/home/node/.n8n
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=VenBraTech2025!
      - WEBHOOK_URL=http://$PUBLIC_IP:5678
      - GENERIC_TIMEZONE=America/Caracas
volumes:
  n8n_data:
DCEOF

# docker compose v2 viene como plugin en docker.io de Ubuntu 22.04+;
# si no existe, usar 'docker compose' fallback o descargar binario
if docker compose version >/dev/null 2>&1; then
  cd /opt/n8n && docker compose up -d
elif command -v docker-compose >/dev/null 2>&1; then
  cd /opt/n8n && docker-compose up -d
else
  curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" \
       -o /usr/local/bin/docker-compose
  chmod +x /usr/local/bin/docker-compose
  cd /opt/n8n && docker-compose up -d
fi

echo ""
echo "=================================================="
echo "  n8n LISTO: http://$PUBLIC_IP:5678"
echo "  Usuario: admin | Password: VenBraTech2025!"
echo "=================================================="
