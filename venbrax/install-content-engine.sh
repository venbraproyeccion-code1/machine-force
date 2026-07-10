#!/bin/bash
# VenBraTech — Instala el Content Engine en la VM (correr DESPUES de n8n)
# Ligero: solo python3 (ya viene en Ubuntu) + requests via apt (sin pip pesado)
set -e

echo "[VenBraTech] Instalando Content Engine..."

apt-get install -y --no-install-recommends python3-requests

mkdir -p /opt/venbrax
curl -fsSL "https://raw.githubusercontent.com/venbraproyeccion-code1/machine-force/main/venbrax/content_engine.py" \
     -o /opt/venbrax/content_engine.py
curl -fsSL "https://raw.githubusercontent.com/venbraproyeccion-code1/machine-force/main/venbrax/visual_generator.py" \
     -o /opt/venbrax/visual_generator.py

# anthropic SDK es opcional (el engine funciona con templates sin el);
# instalarlo solo si hay memoria disponible
FREE_MB=$(free -m | awk '/^Mem:/{print $7}')
if [ "$FREE_MB" -gt 300 ]; then
  apt-get install -y --no-install-recommends python3-pip
  pip3 install --quiet anthropic 2>/dev/null || pip3 install --break-system-packages --quiet anthropic || true
else
  echo "[WARN] Poca memoria libre ($FREE_MB MB) — anthropic SDK omitido."
  echo "       El engine funciona en modo template. Reintentar luego con:"
  echo "       sudo apt-get install python3-pip && sudo pip3 install anthropic"
fi

# Prueba
python3 /opt/venbrax/content_engine.py --json > /dev/null && echo "[OK] Content Engine funcional en /opt/venbrax/"
