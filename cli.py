import http.server
import json
import socketserver
import sys
import threading
import webbrowser
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from claude_cli import ensure_available
from config import OUTPUT_DIR, PRESETS_DIR
from generator import generate as run_generate
from scraper import scrape_creator, scrape_post, slugify
from style_extractor import extract_style

console = Console()


def _preset_path(name: str) -> Path:
    return PRESETS_DIR / f"{slugify(name)}.json"


@click.group()
def cli():
    """Generador de carruseles de Instagram virales para cualquier nicho."""
    pass


@cli.group()
def preset():
    """Manejo de presets de estilo."""
    pass


@preset.command("create")
@click.option("--post", "post_url", default=None, help="URL del post de Instagram a usar como referencia.")
@click.option("--creator", default=None, help="Handle del creador (sin @) — scrapea sus últimos carruseles.")
@click.option("--limit", default=10, show_default=True)
@click.option("--name", required=True, help="Nombre del preset (slug).")
@click.option("--force", is_flag=True, help="Re-genera aunque ya exista cache.")
def preset_create(post_url, creator, limit, name, force):
    """Crea un preset desde un post o un creador de referencia."""
    if not post_url and not creator:
        console.print("[red]✗ Pasa --post <url> o --creator <handle>[/red]")
        sys.exit(1)
    try:
        ensure_available()
    except Exception as e:
        console.print(f"[red]✗ {e}[/red]")
        sys.exit(1)

    slug = slugify(name)
    console.print(f"[cyan]→ Scrapeando con Apify...[/cyan]")
    if post_url:
        post = scrape_post(post_url, slug)
        console.print(f"  ✓ Post {post['short_code']} · {post['slide_count']} slides")
        scraped = [post]
    else:
        scraped = scrape_creator(creator, slug, limit=limit)
        console.print(f"  ✓ {len(scraped)} carruseles")

    console.print(f"[cyan]→ Extrayendo estilo con claude...[/cyan]")
    style_guide = extract_style(scraped, slug, force=force)

    preset_data = {
        "name": slug,
        "source": post_url or f"@{creator}",
        **style_guide,
    }
    path = _preset_path(slug)
    path.write_text(json.dumps(preset_data, indent=2, ensure_ascii=False))
    console.print(f"[green]✓ Preset guardado:[/green] {path}")


@preset.command("list")
def preset_list():
    files = sorted(PRESETS_DIR.glob("*.json"))
    if not files:
        console.print("[yellow]No hay presets aún.[/yellow]")
        return
    table = Table(title="Presets")
    table.add_column("Nombre", style="cyan")
    table.add_column("Fuente")
    table.add_column("Vibe")
    for f in files:
        data = json.loads(f.read_text())
        table.add_row(data.get("name", f.stem), data.get("source", "?"), (data.get("vibe") or "")[:60])
    console.print(table)


@preset.command("show")
@click.argument("name")
def preset_show(name):
    path = _preset_path(name)
    if not path.exists():
        console.print(f"[red]✗ No existe el preset: {name}[/red]")
        sys.exit(1)
    console.print_json(path.read_text())


@preset.command("delete")
@click.argument("name")
def preset_delete(name):
    path = _preset_path(name)
    if not path.exists():
        console.print(f"[red]✗ No existe el preset: {name}[/red]")
        sys.exit(1)
    path.unlink()
    console.print(f"[green]✓ Preset eliminado: {name}[/green]")


