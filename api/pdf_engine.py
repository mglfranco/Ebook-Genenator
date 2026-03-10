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
        base_url=str(_PROJECT_ROOT),
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

        "Executive Dark": """:root {
            --color-bg: #0d1117;
            --color-bg-warm: #161b22;
            --color-bg-cool: #21262d;
            --color-text: #c9d1d9;
            --color-text-secondary: #8b949e;
            --color-text-light: #6e7681;
            --color-accent: #2f81f7;
            --color-accent-light: #58a6ff;
            --color-accent-soft: rgba(47,129,247,0.1);
            --color-accent-border: rgba(47,129,247,0.4);
            --gradient-accent: linear-gradient(135deg, #2f81f7 0%, #1f6feb 100%);
            --gradient-dark: linear-gradient(160deg, #010409 0%, #0d1117 40%, #161b22 70%, #2f81f7 100%);
            --gradient-warm: linear-gradient(135deg, #161b22 0%, #21262d 100%);
            --color-cover-card-bg: rgba(1, 4, 9, 0.85);
            --color-cover-glow-1: rgba(47, 129, 247, 0.15);
            --color-cover-glow-2: rgba(88, 166, 255, 0.10);
            --color-cover-pattern-1: rgba(47, 129, 247, 0.05);
            --color-cover-pattern-2: rgba(88, 166, 255, 0.03);
            --color-accent-shadow: rgba(47, 129, 247, 0.2);
            --shadow-card: 0 4px 30px rgba(0, 0, 0, 0.5);
            --shadow-glow: 0 0 50px rgba(47, 129, 247, 0.15);
            --font-body: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            --font-display: 'Inter', -apple-system, sans-serif;
        }""",

        "Tech Startup": """:root {
            --color-bg: #ffffff;
            --color-bg-warm: #f8f9fa;
            --color-bg-cool: #f1f3f5;
            --color-text: #212529;
            --color-text-secondary: #495057;
            --color-text-light: #868e96;
            --color-accent: #5c7cfa;
            --color-accent-light: #748ffc;
            --color-accent-soft: rgba(92,124,250,0.08);
            --color-accent-border: rgba(92,124,250,0.2);
            --gradient-accent: linear-gradient(135deg, #5c7cfa 0%, #845ef7 100%);
            --gradient-dark: linear-gradient(160deg, #182440 0%, #2b3a67 40%, #4c5ea3 70%, #5c7cfa 100%);
            --gradient-warm: linear-gradient(135deg, #f8f9fa 0%, #f1f3f5 100%);
            --color-cover-card-bg: rgba(24, 36, 64, 0.8);
            --color-cover-glow-1: rgba(92, 124, 250, 0.2);
            --color-cover-glow-2: rgba(132, 94, 247, 0.15);
            --color-cover-pattern-1: rgba(92, 124, 250, 0.08);
            --color-cover-pattern-2: rgba(132, 94, 247, 0.05);
            --color-accent-shadow: rgba(92, 124, 250, 0.25);
            --shadow-card: 0 10px 40px rgba(0, 0, 0, 0.08);
            --shadow-glow: 0 0 60px rgba(92, 124, 250, 0.15);
            --font-body: 'Open Sans', 'Helvetica Neue', sans-serif;
            --font-display: 'Poppins', 'Montserrat', sans-serif;
        }""",

        "Didático Cursos": """:root {
            --color-bg: #FCFCFD;
            --color-bg-warm: #F4F5F7;
            --color-bg-cool: #EBECF0;
            --color-text: #172B4D;
            --color-text-secondary: #42526E;
            --color-text-light: #6B778C;
            --color-accent: #0052CC;
            --color-accent-light: #2684FF;
            --color-accent-soft: rgba(0,82,204,0.05);
            --color-accent-border: rgba(0,82,204,0.15);
            --gradient-accent: linear-gradient(135deg, #0052CC 0%, #0065FF 100%);
            --gradient-dark: linear-gradient(160deg, #091E42 0%, #172B4D 40%, #253858 70%, #0052CC 100%);
            --gradient-warm: linear-gradient(135deg, #F4F5F7 0%, #EBECF0 100%);
            --color-cover-card-bg: rgba(9, 30, 66, 0.85);
            --color-cover-glow-1: rgba(0, 82, 204, 0.15);
            --color-cover-glow-2: rgba(38, 132, 255, 0.1);
            --color-cover-pattern-1: rgba(0, 82, 204, 0.06);
            --color-cover-pattern-2: rgba(38, 132, 255, 0.04);
            --color-accent-shadow: rgba(0, 82, 204, 0.2);
            --shadow-card: 0 4px 12px rgba(9, 30, 66, 0.08);
            --shadow-glow: 0 0 30px rgba(0, 82, 204, 0.1);
            --font-body: 'Roboto', 'Helvetica Neue', sans-serif;
            --font-display: 'Roboto Slab', serif;
        }""",

        "Acadêmico Clean": """:root {
            --color-bg: #FFFFFF;
            --color-bg-warm: #FBFBFB;
            --color-bg-cool: #F5F5F5;
            --color-text: #222222;
            --color-text-secondary: #555555;
            --color-text-light: #888888;
            --color-accent: #7C2A3B;
            --color-accent-light: #A4384E;
            --color-accent-soft: rgba(124,42,59,0.05);
            --color-accent-border: rgba(124,42,59,0.15);
            --gradient-accent: linear-gradient(135deg, #7C2A3B 0%, #521C27 100%);
            --gradient-dark: linear-gradient(160deg, #1C0A0D 0%, #38131A 40%, #521C27 70%, #7C2A3B 100%);
            --gradient-warm: linear-gradient(135deg, #FBFBFB 0%, #F5F5F5 100%);
            --color-cover-card-bg: rgba(28, 10, 13, 0.85);
            --color-cover-glow-1: rgba(124, 42, 59, 0.15);
            --color-cover-glow-2: rgba(164, 56, 78, 0.1);
            --color-cover-pattern-1: rgba(124, 42, 59, 0.05);
            --color-cover-pattern-2: rgba(164, 56, 78, 0.03);
            --color-accent-shadow: rgba(124, 42, 59, 0.2);
            --shadow-card: 0 4px 15px rgba(0,0,0,0.05);
            --shadow-glow: 0 0 30px rgba(124, 42, 59, 0.1);
            --font-body: 'Times New Roman', 'Lora', serif;
            --font-display: 'Times New Roman', 'Lora', serif;
        }""",

        "Agência Digital (Vibrante)": """:root {
            --color-bg: #ffffff;
            --color-bg-warm: #fef6fa;
            --color-bg-cool: #fcf0f5;
            --color-text: #212529;
            --color-text-secondary: #495057;
            --color-text-light: #adb5bd;
            --color-accent: #f03e3e;
            --color-accent-light: #ff6b6b;
            --color-accent-soft: rgba(240,62,62,0.08);
            --color-accent-border: rgba(240,62,62,0.2);
            --gradient-accent: linear-gradient(135deg, #f03e3e 0%, #fd7e14 100%);
            --gradient-dark: linear-gradient(160deg, #340909 0%, #5c1818 40%, #ab2929 70%, #f03e3e 100%);
            --gradient-warm: linear-gradient(135deg, #fef6fa 0%, #fcf0f5 100%);
            --color-cover-card-bg: rgba(52, 9, 9, 0.85);
            --color-cover-glow-1: rgba(240, 62, 62, 0.2);
            --color-cover-glow-2: rgba(253, 126, 20, 0.15);
            --color-cover-pattern-1: rgba(240, 62, 62, 0.08);
            --color-cover-pattern-2: rgba(253, 126, 20, 0.05);
            --color-accent-shadow: rgba(240, 62, 62, 0.25);
            --shadow-card: 0 10px 30px rgba(240, 62, 62, 0.15);
            --shadow-glow: 0 0 50px rgba(240, 62, 62, 0.2);
            --font-body: 'Montserrat', sans-serif;
            --font-display: 'Bebas Neue', 'Montserrat', sans-serif;
        }""",

        "Dark Mode Elegante": """:root {
            --color-bg: #121212;
            --color-bg-warm: #181818;
            --color-bg-cool: #282828;
            --color-text: #e0e0e0;
            --color-text-secondary: #a0a0a0;
            --color-text-light: #606060;
            --color-accent: #bb86fc;
            --color-accent-light: #dfb8ff;
            --color-accent-soft: rgba(187,134,252,0.1);
            --color-accent-border: rgba(187,134,252,0.3);
            --gradient-accent: linear-gradient(135deg, #bb86fc 0%, #3700b3 100%);
            --gradient-dark: linear-gradient(160deg, #000000 0%, #121212 40%, #181818 70%, #bb86fc 100%);
            --gradient-warm: linear-gradient(135deg, #181818 0%, #282828 100%);
            --color-cover-card-bg: rgba(0, 0, 0, 0.8);
            --color-cover-glow-1: rgba(187, 134, 252, 0.15);
            --color-cover-glow-2: rgba(55, 0, 179, 0.1);
            --color-cover-pattern-1: rgba(187, 134, 252, 0.06);
            --color-cover-pattern-2: rgba(55, 0, 179, 0.04);
            --color-accent-shadow: rgba(187, 134, 252, 0.2);
            --shadow-card: 0 4px 20px rgba(0,0,0,0.8);
            --shadow-glow: 0 0 40px rgba(187, 134, 252, 0.15);
            --font-body: 'Proxima Nova', 'Inter', sans-serif;
            --font-display: 'Proxima Nova', 'Inter', sans-serif;
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
