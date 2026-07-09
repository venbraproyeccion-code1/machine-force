"""
VenBraX Content Engine v2
Genera contenido de alto impacto para 5 plataformas sociales.
Sin material genérico — todo basado en insights técnicos reales.

Uso:
  python content_engine.py                    # genera post del día
  python content_engine.py --platform linkedin # plataforma específica
  python content_engine.py --preview          # muestra sin publicar

Requiere: ANTHROPIC_API_KEY en env
"""
import os, sys, json, argparse, hashlib
from datetime import datetime, timedelta

# ── Config ─────────────────────────────────────────────────────────────────────
PLATFORMS = {
    "linkedin":  {"max_chars": 3000, "hashtags": 5, "style": "professional"},
    "twitter":   {"max_chars": 280,  "hashtags": 3, "style": "punchy"},
    "instagram": {"max_chars": 2200, "hashtags": 30, "style": "visual_hook"},
    "tiktok":    {"max_chars": 2200, "hashtags": 10, "style": "video_script"},
    "threads":   {"max_chars": 500,  "hashtags": 5,  "style": "conversational"},
}

# 5 insights técnicos rotando por semana — actualizar mensualmente
INSIGHTS_POOL = [
    {
        "id": "ai-agent-loops",
        "title": "Los loops de agentes IA que nadie te explica",
        "hook_stat": "87% de implementaciones de agentes IA fallan",
        "why": "porque el loop de error-handling es incorrecto",
        "insight": "El secret: define el estado de 'done' ANTES del loop, no dentro. Los agentes sin exit condition clara entran en bucles infinitos costosos.",
        "cta": "¿Cuánto te cuesta cada llamada API fallida?",
        "niches": ["AI Engineering", "LLMs", "DevOps"],
    },
    {
        "id": "rag-chunking",
        "title": "Por qué tu RAG da respuestas incorrectas",
        "hook_stat": "La mayoría de RAGs fallan por chunking mal configurado",
        "why": "los chunks rompen el contexto semántico",
        "insight": "Chunk size ideal: 512 tokens con 128 de overlap. Menos → pierde contexto. Más → dilución semántica. Usa semantic chunking si el documento tiene secciones muy distintas.",
        "cta": "Comparte tu chunk size actual — lo revisamos",
        "niches": ["AI Engineering", "Vector DB", "LLMs"],
    },
    {
        "id": "n8n-vs-make",
        "title": "n8n vs Make: La decisión correcta para 2025",
        "hook_stat": "n8n self-hosted = $0/mes para 100k ejecuciones",
        "why": "Make cobra por operación desde la primera",
        "insight": "n8n wins si: tienes VM propia, necesitas código custom en nodos, o manejas datos sensibles. Make wins si: quieres setup en 10 min y presupuesto fijo.",
        "cta": "¿Qué automatizas hoy con Make que podrías mover a n8n?",
        "niches": ["Automation", "No-Code", "DevOps"],
    },
    {
        "id": "vector-db-battle",
        "title": "Pinecone vs Weaviate vs pgvector: benchmark real",
        "hook_stat": "pgvector en Supabase gratuito supera a Pinecone Starter",
        "why": "en colecciones < 1M vectores el latency es comparable",
        "insight": "Para < 100k vectores: pgvector + Supabase (gratis). 100k-10M: Weaviate cloud o self-hosted. 10M+: Pinecone enterprise. La clave es tu volumen de vectores, no los features.",
        "cta": "¿Cuántos vectores manejas en producción?",
        "niches": ["Vector DB", "AI Engineering", "Database"],
    },
    {
        "id": "prompt-caching",
        "title": "Prompt caching: el truco que reduce costos de Claude 90%",
        "hook_stat": "Cache hit en Claude = 90% descuento en tokens",
        "why": "los prompts del sistema se cobran completos cada vez sin cache",
        "insight": "Agrega <cache_control> al system prompt. Requiere el mismo prompt exacto en < 5 minutos. Ideal para: RAG con contexto fijo, agentes con instrucciones largas, workflows repetitivos.",
        "cta": "¿Ya usas prompt caching? ¿Cuánto ahorras?",
        "niches": ["AI Engineering", "LLMs", "Cost Optimization"],
    },
]

def get_insight_of_day():
    day_of_year = datetime.utcnow().timetuple().tm_yday
    return INSIGHTS_POOL[day_of_year % len(INSIGHTS_POOL)]

