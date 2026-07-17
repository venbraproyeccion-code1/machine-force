# VenBraX — Handoff 2026-07-17 (sesión Claude Sonnet 5)

Modelo: Claude Sonnet 5 (con paso breve por Fable 5 durante la sesión)
Sesión: https://claude.ai/code/session_01FUHuPicFL8hCfeSGHrDe5G
Ramas de trabajo: `claude/handoff-document-review-s3tb9x` (machine-force, print-money-maker, venbrax-ecosistema, nextjs-boilerplate, Meu-Drive)

> Nota: este handoff se guardó en git (no en Google Drive) porque el
> conector de Drive activo en esta sesión rechazó la escritura con
> "The caller does not have permission" — parece tener solo permiso de
> lectura/búsqueda, no de creación de archivos. Si Alfonso otorga permiso
> de escritura al conector, este archivo puede migrarse a Drive.

## ✅ HECHOS VERIFICADOS (comandos/herramientas reales, no intenciones)

### 1. print-money-maker — Market Radar (Módulo 1 del pipeline)
- `src/market_radar.py` implementado: búsqueda YouTube vía yt-dlp, análisis
  de tendencias (unigramas+bigramas, ponderación tags>título>descripción).
  Commit `5cd4df6`.
- Extendido con integración Pinterest: `--pinterest-json` carga un export
  del repo hermano Pinterest-Scraper (normalizado al mismo esquema que un
  video). Probado end-to-end con datos simulados (carga, normalización,
  análisis, JSON de salida válido). Commit `716a66f`.
- `requirements.txt`: `yt-dlp>=2025.1.1` (solo stdlib + yt-dlp).
- PR #1 abierto en draft: https://github.com/venbraproyeccion-code1/print-money-maker/pull/1
  Sin CI configurado, `mergeable_state: clean`, sin comentarios. Vigilado
  con check-in automático cada ~1h (send_later), se detiene al mergear/cerrar.
- Pendiente (no implementado aún): `src/product_generator.py`,
  `src/marketing_auditor.py` — ambos vacíos.

### 2. machine-force — n8n Doctor + seguridad de la VM (venbratech-n8n, GCP)
- Confirmado por Alfonso vía `gcloud compute instances list`: VM RUNNING,
  IP `162.222.183.89`, zona `us-central1-a`, tipo `e2-micro`.
- Firewall (regla `allow-n8n`) restringido por Alfonso desde Cloud Shell a
  su IP de casa `/32` (antes abierto a todo internet en el puerto 5678).
- Contraseña de n8n rotada por Alfonso con `secure-n8n.sh` (generada, 24
  chars, guardada en `/opt/n8n/.env` chmod 600, guardada por Alfonso en el
  gestor de contraseñas de Chrome/Google). La contraseña vieja
  `VenBraTech2025!` queda COMPROMETIDA (estaba en git en texto plano) — ya
  rotada, no reutilizar.
- Credenciales hardcodeadas purgadas de 5 archivos del repo
  (`gcp-startup.sh`, `install-n8n-minimal.sh`, `update-docker-compose.sh`,
  `README.md`, `SKILL.md`). Commit `ea09415`.
- `n8n_doctor.py` creado, desplegado en `/opt/venbrax/` en la VM, cron cada
  15 min instalado por Alfonso. Primera corrida real: reanimó 6 ejecuciones
  fallidas, blindó el workflow "VenBraX — TikTok Content Engine" (retry+
  timeout). El workflow "VenBraX Content Engine — 3x Daily" falló con
  HTTP 400 al intentar blindarlo (bug: `settings.callerPolicy` fuera del
  esquema que acepta el PUT de la API de n8n).
- Fix del bug 400 pusheado (commit `c906b51`, sanea `settings` antes del
  PUT). **PENDIENTE:** Alfonso debe actualizar el script en la VM y
  re-correrlo para confirmar "0 pendientes" (comandos en la sección de
  pendientes abajo).
