# VenBraX — Infraestructura Autosustentable

Repositorio de scripts de infraestructura y content engine para el ecosistema VenBraTech.

## Estructura

```
venbrax/
├── gcp-startup.sh              → Script de inicio para Google Cloud e2-micro
├── content_engine.py           → Motor de contenido (5 plataformas, 3x/día)
├── visual_generator.py         → Tarjetas IG 1080x1350 estilo "terminal hacker"
├── n8n-workflows/
│   └── content-engine-workflow.json  → Workflow n8n para contenido automático
└── README.md
```

## Setup Google Cloud VM

1. Crear VM e2-micro en us-central1 (Always Free)
2. En **Avanzado → Secuencia de comandos de inicio**, pegar el contenido de `gcp-startup.sh`
3. Firewall: permitir HTTP, HTTPS, puerto 5678
4. n8n disponible en `http://IP_PUBLICA:5678`
5. Login: `admin` / `VenBraTech2025!`

## Content Engine

```bash
# Instalar
pip install anthropic requests

# Generar contenido (template)
python content_engine.py

# Con Claude API (mejor calidad)
ANTHROPIC_API_KEY=sk-... python content_engine.py --use-claude

# Solo una plataforma
python content_engine.py --platform linkedin

# Preview sin guardar
python content_engine.py --preview

# Generar además la tarjeta visual IG (HTML 1080x1350)
python content_engine.py --visual
```

## Visual Generator (tarjetas Instagram)

Genera tarjetas 1080x1350 con estética "terminal hacker" (Matrix rain, comando
fake, headline con acento rojo, caja amarilla de "culpable inesperado", fuente
citada). Fórmula basada en formatos de alto save-ratio del nicho tech en español.

```bash
# Insight del día
python visual_generator.py

# Insight específico
python visual_generator.py --insight-id ai-cost-inflation

# Render a PNG (requiere Chromium en la máquina)
chromium --headless --screenshot=card.png --window-size=1080,1350 card.html
```

Vía HTTP (para n8n):

```
GET /visual                              → tarjeta del insight del día
GET /visual?insight_id=ai-cost-inflation → tarjeta de un insight específico
GET /visual?handle=@tucuenta             → cambia el handle mostrado
```

## n8n Workflow

1. Abrir n8n: `http://IP_PUBLICA:5678`
2. Settings → Import Workflow → subir `n8n-workflows/content-engine-workflow.json`
3. Configurar credenciales:
   - LinkedIn OAuth2
   - Twitter API v2
   - Telegram Bot (TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID)
4. Activar workflow — publica automáticamente a las 9:00, 14:00, 19:00 hora Caracas

## Variables de Entorno Requeridas

```
ANTHROPIC_API_KEY=sk-ant-...        # Claude API para contenido premium
TELEGRAM_BOT_TOKEN=...              # Bot de notificaciones
TELEGRAM_CHAT_ID=...                # Chat ID personal
```

## Estado del Ecosistema

| Componente | Estado |
|---|---|
| Google Cloud e2-micro | ⏳ Configurando |
| n8n | ⏳ Pendiente VM |
| Content Engine | ✅ Script listo |
| Oracle A1 Flex | 🔄 Retry cada 2h |
| forensic-api-v5 | ✅ Live en Render |
| HubSpot CRM | ✅ Conectado |
