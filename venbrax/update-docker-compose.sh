#!/bin/bash
# VenBraTech — Reescribe /opt/n8n/docker-compose.yml agregando el servicio
# content-engine (API interna que n8n llama vía HTTP Request, sin
# depender del nodo Execute Command que viene desactivado por seguridad).
set -e

# raw.githubusercontent.com cachea por punto de presencia geografico —
# distintos clientes pueden ver versiones distintas del mismo archivo
# hasta 5 min. Se clona el repo con git (nunca cachea) para eliminar
# ese riesgo de raiz.
rm -rf /tmp/mf-sync
git clone --depth 1 --quiet https://github.com/venbraproyeccion-code1/machine-force.git /tmp/mf-sync

mkdir -p /opt/venbrax
cp /tmp/mf-sync/venbrax/content_engine.py /opt/venbrax/content_engine.py
cp /tmp/mf-sync/venbrax/content_engine_server.py /opt/venbrax/content_engine_server.py
cp /tmp/mf-sync/venbrax/visual_generator.py /opt/venbrax/visual_generator.py

PUBLIC_IP=$(curl -s ifconfig.me)

# El archivo .env NUNCA se versiona en git — vive solo en la VM y
# guarda secretos como ANTHROPIC_API_KEY. Se crea vacio si no existe
# para que el "env_file" de abajo no falle en la primera instalacion.
touch /opt/n8n/.env

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
      - WEBHOOK_URL=http://${PUBLIC_IP}:5678
      - GENERIC_TIMEZONE=America/Caracas
      - N8N_SECURE_COOKIE=false
    depends_on:
      - content-engine

  content-engine:
    image: python:3.11-slim
    restart: always
    volumes:
      - /opt/venbrax:/venbrax
    working_dir: /venbrax
    command: sh -c "pip install --quiet anthropic; python3 content_engine_server.py"
    env_file:
      - /opt/n8n/.env
    environment:
      - PORT=8001
      - PYTHONUNBUFFERED=1
      - PYTHONIOENCODING=UTF-8
      - LANG=C.UTF-8
      - LC_ALL=C.UTF-8

volumes:
  n8n_data:
DCEOF

cd /opt/n8n
sudo docker-compose up -d

echo ""
echo "=================================================="
echo "  Content Engine API: http://content-engine:8001"
echo "  (accesible desde n8n en la red interna de Docker)"
echo "=================================================="
