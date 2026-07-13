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

# Insights técnicos rotando por día — actualizar mensualmente.
# Los campos visual_* y fuente/punch alimentan visual_generator.py (tarjeta IG).
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
        "id": "ai-cost-inflation",
        "title": "Tu próxima computadora costará más — y la culpa es de la IA",
        "hook_stat": "Los precios de DRAM subieron 90-95% en un solo trimestre (Q1 2026)",
        "why": "los data centers de IA están absorbiendo la producción mundial de memoria y la RAM es ~35% del costo de una PC",
        "insight": "TrendForce proyecta que el mercado de memoria llegará a $1.28 billones (trillion USD) en 2027 impulsado por Agentic AI. Los fabricantes ya trasladan el costo: laptops y PCs suben de precio todo 2026. El hardware se encarece — pero tu factura de IA no tiene que hacerlo: prompt caching, modelos correctos por tarea y self-hosting recortan 60-90% del gasto.",
        "cta": "El hardware sube. Tu stack de IA no tiene que costarte más — audita tu gasto con VenBraX",
        "niches": ["AI Economics", "Cost Optimization", "Hardware"],
        "visual_label": "LA IA ENCARECE TU HARDWARE",
        "visual_headline": "Tu próxima **computadora** costará más.",
        "twist_label": "EL CULPABLE NO ES EL FABRICANTE",
        "twist": "Es la **inteligencia artificial**: los data centers absorben la memoria del mundo.",
        "fuente": "TRENDFORCE · TOM'S HARDWARE",
        "punch": "LA IA TIENE LA CULPA.",
    },
    {
        "id": "memory-squeeze-window",
        "title": "La ventana de compra de hardware se está cerrando",
        "hook_stat": "DRAM +58-63% y NAND +70-75% adicionales proyectados para Q2 2026",
        "why": "los cloud providers firmaron contratos de largo plazo que aseguran su suministro — el consumidor paga el ajuste",
        "insight": "TrendForce reporta que los CSPs (AWS, Google, Microsoft) blindaron su memoria vía acuerdos multianuales. Resultado: la oferta para consumo se reduce y los precios retail de notebooks suben todo el año. Si tu operación depende de hardware propio, comprar antes del próximo ajuste trimestral es decisión financiera, no técnica.",
        "cta": "¿Tu empresa planea renovar equipos? El timing importa más que el modelo — hablemos",
        "niches": ["AI Economics", "Hardware", "Strategy"],
        "visual_label": "GUERRA POR LA MEMORIA",
        "visual_headline": "La **memoria** del mundo ya tiene dueño.",
        "twist_label": "QUIÉN GANA REALMENTE",
        "twist": "Los **cloud providers** ya aseguraron su memoria. El ajuste lo pagas tú.",
        "fuente": "TRENDFORCE · BLOOMBERG",
        "punch": "COMPRA ANTES DEL PRÓXIMO AJUSTE.",
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

def get_insight_of_day(slot=0):
    day_of_year = datetime.utcnow().timetuple().tm_yday
    return INSIGHTS_POOL[(day_of_year * 5 + slot) % len(INSIGHTS_POOL)]

def format_for_platform(insight, platform):
    cfg = PLATFORMS[platform]
    style = cfg["style"]

    if style == "professional":  # LinkedIn
        content = f"""🚨 {insight['hook_stat']} — y {insight['why']}.

{insight['insight']}

💡 Lo que esto significa para tu stack:
Si estás construyendo con {', '.join(insight['niches'][:2])}, este insight cambia cómo diseñas tus sistemas.

{insight['cta']}

#{' #'.join([n.replace(' ', '') for n in insight['niches'][:cfg['hashtags']]])} #VenBraX #AIEngineering"""

    elif style == "punchy":  # Twitter/X
        hook = insight['hook_stat'][:100]
        content = f"""{hook}

Aquí el por qué: {insight['why'][:100]}

{insight['cta'][:80]}

#{' #'.join([n.replace(' ', '') for n in insight['niches'][:cfg['hashtags']]])}"""

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
    parser.add_argument("--json", action="store_true", help="Salida JSON pura (para n8n)")
    parser.add_argument("--visual", action="store_true", help="Genera además la tarjeta visual IG (HTML 1080x1350)")
    args = parser.parse_args()

    insight = get_insight_of_day()
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    platforms = [args.platform] if args.platform else list(PLATFORMS.keys())
    results = {}

    for platform in platforms:
        if args.use_claude and os.environ.get("ANTHROPIC_API_KEY"):
            content = generate_with_claude(insight, platform)
        else:
            content = format_for_platform(insight, platform)
        results[platform] = content

    visual_file = None
    if args.visual:
        from visual_generator import generate_visual_html
        visual_file = f"/tmp/venbrax-visual-{insight['id']}-{datetime.utcnow().strftime('%Y%m%d')}.html"
        with open(visual_file, "w", encoding="utf-8") as f:
            f.write(generate_visual_html(insight))

    if args.json:
        # Salida JSON pura por stdout — n8n la parsea con JSON.parse()
        print(json.dumps({
            "timestamp": ts,
            "insight_id": insight["id"],
            "insight_title": insight["title"],
            "posts": results,
            "visual_file": visual_file
        }, ensure_ascii=False))
        return results

    print(f"[{ts}] Insight del día: {insight['title']}")
    for platform, content in results.items():
        print(f"\n{'='*60}")
        print(f"PLATAFORMA: {platform.upper()}")
        print(f"CHARS: {len(content)}/{PLATFORMS[platform]['max_chars']}")
        print(f"{'='*60}")
        print(content)

    if visual_file:
        print(f"\n[VISUAL] Tarjeta IG generada: {visual_file}")
        print(f"[VISUAL] Render PNG: chromium --headless --screenshot=card.png --window-size=1080,1350 {visual_file}")

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


# Insights adicionales v3
INSIGHTS_POOL.extend([
    {"id":"fine-tuning-vs-rag","title":"Fine-tuning vs RAG: la decisión que nadie explica bien","hook_stat":"70% de proyectos eligen mal entre fine-tuning y RAG","why":"porque confunden problemas de conocimiento con problemas de comportamiento","insight":"Fine-tuning cambia COMO responde el modelo. RAG cambia QUE sabe. Dominio estrecho o tono especifico: fine-tuning. Datos frescos, privados o cambiantes: RAG. Error mas caro: fine-tunear para dar conocimiento reciente (se desactualiza en semanas).","cta":"Estas usando la herramienta correcta para tu problema de IA?","niches":["AI Engineering","LLMs","MLOps"]},
    {"id":"llm-hallucinations","title":"Por que los LLMs mienten con confianza","hook_stat":"LLMs alucinan en el 20% de respuestas tecnicas sin grounding externo","why":"porque el entrenamiento optimiza texto plausible, no texto verdadero","insight":"Las alucinaciones no son un bug: son una caracteristica del entrenamiento por siguiente token. Soluciones reales: RAG para anclar en hechos, temperature=0, citation grounding. Lo que NO funciona: pedirle que sea honesto en el prompt.","cta":"Tienes un sistema de deteccion de alucinaciones en produccion?","niches":["LLMs","AI Engineering","Prompting"]},
    {"id":"multimodal-ai","title":"La IA ya no solo lee texto: la revolucion multimodal","hook_stat":"El 60% del conocimiento empresarial esta atrapado en imagenes y PDFs","why":"porque hasta 2023 los modelos solo procesaban texto plano","insight":"GPT-4o, Gemini y Claude son multimodales. Casos de uso reales: analisis de documentos escaneados, descripcion de productos, moderacion visual, analisis de screenshots de dashboards. Una imagen aporta mas contexto que 1000 tokens de descripcion.","cta":"Que proceso manual podrias automatizar con vision por IA esta semana?","niches":["Multimodal","AI Engineering","Automatizacion"]},
    {"id":"ai-agents-vs-rpa","title":"Agentes IA vs RPA: el fin de la automatizacion fragil","hook_stat":"El 68% de implementaciones RPA necesitan mantenimiento mayor antes de 18 meses","why":"porque el RPA se rompe con cada cambio de UI y no maneja excepciones","insight":"RPA automatiza procesos exactos en interfaces estables. Agentes IA entienden el objetivo, adaptan la estrategia y manejan excepciones. El costo de mantenimiento RPA supera al de construccion — los agentes escalan donde el RPA colapsa.","cta":"Cuanto tiempo pasas manteniendo automatizaciones fragiles?","niches":["Automatizacion","AI Agents","n8n"]},
    {"id":"embedding-models","title":"Los embeddings son el alma del RAG","hook_stat":"La diferencia entre modelos de embeddings puede ser 30 puntos en recall al top 5","why":"porque el retrieval determina que informacion llega al LLM para responder","insight":"Puedes tener el LLM mas potente — si tus embeddings son malos, tu RAG devuelve basura. Para espanol: modelos multilingual (multilingual-e5-large) superan a los anglófonos. Siempre benchmarkea en TUS datos, no en rankings publicos.","cta":"Has benchmarkeado tu modelo de embeddings contra alternativas?","niches":["RAG","LLMs","AI Engineering"]},
    {"id":"context-window-wars","title":"1 millon de tokens de contexto: promesa o trampa?","hook_stat":"El recall de informacion al centro de contextos largos cae hasta 40%","why":"por el efecto lost-in-the-middle: los modelos recuerdan inicio y final pero olvidan el centro","insight":"La carrera de contexto largo termino pero nadie te dice la trampa: en contextos de 100K+ tokens la informacion central se pierde. Para documentos largos, RAG con chunks sigue siendo mas efectivo y barato.","cta":"Estas pagando por contexto largo cuando RAG seria mas barato?","niches":["LLMs","RAG","AI Engineering"]},
    {"id":"ai-code-quality","title":"GitHub Copilot genera codigo. Tu eres responsable de el.","hook_stat":"40% del codigo generado por IA en produccion tiene vulnerabilidades de seguridad","why":"porque el codigo parece correcto y baja la guardia del revisor","insight":"Estudios de Stanford muestran que desarrolladores con Copilot producen mas vulnerabilidades CWE que sin el. El codigo parece correcto — ese es el peligro. Nunca hagas merge de codigo IA sin review igual de riguroso que codigo humano.","cta":"Tu equipo tiene proceso de revision para codigo generado por IA?","niches":["DevSecOps","AI Engineering","Code Quality"]},
    {"id":"open-source-vs-closed","title":"Llama 3 vs GPT-4: cuando el open-source es suficiente","hook_stat":"Open-source LLMs alcanzan el 90% del rendimiento en tareas especificas","why":"porque los modelos cerrados ya no tienen el monopolio de la calidad","insight":"Open-source gana cuando: datos privados, fine-tuning profundo, volumen que hace las APIs prohibitivas. GPT-4/Claude ganan cuando: razonamiento complejo, multimodalidad critica, necesitas el mejor resultado sin optimizar costo.","cta":"Calculaste cuando el open-source te da breakeven vs APIs de pago?","niches":["Open Source","LLMs","MLOps"]},
    {"id":"ai-production-failure","title":"Por que el 80% de proyectos de IA nunca llegan a produccion","hook_stat":"Solo 1 de cada 5 proyectos de IA empresariales llega a produccion real","why":"porque el prototipo resuelve el problema facil y produccion revela el problema real","insight":"Las 5 razones reales: 1) Data drift. 2) Latencia subestimada. 3) Sin monitoring. 4) Integration hell con sistemas legados. 5) Expectativas desalineadas. El exito en IA empieza en produccion, no en el notebook.","cta":"Tu proyecto de IA tiene plan de monitoring post-deploy?","niches":["MLOps","AI Engineering","Produccion"]},
    {"id":"latency-cost-quality","title":"El triangulo imposible de la IA: velocidad, costo y calidad","hook_stat":"Empresas desperdician 60% de presupuesto en IA usando el mismo modelo para todo","why":"porque no implementan routing inteligente segun la complejidad de cada tarea","insight":"En IA generativa solo puedes optimizar 2 de 3: velocidad, costo, calidad. Solucion: routing inteligente. Tareas simples a modelo pequeno. Tareas complejas a modelo grande. Resultado: 60-70% reduccion de costos sin perder calidad percibida.","cta":"Tienes routing inteligente o usas el mismo modelo para todo?","niches":["AI Engineering","LLMs","Optimizacion"]},
    {"id":"function-calling-power","title":"Function calling: el puente entre LLMs y el mundo real","hook_stat":"Agentes con function calling resuelven 3 veces mas tareas complejas que prompting puro","why":"porque conectan el razonamiento del LLM con acciones reales en sistemas externos","insight":"Function calling permite al LLM decidir cuando usar herramientas: buscar internet, ejecutar codigo, consultar APIs. Error comun: demasiadas herramientas generan confusion. 5-10 tools bien definidas supera a 50 ambiguas.","cta":"Tus agentes tienen las herramientas correctas o demasiadas?","niches":["AI Agents","LLMs","AI Engineering"]},
    {"id":"prompt-injection-risk","title":"Prompt injection: el ataque que todos ignoran hasta que es tarde","hook_stat":"El 43% de aplicaciones con agentes IA son vulnerables a prompt injection","why":"porque los desarrolladores tratan el input del usuario como texto de confianza","insight":"Prompt injection es el OWASP Top 1 de la era de agentes. Tipos: directo (usuario ataca el system prompt), indirecto (datos externos contaminados). Defensa: separacion estricta datos/instrucciones, principio de minimo privilegio para herramientas.","cta":"Tienes un threat model para tus agentes de IA?","niches":["Seguridad IA","AI Agents","DevSecOps"]},
    {"id":"data-flywheel","title":"El data flywheel: tus datos valen mas que tu modelo","hook_stat":"El 89% del valor competitivo de IA viene de datos propietarios, no del modelo base","why":"porque los modelos base son commodity pero los datos unicos no lo son","insight":"Data flywheel: mas usuarios generan mas datos que mejoran el modelo que atrae mas usuarios. Para startups: el moat de datos se construye desde el dia 1. El modelo de IA es commodity en 2025. Los datos propietarios no.","cta":"Estas construyendo tu flywheel de datos o solo usando modelos de terceros?","niches":["Estrategia IA","Data Strategy","Startups"]},
    {"id":"llm-benchmarks-truth","title":"Los benchmarks de LLMs mienten","hook_stat":"El 78% de los rankings de LLMs no se correlacionan con rendimiento en casos reales","why":"porque los modelos son evaluados en los mismos datasets en que fueron entrenados","insight":"MMLU mide conocimiento general, no razonamiento en tu dominio. La evaluacion que importa: construye un eval set con 50-100 ejemplos REALES de tu caso de uso con respuestas verificadas por humanos. Todo lo demas es marketing.","cta":"Tienes un eval set propio o confias en los benchmarks publicos?","niches":["LLMs","AI Engineering","Evaluacion"]},
    {"id":"startup-ai-moat","title":"Cual es el foso real de tu startup de IA?","hook_stat":"El 91% de startups de IA no tienen ventaja competitiva mas alla del modelo base","why":"porque confunden usar GPT-4 con tener una ventaja competitiva real","insight":"Los 4 fosos reales: 1) Datos propietarios. 2) Distribucion. 3) Integracion profunda en workflows criticos. 4) Network effects. Lo que NO es un foso: el modelo base, el prompt, la UI. Si OpenAI puede replicarte manana, no tienes foso.","cta":"Cual de los 4 fosos estas construyendo activamente?","niches":["Startups","Estrategia IA","Venture"]},
    {"id":"agents-orchestration","title":"Orquestar agentes IA es como dirigir una orquesta caotica","hook_stat":"Sistemas multi-agente mal orquestados fallan 4 veces mas que agentes individuales","why":"porque la complejidad de coordinacion crece exponencialmente con el numero de agentes","insight":"Patrones probados: Supervisor-Worker, Pipeline, Parallel. Regla de oro: cada agente debe tener un unico objetivo claro y herramientas minimas necesarias. Los bloqueos por dependencias circulares son el error mas comun.","cta":"Que patron de orquestacion usas en tus sistemas multi-agente?","niches":["AI Agents","AI Engineering","n8n"]},
    {"id":"tool-use-patterns","title":"5 patrones de tool use que necesitas dominar","hook_stat":"Agentes con tool use estructurado completan 5 veces mas tareas complejas correctamente","why":"porque saber cuando y como usar herramientas es tan importante como tenerlas","insight":"Los 5 patrones esenciales: 1) Search-then-synthesize. 2) Code-then-execute. 3) Plan-then-act. 4) Reflect-then-retry. 5) Delegate-then-merge. Mezclarlos incorrectamente multiplica errores en cascada.","cta":"Cuantos de estos 5 patrones implementas en tus agentes?","niches":["AI Agents","AI Engineering","Automatizacion"]},
    {"id":"inference-cost-analysis","title":"GPU cloud vs inference APIs: el analisis que nadie hace","hook_stat":"Empresas gastan 40% mas de lo necesario en inferencia por no hacer este calculo","why":"porque comparan costos sin considerar utilizacion real de GPU ni volumen de tokens","insight":"Breakeven: A100 a 3 dolares por hora produce 300K tokens por hora igual a 1 centavo por mil tokens. OpenAI GPT-4o cuesta entre 0.5 y 1.5 centavos por mil. Para startups con menos de 10M tokens al mes las APIs ganan claramente.","cta":"Calculaste tu breakeven de tokens para justificar infraestructura propia?","niches":["MLOps","AI Engineering","Cloud"]},
])

if __name__ == "__main__":
    main()
