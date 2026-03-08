"""
Motor de PDF V3
================
Markdown → HTML, renderização Jinja2, compilação WeasyPrint.
Inclui temas refinados com fontes dedicadas, suporte a epígrafe,
e design tokens premium.
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
    epigraph: str = None,
    epigraph_author: str = None,
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
        epigraph=epigraph,
        epigraph_author=epigraph_author,
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

    # =====================================================================
    # CSS Dinâmico por Tema — TODOS os tokens visuais que mudam por tema
    # Inclui: cores, gradientes, fontes, cover card bg, glows, patterns
    # =====================================================================
    css_dict = {
        "Minimalista Moderno": """:root {
            --color-bg: #ffffff;
            --color-bg-warm: #fafafa;
            --color-bg-cool: #f5f5f5;
            --color-text: #1a1a1a;
            --color-text-secondary: #666666;
            --color-text-light: #999999;
            --color-accent: #111111;
            --color-accent-light: #444444;
            --color-accent-soft: rgba(0,0,0,0.04);
            --color-accent-border: rgba(0,0,0,0.08);
            --gradient-accent: linear-gradient(135deg, #222 0%, #555 100%);
            --gradient-dark: linear-gradient(160deg, #0a0a0a 0%, #1a1a1a 40%, #333 70%, #555 100%);
            --gradient-warm: linear-gradient(135deg, #fafafa 0%, #f0f0f0 100%);
            --color-cover-card-bg: rgba(10, 10, 10, 0.70);
            --color-cover-glow-1: rgba(100, 100, 100, 0.10);
            --color-cover-glow-2: rgba(80, 80, 80, 0.08);
            --color-cover-pattern-1: rgba(100, 100, 100, 0.05);
            --color-cover-pattern-2: rgba(80, 80, 80, 0.04);
            --color-accent-shadow: rgba(0, 0, 0, 0.15);
            --shadow-card: 0 2px 20px rgba(0, 0, 0, 0.06);
            --shadow-glow: 0 0 40px rgba(0, 0, 0, 0.08);
            --font-body: 'Inter', 'Helvetica Neue', Arial, sans-serif;
            --font-display: 'Inter', 'Helvetica Neue', Arial, sans-serif;
        }""",

        "Fantasia Épica": """:root {
            --color-bg: #FDF6E3;
            --color-bg-warm: #F8E9C9;
            --color-bg-cool: #FAF1DD;
            --color-text: #2C1E16;
            --color-text-secondary: #5D4037;
            --color-text-light: #8D6E63;
            --color-accent: #8B4513;
            --color-accent-light: #CD853F;
            --color-accent-soft: rgba(139,69,19,0.06);
            --color-accent-border: rgba(139,69,19,0.15);
            --gradient-accent: linear-gradient(135deg, #8B4513 0%, #D2691E 50%, #CD853F 100%);
            --gradient-dark: linear-gradient(160deg, #1a0f08 0%, #2C1E16 40%, #5D4037 70%, #8B4513 100%);
            --gradient-warm: linear-gradient(135deg, #FDF6E3 0%, #F8E9C9 100%);
            --color-cover-card-bg: rgba(44, 30, 22, 0.70);
            --color-cover-glow-1: rgba(139, 69, 19, 0.20);
            --color-cover-glow-2: rgba(205, 133, 63, 0.15);
            --color-cover-pattern-1: rgba(139, 69, 19, 0.08);
            --color-cover-pattern-2: rgba(205, 133, 63, 0.06);
            --color-accent-shadow: rgba(139, 69, 19, 0.3);
            --shadow-card: 0 2px 20px rgba(139, 69, 19, 0.08);
            --shadow-glow: 0 0 40px rgba(139, 69, 19, 0.12);
            --font-body: Georgia, 'Palatino Linotype', serif;
            --font-display: 'Playfair Display', Georgia, 'Garamond', serif;
        }""",

        "Corporativo Clean": """:root {
            --color-bg: #ffffff;
            --color-bg-warm: #f0f4f8;
            --color-bg-cool: #e8ecf1;
            --color-text: #1a1a2e;
            --color-text-secondary: #4a5568;
            --color-text-light: #718096;
            --color-accent: #003366;
            --color-accent-light: #1a73e8;
            --color-accent-soft: rgba(0,51,102,0.05);
            --color-accent-border: rgba(0,51,102,0.12);
            --gradient-accent: linear-gradient(135deg, #003366 0%, #00509e 50%, #1a73e8 100%);
            --gradient-dark: linear-gradient(160deg, #0a1628 0%, #152238 40%, #1d3557 70%, #003366 100%);
            --gradient-warm: linear-gradient(135deg, #f0f4f8 0%, #e8ecf1 100%);
            --color-cover-card-bg: rgba(10, 22, 40, 0.72);
            --color-cover-glow-1: rgba(0, 51, 102, 0.18);
            --color-cover-glow-2: rgba(26, 115, 232, 0.12);
            --color-cover-pattern-1: rgba(0, 51, 102, 0.06);
            --color-cover-pattern-2: rgba(26, 115, 232, 0.04);
            --color-accent-shadow: rgba(0, 51, 102, 0.25);
            --shadow-card: 0 2px 20px rgba(0, 51, 102, 0.08);
            --shadow-glow: 0 0 40px rgba(0, 51, 102, 0.10);
            --font-body: 'Inter', 'Roboto', 'Segoe UI', sans-serif;
            --font-display: 'Playfair Display', Georgia, serif;
        }""",

        "Sci-Fi Neon": """:root {
            --color-bg: #0b0c10;
            --color-bg-warm: #13141a;
            --color-bg-cool: #1f2833;
            --color-text: #c5c6c7;
            --color-text-secondary: #a3a5a7;
            --color-text-light: #7d7f81;
            --color-accent: #45a29e;
            --color-accent-light: #66fcf1;
            --color-accent-soft: rgba(69,162,158,0.08);
            --color-accent-border: rgba(102,252,241,0.15);
            --gradient-accent: linear-gradient(135deg, #45a29e 0%, #66fcf1 50%, #00f5d4 100%);
            --gradient-dark: linear-gradient(160deg, #020304 0%, #0b0c10 40%, #1f2833 70%, #45a29e 100%);
            --gradient-warm: linear-gradient(135deg, #13141a 0%, #1f2833 100%);
            --color-cover-card-bg: rgba(5, 6, 8, 0.75);
            --color-cover-glow-1: rgba(69, 162, 158, 0.25);
            --color-cover-glow-2: rgba(102, 252, 241, 0.15);
            --color-cover-pattern-1: rgba(69, 162, 158, 0.10);
            --color-cover-pattern-2: rgba(102, 252, 241, 0.06);
            --color-accent-shadow: rgba(102, 252, 241, 0.35);
            --shadow-card: 0 2px 20px rgba(69, 162, 158, 0.10);
            --shadow-glow: 0 0 40px rgba(102, 252, 241, 0.20);
            --font-body: 'Inter', 'Courier New', monospace;
            --font-display: 'Playfair Display', 'Courier New', monospace;
        }""",

        "Romance Clássico": """:root {
            --color-bg: #FFFAFC;
            --color-bg-warm: #FFF0F5;
            --color-bg-cool: #FFE8EF;
            --color-text: #4A3B3F;
            --color-text-secondary: #705B61;
            --color-text-light: #9a8b90;
            --color-accent: #b76e79;
            --color-accent-light: #d18d96;
            --color-accent-soft: rgba(183,110,121,0.07);
            --color-accent-border: rgba(183,110,121,0.18);
            --gradient-accent: linear-gradient(135deg, #b76e79 0%, #d18d96 50%, #e8a5b0 100%);
            --gradient-dark: linear-gradient(160deg, #1a0f12 0%, #2d1f24 40%, #4A3B3F 70%, #b76e79 100%);
            --gradient-warm: linear-gradient(135deg, #FFFAFC 0%, #FFF0F5 100%);
            --color-cover-card-bg: rgba(26, 15, 18, 0.68);
            --color-cover-glow-1: rgba(183, 110, 121, 0.22);
            --color-cover-glow-2: rgba(232, 165, 176, 0.15);
            --color-cover-pattern-1: rgba(183, 110, 121, 0.08);
            --color-cover-pattern-2: rgba(209, 141, 150, 0.06);
            --color-accent-shadow: rgba(183, 110, 121, 0.3);
            --shadow-card: 0 2px 20px rgba(183, 110, 121, 0.08);
            --shadow-glow: 0 0 40px rgba(183, 110, 121, 0.12);
            --font-body: Georgia, 'Palatino Linotype', serif;
            --font-display: 'Playfair Display', Georgia, serif;
        }""",

        "Cyberpunk": """:root {
            --color-bg: #12041D;
            --color-bg-warm: #1A0A29;
            --color-bg-cool: #240F38;
            --color-text: #E0E0FF;
            --color-text-secondary: #B0B0CC;
            --color-text-light: #8080AA;
            --color-accent: #FF00FF;
            --color-accent-light: #F3E600;
            --color-accent-soft: rgba(255,0,255,0.08);
            --color-accent-border: rgba(255,0,255,0.20);
            --gradient-accent: linear-gradient(135deg, #FF00FF 0%, #F3E600 50%, #00FFFF 100%);
            --gradient-dark: linear-gradient(160deg, #050108 0%, #12041D 40%, #240F38 70%, #FF00FF 100%);
            --gradient-warm: linear-gradient(135deg, #1A0A29 0%, #240F38 100%);
            --color-cover-card-bg: rgba(5, 1, 8, 0.75);
            --color-cover-glow-1: rgba(255, 0, 255, 0.25);
            --color-cover-glow-2: rgba(243, 230, 0, 0.15);
            --color-cover-pattern-1: rgba(255, 0, 255, 0.10);
            --color-cover-pattern-2: rgba(0, 255, 255, 0.06);
            --color-accent-shadow: rgba(255, 0, 255, 0.35);
            --shadow-card: 0 2px 20px rgba(255, 0, 255, 0.10);
            --shadow-glow: 0 0 40px rgba(255, 0, 255, 0.20);
            --font-body: 'Inter', 'Consolas', monospace;
            --font-display: 'Playfair Display', 'Consolas', monospace;
        }""",

        "Vintage / Retrô": """:root {
            --color-bg: #F5E6D0;
            --color-bg-warm: #E8D5BF;
            --color-bg-cool: #DBC7AA;
            --color-text: #3E2723;
            --color-text-secondary: #5D4037;
            --color-text-light: #8D6E63;
            --color-accent: #8D6E63;
            --color-accent-light: #A1887F;
            --color-accent-soft: rgba(141,110,99,0.07);
            --color-accent-border: rgba(141,110,99,0.18);
            --gradient-accent: linear-gradient(135deg, #6D4C41 0%, #8D6E63 50%, #A1887F 100%);
            --gradient-dark: linear-gradient(160deg, #1a100c 0%, #3E2723 40%, #5D4037 70%, #8D6E63 100%);
            --gradient-warm: linear-gradient(135deg, #F5E6D0 0%, #E8D5BF 100%);
            --color-cover-card-bg: rgba(26, 16, 12, 0.70);
            --color-cover-glow-1: rgba(141, 110, 99, 0.20);
            --color-cover-glow-2: rgba(161, 136, 127, 0.12);
            --color-cover-pattern-1: rgba(141, 110, 99, 0.08);
            --color-cover-pattern-2: rgba(109, 76, 65, 0.06);
            --color-accent-shadow: rgba(141, 110, 99, 0.3);
            --shadow-card: 0 2px 20px rgba(141, 110, 99, 0.08);
            --shadow-glow: 0 0 40px rgba(141, 110, 99, 0.12);
            --font-body: 'Palatino Linotype', 'Book Antiqua', Palatino, serif;
            --font-display: 'Playfair Display', 'Palatino Linotype', serif;
        }""",

        "Aquarela Suave": """:root {
            --color-bg: #fdfefe;
            --color-bg-warm: #f4f8fa;
            --color-bg-cool: #edf2f5;
            --color-text: #4d5e6f;
            --color-text-secondary: #7d8e9e;
            --color-text-light: #a0b0c0;
            --color-accent: #5DADE2;
            --color-accent-light: #AED6F1;
            --color-accent-soft: rgba(93,173,226,0.07);
            --color-accent-border: rgba(93,173,226,0.18);
            --gradient-accent: linear-gradient(135deg, #3498DB 0%, #5DADE2 50%, #85C1E9 100%);
            --gradient-dark: linear-gradient(160deg, #0a1929 0%, #1a2f45 40%, #2c5f8a 70%, #5DADE2 100%);
            --gradient-warm: linear-gradient(135deg, #f4f8fa 0%, #edf2f5 100%);
            --color-cover-card-bg: rgba(10, 25, 41, 0.68);
            --color-cover-glow-1: rgba(93, 173, 226, 0.22);
            --color-cover-glow-2: rgba(174, 214, 241, 0.15);
            --color-cover-pattern-1: rgba(93, 173, 226, 0.08);
            --color-cover-pattern-2: rgba(52, 152, 219, 0.05);
            --color-accent-shadow: rgba(93, 173, 226, 0.3);
            --shadow-card: 0 2px 20px rgba(93, 173, 226, 0.08);
            --shadow-glow: 0 0 40px rgba(93, 173, 226, 0.12);
            --font-body: 'Inter', 'Verdana', sans-serif;
            --font-display: 'Playfair Display', Georgia, serif;
        }""",
    }
    
    theme_base = theme.split(" - ")[0] if " - " in theme else theme
    theme_css = css_dict.get(theme_base, css_dict["Minimalista Moderno"])

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
        background-color: rgba(255, 255, 255, 0.92);
        padding: 30px;
        border-radius: 12px;
        min-height: 85vh;
    }}
    """
    return compile_pdf(html_content, output_path, style)
