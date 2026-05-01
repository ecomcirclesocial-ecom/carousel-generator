---
name: carrusel
description: Genera carruseles de Instagram virales con estructura Hook→Dolor→Valor→Recap→CTA replicando el estilo visual de cualquier creador. Use when the user asks to "generar carrusel", "carrusel para Instagram", "post para IG", "hacer un carrusel", or anything related to generating Instagram carousel slides.
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
---

# Carrusel Generator

Skill para generar carruseles de Instagram (1080×1350 PNGs) con la estructura probada Hook → Dolor → Valor (×5) → Recap → CTA, replicando el estilo visual de cualquier creador a partir de un post o handle de Instagram.

**Repo:** https://github.com/ecomcirclesocial-ecom/carousel-generator
**CLI path:** `/Users/nainguevara/Desktop/Second brain/labs/carousel-generator`

## Cuándo invocar este skill

- "Generar un carrusel sobre X"
- "Hacer un post para Instagram sobre Y"
- "Quiero un carrusel viral de [tema]"
- "Replicar el estilo de [creador] con un carrusel sobre [tema]"

## Workflow

### Paso 1 — Validar setup

Ejecuta:
```bash
test -f "/Users/nainguevara/Desktop/Second brain/labs/carousel-generator/.env" && echo "OK env" || echo "FALTA .env"
which claude
```

Si falta `.env`, indícale al usuario que copie de `ecom-circle-web/.env.local` el `APIFY_TOKEN` (y opcionalmente `GEMINI_API_KEY`).

### Paso 2 — Recopilar inputs con AskUserQuestion

Pregunta al usuario:

1. **Tema** del carrusel (campo libre, ej: "errores en dropshipping")
2. **Palabra del CTA** (ej: "DROPI", "GUIA", "SCRIPT") — qué deben comentar para recibir lo prometido
3. **Preset de estilo**: lista los disponibles primero con:
   ```bash
   cd "/Users/nainguevara/Desktop/Second brain/labs/carousel-generator" && source ../.venv/bin/activate && python cli.py preset list
   ```
   Si no hay presets o el usuario quiere uno nuevo, pregúntale por una URL de post de Instagram o un handle de creador y créalo:
   ```bash
   python cli.py preset create --post <URL> --name <slug>
   # o
   python cli.py preset create --creator <handle> --name <slug>
   ```
4. **Foto de fondo**: 3 opciones
   - **Generar con Nano Banana** (default si no tiene foto propia) → flag `--generate-photo` (genera una foto contextual al tema con Gemini 2.5 Flash Image, ~$0.04)
   - **Foto propia** → pídele el path absoluto, va con flag `--photo <path>`
   - **Sin foto** → fondo plano, omite ambos flags
5. **Idioma**: español (default) o inglés.

### Paso 3 — Generar

```bash
cd "/Users/nainguevara/Desktop/Second brain/labs/carousel-generator"
source ../.venv/bin/activate
python cli.py generate \
  --preset <preset> \
  --tema "<tema>" \
  --cta "<CTA_WORD>" \
  [--photo <path> | --generate-photo] \
  --idioma <es|en> \
  --handle "@nain_guevara"
```

**Costo aproximado por carrusel**:
- Solo HTML+texto: ~$0 (Apify una sola vez al crear preset)
- Con `--generate-photo`: ~$0.04 (Nano Banana)
- Con `--photo` propia: ~$0

El comando demora ~30-60 segundos (Claude genera el copy + Playwright renderiza 9 slides).

### Paso 4 — Mostrar y abrir preview

Cuando termina, lee el output del comando para extraer el path del directorio generado y ejecuta:

```bash
python cli.py preview --dir <output_dir>
```

Esto abre los 9 slides en el navegador en grid. El usuario puede aprobar o pedir regenerar.

## Notas

- **Costo aproximado**: $0.025 (Apify scraping de 1 post) + $0 IA (usa el plan Max de Claude Code via subprocess al binario `claude`).
- **Estructura fija**: 9 slides. Hook (1) + Dolor (1) + Valor (5) + Recap (1) + CTA (1).
- **Cualquier nicho**: el prompt está optimizado para servir cualquier tema — dropshipping, fitness, finanzas personales, productividad, etc.
- **Auto-keyword highlight**: Claude marca palabras clave con `**bold**` y se renderizan en color de acento en cada slide.

## Si el usuario quiere modificar manualmente

- **Editar copy**: `output/<tema-slug>/copy.json` está disponible. Si edita y quiere re-renderizar:
  ```bash
  python cli.py render --preset <name> --copy <copy.json>
  ```
  *(comando aún no implementado al cierre — mencionarlo solo si existe)*
- **Editar preset**: `presets/<name>.json` es JSON editable. Cambiar paleta, tipografía, etc., y re-generar.
