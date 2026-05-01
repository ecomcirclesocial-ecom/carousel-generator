import json
from pathlib import Path

from claude_cli import query_json
from prompts import COPY_GENERATION_PROMPT
from renderer import render_carousel


def generate_copy(
    style_guide: dict,
    tema: str,
    cta_word: str,
    idioma: str = "es",
) -> dict:
    """Llama a claude CLI para generar el copy del carrusel con estructura Hook→Dolor→Valor→Recap→CTA."""
    cta_text = f'Comenta "{cta_word}" y te lo envío' if idioma == "es" else f'Comment "{cta_word}" and I\'ll send it'
    prompt = COPY_GENERATION_PROMPT.format(
        style_guide=json.dumps(style_guide, indent=2, ensure_ascii=False),
        tema=tema,
        cta_word=cta_word,
        cta_text=cta_text,
        idioma=idioma,
    )
    return query_json(prompt)


def generate(
    preset: dict,
    tema: str,
    cta_word: str,
    photo_path: Path | None = None,
    idioma: str = "es",
    out_dir: Path | None = None,
    handle: str = "@ecomcircle",
) -> tuple[Path, dict]:
    """Pipeline completo: tema + cta → copy → render → carpeta de PNGs."""
    copy = generate_copy(preset, tema, cta_word, idioma=idioma)
    output_dir = render_carousel(
        preset=preset,
        copy=copy,
        photo_path=photo_path,
        out_dir=out_dir,
        handle=handle,
    )
    return output_dir, copy
