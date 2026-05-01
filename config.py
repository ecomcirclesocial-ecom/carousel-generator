import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")

APIFY_TOKEN = os.getenv("APIFY_TOKEN")

PRESETS_DIR = ROOT / "presets"
CACHE_SCRAPED = ROOT / "cache" / "scraped"
CACHE_STYLE = ROOT / "cache" / "style_analysis"
OUTPUT_DIR = ROOT / "output"
TEMPLATES_DIR = ROOT / "templates"

for d in [PRESETS_DIR, CACHE_SCRAPED, CACHE_STYLE, OUTPUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

SLIDE_WIDTH = 1080
SLIDE_HEIGHT = 1350

CLAUDE_TIMEOUT = 180