def format_for_platform(insight, platform):
    cfg = PLATFORMS[platform]
    style = cfg["style"]

    if style == "professional":  # LinkedIn
        content = f"""🚨 {insight['hook_stat']} — y {insight['why']}.

{insight['insight']}

💡 Lo que esto significa para tu stack:
Si estás construyendo con {', '.join(insight['niches'][:2])}, este insight cambia cómo diseñas tus sistemas.

{insight['cta']}

#{'  #'.join(insight['niches'][:cfg['hashtags']])} #VenBraX #AIEngineering"""

    elif style == "punchy":  # Twitter/X
        hook = insight['hook_stat'][:100]
        content = f"""{hook}

Aquí el por qué: {insight['why'][:100]}

{insight['cta'][:80]}

#{' #'.join(insight['niches'][:cfg['hashtags']])}"""

    elif style == "visual_hook":  # Instagram
        content = f"""⚡ {insight['hook_stat']}

El problema: {insight['why']}.

La solución 👇

{insight['insight']}

——
{insight['cta']}

{'  '.join(['#' + n.replace(' ', '') for n in insight['niches']])} #AI #Tech #Startup #Automation #VenBraX #TechTips #ArtificialIntelligence #MachineLearning #DevOps #Productivity"""

    elif style == "video_script":  # TikTok
        content = f"""🎬 SCRIPT — "{insight['title']}"

[HOOK - 3s]
"{insight['hook_stat']}"

[PROBLEMA - 10s]
¿Por qué? {insight['why']}.

[SOLUCIÓN - 20s]
{insight['insight']}

[CTA - 5s]
{insight['cta']}

HASHTAGS: #{' #'.join([n.replace(' ', '') for n in insight['niches'][:cfg['hashtags']]])} #VenBraX #AITips"""

    else:  # Threads / conversational
        content = f"""{insight['hook_stat']}.

{insight['why']}.

{insight['cta']}

#AI #Tech"""

    return content[:cfg["max_chars"]]

def generate_with_claude(insight, platform):
    """Genera versión mejorada usando Claude API."""
    try:
        import anthropic
        client = anthropic.Anthropic()
        cfg = PLATFORMS[platform]

        prompt = f"""Eres el content strategist de VenBraX/VenBraTech.
Crea un post para {platform.upper()} basado en este insight técnico REAL.

INSIGHT: {insight['title']}
DATO: {insight['hook_stat']} — {insight['why']}
CONTENIDO: {insight['insight']}
CTA: {insight['cta']}
NICHOS: {', '.join(insight['niches'])}

REGLAS:
- Máximo {cfg['max_chars']} caracteres
- Estilo: {cfg['style']}
- Sin material genérico — datos concretos únicamente
- Voz directa, sin relleno
- En español técnico
- Incluir {cfg['hashtags']} hashtags relevantes
- Terminar con el CTA

Devuelve SOLO el post, sin comentarios."""

        msg = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text
    except ImportError:
        print("[WARN] anthropic no instalado — usando template base")
        return format_for_platform(insight, platform)
    except Exception as e:
        print(f"[WARN] Claude API error: {e} — usando template base")
        return format_for_platform(insight, platform)

def main():
    parser = argparse.ArgumentParser(description="VenBraX Content Engine v2")
    parser.add_argument("--platform", choices=list(PLATFORMS.keys()), help="Plataforma específica")
    parser.add_argument("--preview", action="store_true", help="Solo muestra, no publica")
    parser.add_argument("--use-claude", action="store_true", help="Usa Claude API para mejorar")
    args = parser.parse_args()

    insight = get_insight_of_day()
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    print(f"[{ts}] Insight del día: {insight['title']}")

    platforms = [args.platform] if args.platform else list(PLATFORMS.keys())
    results = {}

    for platform in platforms:
        if args.use_claude and os.environ.get("ANTHROPIC_API_KEY"):
            content = generate_with_claude(insight, platform)
        else:
            content = format_for_platform(insight, platform)

        results[platform] = content
        print(f"\n{'='*60}")
        print(f"PLATAFORMA: {platform.upper()}")
        print(f"CHARS: {len(content)}/{PLATFORMS[platform]['max_chars']}")
        print(f"{'='*60}")
        print(content)

    if not args.preview:
        output_file = f"/tmp/venbrax-content-{datetime.utcnow().strftime('%Y%m%d-%H%M')}.json"
        with open(output_file, "w") as f:
            json.dump({
                "timestamp": ts,
                "insight_id": insight["id"],
                "posts": results
            }, f, ensure_ascii=False, indent=2)
        print(f"\n[GUARDADO] {output_file}")

    return results

if __name__ == "__main__":
    main()
