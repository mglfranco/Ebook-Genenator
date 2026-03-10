import json
import os
import uuid
import time
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from api.chat_handler import processar_mensagem
from api.content_generator import gerar_conteudo_capitulo
from api.text_corrector import corrigir_capitulos
from api.image_generator import generate_all_images
from api.pdf_engine import generate_pdf
from api.epub_engine import create_epub, inject_qr_codes
from supabase import create_client, Client

_PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(_PROJECT_ROOT / ".env")

app = FastAPI(title="BookBot SaaS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None

_ASSETS_DIR = _PROJECT_ROOT / "assets"
_OUTPUT_DIR = _PROJECT_ROOT / "output"
_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class GenerateRequest(BaseModel):
    niche: str
    artStyle: str
    coverStyle: str
    pageLayout: str
    writingTone: str
    prompt: str

jobs = {}

def process_book_task(job_id: str, req: GenerateRequest):
    try:
        jobs[job_id] = {"status": "writing", "progress": 5, "message": "Iniciando Roteirização por IA..."}
        
        # Mapeamento do Wizard para Variáveis de Engine
        # Page layout define bleed ou margens
        bleed = 0 if req.pageLayout == "Livro de Fotografia (Sangria Total)" else 5
        colorful_mode = (req.artStyle == "Aquarela Clássica" or req.artStyle == "Anime Makoto Shinkai")
        # Cover style goes to theme
        theme_map = {
            "Minimalista Elegante": "Minimalist White",
            "Tipográfico Forte": "Minimalist Dark",
            "Manga Style (PB)": "Classic Noir",
            "Sci-Fi Neon": "Sci-Fi Neon",
            "Clássico Acadêmico": "Minimalist White"
        }
        theme = theme_map.get(req.coverStyle, "Minimalist White")

        tema_completo = f"{theme} (Arte: {req.artStyle})"
        
        # 1. Estrutura do livro
        jobs[job_id]["message"] = "Desenhando a Estrutura (Chapters)..."
        process_dict = processar_mensagem(
            historico=[{"role": "assistant", "content": "Olá, sou o SaaS BookBot."}],
            mensagem_usuario=req.prompt,
            theme=tema_completo,
            style=req.writingTone,
            audience=req.niche,
            language="Português"
        )
        
        ebook_data = process_dict.get("ebook_data")
        if not ebook_data:
            raise Exception("A IA falhou em retornar o JSON com os Capítulos.")
            
        titulo_livro = ebook_data.get("title", "Obra de Arte Digital")
        capitulos_lista = ebook_data.get("chapters", [])[:6] # Cap_limit to 6 for speed
        total_cap = len(capitulos_lista)
        
        if total_cap == 0:
             raise Exception("A IA não listou Capítulos para esta história.")

        raw_capitulos = []
        for idx, ch in enumerate(capitulos_lista):
            jobs[job_id]["message"] = f"Escrevendo Capítulo {idx+1}/{total_cap}..."
            jobs[job_id]["progress"] = 10 + int((idx / total_cap) * 30)
            
            content_md = gerar_conteudo_capitulo(
                titulo_livro=titulo_livro,
                titulo_capitulo=ch["title"],
                numero_capitulo=idx + 1,
                total_capitulos=total_cap,
                paginas=ch.get("pages", 3),
                tema_historia=tema_completo,
                ideia_principal=req.prompt,
                idioma="Português",
                publico_alvo=req.niche,
                estilo_escrita=req.writingTone,
            )
            raw_capitulos.append({
                "title": ch["title"],
                "content": content_md,
                "content_md": content_md
            })
            
        raw_capitulos = corrigir_capitulos(raw_capitulos)
        
        # 2. Markdown to HTML
        jobs[job_id] = {"status": "html", "progress": 45, "message": "Renderizando códigos visuais..."}
        import markdown
        job_assets_dir = str(_ASSETS_DIR / job_id)
        Path(job_assets_dir).mkdir(parents=True, exist_ok=True)
        output_pdf_path = str(_OUTPUT_DIR / f"{job_id}.pdf")
        
        chapters_data = []
        for i, ch in enumerate(raw_capitulos):
            content_html = markdown.markdown(ch.get("content", ch.get("content_md", "")))
            chapters_data.append({
                "title": ch.get("title", ""),
                "content": ch.get("content", ""),
                "content_html": content_html,
            })
            
        # 3. Imagens
        jobs[job_id] = {"status": "images", "progress": 55, "message": "Estúdio de Imagens Operando..."}
        image_paths = generate_all_images(
            chapters=chapters_data,
            theme=tema_completo,
            assets_dir=job_assets_dir,
            colorful_mode=colorful_mode,
            frequency="Apenas Imagem de Capa e Hero"
        )
        
        # 4. Weasyprint PDF
        jobs[job_id] = {"status": "weasyprint", "progress": 80, "message": "Compilando Matriz PDF de Alta Qualidade..."}
        pdf_path = generate_pdf(
            title=titulo_livro,
            author="BookBot Platform",
            theme=theme,
            chapters=raw_capitulos,
            image_paths=image_paths,
            output_path=output_pdf_path,
            bleed_mm=bleed,
            colorful_mode=colorful_mode
        )
        
        # 5. Cloud Sync Supabase
        jobs[job_id] = {"status": "sync", "progress": 95, "message": "Sincronizando com a Nuvem..."}
        pdf_public_url = ""
        if supabase:
            file_name_in_bucket = f"{job_id}.pdf"
            supabase.storage.from_("ebooks").upload(
                path=file_name_in_bucket,
                file=os.path.abspath(output_pdf_path),
                file_options={"content-type": "application/pdf"}
            )
            pdf_public_url = supabase.storage.from_("ebooks").get_public_url(file_name_in_bucket)
            
            # Update Database
            supabase.table("generations").update({
                "status": "finished",
                "pdf_url": pdf_public_url
            }).eq("id", job_id).execute()
        
        jobs[job_id] = {
            "status": "complete", 
            "progress": 100, 
            "message": "E-book Finalizado!",
            "result": {
                "title": titulo_livro,
                "pdf_url": pdf_public_url
            }
        }
        
    except Exception as e:
        jobs[job_id] = {"status": "error", "message": str(e), "progress": 0}
        if supabase:
             supabase.table("generations").update({
                "status": "error"
             }).eq("id", job_id).execute()

@app.post("/api/generate")
async def generate_ebook(req: GenerateRequest, background_tasks: BackgroundTasks):
    job_id = uuid.uuid4().hex[:12] # Fallback
    
    # 1. Start generation entry in Supabase Native
    if supabase:
        try:
            resp = supabase.table("generations").insert({
                "user_prompt": req.prompt,
                "niche": req.niche,
                "art_style": req.artStyle,
                "cover_style": req.coverStyle,
                "writing_tone": req.writingTone,
                "layout_style": req.pageLayout,
                "status": "processing"
            }).execute()
            if resp.data and len(resp.data) > 0:
                 job_id = resp.data[0]['id']
        except Exception as e:
             print("Erro salvando Supabase Generation:", e)

    jobs[job_id] = {"status": "queued", "progress": 0, "message": "Alocando GPUs..."}
    background_tasks.add_task(process_book_task, job_id, req)
    return {"job_id": job_id}

@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    # Retrieve real-time metrics mapped to front-end loader
    return jobs.get(job_id, {"status": "unknown", "message": "Buscando Status...", "progress": 0})

@app.get("/api/library")
async def get_library():
    if not supabase:
        return []
    try:
        # Busca prateleira
        response = supabase.table("generations").select("*").order("created_at", desc=True).limit(50).execute()
        return response.data
    except Exception as e:
        print("Erro lendo biblioteca: ", e)
        return []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
