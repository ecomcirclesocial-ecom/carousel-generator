"""Wrapper de Gemini 2.5 Flash Image (Nano Banana) para generar fotos acorde al tema."""
import re
from pathlib import Path

from google import genai
from google.genai import types

from config import GEMINI_API_KEY


MODEL = "gemini-2.5-flash-image"


class NanoBananaError(Exception):
    pass


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-") or "image"


PHOTO_PROMPT = """Genera una foto vertical (aspecto 4:5, 1080×1350) que sirva de fondo para un carrusel de Instagram sobre el tema:

**TEMA**: {tema}

# Reglas
- Composición vertical 4:5 (no cuadrada, no horizontal)
- Estilo: editorial, cinemático, moody — paleta oscura/desaturada con un acento vibrante (naranja o cálido)
- La imagen debe sugerir el tema visualmente, no ilustrarlo de forma literal
- Espacio negativo amplio en la mitad izquierda y superior — el texto irá encima, evita poner el sujeto principal a la izquierda
- Sin texto, sin logos, sin marcas de agua, sin firmas
- Sin caras humanas reconocibles — usa siluetas, manos, perfiles, o composiciones abstractas/conceptuales
- Foto realista o cinemática, NO ilustración cartoon
- Iluminación suave, atmosférica
- Si el tema es técnico (código, software, herramientas), considera: pantallas con luz tenue, manos en teclado, escritorio minimalista
- Si el tema es de negocio/ventas, considera: oficina moderna, vista urbana, escritorio con detalles relevantes
- Si el tema es de mindset/lifestyle, considera: espacios aspiracionales, ambientes urbanos, vista exterior

Genera la imagen."""


def generate_topic_photo(tema: str, out_dir: Path) -> Path:
    """Genera una foto de fondo acorde al tema usando Nano Banana.

    Returns: path a la imagen generada (PNG).
    Raises: NanoBananaError si falla.
    """
    if not GEMINI_API_KEY:
        raise NanoBananaError("GEMINI_API_KEY no está en .env")

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{_slugify(tema)}.png"

    if out_path.exists():
        return out_path

    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = PHOTO_PROMPT.format(tema=tema)

    response = client.models.generate_content(
        model=MODEL,
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        ),
    )

    if not response.candidates:
        raise NanoBananaError("Nano Banana no devolvió candidatos")

    for part in response.candidates[0].content.parts:
        if getattr(part, "inline_data", None) and part.inline_data.data:
            out_path.write_bytes(part.inline_data.data)
            return out_path

    raise NanoBananaError("Nano Banana no devolvió imagen en la respuesta")
