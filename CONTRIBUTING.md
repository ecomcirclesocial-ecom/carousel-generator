# Contributing

¡Bienvenido! Este proyecto crece con la comunidad. Ideas para aportar:

## Tipos de contribución

### 1. Templates visuales nuevos

Cada estilo de creador puede ser un template propio. Para aportar uno:

1. Crea `templates/<nombre>.html` siguiendo la convención de variables Jinja2 del template existente (`templates/diferencia_foto.html`).
2. Define los 5 roles: `hook`, `pain`, `value`, `recap`, `cta`.
3. Añade screenshots de ejemplo en `examples/<nombre>/`.
4. Documenta tu template en una sección del README.

### 2. Presets de creadores

Si scrapeaste un creador y el preset quedó bueno, súbelo a `presets/community/<creador>.json`.

⚠️ **No subas presets con datos personales o URLs privadas.**

### 3. Mejoras al pipeline

Issues abiertas que necesitan trabajo:

- Multi-foto (1 por slide)
- Generación con Nano Banana cuando no hay `--photo`
- Pinterest scraper
- Posicionamiento dinámico que evita al sujeto en la foto
- Variantes A/B del hook

### 4. Bug reports

Usa el [issue template](.github/ISSUE_TEMPLATE/bug.md). Incluye:
- Sistema operativo
- Versión de Python
- Comando exacto que falló
- Salida del error
- Screenshots si es visual

## Convenciones

- **Idioma**: código en inglés, comentarios y docstrings en español
- **Imports**: módulos primero, después third-party, después locales
- **Dependencias nuevas**: justificarlas en el PR
- **Sin secrets**: nunca commitees `.env`, tokens, ni assets personales (fotos)

## Setup de desarrollo

```bash
git clone https://github.com/ecomcirclesocial-ecom/carousel-generator.git
cd carousel-generator
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
playwright install chromium
cp .env.example .env  # edita con tu token de Apify
```

## Flujo de PR

1. Fork del repo
2. Branch nueva: `git checkout -b feature/mi-mejora`
3. Commit con mensajes claros en español o inglés
4. Push y abre PR contra `main`
5. Describe qué cambió, por qué, y cómo se prueba