- Error Sentinel (workflow de alerta Telegram ante cualquier error) creado
  en el repo, JSON listo para importar por la UI de n8n — Alfonso AÚN NO
  lo importó.
- `n8n_export.py` creado (exporta workflows vía API a JSON) — no se usó al
  final porque Alfonso resolvió la exportación local con el comando nativo
  `n8n export:workflow --all --separate` (ver siguiente punto).

### 3. n8n LOCAL (PC de Alfonso, PowerShell, puerto 5678 + túnel ngrok)
- Instancia real: n8n v2.8.4, corriendo local, expuesta por ngrok en
  `https://sneer-phrasing-unclasp.ngrok-free.dev` (verificado por captura
  de terminal de Alfonso).
- 2 workflows activos ahí: "My workflow" (ID `u16BAIsaiQROONuR`) y
  "VenBraX_V4" (ID `vUBcZbEH2rUiajFa`).
- Aviso de la propia terminal de n8n: "Python 3 is missing from this
  system" para el Python Task Runner — INCORRECTO, Alfonso sí tiene Python
  3.11 instalado (confirmado por captura del buscador de Windows); el
  problema real es que n8n no lo encuentra en el PATH del proceso. No
  resuelto aún, prioridad baja (solo afecta nodos de código en modo Python
  interno, no bloquea nada crítico).
- Alfonso exportó los 10 workflows con éxito:
  `n8n export:workflow --all --separate --output=C:\venbrax-export-local\`
  → 10 archivos .json confirmados por `dir` (gLTPEvMd3YOrxTE3.json,
  jlduRnh4SfmYIejR.json, jNjlPMaNo1FquV0H.json, MXBkGsicUPrfbvQu.json,
  OtOUAPrMmXsCjDAI.json, qSL4BT53CFcoQBDf.json, r0wjwE9xJgJo1VNV.json,
  u16BAIsaiQROONuR.json, vUBcZbEH2rUiajFa.json, ys3uAbtIxlXTaCTx.json).
  **PENDIENTE:** Alfonso aún no pegó/subió esos 10 archivos a Claude para
  el diagnóstico de nodos rotos que pidió.

### 4. Gmail (venbraproyeccion@gmail.com) — diagnóstico de almacenamiento
- Herramienta Gmail MCP NO tiene función de borrado/papelera — solo
  búsqueda, etiquetado, borradores. El borrado real lo debe hacer Alfonso
  desde la interfaz de Gmail o usando Gemini nativo de Gmail.
- Diagnóstico real (`search_threads`):
  - `in:trash` → solo 1 hilo. La papelera NO es el problema.
  - `category:promotions` → ~201 hilos. Candidato seguro de borrado masivo
    (categoría nativa de Gmail, un clic en la pestaña "Promociones").
  - `larger:10M` → 9 hilos, casi todos correos que Alfonso se envía A SÍ
    MISMO con videos/fotos (asuntos: "Video", "Videos interesantes",
    "Para contenido de venbrax", "fotod de venbrax inicio", "fotos",
    "documentos de mi hija", "Foto" x3). Estos SÍ pueden contener contenido
    que Alfonso quiere conservar (incluye documentos de su hija) — NO se
    borraron, se etiquetaron con la nueva etiqueta "📦 Revisar-Pesados"
    (label creado: `Label_9`) para que Alfonso los revise y decida
    quedárselos/moverlos a Drive/borrarlos.
- Recomendación dada: usar el Gestor de almacenamiento oficial de Google
  (https://one.google.com/storage) para borrado masivo seguro por tamaño
  a través de Gmail+Drive+Fotos — Claude no tiene esa capacidad vía API.
- Propuesta de almacenamiento adicional gratis y sostenible: bucket de
  Google Cloud Storage en el proyecto GCP `venbrax` ya existente (cuota
  Always Free separada del pool de 15GB de Gmail/Drive; ya se usa
  parcialmente por el content engine, `gs://venbrax-public-assets/`) — NO
  creado aún, pendiente confirmación de Alfonso.

