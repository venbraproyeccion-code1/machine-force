#!/bin/bash
# VenBraTech — Google Cloud e2-micro startup script
# Installs Docker + n8n + nginx proxy automatically at VM boot
# VM: venbratech-n8n | Project: venbrax | Region: us-central1

set -e

LOG="/var/log/venbratech-setup.log"
exec > >(tee -a $LOG) 2>&1
echo "[$(date -u)] VenBraTech n8n setup iniciando..."

# System update + deps
apt-get update -y
apt-get install -y docker.io curl ufw nginx certbot python3-certbot-nginx

# Docker service
systemctl enable docker
systemctl start docker

# docker-compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" \
     -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Firewall
ufw allow 22
ufw allow 80
ufw allow 443
ufw allow 5678
ufw --force enable

# n8n directory
mkdir -p /opt/n8n
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google")

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
      - N8N_LOG_LEVEL=info
      - N8N_METRICS=true
volumes:
  n8n_data:
DCEOF

cd /opt/n8n
docker-compose up -d

# Wait for n8n to start
sleep 15

# Send Telegram notification
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"

if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -H "Content-Type: application/json" \
    -d "{
      \"chat_id\": \"${TELEGRAM_CHAT_ID}\",
      \"text\": \"✅ <b>n8n LISTO en Google Cloud</b>\n\n🖥 venbratech-n8n (e2-micro)\n🌐 http://${PUBLIC_IP}:5678\n\n👤 admin / VenBraTech2025!\n\n⚡ Ecosistema VenBraX activo\",
      \"parse_mode\": \"HTML\"
    }"
fi

echo "[$(date -u)] Setup completado. n8n en: http://${PUBLIC_IP}:5678"
