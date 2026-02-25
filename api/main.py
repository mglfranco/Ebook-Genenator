"""
API Geradora de E-books V4 — Chat + Geração Autônoma
======================================================
Três fluxos:
  1. /chat              → conversa com IA para definir o e-book
  2. /generate-from-form → gera conteúdo via Gemini a partir de títulos+páginas
  3. /generate-ebook     → aceita conteúdo Markdown pronto
"""

import os
import uuid
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from api.models import EbookRequest, EbookFormRequest
from api.text_corrector import corrigir_capitulos, corrigir_texto
from api.image_generator import generate_all_images
from api.pdf_engine import generate_pdf
from api.epub_engine import create_epub, inject_qr_codes
from api.content_generator import gerar_todos_capitulos
from api.chat_handler import processar_mensagem
import zipfile
import markdown


# ---------------------------------------------------------------------------
# Carregar .env
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

_ASSETS_DIR = _PROJECT_ROOT / "assets"
_OUTPUT_DIR = _PROJECT_ROOT / "output"
_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Aplicação FastAPI
# ---------------------------------------------------------------------------
app = FastAPI(
    title="BookBot — Gerador de E-books com IA",
    description="Chat com IA + Geração autônoma de e-books profissionais.",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Modelos para o Chat
# ---------------------------------------------------------------------------
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    history: list[ChatMessage] = Field(default_factory=list)
    message: str
    theme: Optional[str] = "Minimalista Moderno"
    style: Optional[str] = "Profissional"
    audience: Optional[str] = "Público geral"
    language: Optional[str] = "Português Brasileiro"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/", tags=["Frontend"])
async def serve_frontend():
    """Servir a página do BookBot."""
    return FileResponse(
        str(_PROJECT_ROOT / "static" / "index.html"),
        media_type="text/html",
    )


@app.get("/health", tags=["Saúde"])
async def health_check():
    return {
        "status": "ativo",
        "servico": "BookBot V5",
        "versao": "5.0.0",
        "gemini": bool(os.getenv("GEMINI_API_KEY")),
    }


@app.post("/chat", tags=["Chat"])
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint de chat — processa mensagem e retorna resposta + dados do ebook se prontos.
    """
    try:
        historico = [
            {"role": m.role, "content": m.content}
            for m in request.history
        ]

        # Build context from sidebar settings
        contexto_extra = (
            f"\n[CONFIGURAÇÕES DO USUÁRIO: "
            f"Tema='{request.theme}', "
            f"Estilo='{request.style}', "
            f"Público='{request.audience}', "
            f"Idioma='{request.language}']"
        )

        resultado = processar_mensagem(
            historico=historico,
            mensagem_usuario=request.message + contexto_extra,
        )

        return {
            "response": resultado["response"],
            "ebook_data": resultado["ebook_data"],
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro no chat: {str(e)}",
        )


@app.post("/generate-from-form", tags=["E-book"])
async def generate_from_form(request: EbookFormRequest):
    """Gerar ebook a partir do formulário/chat (conteúdo gerado via Gemini)."""
    job_id = uuid.uuid4().hex[:12]
    job_assets_dir = str(_ASSETS_DIR / job_id)
    output_pdf_path = str(_OUTPUT_DIR / f"ebook_{job_id}.pdf")
    output_epub_path = str(_OUTPUT_DIR / f"ebook_{job_id}.epub")
    output_zip_path = str(_OUTPUT_DIR / f"ebook_bundle_{job_id}.zip")

    try:
        chapters_input = [
            {"title": ch.title, "pages": ch.pages}
            for ch in request.chapters
        ]
        chapters_data = gerar_todos_capitulos(
            titulo_livro=request.title,
            capitulos=chapters_input,
            tema=request.theme,
        )

        chapters_data = corrigir_capitulos(chapters_data)

        image_paths = generate_all_images(
            chapters=chapters_data,
            theme=request.theme,
            assets_dir=job_assets_dir,
        )

        # 3. Gerar PDF
        pdf_path = generate_pdf(
            title=request.title,
            author=request.author,
            theme=request.theme,
            chapters=chapters_data,
            image_paths=image_paths,
            output_path=output_pdf_path,
        )

        # 4. Gerar EPUB
        epub_path = create_epub(
            title=request.title,
            author=request.author,
            chapters_data=chapters_data,
            output_path=output_epub_path,
            cover_image_path=image_paths[0] if image_paths else None
        )

        # 5. Criar ZIP com ambos os formatos
        with zipfile.ZipFile(output_zip_path, 'w') as zipf:
            zipf.write(pdf_path, arcname=f"{request.title}.pdf")
            zipf.write(epub_path, arcname=f"{request.title}.epub")

        return FileResponse(
            path=output_zip_path,
            media_type="application/zip",
            filename=f"{request.title}_bundle.zip",
            headers={
                "Content-Disposition": f'attachment; filename="{request.title}_bundle.zip"'
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na geração do e-book: {str(e)}",
        )


@app.post("/generate-ebook", tags=["E-book"])
async def generate_ebook(request: EbookRequest):
    """Gerar ebook a partir de conteúdo Markdown já escrito."""
    job_id = uuid.uuid4().hex[:12]
    job_assets_dir = str(_ASSETS_DIR / job_id)
    output_pdf_path = str(_OUTPUT_DIR / f"ebook_{job_id}.pdf")
    output_epub_path = str(_OUTPUT_DIR / f"ebook_{job_id}.epub")
    output_zip_path = str(_OUTPUT_DIR / f"ebook_bundle_{job_id}.zip")

    try:
        chapters_data = []
        for ch in request.chapters:
            content_md = ch.content
            # Corrige ortografia
            content_md = corrigir_texto(content_md)
            # Converte HTML
            content_html = markdown.markdown(content_md)
            # Tenta gerar QR Codes
            content_html = inject_qr_codes(content_html, job_assets_dir, len(chapters_data))
            
            chapters_data.append({
                "title": ch.title,
                "content": content_md,
                "content_md": content_md,
                "content_html": content_html,
            })

        image_paths = generate_all_images(
            chapters=chapters_data,
            theme=request.theme,
            assets_dir=job_assets_dir,
        )

        pdf_path = generate_pdf(
            title=request.title,
            author=request.author,
            theme=request.theme,
            chapters=chapters_data,
            image_paths=image_paths,
            output_path=output_pdf_path,
        )

        epub_path = create_epub(
            title=request.title,
            author=request.author,
            chapters_data=chapters_data,
            output_path=output_epub_path,
            cover_image_path=image_paths[0] if image_paths else None
        )

        with zipfile.ZipFile(output_zip_path, 'w') as zipf:
            zipf.write(pdf_path, arcname=f"{request.title}.pdf")
            zipf.write(epub_path, arcname=f"{request.title}.epub")

        return FileResponse(
            path=output_zip_path,
            media_type="application/zip",
            filename=f"{request.title}_bundle.zip",
            headers={
                "Content-Disposition": f'attachment; filename="{request.title}_bundle.zip"'
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na geração do e-book: {str(e)}",
        )
