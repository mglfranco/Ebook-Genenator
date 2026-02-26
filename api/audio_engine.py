"""
Módulo de Geração de Audiobook (TTS)
=====================================
Utiliza o Microsoft Edge-TTS para narrar os capítulos do e-book.
"""

import sys
import os
import subprocess
import tempfile
from pathlib import Path

def generate_audiobook_cli(title: str, chapters: list[dict], output_path: str) -> str:
    """
    Usa um subprocesso para chamar o CLI do edge-tts.
    """
    texto_livro = f"Bem-vindo ao audiolivro especial de {title}.\\n\\n"
    
    for i, ch in enumerate(chapters):
        texto_livro += f"Capítulo {i+1}: {ch['title']}.\\n\\n"
        # Limpa marcações markdown
        texto_limpo = ch.get("content", "").replace("#", "").replace("*", "").replace("`", "")
        texto_livro += texto_limpo + "\\n\\n"
        
    texto_livro += "Fim do audiolivro. Produzido com BookBot Studio."
    
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as f:
        f.write(texto_livro)
        temp_txt = f.name
        
    try:
        # Voz padrão PT-BR Neural do Edge
        voz = "pt-BR-AntonioNeural"
        cmd = ["edge-tts", "--voice", voz, "-f", temp_txt, "--write-media", output_path]
        subprocess.run(cmd, check=True)
    finally:
        os.remove(temp_txt)
        
    return output_path
