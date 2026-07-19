# VENBRAX — HANDOFF MAESTRO (DOCUMENTO ÚNICO)

Última actualización: 2026-07-19 (sesión Claude Sonnet 5, tarde). ÚNICO documento de handoff del ecosistema. NO se crean anexos por sesión — cada sesión actualiza ESTE documento (nueva versión, MISMO título; borrar la anterior).

> Nota de origen: este archivo es la copia autoritativa en GIT del "VenBraX — HANDOFF MAESTRO" de Google Drive (leído hoy desde Drive, fileId `1Wp-KaOI--yhPXOQ-PpeljuLzVQq5InSOXbD5ZkfPwlw`). Se replica aquí porque el conector de Drive de esta sesión devolvió "permission denied" al intentar escribir, aunque reporta estar "connected" con `create_file` en su lista de herramientas — bloqueo sin resolver, ver Bloqueos Técnicos abajo. **Si otra sesión SÍ puede escribir en Drive, esa es la copia canónica; sincronizar ambas.**

## PROTOCOLO

1.  Inicio de sesión: buscar "HANDOFF MAESTRO" en Drive, leer completo antes de actuar. Si Drive falla, esta copia en `machine-force/docs/handoff/HANDOFF_MAESTRO.md` es el respaldo fiel.
2.  Cierre: integrar hechos verificados, actualizar pendientes, nueva versión con MISMO título.
3.  Canal Gemini: docs separados "VenBraX — CANAL CLAUDE-GEMINI — YYYY-MM-DD".
4.  Se conservan aparte: Inventario Secret Manager, RUNBOOK Cloud Shell, PACKs, canal Gemini, CV, carta.
5.  Rutinas automáticas activas (3): Reporte AM 8:00 · Reporte PM 20:00 · Auditor de Oportunidades 7:00 (top 5 diario, prioriza lo que paga). Hora Brasil, entregan en sesión "Trabajo con códigos".
6.  REGLA: toda tarea de Alfonso lleva SIEMPRE su link directo.

## SOBRE ALFONSO

Venezolano en São Lourenço do Oeste, SC, Brasil. Fundador VenBraTech/VenBraX. Ex-Kellanova (may 2023–abr 2026), ex-PDVSA (2010-2015), ex-Pequiven (2008-2010). Certificaciones: Google Data Analytics, SENAI/SC AI-in-Practice. Español/portugués fluido, inglés intermedio. PRIORIDAD: generar ingresos — ecosistema en $0 (Gumroad $0, Hotmart 0 ventas, PayPal 0, HubSpot 0 deals, Shopify bloqueada). Cuello de botella: distribución, no infraestructura. Estilo: directo, links directos, capturas como verificación, español. Visión creativa: calidad NVIDIA/F1/NASDAQ/X; nicho ciberseguridad/velocidad; copy anti-miedo. Meta: "etapa 2 de la IA" — máxima automatización, mínima operación manual.

**REGLA DE ORO FINANCIERA (reafirmada 19/07 en sesión Claude):** prohibido pedir dinero, tarjetas o suscripciones bajo cualquier circunstancia. Primero producir ingresos con lo gratuito, luego (y solo luego) se habla de gastar. Todo agente debe reprogramar/pivotar de forma predictiva ante cualquier límite de free-tier antes de sugerir upgrade de pago (ej.: banner "Add a Credit Card" de Vercel AI Gateway — ignorar siempre; Metricool descartado por ser de pago).

## REGLAS PERMANENTES

