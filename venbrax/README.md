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

## Social Publisher (sin OAuth redirect)

Publica directo vía API con tokens de larga duración — elimina el problema
de "localhost / redirect URI" porque no usa el flujo OAuth de n8n.

```bash
python social_publisher.py --all --dry-run          # prueba sin publicar
python social_publisher.py --platform facebook      # publica insight del día
python social_publisher.py --platform instagram --image-url https://...
```

### Cómo generar cada token (una sola vez, ~20 min)

**Facebook Page + Instagram** (misma app de Meta, App Dashboard → caso de uso Business):
1. [Graph API Explorer](https://developers.facebook.com/tools/explorer/) → selecciona tu app
   → User Token con permisos `pages_manage_posts`, `pages_read_engagement`,
   `instagram_basic`, `instagram_content_publish`.
2. Canjear por token de larga duración:
   `GET /oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=TOKEN_CORTO`
3. Con ese token: `GET /me/accounts` → te da el **FB_PAGE_ID** y el
   **FB_PAGE_ACCESS_TOKEN** (los page tokens derivados de un user token de
   larga duración no expiran).
4. **IG_USER_ID**: `GET /{FB_PAGE_ID}?fields=instagram_business_account`
   (requiere IG Professional/Creator vinculada a la Page).
5. No requiere App Review mientras publiques en tus propias cuentas con rol
   de admin en la app (modo desarrollo).

**LinkedIn** ([developer portal](https://developer.linkedin.com/)):
1. App → Products → habilitar "Share on LinkedIn" y "Sign In with LinkedIn
   using OpenID Connect".
2. Auth → usar el **Token Generator** del portal (no requiere redirect propio)
   → scope `w_member_social` + `openid profile`.
3. **LINKEDIN_AUTHOR_URN**: `GET https://api.linkedin.com/v2/userinfo` →
   `urn:li:person:{sub}`.

Tokens van en `/opt/n8n/.env` (VM) o en las env vars de Render — nunca en git.

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
