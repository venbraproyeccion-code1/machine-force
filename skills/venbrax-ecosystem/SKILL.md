# VenBraX Ecosystem Skill

## Trigger
Auto-trigger when the human partner mentions: VenBraX, VenBraTech, n8n, Oracle, Google Cloud, content engine, social media automation, forensic API, ecosystem, autosustentable, handoff.

## Context
VenBraTech is building a fully autonomous AI-powered ecosystem. The goal is zero human intervention — content generates and posts itself, leads are captured and responded to automatically, infrastructure self-heals. 100-year operational horizon. No generic content. Higgsfield-quality production. Predictive content always 1 month ahead.

## Ecosystem Map

```
INFRASTRUCTURE
├── Google Cloud e2-micro (us-central1-f) → n8n [VM RUNNING — PRIMARY]
│   └── venbratech-n8n → IP externa: 162.222.183.89 → n8n: http://162.222.183.89:5678
├── Oracle A1 Flex → retrying every 2h (background, low priority)
├── Render.com → forensic-api-v5 [LIVE]
└── venbratech.com → main domain

AUTOMATION (n8n workflows)
├── VenBraX Content Engine → 3x/day → LinkedIn, Instagram, TikTok, Twitter, Threads
├── Lead capture → HubSpot CRM → auto-response
├── Telegram → system notifications (control plane)
└── GitHub Actions → CI/CD + Oracle retry

REPOSITORIES (venbraproyeccion-code1)
├── machine-force → skills framework + venbrax scripts
│   ├── venbrax/gcp-startup.sh          → VM startup script
│   ├── venbrax/content_engine.py       → Content Engine v2 (5 platforms)
│   ├── venbrax/n8n-workflows/          → n8n workflow JSONs to import
│   └── skills/venbrax-ecosystem/       → this skill
└── oracle-a1-retry → Oracle VM provisioning (background)

CONTENT ENGINE (5 insights × 5 platforms × 3x/day)
├── Platforms: LinkedIn, Twitter/X, Instagram, TikTok, Threads
├── Tech Insights pool: AI loops, RAG chunking, n8n vs Make, Vector DBs, Prompt caching
├── Schedule: 09:00, 14:00, 19:00 America/Caracas
└── Generation: Claude Opus via ANTHROPIC_API_KEY
```

## Operating Principles

**Always push toward autonomy.** Every manual step should be a candidate for automation.

**Telegram is the control plane.** All system events notify via Telegram. The human partner should only receive notifications, not perform tasks.

**Infrastructure is ephemeral, data is permanent.** Workflows, content, and leads persist in databases. VMs can be rebuilt from code.

**Prioritize what unblocks the ecosystem.** n8n running > perfect code. Working automation > clean architecture.

**Zero generic content.** All posts based on real technical insights. Predictive, 1 month ahead.

**100-year horizon.** Design every automation as if it needs to run without human intervention for decades.

## Current State

| Component | Status | Next Action |
|---|---|---|
| Google Cloud VM | ✅ RUNNING — venbratech-n8n, us-central1-f, IP 162.222.183.89 | Firewall allow-n8n (5678) created |
| n8n | ⏳ Installing via startup script | Verify http://162.222.183.89:5678 |
| Content Engine | ✅ Ready in machine-force/venbrax/ | Deploy to VM after n8n up |
| Oracle A1 Flex | 🔄 Retry every 2h | Low priority — GCP is primary |
| forensic-api-v5 | ✅ Live on Render.com | No action needed |
| HubSpot CRM | ✅ Connected via MCP | Add n8n workflows |
| Telegram Bot | ⚠️ Secrets pending | Need BOT_TOKEN + CHAT_ID |
| Obsidian | 📋 Requested | Pending VM setup |

## Google Cloud VM — Steps to Complete

1. **"Redes"** section of VM creation:
   - ✅ "Permitir tráfico HTTP"
   - ✅ "Permitir tráfico HTTPS"
2. **"Avanzado" → "Secuencia de comandos de inicio"** — paste `venbrax/gcp-startup.sh`
3. Click "Crear" — n8n installs automatically in ~5 min
4. Get public IP: Compute Engine → Instances → venbratech-n8n

## Standard Responses

When asked about infrastructure: Google Cloud e2-micro is PRIMARY. Oracle keeps retrying in background silently.

When asked about content: VenBraX Content Engine v2 — 5 tech insights rotating, 5 platforms, 3x/day, Claude Opus generation. Script in machine-force/venbrax/content_engine.py.

When asked about tokens/credentials: store in GitHub Secrets. Needed: ANTHROPIC_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID.

When the ecosystem is blocked: identify the single bottleneck. Current: VM creation (user must complete manually).

When asked for links: always provide direct links:
- Google Cloud Console: https://console.cloud.google.com/compute/instances?project=venbrax
- GitHub repos: https://github.com/venbraproyeccion-code1
- n8n: http://162.222.183.89:5678 (admin / VenBraTech2025!)
- Firewall rules: https://console.cloud.google.com/networking/firewalls/list?project=venbrax

## Credentials Map

```
n8n admin:   admin / VenBraTech2025!
Telegram:    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID (pending setup)
Anthropic:   ANTHROPIC_API_KEY (pending — needed for Content Engine Claude generation)
LinkedIn:    OAuth2 (configure in n8n after VM is up)
Twitter/X:   API v2 (configure in n8n after VM is up)
HubSpot:     Connected via MCP
Oracle:      OCI secrets in oracle-a1-retry GitHub Secrets
```
