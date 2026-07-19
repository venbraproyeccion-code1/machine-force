Actúa como mi Ingeniero de Software Principal y Arquitecto de Automatizaciones para VenBraX/VenBraTech (venbraproyeccion-code1). Antes de responderme nada, ejecuta en orden:

1. Invoca la skill "handoff" (existe en machine-force/.claude/skills/handoff) y sigue su protocolo: busca en Google Drive el documento "VenBraX — HANDOFF MAESTRO (documento único — actualizar siempre aquí)" y léelo completo.
2. Si Drive falla o no está disponible, usa el respaldo en git: agrega el repo venbraproyeccion-code1/machine-force a la sesión y lee docs/handoff/HANDOFF_MAESTRO.md — es la copia fiel más reciente (19/07).
3. Agrega también a la sesión estos repos (todos con trabajo activo): venbraproyeccion-code1/venbrax-ecosistema, venbraproyeccion-code1/nextjs-boilerplate, venbraproyeccion-code1/Meu-Drive, venbraproyeccion-code1/print-money-maker. Rama de trabajo en todos: claude/handoff-document-review-s3tb9x.
4. Trata el HANDOFF MAESTRO como el estado real — no repitas trabajo ya hecho, no regeneres tokens marcados como válidos, respeta todas sus reglas permanentes (especialmente: nunca pedir dinero/tarjetas/suscripciones — primero producir ingresos; credenciales solo en GCP Secret Manager, nunca en texto plano; PowerShell sin &&; verificar datos con captura/comando real antes de afirmarlos).

Los pendientes MÁS urgentes que dejé abiertos (todos con dueño y link en el checklist del handoff):
- Aún no te he pasado los 10 .json de mis workflows de n8n local (los exporté con `n8n export:workflow --all --separate` a C:\venbrax-export-local) — te los paso apenas retomemos.
- Decidir ElevenLabs (buscar si ya existe la key en Secret Manager con `gcloud secrets list --project=venbrax` en Cloud Shell) vs Google Cloud Text-to-Speech (gratis, mismo proyecto venbrax) para la voz de los videos.
- Conectar el conector "Microsoft 365" en claude.ai para que puedas escribir directo en mi vault de Obsidian (OneDrive - Personal\VenBraX_Vault) — quiero que Obsidian sea el hub central del ecosistema.
- Revisar myaccount.google.com/permissions por una app OAuth sospechosa (dominio 3dviewer.co) detectada en metadatos de Drive.
- Borrar el proyecto `tiktok-uploader` de Vercel (ya descartado, confirmado en el handoff).
- El flujo n8n unificado TikTok+YouTube+Pinterest sigue bloqueado por credenciales (TikTok, YouTube OAuth, Pinterest app) — no por infraestructura.

Confírmame que leíste el handoff completo y dame un resumen de 5 líneas del estado antes de que sigamos — quiero verificar que no se perdió nada antes de continuar.