@cli.command("generate")
@click.option("--preset", "preset_name", required=True, help="Preset a usar.")
@click.option("--tema", required=True, help="Tema del carrusel (cualquier nicho).")
@click.option("--cta", "cta_word", required=True, help="Palabra clave del CTA (ej: DROPI, GUIA, SCRIPT).")
@click.option("--photo", "photo_path", default=None, help="Path a foto de fondo (opcional).")
@click.option("--idioma", default="es", show_default=True, type=click.Choice(["es", "en"]))
@click.option("--handle", default="@ecomcircle", show_default=True)
@click.option("--out", "out_dir", default=None)
def generate_cmd(preset_name, tema, cta_word, photo_path, idioma, handle, out_dir):
    """Genera un carrusel completo (Hook→Dolor→Valor→Recap→CTA)."""
    try:
        ensure_available()
    except Exception as e:
        console.print(f"[red]✗ {e}[/red]")
        sys.exit(1)

    path = _preset_path(preset_name)
    if not path.exists():
        console.print(f"[red]✗ No existe el preset: {preset_name}[/red]")
        sys.exit(1)
    preset_data = json.loads(path.read_text())

    photo = Path(photo_path) if photo_path else None
    if photo and not photo.exists():
        console.print(f"[red]✗ No existe la foto: {photo}[/red]")
        sys.exit(1)

    console.print(f"[cyan]→ Generando copy con claude (tema: {tema}, cta: {cta_word})...[/cyan]")
    out_path = Path(out_dir) if out_dir else None
    result_dir, copy = run_generate(
        preset_data,
        tema=tema,
        cta_word=cta_word,
        photo_path=photo,
        idioma=idioma,
        out_dir=out_path,
        handle=handle,
    )
    pngs = sorted(result_dir.glob("*.png"))
    console.print(f"[green]✓ {len(pngs)} slides generados en:[/green] {result_dir}")
    (result_dir / "copy.json").write_text(json.dumps(copy, indent=2, ensure_ascii=False))
    for p in pngs:
        console.print(f"  · {p.name}")
    console.print(f"\n[dim]Preview: carousel preview --dir {result_dir}[/dim]")


@cli.command("preview")
@click.option("--dir", "out_dir", required=True, help="Directorio con los PNGs generados.")
@click.option("--port", default=8765, show_default=True)
@click.option("--no-open", is_flag=True, help="No abrir el navegador automáticamente.")
def preview_cmd(out_dir, port, no_open):
    """Abre los slides en el navegador en una galería simple."""
    out_path = Path(out_dir).resolve()
    if not out_path.exists():
        console.print(f"[red]✗ No existe: {out_path}[/red]")
        sys.exit(1)

    pngs = sorted([p.name for p in out_path.glob("*.png")])
    if not pngs:
        console.print(f"[yellow]No hay PNGs en {out_path}[/yellow]")
        return

    index_html = _build_preview_html(out_path.name, pngs)
    (out_path / "index.html").write_text(index_html)

    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(*a, directory=str(out_path), **kw)
    httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
    url = f"http://127.0.0.1:{port}/index.html"
    console.print(f"[green]→ Sirviendo en {url}[/green]")
    console.print("[dim]Ctrl+C para detener[/dim]")

    if not no_open:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()
        console.print("\n[dim]Detenido.[/dim]")


def _build_preview_html(title: str, pngs: list[str]) -> str:
    cards = "\n".join(
        f'<a class="card" href="{p}" target="_blank"><img src="{p}" alt="{p}"/><span>{p}</span></a>'
        for p in pngs
    )
    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><title>{title}</title>
<style>
  body {{ background:#0A0A0A; color:#fff; font-family:-apple-system,sans-serif; margin:0; padding:40px; }}
  h1 {{ font-size:24px; font-weight:600; margin:0 0 24px 0; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:20px; }}
  .card {{ background:#161616; border-radius:12px; overflow:hidden; text-decoration:none; color:#fff; border:1px solid rgba(255,255,255,0.06); transition:transform 0.15s; }}
  .card:hover {{ transform:translateY(-2px); border-color:#FF5911; }}
  .card img {{ width:100%; aspect-ratio:4/5; object-fit:cover; display:block; }}
  .card span {{ display:block; padding:12px; font-size:13px; color:rgba(255,255,255,0.6); }}
</style></head>
<body>
<h1>{title} · {len(pngs)} slides</h1>
<div class="grid">{cards}</div>
</body></html>"""


if __name__ == "__main__":
    cli()
