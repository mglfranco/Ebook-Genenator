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
    body {{
        font-family: Arial, sans-serif;
        line-height: 1.6;
    }}
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
