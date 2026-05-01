# carousel-generator

> Genera carruseles de Instagram virales en cualquier nicho. Replica el estilo visual de cualquier creador desde un post o handle de su feed.

CLI Python que combina **scraping con Apify** + **Claude Code (vision + texto)** + **HTML/CSS** + **Playwright** para producir 9 slides PNG (1080×1350) listos para publicar.

Estructura de copy probada: **Hook → Dolor → Valor (×5) → Recap → CTA**.

---

## Demo

| Hook | Dolor | Valor |
|---|---|---|
| ![](examples/dropshipping/slide-01.png) | ![](examples/dropshipping/slide-02.png) | ![](examples/dropshipping/slide-04.png) |

| Recap | CTA |
|---|---|
| ![](examples/dropshipping/slide-08.png) | ![](examples/dropshipping/slide-09.png) |

Ejemplo completo en [`examples/dropshipping/`](examples/dropshipping).

---

## Cómo funciona

```
[Apify scrapea post/creador] → [Claude analiza estilo] → [Preset JSON]
                                                              ↓
[CTA + tema + idioma + foto opcional] → [Claude genera copy] → [HTML+CSS] → [Playwright PNGs]
```

1. **Scrapeas** un post de Instagram o el feed de un creador con Apify
2. **Claude (vision)** extrae paleta, tipografía, layout, vibra → guarda como **preset JSON editable**
3. Le pasas un **tema + CTA + idioma + foto opcional**
4. **Claude genera el copy** con la estructura Hook/Dolor/Valor/Recap/CTA y marca palabras clave
5. **HTML/CSS + Playwright** renderiza 9 PNGs 1080×1350 con el estilo del preset

---

## Requisitos

- Python 3.13 + venv
- [Claude Code](https://claude.com/code) instalado (el binario `claude` en PATH) — usa tu plan Max sin costo extra de tokens
- Token de [Apify](https://console.apify.com/) (free tier $5/mes alcanza para ~200 presets)
- Chromium para Playwright

---

## Setup

```bash
git clone https://github.com/ecomcirclesocial-ecom/carousel-generator.git
cd carousel-generator

# Crear venv (con uv o python -m venv)
uv venv
source .venv/bin/activate

# Instalar deps
uv pip install -r requirements.txt
playwright install chromium

# Configurar token de Apify
cp .env.example .env
# Edita .env y pega tu APIFY_TOKEN
```

Verifica que `claude` está en PATH:

```bash
which claude && claude --version
```

---

## Uso

### 1. Crear un preset desde un post de referencia

```bash
python cli.py preset create \
  --post https://www.instagram.com/p/<shortcode>/ \
  --name <slug>
```

O desde un creador (top 10 carruseles de su feed):

```bash
python cli.py preset create --creator <handle> --name <slug>
```

### 2. Listar / ver / borrar presets

```bash
python cli.py preset list
python cli.py preset show <slug>
python cli.py preset delete <slug>
```

### 3. Generar un carrusel

```bash
python cli.py generate \
  --preset <slug> \
  --tema "Errores en dropshipping" \
  --cta "DROPI" \
  --photo path/to/your-photo.jpg \
  --idioma es \
  --handle "@tu_handle"
```

Salida en `output/<tema-slug>/slide-01.png ... slide-09.png` + `copy.json`.

### 4. Preview en navegador

```bash
python cli.py preview --dir output/<tema-slug>
```

Abre una galería con los 9 slides.

---

## Estructura de copy

Los 9 slides siguen una fórmula probada:

| # | Rol | Qué cumple |
|---|---|---|
| 1 | **Hook** | Máx 6 palabras. Idea que rompe patrón. |
| 2 | **Dolor** | "Si llevas X meses sin..." Reconoce el dolor del lector. |
| 3-7 | **Valor** | 5 puntos. Cada uno: título corto + 2 líneas + 1 ejemplo concreto. |
| 8 | **Recap** | Lista numerada de los 5 puntos. "Guarda esto." |
| 9 | **CTA** | UNA sola acción. "Comenta X y te lo envío." |

Claude marca las palabras clave con `**doble asterisco**` y la herramienta las renderiza en color de acento.

---

## Estilo visual

El template `diferencia_foto.html` replica los elementos típicos de carruseles virales:

- Subrayado naranja "hand-drawn" en headlines
- Tarjeta tipo terminal con texto mono y palabras coloreadas
- Carpetas azules estilo macOS para portadas
- Sparkle/asterisco naranja
- Etiquetas en cursiva (Caveat) tipo nota a mano
- Foto opcional como fondo con overlay degradado

Si quieres añadir tu propio template visual, ver [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Costos aproximados

| Servicio | Costo por carrusel |
|---|---|
| Apify (scraping de 1 post) | ~$0.025 (free tier $5/mes alcanza para ~200) |
| Claude Code (copy + análisis) | $0 — usa tu plan Max via subprocess |
| **Total** | **~$0.025** |

---

## Skill de Claude Code

Si usas Claude Code, hay un skill que orquesta todo el flujo:

```bash
mkdir -p ~/.claude/skills/carrusel
# Copia SKILL.md desde este repo a esa carpeta
```

Después invocas con `/carrusel` desde cualquier sesión y te pregunta tema, CTA, preset, foto.

---

## Roadmap

- [ ] Templates como plugins (carga automática desde `templates/`)
- [ ] Multi-foto: 1 foto por slide
- [ ] Generación de fotos con Nano Banana (Gemini 2.5 Flash Image) cuando no se pase `--photo`
- [ ] Pinterest scraper como fuente de referencia visual
- [ ] Variantes A/B del hook (3 versiones del slide 1)
- [ ] Re-render parcial: `--regenerate-slide N`
- [ ] Posicionamiento dinámico que evita el sujeto en la foto

---

## Licencia

MIT — ver [LICENSE](LICENSE).

## Créditos

Construido por [Nain Guevara](https://www.instagram.com/nain_guevara/) (fundador de [Ecom Circle](https://ecomcircle.co)) con Claude Code.

Estructura de copy inspirada en carruseles virales de Instagram. Templates visuales inspirados en el estilo del creador "diferencia" — el preset inicial replica su estética.
