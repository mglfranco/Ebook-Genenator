"""
Motor de PDF V2
================
Markdown → HTML, renderização Jinja2, compilação WeasyPrint.
Agora inclui o campo `theme` no template.
"""

import os
from datetime import datetime
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS


_THIS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _THIS_DIR.parent
_TEMPLATES_DIR = _PROJECT_ROOT / "templates"


def _markdown_to_html(md_text: str) -> str:
    """Converte Markdown para HTML com extensões comuns."""
    extensions = [
        "extra",
        "codehilite",
        "toc",
        "sane_lists",
        "smarty",
    ]
    return markdown.markdown(md_text, extensions=extensions)


def render_ebook_html(
    title: str,
    author: str,
    theme: str,
    chapters: list[dict],
    image_paths: list[str],
    colorful_mode: bool = False,
) -> str:
    """Renderiza o HTML completo do e-book a partir do template Jinja2."""
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=False,
    )
    template = env.get_template("ebook.html")

    rendered_chapters = []
    for i, ch in enumerate(chapters):
        # Se html_content já foi gerado na pipeline, usamos. Senão, convertemos.
        if "content_html" in ch:
            html_content = ch["content_html"]
        else:
            html_content = _markdown_to_html(ch.get("content", ch.get("content_md", "")))
            
        img_path = image_paths[i] if i < len(image_paths) else None

        if img_path:
            img_path = Path(img_path).resolve().as_uri()

        rendered_chapters.append({
            "title": ch["title"],
            "html_content": html_content,
            "image_path": img_path,
        })

    html_str = template.render(
        title=title,
        author=author,
        theme=theme,
        year=datetime.now().year,
        chapters=rendered_chapters,
        colorful_mode=colorful_mode,
    )
    return html_str


def compile_pdf(html_content: str, output_path: str, additional_css: str = None) -> str:
    """Compila HTML + CSS em PDF via WeasyPrint."""
    css_path = _TEMPLATES_DIR / "style.css"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    html_doc = HTML(
        string=html_content,
        base_url=str(_TEMPLATES_DIR),
    )
    stylesheets = [CSS(filename=str(css_path))]
    
    if additional_css:
        stylesheets.append(CSS(string=additional_css))

    html_doc.write_pdf(
        output_path,
        stylesheets=stylesheets,
    )
    return os.path.abspath(output_path)


def generate_pdf(
    title: str,
    author: str,
    theme: str,
    chapters: list[dict],
    image_paths: list[str] | dict[int, str],
    output_path: str,
    bleed_mm: int = 3,
    colorful_mode: bool = False
) -> str:
    """Compila HTML final e renderiza PDF via Weasyprint com sangria (bleed)."""
    # Transform dict to list if legacy code sends a dict
    if isinstance(image_paths, dict):
        ordered_paths = []
        for i in range(len(chapters)):
            ordered_paths.append(image_paths.get(i, ""))
        image_paths = ordered_paths

    html_content = render_ebook_html(title, author, theme, chapters, image_paths, colorful_mode)

    # CSS Dinâmico Baseado no Tema Visual Escolhido no Painel
    css_dict = {
        "Minimalista Moderno": "body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background: #ffffff; color: #333333; } h1, h2 { color: #000000; letter-spacing: -0.5px; font-weight: 300; } h3 { color: #555555; }",
        "Fantasia Épica": "body { font-family: 'Garamond', 'Georgia', serif; background: #FDF6E3; color: #2C1E16; } h1, h2 { color: #8B4513; text-transform: uppercase; letter-spacing: 2px; border-bottom: 2px solid #8B4513; padding-bottom: 5px; } p { font-size: 1.05em; line-height: 1.7; }",
        "Corporativo Clean": "body { font-family: 'Roboto', 'Segoe UI', Tahoma, sans-serif; background: #ffffff; color: #1a1a1a; } h1, h2 { color: #003366; border-left: 5px solid #003366; padding-left: 15px; font-weight: bold; }",
        "Sci-Fi Neon": "body { font-family: 'Courier New', Courier, monospace; background: #0b0c10; color: #66fcf1; } h1, h2 { color: #45a29e; border-bottom: 1px dashed #66fcf1; text-transform: uppercase; } p { color: #c5c6c7; }",
        "Romance Clássico": "body { font-family: 'Georgia', serif; background: #FFFAFC; color: #4A3B3F; } h1, h2 { color: #b76e79; font-style: italic; text-align: center; font-weight: normal; } p { text-align: justify; }",
        "Cyberpunk": "body { font-family: 'Consolas', 'Courier New', monospace; background: #12041D; color: #F3E600; } h1, h2 { color: #FF00FF; text-transform: uppercase; letter-spacing: 3px; background: #000000; padding: 5px; } p { color: #00FFFF; }",
        "Vintage / Retrô": "body { font-family: 'Palatino Linotype', 'Book Antiqua', Palatino, serif; background: #E6D5B8; color: #3E2723; } h1, h2 { color: #5D4037; font-weight: bold; text-decoration: underline; } blockquote { font-style: italic; border-left: 4px solid #8D6E63; padding-left: 10px; }",
        "Aquarela Suave": "body { font-family: 'Verdana', sans-serif; background: #fdfefe; color: #5d6d7e; } h1, h2 { color: #AED6F1; font-weight: normal; } p { line-height: 1.8; }",
    }
    
    theme_base = theme.split(" - ")[0] if " - " in theme else theme
    theme_css = css_dict.get(theme_base, "body { font-family: Arial, sans-serif; line-height: 1.6; }")

    # Injetamos CSS adicional base para PDF + Sangria KDP
    style = f"""
    @page {{
        size: A5;
        margin: {bleed_mm}mm;
        bleed: {bleed_mm}mm;
    }}
    @page colorful_page {{
        margin: 0;
        bleed: {bleed_mm}mm;
    }}
    {theme_css}
    .chapter-img {{
        width: 100%;
        max-height: 400px;
        object-fit: cover;
        margin-bottom: 20px;
        border-radius: 8px;
    }}
    .colorful-mode {{
        page: colorful_page;
        min-height: 100vh;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        padding: 15mm;
        box-sizing: border-box;
    }}
    .colorful-mode .glass-container {{
        background-color: rgba(255, 255, 255, 0.90);
        padding: 30px;
        border-radius: 12px;
        min-height: 85vh;
    }}
    """
    return compile_pdf(html_content, output_path, style)
