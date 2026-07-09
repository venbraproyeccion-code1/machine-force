# VenBraX Ecosystem Skill

## Trigger
Auto-trigger when the human partner mentions: VenBraX, VenBraTech, n8n, Oracle, Google Cloud, content engine, social media automation, forensic API, ecosystem, autosustentable, handoff.

## Context
VenBraTech is building a fully autonomous AI-powered ecosystem. The goal is zero human intervention — content generates and posts itself, leads are captured and responded to automatically, infrastructure self-heals.

## Ecosystem Map

```
INFRASTRUCTURE
├── Google Cloud e2-micro → n8n (automation hub)
├── Oracle A1 Flex → n8n migration target (high capacity)
├── Render.com → forensic-api-v5 (already live)
└── venbratech.com → main domain

AUTOMATION (n8n workflows)
├── VenBraX Content Engine → 3x/day → LinkedIn, Instagram, TikTok, Twitter
├── Lead capture → HubSpot CRM → auto-response
├── Telegram → system notifications
└── GitHub Actions → CI/CD + Oracle retry

REPOSITORIES (venbraproyeccion-code1)
├── machine-force → skills framework (this repo)
├── oracle-a1-retry → Oracle VM provisioning
└── [venbrax-content] → content generation scripts
```

## Operating Principles

**Always push toward autonomy.** Every manual step should be a candidate for automation.

**Telegram is the control plane.** All system events notify via Telegram. The human partner should only receive notifications, not perform tasks.

**Infrastructure is ephemeral, data is permanent.** Workflows, content, and leads persist in databases. VMs can be rebuilt from code.

**Prioritize what unblocks the ecosystem.** n8n running > perfect code. Working automation > clean architecture.

## Current State (check before advising)
- Oracle E2.1.Micro: being provisioned (GitHub Actions running every 2h)
- Oracle A1 Flex: waiting for capacity (parallel retry)  
- n8n: not yet deployed (blocked on VM)
- Content engine: script ready, needs n8n for scheduling
- Google Cloud: alternative path if Oracle access issues

## Standard Responses

When asked about infrastructure: check Oracle status first, then suggest Google Cloud as fallback.

When asked about content: reference the VenBraX Content Engine (5 insights rotating daily, 5 social platforms).

When asked about tokens/credentials: refer to the ecosystem credential map and remind to store in GitHub Secrets, never in code.

When the ecosystem is blocked: identify the single bottleneck and solve it before anything else.
