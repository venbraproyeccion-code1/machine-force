"""
VenBraX Visual Generator — estética "terminal hacker" para Instagram.
Genera una tarjeta HTML autocontenida de 1080x1350 (formato retrato IG)
a partir de un insight del content engine. Cero dependencias externas.

Fórmula visual (validada por engagement real del nicho cripto/tech MX):
  1. Chrome de terminal + comando fake       → identidad de nicho
  2. Etiqueta // CATEGORIA · FECHA           → urgencia de "evento"
  3. Headline gigante con palabra en rojo    → hook de impacto personal
  4. Caja amarilla "culpable inesperado"     → el giro que genera shares
  5. // FUENTE · ...                          → credibilidad que genera saves
  6. Punch line final + handle               → cierre memorable

Uso:
  python visual_generator.py                  # insight del día → /tmp/venbrax-visual-*.html
  python visual_generator.py --insight-id ai-cost-inflation
  python visual_generator.py --output card.html

Render a PNG (opcional, requiere Chromium/Playwright en la máquina):
  chromium --headless --screenshot=card.png --window-size=1080,1350 card.html
"""
import argparse
import random
from datetime import datetime

# Marcador de resaltado en textos: **palabra** → color de acento
HIGHLIGHT_OPEN = "**"

MATRIX_CHARS = "アイウエオカキクケコサシスセソタチツテトナニヌネノ0123456789"

MESES = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
         "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]


def _highlight(text, css_class):
    """Convierte **palabra** en <span class="...">palabra</span>."""
    parts = text.split(HIGHLIGHT_OPEN)
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            out.append(f'<span class="{css_class}">{part}</span>')
        else:
            out.append(part)
    return "".join(out)


def _matrix_rain(seed, columns=26, chars_per_column=22):
    """Columnas estáticas de caracteres estilo Matrix como fondo."""
    rng = random.Random(seed)
    cols = []
    for c in range(columns):
        left = round(c * (100 / columns) + rng.uniform(-1, 1), 2)
        top = rng.randint(-20, 10)
        opacity = round(rng.uniform(0.04, 0.14), 2)
        size = rng.choice([16, 18, 20])
        chars = "<br>".join(rng.choice(MATRIX_CHARS) for _ in range(chars_per_column))
        cols.append(
            f'<div class="rain" style="left:{left}%;top:{top}%;'
            f'opacity:{opacity};font-size:{size}px">{chars}</div>'
        )
    return "\n".join(cols)


