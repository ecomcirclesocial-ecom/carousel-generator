STYLE_EXTRACTION_PROMPT = """Analiza estas imágenes de slides de un carrusel de Instagram. Vas a extraer el "estilo visual" del creador para que después yo pueda replicarlo en otros carruseles.

Las imágenes están en estos paths absolutos (léelas con tu Read tool):

{image_paths}

Analízalas todas y devuelve UN SOLO objeto JSON (sin texto antes ni después, sin markdown, sin ```) con este schema exacto:

{{
  "palette": {{
    "background": "#hex",
    "text_primary": "#hex",
    "text_secondary": "#hex",
    "accent": "#hex"
  }},
  "typography": {{
    "family_hint": "serif clásica | sans-serif limpia | mono | display",
    "weight": "regular | medium | bold | black",
    "size_ratio": 0.08,
    "letter_spacing": "normal | tight | wide",
    "case": "normal | uppercase | mixed"
  }},
  "layout": {{
    "text_position": "centro | superior | inferior | izquierda | derecha",
    "text_density": "muy baja | baja | media | alta",
    "alignment": "centro | izquierda | derecha",
    "padding": "minimal | comfortable | generous",
    "uses_imagery": true,
    "imagery_style": "fotos | ilustraciones | solo texto | mixto"
  }},
  "structure": {{
    "slide_count": 9,
    "slide_1_role": "qué cumple el slide 1",
    "middle_slides_pattern": "patrón de los slides intermedios",
    "last_slide_role": "qué cumple el último slide"
  }},
  "vibe": "una frase descriptiva del feel general",
  "voice_hint": "tono del copy observado"
}}

Reglas:
- Sé PRECISO con los colores hex (mira las imágenes reales).
- size_ratio = altura_aprox_del_texto / altura_total_del_slide. Estima entre 0.04 y 0.20.
- Si hay un solo color de texto, repite el hex en text_primary y text_secondary.
- Si no hay color de acento claro, usa el hex del texto principal.
- Tu respuesta debe ser SOLO el JSON. Nada más."""


COPY_GENERATION_PROMPT = """Genera el copy de un carrusel de Instagram para cualquier nicho usando una estructura probada.

# Estilo del creador a replicar
```json
{style_guide}
```

# Tema
{tema}

# CTA
{cta_text}

# Idioma
{idioma}

# Estructura obligatoria (9 slides exactos)

1. **Hook** — máximo 6 palabras, idea que rompa patrón. Provoca curiosidad o desafía un supuesto.
2. **Dolor** — empieza por "Si llevas..." o frase similar que reconozca el dolor del lector. 1 frase corta, directo.
3-7. **Valor** (5 slides) — uno por punto. Cada slide tiene:
   - **título corto** (máx 6 palabras, el nombre del punto)
   - **body**: 2 líneas que explican + 1 ejemplo concreto
8. **Recap** — lista numerada de los 5 puntos del valor. Cierra con "Guarda esto."
9. **CTA** — UNA sola acción. "Comenta {cta_word} y te lo envío" (o variación natural).

# Reglas de voz
- Idioma: {idioma}
- Voz: directa, sin emojis, "menos es más"
- Sin clichés ni frases de gurú genérico
- Habla de tú a tú al lector
- Replica el `voice_hint` y el `vibe` del style guide

# Reglas de keywords
En cada slide de valor (3-7) y en el dolor (2), envuelve 2-4 palabras o frases CORTAS importantes con `**doble asterisco**`. Esas palabras se resaltarán en color de acento. Ejemplos: `**3 días**`, `**valida con datos**`, `**tu primera venta**`.

# Schema de respuesta

Devuelve UN SOLO objeto JSON (sin texto antes ni después, sin markdown, sin ```) con este schema exacto:

{{
  "tema": "{tema}",
  "cta_word": "{cta_word}",
  "idioma": "{idioma}",
  "slides": [
    {{ "n": 1, "role": "hook",  "headline": "...", "body": "" }},
    {{ "n": 2, "role": "pain",  "headline": "Si llevas...", "body": "..." }},
    {{ "n": 3, "role": "value", "title": "Nombre del punto 1", "body": "Línea 1.\\nLínea 2.\\n\\nEjemplo: ..." }},
    {{ "n": 4, "role": "value", "title": "Nombre del punto 2", "body": "..." }},
    {{ "n": 5, "role": "value", "title": "Nombre del punto 3", "body": "..." }},
    {{ "n": 6, "role": "value", "title": "Nombre del punto 4", "body": "..." }},
    {{ "n": 7, "role": "value", "title": "Nombre del punto 5", "body": "..." }},
    {{ "n": 8, "role": "recap", "headline": "Recapitulando", "items": ["Punto 1", "Punto 2", "Punto 3", "Punto 4", "Punto 5"] }},
    {{ "n": 9, "role": "cta",   "headline": "...", "body": "Comenta \\"{cta_word}\\" y te lo envío" }}
  ]
}}

Tu respuesta debe ser SOLO el JSON. Nada más."""
