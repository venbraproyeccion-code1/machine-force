---
name: publicar-hoy
description: Generar y publicar el contenido VenBraX del día en todas las redes — pack de textos por plataforma, tarjeta visual IG y publicación vía social_publisher.py o Postiz. Usar cuando Alfonso pida publicar, generar contenido del día, o el pack de redes.
---

# Publicar hoy — VenBraX

## 1. Generar el pack

```bash
cd venbrax
python3 content_engine.py --preview --visual
```

- Produce los textos de las 5 plataformas + la tarjeta HTML en /tmp.
- Renderizar PNG: `chromium --headless --no-sandbox --screenshot=card.png --window-size=1080,1350 --hide-scrollbars /tmp/venbrax-visual-*.html`
- Revisar SIEMPRE el render antes de publicar (hubo bugs de solapamiento en el pasado).
- El estilo Twitter puede cortar palabras al truncar: revisar y reescribir a mano si pasa.

## 2. Entregar el pack

- Subir a Drive un doc "VenBraX — PACK DE PUBLICACIÓN YYYY-MM-DD" con los textos finales etiquetados por red, y enviar la tarjeta PNG a Alfonso.

## 3. Publicar

Orden de preferencia:

1. **Postiz** (cuando esté desplegado en la VM): `POST {BACKEND_URL}/public/v1/posts` con `Authorization: {apiKey}` — publica en todas las redes conectadas. Docs: docs.postiz.com/public-api
2. **social_publisher.py** (FB/IG/LinkedIn directo, tokens desde Secret Manager `venbrax`):
   ```bash
   export FB_PAGE_ID=1099025373297613
   export FB_PAGE_ACCESS_TOKEN=$(gcloud secrets versions access latest --secret=facebook-system-user-token --project=venbrax)
   python3 social_publisher.py --platform facebook --dry-run   # verificar
   python3 social_publisher.py --platform facebook             # real
   ```
   Instagram vía API exige URL pública de imagen (`--image-url`). LinkedIn exige token vigente (`linkedin-api-key`; si da 401, regenerar según el handoff 2026-07-13).
3. **Metricool / manual**: copiar del pack (5 redes conectadas en Metricool).

## Reglas

- SIEMPRE `--dry-run` antes de la publicación real.
- Nunca publicar sin que el PNG esté verificado visualmente.
- Registrar en el handoff de cierre qué se publicó, dónde y con qué resultado (IDs/links de los posts).
