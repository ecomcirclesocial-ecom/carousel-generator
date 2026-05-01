import json
from pathlib import Path

from PIL import Image

from claude_cli import query_json
from config import CACHE_STYLE
from prompts import STYLE_EXTRACTION_PROMPT


def _resize_for_analysis(src: Path, dest: Path, max_side: int = 1024) -> Path:
    if dest.exists():
        return dest
    img = Image.open(src)
    img.thumbnail((max_side, max_side))
    if img.mode != "RGB":
        img = img.convert("RGB")
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, "JPEG", quality=85)
    return dest


def extract_style(scraped_posts: list[dict], slug: str, force: bool = False) -> dict:
    """Llama a claude CLI con vision para extraer el style guide del creador."""
    cache_path = CACHE_STYLE / f"{slug}.json"
    if cache_path.exists() and not force:
        return json.loads(cache_path.read_text())

    image_paths = []
    for post in scraped_posts[:5]:
        for path_str in post["image_paths"][:2]:
            src = Path(path_str)
            if not src.exists():
                continue
            dest = src.parent / f"resized_{src.stem}.jpg"
            resized = _resize_for_analysis(src, dest)
            image_paths.append(str(resized.resolve()))

    if not image_paths:
        raise RuntimeError("No hay imágenes scrapeadas para analizar")

    paths_block = "\n".join(f"- {p}" for p in image_paths)
    prompt = STYLE_EXTRACTION_PROMPT.format(image_paths=paths_block)

    style_guide = query_json(prompt)

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(style_guide, indent=2, ensure_ascii=False))
    return style_guide