1.  PowerShell: nunca &&.
2.  Credenciales NUNCA en texto plano. Fuente única: GCP Secret Manager proyecto venbrax. Índice local: VenBraX-Secrets\\credenciales_indice.md. PENDIENTE: migrar twitter_tokens_temp.txt y comandos de apikeys.txt (valores reales) a KeePassXC y borrar los .txt.
3.  Antes de gcloud secrets versions add: verificar ${VAR:0:8} no sea placeholder.
4.  Meta (FB/IG): tokens en producción, NO tocar.
5.  Datos numéricos solo con captura o comando verificado.
6.  No inventar capacidades; investigar primero.
7.  Sin lenguaje de sumisión: respeto + ejecución + verdad.
8.  "Regional Access Boundary 404" en Cloud Shell: ignorar.
9.  Legal Hub: deploy solo Railway.
10. Windows+gcloud: scripts locales + scp + bash.
11. Tras cambiar timezone en VM: reiniciar cron.
12. Publicación: siempre --dry-run antes; verificar visualmente; registrar IDs.
13. Voz sintética en video: etiqueta "generado o alterado con IA".
14. Ningún agente ejecuta pagos/retiros sin aprobación humana explícita.
15. Links raros tipo aitoolsite.top en Drive: investigado 12/07, es backup de Google Drive Desktop, NO malware. No re-alarmar.
16. **(Nueva 19/07)** ElevenLabs no soporta registro OAuth automático de conectores en claude.ai (error "no admite el registro automático de clientes"). Solución: usar API key directa (`xi-api-key`) obtenida en elevenlabs.io → Profile → API Keys, guardada en Secret Manager como `elevenlabs-api-key`. Alternativa sin cuenta nueva y con tier gratis mayor: Google Cloud Text-to-Speech (mismo proyecto `venbrax`, 4M caracteres/mes gratis con voces estándar) — activar en console.cloud.google.com/apis/library/texttospeech.googleapis.com?project=venbrax. Decisión pendiente: ¿cuál priorizamos?
17. **(Nueva 19/07 — SEGURIDAD, distinta de la regla #15)** Varios archivos de Drive (GPT5*ReasoningEffortSlider.tsx, mdx de docs de terceros) tienen `viewUrl` apuntando a una URL de autorización OAuth real: `accounts.google.com/o/oauth2/auth?...redirect_uri=https://3dviewer.co&...`. Esto NO es el mismo caso que aitoolsite.top (que es benigno, backup de Drive Desktop) — este es un patrón de solicitud de permiso OAuth de una app de terceros. PENDIENTE: Alfonso debe revisar https://myaccount.google.com/permissions y revocar cualquier app desconocida (buscar "3dviewer" o similar). No confirmado como malicioso, pero no descartado — no tratar como cerrado hasta que Alfonso confirme.

## ARQUITECTURA

  - PC Windows i7-3770 16GB: Ollama (Gemma 8B, qwen2.5:3b, llama3.1:8b), AnythingLLM, Tailscale, n8n local :5678, Node-RED instalado (NO usar, todo flujo nuevo va a n8n).
  - VM GCP venbratech-n8n: us-central1-a, IP 162.222.183.89, TZ America/Caracas. SSH: gcloud compute ssh venbratech-n8n --zone us-central1-a --quiet.
    - **(Actualizado 17-19/07 en sesión Claude):** firewall (regla `allow-n8n`) restringido a la IP de casa de Alfonso `/32` (antes abierto a todo internet). Password de n8n rotada (secure-n8n.sh), guardada en `/opt/n8n/.env` chmod 600 + gestor de contraseñas de Chrome. Credenciales hardcodeadas purgadas de 5 archivos del repo machine-force. `n8n_doctor.py` desplegado + cron 15min: blinda workflows (retry+timeout) y reanima ejecuciones fallidas automáticamente. `error-sentinel-workflow.json` listo para importar (alerta Telegram ante cualquier error) — AÚN NO importado por Alfonso.
  - GitHub (venbraproyeccion-code1): machine-force (publicación), venbrax-ecosistema, nextjs-boilerplate, Meu-Drive, **print-money-maker (REVISADO 17/07 en sesión Claude — `market_radar.py` implementado: búsqueda YouTube vía yt-dlp + integración Pinterest-Scraper vía `--pinterest-json`, probado end-to-end, PR #1 abierto en borrador, sin CI, mergeable clean)**, Tiktok-uploader (REVISADO 19/07 — script no oficial vía cookie, riesgo de ban + no corre en Vercel free por límite de 10s; DESCARTADO, no invertir más tiempo ahí — **confirmado 19/07 en sesión Claude: borrar el proyecto de Vercel, ya no despliega nada útil**), venbratech.github.io, forensic-api-v5, cba-website, data-analytics-portfolio, oracle-a1-retry.
  - **Vercel (conectado 19/07 en sesión Claude):** proyectos activos `tiktok-uploader` (Build Failed permanente, descartar — ver arriba) y `nextjs-boilerplate` (producción viva y estable desde el deploy del 10/06; un redeploy fallido del 14/07 no afecta la producción, es cosmético). Banner de upsell "AI Gateway — Add a Credit Card": ignorar siempre, nunca agregar tarjeta.
  - Obsidian vault REAL: OneDrive - Personal\\VenBraX_Vault (00_VISION...90_INBOX, HOME.md). **(19/07) Alfonso pide que Obsidian sea el hub central del ecosistema con conectores.** Recomendación: conectar "Microsoft 365" (SharePoint/OneDrive/Outlook/Teams) en claude.ai — no instalado aún — para que Claude escriba directo en el vault vía OneDrive. Gratis, sin suscripción nueva.
  - venbratech.com LIVE (GoDaddy). Correo <alfonso@venbratech.com> vía ImprovMX → Gmail. Zoho abandonado.
  - Assets de marca: VenBraTech-Logo.svg, logo venbrax.png, landing HTML (negro+dorado \#C9A84C), banners LinkedIn, guiones, video de prueba. Pendiente: logo águila.
  - **Gmail (venbraproyeccion@gmail.com) — diagnosticado 17/07 en sesión Claude:** `category:promotions` ~201 hilos (borrado masivo seguro, pendiente que Alfonso lo haga — Gmail MCP no tiene función de borrado). `larger:10M` → 9 hilos pesados (autoenvíos de video/fotos, incluye "documentos de mi hija") etiquetados con "📦 Revisar-Pesados" para revisión manual, NO borrados. `in:trash` solo 1 hilo, no es el problema.

## PUBLICACIÓN — ESTADO POR RED

FACEBOOK ✅ cron 9/13/16/20 VET. LINKEDIN ✅ cron 8/12/16/20 VET. Última verificación real de logs: 15/07 (sin verificación nueva desde entonces). INSTAGRAM manual vía API. TWITTER ⏸️ sin créditos. TIKTOK/YOUTUBE/PINTEREST: automatización en construcción — VER sección "AUTOMATIZACIÓN TIKTOK/YOUTUBE/PINTEREST" abajo (Metricool descartado por costo).

## AUTOMATIZACIÓN TIKTOK/YOUTUBE/PINTEREST (19/07)

  - Metricool: API es de pago ("Advanced & Custom plans") — DESCARTADO para $0 presupuesto. Confirmado con captura real.
  - Decisión: Postiz (self-hosted gratis en la VM) para TikTok/YouTube/Pinterest, o APIs oficiales directas.
  - TikTok: Alfonso YA tiene API key propia. PENDIENTE: confirmar si es de TikTok for Developers (Content Posting API oficial) o de otra fuente; guardar en Secret Manager como tiktok-api-key.
  - YouTube: pendiente credenciales OAuth (Google Cloud Console, proyecto venbrax, habilitar YouTube Data API v3).
  - Pinterest: pendiente crear app en developers.pinterest.com/apps, obtener App ID/secret.
  - Diseño de flujo n8n unificado (video entra → publica en las 3): pendiente hasta tener las 3 credenciales. **Este es también el bloqueo real para la "unión de todos los nodos n8n" que Alfonso pidió el 19/07 — no es un problema de infraestructura, es falta de credenciales.**
  - **n8n LOCAL (PC de Alfonso, v2.8.4, túnel ngrok `sneer-phrasing-unclasp.ngrok-free.dev`):** 2 workflows activos ("My workflow", "VenBraX_V4"). Alfonso exportó los 10 workflows con `n8n export:workflow --all --separate --output=C:\venbrax-export-local\` (confirmado, 10 archivos .json) — **PENDIENTE desde el 17/07: Alfonso AÚN NO ha pasado esos 10 .json a Claude para el diagnóstico de nodos rotos que él mismo pidió.**

## PRODUCTOS E INGRESOS (auditado 18/07 con capturas)

  - GUMROAD: 12 productos, 0 ventas, $0 TOTAL. NUEVO 19/07: Gumroad lanzó pestaña "Agent" (IA integrada gratis para gestionar la tienda) — probar.
  - HOTMART: 12 listados. Producto muestreado (Arsenal IA): 0 ventas, 0 clics, 0 leads/7 días. Dos verticales mezcladas: automatización + finanzas personales.
  - HubSpot (ID 51419824): 7 contactos de prueba, 0 deals.
  - DIAGNÓSTICO: problema = distribución, no producto. ESTRATEGIA: copy anti-miedo (ya escrito para los 12), fórmula video 4 pasos, afiliados Hotmart, 1 piloto antes de escalar.
  - OPORTUNIDAD NUEVA 19/07 (Auditor): TikTok Shop Affiliate ya activo en Brasil — paga 5-15% comisión por venta, gratis, sin espera. Prioridad #1 recomendada por el Auditor — conecta distribución TikTok + venta de productos en un solo movimiento. Link: tiktok.com/discover/tiktok-shop-affiliate-eligible-countries
  - Pinterest: perfil de negocio gratis permite vender productos/afiliados desde el día 1, sin mínimo de seguidores — no hace falta esperar el Creator Fund (limitado/EEUU).

## IAs DEL EQUIPO (capa gratuita, sin caducidad)

  - Ollama local (modelos arriba).
  - OpenRouter: cuenta lista. PENDIENTE: key → Secret Manager (openrouter-api-key).
  - NVIDIA build.nvidia.com: ✅ CONFIRMADO ACTIVO — 1 API key real, 40 rpm (verificado en dashboard 19/07). PENDIENTE: mover key a Secret Manager (nvidia-api-key).
  - Google AI Studio (Gemini 2.0 Flash, hallazgo Auditor 19/07): 15 rpm, 1M contexto, sin tarjeta — candidato a sumar al router.
  - Router de fallback en n8n (llm_router_fallback.json): pendiente de importar/construir.
  - Gemini: colaborador activo de Alfonso en paralelo. Claude valida prompts de Gemini contra la realidad del ecosistema antes de ejecutar (ver caso Tiktok-uploader 19/07: se corrigió el enfoque original).
  - **(19/07, sesión Claude) Voz/audio para videos:** ningún audio generado todavía — ni ElevenLabs ni Google TTS están activos aún (ver regla #16). Sin key/API activada no se puede producir ni un archivo de prueba.

## ÁREAS CON NOMBRE

Mateo=Productos. Sofía=Contenido. Lucía=Infraestructura/IAs. Diego=Outreach/Empleo.

## BÚSQUEDA DE EMPLEO

vacantes.com: PENDIENTE Kellanova Educación→Experiencia, vincular 8 certificaciones y 24 experiencias. WeCP: código de verificación pendiente de confirmar. Proceso activo: Data Engineer Semi-Senior con Jesica Quinteros (hunting-talent.com), en seguimiento. Carta PDF lista. Meridial/Invisible: cédula unificada entregada.

## CHECKLIST MAESTRO (actualizado 19/07, tarde)

TAREAS ALFONSO (con links):

1.  ☐ Confirmar guardado de tiktok-api-key en Secret Manager: https://console.cloud.google.com/security/secret-manager?project=venbrax
2.  ☐ Terminar key NVIDIA (cuenta ya activa) → Secret Manager (nvidia-api-key)
3.  ☐ Key OpenRouter → Secret Manager (openrouter-api-key): https://openrouter.ai/settings/keys
4.  ☐ Credenciales YouTube OAuth: https://console.cloud.google.com/apis/credentials?project=venbrax
5.  ☐ App Pinterest: https://developers.pinterest.com/apps/
6.  ☐ TikTok Shop Affiliate (prioridad Auditor): https://www.tiktok.com/discover/tiktok-shop-affiliate-eligible-countries
7.  ☐ Shopify billing: https://admin.shopify.com/settings/billing
8.  ☐ KeePassXC + migrar .txt: https://keepassxc.org/download/
9.  ☐ Afiliados Hotmart: https://app.hotmart.com/products/producer
10. ☐ Confirmar código WeCP en Gmail
11. ☐ Twitter: recargar créditos https://developer.x.com
12. ☑ ~~Aprobar add_repo de print-money-maker~~ — HECHO 17/07, ver Arquitectura
13. ☐ **(Nueva)** Pasar los 10 .json de n8n local (C:\venbrax-export-local) a Claude para diagnóstico
14. ☐ **(Nueva)** Buscar en Secret Manager si ya existe una key de ElevenLabs (`gcloud secrets list --project=venbrax` en Cloud Shell) — o decidir usar Google TTS en su lugar
15. ☐ **(Nueva)** Conectar "Microsoft 365" en claude.ai (Conectores) para que Claude escriba directo en el vault de Obsidian (OneDrive)
16. ☐ **(Nueva)** Revisar https://myaccount.google.com/permissions por la app sospechosa "3dviewer.co" (regla #17)
17. ☐ **(Nueva)** Borrar proyecto `tiktok-uploader` de Vercel (descartado, confirma la regla de Arquitectura arriba)
18. ☐ **(Nueva)** Conectar Vercel ya está hecho (19/07) — falta decidir si borrar también el deployment fallido de nextjs-boilerplate (cosmético, no urgente)

TAREAS CLAUDE:

19. ☐ Flujo n8n leads→HubSpot (bloqueado por keys)
20. ☐ Flujo n8n unificado TikTok+YouTube+Pinterest (bloqueado por credenciales de las 3 — ver checklist Alfonso 4-6)
21. ☐ Guiones de video para 3 productos piloto
22. ☐ Logo VenBraX emblema águila
23. ☑ ~~Revisar print-money-maker~~ — HECHO 17/07
24. ☐ Probar el nuevo "Agent tab" de Gumroad
25. ☐ **(Nueva)** Implementar src/product_generator.py y src/marketing_auditor.py (print-money-maker)
26. ☐ **(Nueva)** Diagnosticar los 10 workflows de n8n local en cuanto Alfonso pase los .json

## BLOQUEOS TÉCNICOS

  - TikTok bloquea lectura automática de video (403) — pedir capturas a Alfonso.
  - Reportes automáticos no envían a Telegram aún (requiere flujo n8n).
  - Metricool API de pago — resuelto con pivote a Postiz/APIs oficiales, sin acción pendiente.
  - Herramienta crear-archivo en Drive: fue intermitente el 18/07, funcionando normal el 19/07 (según sesión que escribió este doc en Drive) — **pero la sesión Claude de esta tarde (17-19/07) recibió "permission denied" en cada intento de `create_file`, con o sin parentId, aunque el conector reporta `connected` con `create_file` en su lista de herramientas. Discrepancia sin resolver — puede ser un token/scope distinto entre sesiones.** Mientras tanto, la copia autoritativa vive en git: `machine-force/docs/handoff/HANDOFF_MAESTRO.md`.
  - ElevenLabs: conector OAuth de claude.ai no soportado por ElevenLabs (ver regla #16) — usar API key directa.

## HISTORIAL RESUMIDO

12/06 freelance · 09-13/07 infraestructura+credenciales · 14/07 primera unificación · 15/07 rotación keys+cron verificado · 16/07 guiones+canal Gemini · 17/07 (sesión Claude) hardening n8n VM completo (firewall, password, n8n_doctor+cron, Error Sentinel) + market_radar.py con integración Pinterest (PR #1) + diagnóstico Gmail (etiquetado, sin borrar) + intento fallido de escritura en Drive (fallback a git) · 18/07 empleo+correo propio+auditoría productos+estrategia anti-miedo+3 rutinas+segunda unificación · 19/07 análisis Tiktok-uploader (descartado)+Metricool descartado por costo+NVIDIA confirmado activo+Auditor de Oportunidades ejecutado (TikTok Shop Affiliate como hallazgo top) · 19/07 tarde (sesión Claude) diagnóstico Vercel (confirma descarte de tiktok-uploader, producción de nextjs-boilerplate estable), decisión ElevenLabs vs Google TTS pendiente, pedido de Obsidian-como-hub (recomendado conector Microsoft 365/OneDrive), nueva alerta de seguridad OAuth (3dviewer.co, distinta de aitoolsite.top), reconciliación de que print-money-maker ya fue aprobado y trabajado.

## DOCUMENTOS A BORRAR (ya integrados aquí)

Todos los "VenBraX — Handoff [fecha]" (09-16/07), "handoff.md" (junio + copia local), "VenBraX_SYSTEM_HANDOFF.md", "CEREBRO MATRIZ v2026-07-14", "HANDOFF_MAESTRO.md" (16/07), "HANDOFF_SESSION_20260716.md", el anexo de git "2026-07-17-n8n-hardening-radar-pinterest-gmail.md" (ya integrado en este documento único).

Fin. Próxima sesión: leer completo (Drive primero, este archivo como respaldo), actualizar esta misma versión al cierre.
