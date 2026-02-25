"""
Conversor EPUB e Extrator de QR Codes
======================================
Este módulo contém funções para:
1. Extrair URLs do texto e gerar QR Codes em imagens .png
2. Compilar capítulos gerados em um arquivo .epub válido
"""

import os
import re
from pathlib import Path
import qrcode
from PIL import Image
from ebooklib import epub

def generate_qr_code(url: str, output_path: str, color: tuple = (124, 58, 237)):
    """Gera um QR code elegante para a URL fornecida e salva em output_path."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color=color, back_color="transparent").convert('RGBA')
    # Background branco redondo para contraste
    bg = Image.new('RGBA', img.size, (255, 255, 255, 255))
    out = Image.alpha_composite(bg, img)
    out.save(output_path, "PNG")
    return output_path


def inject_qr_codes(content_html: str, assets_dir: str, chapter_idx: int) -> str:
    """
    Procura links (<a href="...">) no HTML do capítulo.
    Se encontrar, gera QR codes e insere um bloco visual no final do capítulo.
    """
    urls = re.findall(r'href=[\'"]?([^\'" >]+)', content_html)
    # Filtra links internos (começam com #)
    urls = [u for u in set(urls) if u.startswith('http')]
    
    if not urls:
        return content_html

    qr_block = "<div class='qr-references' style='margin-top: 3rem; padding: 1.5rem; background: rgba(0,0,0,0.03); border-radius: 12px; page-break-inside: avoid;'>"
    qr_block += "<h3 style='font-size: 14px; color: #7c3aed; margin-bottom: 1rem; text-transform: uppercase; letter-spacing: 1px;'>Referências em QR Code</h3>"
    qr_block += "<div style='display: flex; gap: 1.5rem; flex-wrap: wrap;'>"

    for i, url in enumerate(urls[:4]): # Limita a 4 QRs por cap para espaço
        qr_filename = f"qr_cap{chapter_idx}_{i}.png"
        qr_path = str(Path(assets_dir) / qr_filename)
        generate_qr_code(url, qr_path)
        
        qr_block += f"""
        <div style='text-align: center; width: 120px;'>
            <img src="{qr_path}" width="100" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
            <p style='font-size: 10px; word-break: break-all; margin-top: 8px; color: #555;'>{url[:30]}...</p>
        </div>
        """
    qr_block += "</div></div>"
    
    return content_html + qr_block


def create_epub(
    title: str,
    author: str,
    chapters_data: list[dict],
    output_path: str,
    cover_image_path: str = None
) -> str:
    """Compila os dados dos capítulos em um arquivo .epub usando EbookLib."""
    book = epub.EpubBook()

    # Metadata
    book.set_identifier(f"id-{title.replace(' ', '')}")
    book.set_title(title)
    book.set_language('pt')
    book.add_author(author)

    if cover_image_path and os.path.exists(cover_image_path):
        with open(cover_image_path, 'rb') as f:
            book.set_cover("cover.jpg", f.read())

    epub_chapters = []
    
    # Adicionar base CSS para EPUB
    style = 'BODY { font-family: sans-serif; line-height: 1.6; } h1, h2 { color: #333; }'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    for i, chapter in enumerate(chapters_data):
        c = epub.EpubHtml(title=chapter['title'], file_name=f'chap_{i}.xhtml', lang='pt')
        
        # Estrutura HTML limpa para EPUB
        html_body = chapter.get('content_html') or chapter.get('content', '')
        content = f"<h1>{chapter['title']}</h1><br/>{html_body}"
        
        c.content = content
        c.add_item(nav_css)
        book.add_item(c)
        epub_chapters.append(c)

    # Definir TOC e SPINE
    book.toc = tuple(epub_chapters)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    book.spine = ['nav', *epub_chapters]

    # Salvar
    epub.write_epub(output_path, book)
    return output_path