## ⚠️ ANOMALÍAS SIN RESOLVER (marcadas, no bloqueantes)
- El archivo de Drive "HANDOFF_MAESTRO.md" (y "HANDOFF_SESSION_20260716.md")
  trae un campo `viewUrl` apuntando a `www.aitoolsite.top` (NO
  `drive.google.com`). Alfonso indicó que es "residuo externo irrelevante
  de sesiones previas" y pidió ignorarlo. Se ignora por instrucción directa
  del Director, pero queda registrado aquí por si reaparece en otro archivo.
- Esos mismos documentos afirman que una sesión previa con "Claude Haiku
  4.5" reorganizó 82,430 archivos del PC y refactorizó referencias a
  "Denise Vargas". Esta sesión NO verificó ese hecho directamente (no hay
  comando/captura en este hilo). Alfonso lo dio por válido como Director;
  se acepta como estado base pero no se re-verificó.
- El conector de Google Drive de esta sesión rechazó la escritura
  ("The caller does not have permission") — parece de solo lectura/búsqueda.

## ⏳ PENDIENTES (dueño + estimado)

| Tarea | Dueño | Estimado |
|---|---|---|
| Actualizar n8n_doctor.py en la VM y re-correr (confirmar 0 pendientes tras fix del HTTP 400) | Alfonso (comandos ya dados) | 5 min |
| Importar Error Sentinel workflow en n8n VM (UI, asignar credencial Telegram) | Alfonso | 5 min |
| Pegar/subir los 10 .json de n8n local a Claude para diagnóstico de nodos | Alfonso | 2 min |
| Diagnosticar los 10 workflows locales (nodos rotos, vars Supabase, ineficiencias) | Claude | tras recibir archivos |
| Implementar src/product_generator.py (usa trends_detected.json + Anthropic API) | Claude | próxima sesión |
| Implementar src/marketing_auditor.py | Claude | próxima sesión |
| Decidir: crear bucket GCS en proyecto venbrax para almacenamiento adicional | Alfonso (confirmar) + Claude (ejecutar) | 15 min |
| Revisar y actuar sobre label "📦 Revisar-Pesados" en Gmail (9 hilos) | Alfonso | 10 min |
| Borrar masivamente category:promotions en Gmail (o usar Gestor de almacenamiento de Google) | Alfonso | 5 min |
| Otorgar permiso de escritura al conector de Google Drive (o confirmar que se queda solo-lectura) | Alfonso | 2 min |
| Reactivar Twitter (recarga créditos developer.x.com) — pendiente de handoff anterior 07-16 | Alfonso | — |
| Generación de audio clonado (Gemini, 3 WAV) — pendiente de handoff anterior 07-16 | Alfonso/Gemini | — |

## 📐 REGLAS NUEVAS ACUMULADAS
- n8n Doctor: antes de PUT a `/api/v1/workflows/{id}`, sanear `settings` a
  solo las claves que la API pública acepta (ver `ALLOWED_SETTINGS_KEYS` en
  `n8n_doctor.py`) — evita HTTP 400 en workflows con settings de versiones
  viejas de n8n.
- Gmail MCP no tiene borrado — cualquier limpieza masiva de correo requiere
  acción manual de Alfonso (Gmail UI, Gemini nativo, o Google Storage
  Manager). Claude puede diagnosticar y etiquetar, no borrar.
- Anomalías de dominio ajeno en metadatos de Drive (viewUrl u otros) se
  reportan una vez; si el Director confirma que son irrelevantes, no se
  re-litigan en sesiones siguientes salvo que reaparezcan en un contexto
  distinto.
- Si Google Drive rechaza escritura con "permission denied", no reintentar
  en bucle — reportar y usar git (`machine-force/docs/handoff/`) como
  respaldo durable del handoff.