def generate_visual_html(insight, handle="@venbrax", fecha=None):
    """Genera el HTML de la tarjeta 1080x1350 para un insight.

    Campos del insight que usa (todos con fallback):
      visual_label    → etiqueta verde superior (default: title truncado)
      visual_headline → headline con **resaltado** rojo (default: hook_stat)
      twist_label     → comentario de la caja amarilla
      twist           → texto del giro con **resaltado** amarillo (default: why)
      fuente          → fuentes citadas (default: VENBRAX RESEARCH)
      punch           → frase final (default: cta)
    """
    if fecha is None:
        now = datetime.utcnow()
        fecha = f"{now.day} {MESES[now.month - 1]}"

    topic = insight["id"]
    label = insight.get("visual_label", insight["title"][:42].upper())
    headline = _highlight(insight.get("visual_headline", insight["hook_stat"]), "hl-red")
    twist_label = insight.get("twist_label", "EL DATO QUE NADIE TE DICE")
    twist = _highlight(insight.get("twist", insight["why"]), "hl-yellow")
    fuente = insight.get("fuente", "VENBRAX RESEARCH")
    punch = insight.get("punch", insight["cta"])
    rain = _matrix_rain(seed=topic)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>VenBraX — {label}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{ width: 1080px; height: 1350px; overflow: hidden; background: #060a06; }}
  body {{
    background: #060a06;
    font-family: "SF Mono", "Cascadia Code", "Fira Code", Menlo, Consolas, monospace;
    color: #e8f0e8;
    position: relative;
  }}
  .rain {{
    position: absolute;
    color: #1f8f3f;
    line-height: 1.35;
    z-index: 0;
    user-select: none;
  }}
  .card {{ position: relative; z-index: 1; padding: 0 64px; }}
  .titlebar {{
    display: flex; align-items: center; gap: 14px;
    padding: 28px 64px; font-size: 22px; color: #4caf6d;
    border-bottom: 1px solid #123a1c;
    background: rgba(6,14,6,0.85);
  }}
  .dot {{ width: 16px; height: 16px; border-radius: 50%; display: inline-block; }}
  .titlebar .handle {{ margin-left: auto; color: #2e7d4f; }}
  .cmd {{ font-size: 30px; color: #57d977; margin: 44px 0 32px; }}
  .cmd .p {{ color: #8affae; }}
  .tag {{
    display: inline-block; border: 2px solid #2fbf5a; color: #57d977;
    padding: 14px 26px; font-size: 26px; letter-spacing: 2px;
    margin-bottom: 44px; background: rgba(6,20,8,0.7);
  }}
  h1 {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 96px; font-weight: 800; line-height: 1.05;
    letter-spacing: -2px; margin-bottom: 48px;
  }}
  .hl-red {{ color: #ff4b3e; text-shadow: 0 0 34px rgba(255,75,62,0.45); }}
  .twist {{
    border: 2px solid #e6b93c; border-radius: 10px;
    padding: 36px 40px; margin-bottom: 44px;
    background: rgba(14,14,4,0.75);
  }}
  .twist .label {{ font-size: 24px; color: #b8dcb8; letter-spacing: 3px; margin-bottom: 18px; }}
  .twist .text {{
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 44px; font-weight: 700; line-height: 1.18; color: #f2f2ea;
  }}
  .hl-yellow {{ color: #f5c542; text-shadow: 0 0 30px rgba(245,197,66,0.35); }}
  .fuente {{
    display: inline-block; border: 2px solid #d94f3e; color: #ff8a75;
    padding: 12px 24px; font-size: 24px; letter-spacing: 2px;
    background: rgba(20,8,6,0.7);
  }}
  .punch {{
    position: absolute; left: 0; right: 0; bottom: 210px;
    text-align: center;
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 58px; font-weight: 800; letter-spacing: 1px;
    text-shadow: 0 0 24px rgba(0,0,0,0.9);
  }}
  .punch .h {{ display: block; font-family: inherit; font-size: 26px;
    color: #57d977; font-weight: 400; margin-top: 18px;
    font-family: "SF Mono", Menlo, Consolas, monospace; }}
  .brand {{
    position: absolute; left: 0; right: 0; bottom: 100px;
    display: flex; align-items: center; justify-content: center; gap: 18px;
    font-size: 30px; font-weight: 700; color: #e8f0e8;
  }}
  .brand .logo {{
    width: 54px; height: 54px; border-radius: 50%;
    background: linear-gradient(135deg, #6a2fbf, #2fbf5a);
    display: inline-block;
  }}
</style>
</head>
<body>
{rain}
<div class="titlebar">
  <span class="dot" style="background:#ff5f57"></span>
  <span class="dot" style="background:#febc2e"></span>
  <span class="dot" style="background:#28c840"></span>
  <span>~/ venbrax / tech / $ trace --topic={topic}</span>
  <span class="handle">{handle}</span>
</div>
<div class="card">
  <div class="cmd"><span class="p">$</span> trace --event --{topic}</div>
  <div class="tag">// {label} &nbsp;·&nbsp; {fecha}</div>
  <h1>{headline}</h1>
  <div class="twist">
    <div class="label">// {twist_label}</div>
    <div class="text">{twist}</div>
  </div>
  <div class="fuente">// FUENTE &nbsp;·&nbsp; {fuente}</div>
</div>
<div class="punch">{punch}<span class="h">{handle}</span></div>
<div class="brand"><span class="logo"></span> VenBraX</div>
</body>
</html>"""


def main():
    from content_engine import INSIGHTS_POOL, get_insight_of_day

    parser = argparse.ArgumentParser(description="VenBraX Visual Generator")
    parser.add_argument("--insight-id", help="ID del insight (default: insight del día)")
    parser.add_argument("--handle", default="@venbrax", help="Handle de la cuenta")
    parser.add_argument("--output", help="Ruta del HTML de salida")
    args = parser.parse_args()

    if args.insight_id:
        matches = [i for i in INSIGHTS_POOL if i["id"] == args.insight_id]
        if not matches:
            ids = ", ".join(i["id"] for i in INSIGHTS_POOL)
            raise SystemExit(f"Insight '{args.insight_id}' no existe. Disponibles: {ids}")
        insight = matches[0]
    else:
        insight = get_insight_of_day()

    html = generate_visual_html(insight, handle=args.handle)
    output = args.output or f"/tmp/venbrax-visual-{insight['id']}-{datetime.utcnow().strftime('%Y%m%d')}.html"
    with open(output, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[VISUAL] {insight['title']} → {output}")
    print("Render PNG: chromium --headless --screenshot=card.png --window-size=1080,1350 " + output)


if __name__ == "__main__":
    main()
