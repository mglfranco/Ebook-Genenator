import os
from pathlib import Path

# Configurações falsas de simulação
TITLE = "Micro Livro de Teste"
AUTHOR = "BookBot QA"
THEME = "Minimalista"
ASSETS_DIR = Path("assets/test_run")
OUTPUT_DIR = Path("output/test_run")

ASSETS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

raw_capitulos = [
    {
        "title": "Capítulo 1: O Teste",
        "content_md": "## Introdução\n\nEste é um teste **automatizado** super rápido para validar a pipeline."
    }
]

print("1. Processando HTML e MD...")
import markdown
from api.epub_engine import inject_qr_codes

chapters_data = []
for i, ch in enumerate(raw_capitulos):
    c_md = ch["content_md"]
    c_html = markdown.markdown(c_md)
    c_html = inject_qr_codes(c_html, str(ASSETS_DIR), i)
    chapters_data.append({
        "title": ch["title"],
        "content_md": c_md,
        "content_html": c_html,
    })

print("2. Simulando Imagens...")
image_paths = {0: ""} # Sem imagens para o teste rápido

print("3. Gerando PDF via WeasyPrint...")
from api.pdf_engine import generate_pdf
pdf_out = str(OUTPUT_DIR / "test.pdf")
generate_pdf(
    title=TITLE,
    author=AUTHOR,
    theme=THEME,
    chapters=chapters_data,
    image_paths=image_paths,
    output_path=pdf_out,
    bleed_mm=5
)
print(f" PDF gerado com sucesso em: {pdf_out}")

print("4. Gerando EPUB via EbookLib...")
from api.epub_engine import create_epub
epub_out = str(OUTPUT_DIR / "test.epub")
create_epub(
    title=TITLE,
    author=AUTHOR,
    chapters_data=chapters_data,
    output_path=epub_out
)
print(f" EPUB gerado com sucesso em: {epub_out}")

print("\n🚀 FULL PIPELINE EXECUTADA SEM ERROS!")
