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
    # Em vez de tentar sobrescrever a tag `body`, injetamos Variáveis :root.
    # Essas variáveis alimentam os card styles e shadows refinados de `style.css`.
    css_dict = {
        "Minimalista Moderno": ":root { --color-bg: #ffffff; --color-bg-warm: #fcfcfc; --color-bg-cool: #f8f9fa; --color-text: #222222; --color-text-secondary: #555555; --color-accent: #000000; --font-sans: 'Helvetica Neue', Arial, sans-serif; --font-serif: 'Helvetica Neue', Arial, sans-serif; }",
        "Fantasia Épica": ":root { --color-bg: #FDF6E3; --color-bg-warm: #F8E9C9; --color-bg-cool: #FAF1DD; --color-text: #2C1E16; --color-text-secondary: #4A3A2C; --color-accent: #8B4513; --color-accent-light: #A0522D; --font-sans: 'Georgia', serif; --font-serif: 'Garamond', 'Georgia', serif; }",
        "Corporativo Clean": ":root { --color-bg: #ffffff; --color-bg-warm: #f0f4f8; --color-bg-cool: #e8ecf1; --color-text: #1a1a1a; --color-text-secondary: #4a5568; --color-accent: #003366; --color-accent-light: #00509e; --font-sans: 'Roboto', 'Segoe UI', Tahoma, sans-serif; --font-serif: 'Roboto', 'Segoe UI', Tahoma, sans-serif; }",
        "Sci-Fi Neon": ":root { --color-bg: #0b0c10; --color-bg-warm: #13141a; --color-bg-cool: #1f2833; --color-text: #c5c6c7; --color-text-secondary: #a3a5a7; --color-accent: #45a29e; --color-accent-light: #66fcf1; --font-sans: 'Courier New', Courier, monospace; --font-serif: 'Courier New', Courier, monospace; }",
        "Romance Clássico": ":root { --color-bg: #FFFAFC; --color-bg-warm: #FFEAF1; --color-bg-cool: #FFF0F5; --color-text: #4A3B3F; --color-text-secondary: #705B61; --color-accent: #b76e79; --color-accent-light: #d18d96; --font-sans: 'Georgia', serif; --font-serif: 'Georgia', serif; }",
        "Cyberpunk": ":root { --color-bg: #12041D; --color-bg-warm: #1A0A29; --color-bg-cool: #240F38; --color-text: #00FFFF; --color-text-secondary: #00CCCC; --color-accent: #FF00FF; --color-accent-light: #F3E600; --font-sans: 'Consolas', monospace; --font-serif: 'Consolas', monospace; }",
        "Vintage / Retrô": ":root { --color-bg: #E6D5B8; --color-bg-warm: #D4BFA6; --color-bg-cool: #C2A88B; --color-text: #3E2723; --color-text-secondary: #5D4037; --color-accent: #8D6E63; --color-accent-light: #A1887F; --font-sans: 'Palatino Linotype', 'Book Antiqua', Palatino, serif; --font-serif: 'Palatino Linotype', 'Book Antiqua', Palatino, serif; }",
        "Aquarela Suave": ":root { --color-bg: #fdfefe; --color-bg-warm: #f4f8fa; --color-bg-cool: #edf2f5; --color-text: #5d6d7e; --color-text-secondary: #85929e; --color-accent: #5DADE2; --color-accent-light: #AED6F1; --font-sans: 'Verdana', sans-serif; --font-serif: 'Verdana', sans-serif; }",
    }
    
    theme_base = theme.split(" - ")[0] if " - " in theme else theme
    theme_css = css_dict.get(theme_base, ":root { --color-bg: #ffffff; --color-text: #1a1a2e; }")

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
