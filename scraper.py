import asyncio
import json
import re
from pathlib import Path

import aiohttp
from apify_client import ApifyClient

from config import APIFY_TOKEN, CACHE_SCRAPED


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-") or "untitled"


def _client() -> ApifyClient:
    if not APIFY_TOKEN:
        raise RuntimeError("APIFY_TOKEN no encontrado en .env")
    return ApifyClient(APIFY_TOKEN)


def _normalize_post_url(url: str) -> str:
    m = re.search(r"/p/([A-Za-z0-9_-]+)", url)
    if not m:
        raise ValueError(f"URL inválida — no parece un post de Instagram: {url}")
    return f"https://www.instagram.com/p/{m.group(1)}/"


def _extract_short_code(url: str) -> str:
    m = re.search(r"/p/([A-Za-z0-9_-]+)", url)
    return m.group(1) if m else "unknown"


def scrape_post(post_url: str, slug: str) -> dict:
    """Scrapea un post específico de Instagram. Devuelve metadata y paths locales."""
    url = _normalize_post_url(post_url)
    short_code = _extract_short_code(url)

    cache_dir = CACHE_SCRAPED / slug
    cache_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = cache_dir / "posts.json"

    client = _client()
    run_input = {
        "directUrls": [url],
        "resultsType": "posts",
        "resultsLimit": 1,
        "addParentData": False,
    }
    run = client.actor("apify/instagram-scraper").call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    if not items:
        raise RuntimeError(f"Apify no devolvió resultados para {url}")

    post = items[0]
    if post.get("type") != "Sidecar":
        raise RuntimeError(
            f"El post {short_code} no es un carrusel (type={post.get('type')})"
        )

    images = post.get("images") or []
    if not images:
        child_posts = post.get("childPosts") or []
        images = [c.get("displayUrl") for c in child_posts if c.get("displayUrl")]

    if not images:
        raise RuntimeError(f"No se encontraron imágenes en el post {short_code}")

    post_dir = cache_dir / short_code
    post_dir.mkdir(parents=True, exist_ok=True)
    local_paths = asyncio.run(_download_images(images, post_dir))

    result = {
        "post_url": url,
        "short_code": short_code,
        "caption": post.get("caption", ""),
        "likes": post.get("likesCount", 0),
        "comments": post.get("commentsCount", 0),
        "owner": post.get("ownerUsername", ""),
        "slide_count": len(local_paths),
        "image_paths": [str(p) for p in local_paths],
    }
    metadata_path.write_text(json.dumps([result], indent=2, ensure_ascii=False))
    return result


def scrape_creator(handle: str, slug: str, limit: int = 10) -> list[dict]:
    """Scrapea posts del feed de un creador. Filtra solo carruseles."""
    handle = handle.lstrip("@")
    cache_dir = CACHE_SCRAPED / slug
    cache_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = cache_dir / "posts.json"

    client = _client()
    run_input = {
        "directUrls": [f"https://www.instagram.com/{handle}/"],
        "resultsType": "posts",
        "resultsLimit": limit,
        "addParentData": False,
    }
    run = client.actor("apify/instagram-scraper").call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    carousels = [p for p in items if p.get("type") == "Sidecar"]
    carousels.sort(key=lambda p: p.get("likesCount", 0), reverse=True)

    results = []
    for post in carousels[:limit]:
        short_code = post.get("shortCode") or _extract_short_code(post.get("url", ""))
        images = post.get("images") or []
        if not images:
            child = post.get("childPosts") or []
            images = [c.get("displayUrl") for c in child if c.get("displayUrl")]
        if len(images) < 3:
            continue

        post_dir = cache_dir / short_code
        post_dir.mkdir(parents=True, exist_ok=True)
        local_paths = asyncio.run(_download_images(images, post_dir))

        results.append(
            {
                "post_url": post.get("url"),
                "short_code": short_code,
                "caption": post.get("caption", ""),
                "likes": post.get("likesCount", 0),
                "comments": post.get("commentsCount", 0),
                "owner": post.get("ownerUsername", handle),
                "slide_count": len(local_paths),
                "image_paths": [str(p) for p in local_paths],
            }
        )

    if not results:
        raise RuntimeError(f"No se encontraron carruseles para @{handle}")

    metadata_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    return results


async def _download_images(urls: list[str], dest_dir: Path) -> list[Path]:
    paths = []
    async with aiohttp.ClientSession() as session:
        tasks = [
            _download_one(session, url, dest_dir / f"slide-{i + 1:02d}.jpg")
            for i, url in enumerate(urls)
        ]
        paths = await asyncio.gather(*tasks)
    return [p for p in paths if p is not None]


async def _download_one(session, url: str, path: Path) -> Path | None:
    if path.exists() and path.stat().st_size > 0:
        return path
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            resp.raise_for_status()
            data = await resp.read()
            path.write_bytes(data)
            return path
    except Exception as e:
        print(f"  ! falló descarga {url}: {e}")
        return None
