import base64
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from playwright.sync_api import sync_playwright

from config import OUTPUT_DIR, SLIDE_HEIGHT, SLIDE_WIDTH, TEMPLATES_DIR


KW_PATTERN = re.compile(r"\*\*([^*]+)\*\*")


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-") or "untitled"


def highlight_keywords(text: str) -> str:
    """Convierte **bold** en <span class='kw'>bold</span>."""
    if not text:
        return ""
    return KW_PATTERN.sub(r'<span class="kw">\1</span>', text)


def photo_data_uri(photo_path: Path | None) -> str | None:
    if not photo_path or not photo_path.exists():
        return None
    data = photo_path.read_bytes()
    mime = "image/jpeg" if photo_path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _terminal_label_for(role: str, n: int, idioma: str) -> str:
    labels_es = ["Cómo aplicarlo", "El truco", "La verdad", "Mira esto", "El detalle", "El error"]
    labels_en = ["How to apply", "The trick", "The truth", "Look at this", "The detail", "The mistake"]
    labels = labels_en if idioma == "en" else labels_es
    return labels[(n - 1) % len(labels)]


def render_carousel(
    preset: dict,
    copy: dict,
    photo_path: Path | None = None,
    out_dir: Path | None = None,
    template_name: str = "diferencia_foto.html",
    handle: str = "@ecomcircle",
) -> Path:
    """Renderiza todos los slides del carrusel a PNGs 1080x1350 (2x device scale)."""
    slides = copy["slides"]
    tema = copy.get("tema", "carrusel")
    idioma = copy.get("idioma", "es")

    if out_dir is None:
        out_dir = OUTPUT_DIR / _slugify(tema)
    out_dir.mkdir(parents=True, exist_ok=True)

    palette = preset.get("palette", {})
    accent = palette.get("accent", "#FF6B3D")
    accent_soft = palette.get("text_secondary") if palette.get("text_secondary", "").startswith("#") else "#E5734A"

    photo_uri = photo_data_uri(photo_path)
    value_total = sum(1 for s in slides if s.get("role") == "value")

    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template(template_name)
    total = len(slides)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": SLIDE_WIDTH, "height": SLIDE_HEIGHT},
            device_scale_factor=2,
        )
        page = context.new_page()

        for slide in slides:
            n = slide.get("n", 1)
            role = slide.get("role", "value")
            headline_raw = slide.get("headline") or slide.get("title", "")
            body_raw = slide.get("body", "")
            items = [highlight_keywords(it) for it in slide.get("items", [])]

            html = template.render(
                n=n,
                total=total,
                role=role,
                headline=highlight_keywords(headline_raw),
                title=slide.get("title", ""),
                body=highlight_keywords(body_raw),
                items=items,
                terminal_label=slide.get("terminal_label") or _terminal_label_for(role, n, idioma),
                value_total=value_total,
                handle=handle,
                idioma=idioma,
                photo_data_uri=photo_uri,
                accent=accent,
                accent_soft=accent_soft,
            )
            page.set_content(html, wait_until="networkidle")
            out_path = out_dir / f"slide-{n:02d}.png"
            page.screenshot(path=str(out_path))

        browser.close()

    return out_dir
