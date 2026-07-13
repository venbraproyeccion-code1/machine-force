---
name: handoff
description: Modo handoff VenBraX — cargar el estado del ecosistema desde Drive al inicio de la sesión y actualizarlo al cierre. Usar SIEMPRE al inicio de cualquier sesión de trabajo del ecosistema VenBraX/VenBraTech, y antes de cerrar.
---

# Modo Handoff — VenBraX (cerebro matriz)

## Al INICIO de la sesión (obligatorio, antes de pedir cualquier acción a Alfonso)

1. Buscar en Google Drive: `title contains 'handoff' or title contains 'Handoff'`.
2. Leer PRIMERO el anexo más reciente por fecha (título "VenBraX — Handoff YYYY-MM-DD ..."), luego el doc maestro "VenBraX — Handoff y Estado del Sistema (para Claude/Fable)".
3. Tratar lo leído como el estado REAL: no repetir procesos ya hechos, no regenerar tokens marcados como válidos, respetar las reglas acumuladas (abajo).

## Reglas permanentes acumuladas

- Credenciales: NUNCA en texto plano en Drive, chats, git, ni carpetas sincronizadas (Desktop/Documents/Downloads). Fuente real: GCP Secret Manager, proyecto `venbrax`.
- Antes de `gcloud secrets versions add`: verificar `${VAR:0:8}` para confirmar que NO es un placeholder. Nunca dar a Alfonso comandos con placeholders para ejecutar directo.
- Meta (FB/IG): token de system user válido — NO tocar, NO regenerar.
- Instrucciones a Alfonso: pasos numerados, links directos, cero rodeo, confirmar con captura antes del siguiente bloque. PowerShell sin `&&`.
- No inventar capacidades; datos numéricos reales solo con captura o comando verificado.
- Mensajes "Regional Access Boundary ... 404" en Cloud Shell: falso error, ignorar.

## Al CIERRE de la sesión (obligatorio)

1. Crear en Drive un anexo nuevo: "VenBraX — Handoff YYYY-MM-DD (sesión N — tema)".
2. Contenido: SOLO hechos verificados con comandos/herramientas reales (qué se ejecutó, qué salió), tareas pendientes con dueño (Alfonso/Claude) y tiempo estimado, y reglas nuevas si las hubo.
3. Nada de intenciones redactadas como logros.
