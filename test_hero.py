# -*- coding: utf-8 -*-
import os
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(".env")
print(f"KEY: {bool(os.getenv('GEMINI_API_KEY'))}")

from api.content_generator import gerar_conteudo_capitulo
from api.image_generator import generate_all_images
from api.pdf_engine import generate_pdf

def run_test():
    print("🚀 Iniciando Teste Automatizado: Herói e Ambiente")
    
    title = "A Lenda de Kael, o Cavaleiro de Prata"
    theme = "Fantasia Épica (Estilo artístico recomendado para imagens geradas: Pintura a Óleo)"
    chapters = [
        {
            "title": "A Caverna de Cristal",
            "content": "Kael, um guerreiro alto vestindo uma armadura de prata brilhante, adentrou a Caverna de Cristal. O ambiente era escuro, iluminado apenas pelo brilho azul mágico das estalactites cristalinas penduradas no teto. Ele segurava sua espada flamejante com firmeza, sentindo o ardor do fogo iluminar as rochas ao seu redor."
        },
        {
            "title": "O Dragão das Sombras",
            "content": "No fundo da caverna, Kael encontrou o monstruoso Dragão das Sombras. Uma fera de escamas negras de vinte metros, cujos olhos brilhavam como rubis. O dragão cuspiu um fogo roxo intenso em direção ao guerreiro de prata, derretendo o gelo cristalino."
        }
    ]
    
    print("1️⃣ Construindo Pastas de Arquivos Temporários")
    job_dir = Path("assets/test_hero_job")
    job_dir.mkdir(parents=True, exist_ok=True)
    
    print("2️⃣ Solicitando Imagens ao Nano Banana 2 (Imagen 3.0)")
    start = time.time()
    try:
        image_paths = generate_all_images(chapters, theme, str(job_dir), colorful_mode=False)
        print(f"✅ Imagens geradas com sucesso em {time.time() - start:.2f} segundos!")
        for p in image_paths:
            print(f"   -> Encontrado: {p}")
    except Exception as e:
        print(f"❌ Erro na geração de imagens: {e}")
        return
        
    print("3️⃣ Compilando o PDF Final (WeasyPrint) com Temas e Sangria")
    try:
        pdf_path = "output/test_hero.pdf"
        generate_pdf(
            title=title,
            author="BookBot Tester",
            theme=theme,
            chapters=chapters,
            image_paths=image_paths,
            output_path=pdf_path,
            bleed_mm=3,
            colorful_mode=False
        )
        print(f"✅ PDF '{pdf_path}' Compilado e montado com sucesso!")
        
        if os.path.exists(pdf_path):
            size_mb = os.path.getsize(pdf_path) / (1024*1024)
            print(f"   -> Tamanho do PDF Final: {size_mb:.2f} MB")
            
    except Exception as e:
        print(f"❌ Erro na compilação do WeasyPrint: {e}")
        return

    print("🎉 TEXTO FINALIZADO COM SUCESSO!")

if __name__ == '__main__':
    run_test()
