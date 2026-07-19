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

# Password: usar N8N_PASSWORD del entorno o generar uno aleatorio.
# NUNCA hardcodear credenciales en este script (vive en git).
N8N_PASSWORD="${N8N_PASSWORD:-$(tr -dc 'A-Za-z0-9' </dev/urandom | head -c 24)}"
cat > /opt/n8n/.env <<ENVEOF
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=$N8N_PASSWORD
ENVEOF
chmod 600 /opt/n8n/.env

# docker compose interpola automaticamente las variables de /opt/n8n/.env
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
      - N8N_BASIC_AUTH_USER=\${N8N_BASIC_AUTH_USER}
      - N8N_BASIC_AUTH_PASSWORD=\${N8N_BASIC_AUTH_PASSWORD}
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
echo "  Usuario: admin | Password: ver /opt/n8n/.env (chmod 600)"
echo "=================================================="
