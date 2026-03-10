"""
Gerador de Imagens para E-books — IA Gemini + Pillow Fallback
===============================================================
Gera imagens com IA generativa (Gemini) para cada capítulo.
Se o modelo de imagem falhar (quota, etc.), cria arte geométrica
profissional com Pillow como fallback.
"""

import base64
import hashlib
import os
import math
import random
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------
# Paletas de cores por tema
# ---------------------------------------------------------------
THEME_PALETTES = {
    "Minimalista Moderno": {
        "bg": [(10, 10, 10), (26, 26, 26)],
        "accent": [(34, 34, 34), (85, 85, 85)],
        "glow": (100, 100, 100),
    },
    "Fantasia Épica": {
        "bg": [(26, 15, 8), (44, 30, 22)],
        "accent": [(139, 69, 19), (205, 133, 63)],
        "glow": (139, 69, 19),
    },
    "Corporativo Clean": {
        "bg": [(10, 22, 40), (21, 34, 56)],
        "accent": [(0, 51, 102), (26, 115, 232)],
        "glow": (0, 80, 158),
    },
    "Sci-Fi Neon": {
        "bg": [(5, 6, 8), (11, 12, 16)],
        "accent": [(69, 162, 158), (102, 252, 241)],
        "glow": (102, 252, 241),
    },
    "Romance Clássico": {
        "bg": [(26, 15, 18), (45, 31, 36)],
        "accent": [(183, 110, 121), (209, 141, 150)],
        "glow": (183, 110, 121),
    },
    "Cyberpunk": {
        "bg": [(5, 1, 8), (18, 4, 29)],
        "accent": [(255, 0, 255), (243, 230, 0)],
        "glow": (255, 0, 255),
    },
    "Vintage / Retrô": {
        "bg": [(26, 16, 12), (62, 39, 35)],
        "accent": [(141, 110, 99), (161, 136, 127)],
        "glow": (141, 110, 99),
    },
    "Aquarela Suave": {
        "bg": [(10, 25, 41), (26, 47, 69)],
        "accent": [(93, 173, 226), (174, 214, 241)],
        "glow": (93, 173, 226),
    },
}


def _get_palette(theme: str) -> dict:
    return THEME_PALETTES.get(theme, THEME_PALETTES["Minimalista Moderno"])


# ---------------------------------------------------------------
# Tentativa 1: Nano Banana (gemini-2.5-flash-image-preview)
# ---------------------------------------------------------------
def _try_gemini_image(prompt: str, output_path: str, colorful_mode: bool = False) -> bool:
    """Tenta gerar imagem via Gemini Nano Banana (gemini-2.5-flash-image).
    Usa generate_content com response_modalities=['image'] para native image generation.
    Implementa backoff exponencial conforme regras Antigravity.
    Retorna True se sucesso.
    """
    import time

    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return False

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        # Backoff exponencial: 3 tentativas (1s, 2s, 4s)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash-image",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                    ),
                )

                # Extract image from response parts
                if response.candidates and response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                            img_bytes = part.inline_data.data
                            img = Image.open(BytesIO(img_bytes))

                            # Resize to match ebook constraints
                            if colorful_mode:
                                img = img.resize((800, 1200), Image.LANCZOS)
                            else:
                                img = img.resize((800, 450), Image.LANCZOS)

                            img.save(output_path, format="JPEG", quality=92)
                            print(f"[IMG] ✓ Nano Banana gerou imagem: {output_path}")
                            return True

                print(f"[IMG] Nano Banana: resposta sem imagem (tentativa {attempt+1})")
                return False

            except Exception as retry_err:
                err_str = str(retry_err)
                if "429" in err_str or "quota" in err_str.lower() or "rate" in err_str.lower():
                    wait = 2 ** attempt  # 1s, 2s, 4s
                    print(f"[IMG] Rate limit Nano Banana, aguardando {wait}s (tentativa {attempt+1}/{max_retries})...")
                    time.sleep(wait)
                    continue
                else:
                    print(f"[IMG] Nano Banana erro: {err_str[:120]}")
                    return False

        return False

    except Exception as e:
        print(f"[IMG] Nano Banana falhou: {str(e)[:120]}")
        return False


# ---------------------------------------------------------------
# Fallback 1: Pollinations.ai (Free Text-to-Image AI)
# ---------------------------------------------------------------
def _try_pollinations_image(prompt: str, output_path: str, colorful_mode: bool = False) -> bool:
    """Fallback gratuito que gera imagens por IA caso o Gemini seja barrado por Payload/Billing."""
    try:
        import urllib.request
        from urllib.parse import quote_plus
        
        W, H = (800, 1200) if colorful_mode else (800, 450)
        # Adding seed to bypass cache occasionally, though not strictly required
        seed = random.randint(1, 999999)
        url = f"https://image.pollinations.ai/prompt/{quote_plus(prompt)}?width={W}&height={H}&nologo=true&seed={seed}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=6) as response, open(output_path, 'wb') as out_file:
            out_file.write(response.read())
            
        print(f"[IMG] ✓ Pollinations.ai gerou imagem: {output_path}")
        return True
    except Exception as e:
        print(f"[IMG] Pollinations falhou: {str(e)[:100]}, usando fallback geométrico Pillow")
        return False


# ---------------------------------------------------------------
# Fallback 1.5: Replicate (Flux.1 / SDXL LoRAs)
# ---------------------------------------------------------------
def _try_replicate_image(prompt: str, output_path: str, colorful_mode: bool = False, theme: str = "") -> bool:
    """Motor Visual Premium via API Replicate (Modelos Open-Source State-of-the-Art)"""
    replicate_api_token = os.getenv("REPLICATE_API_TOKEN", "")
    if not replicate_api_token:
        return False
        
    try:
        import replicate
        import urllib.request
        
        # Flux.1-schnell (Extremamente rápido e altamente responsivo a estilos complexos)
        model_id = "black-forest-labs/flux-schnell" 
        print(f"[IMG] Replicate LPU (Flux.1) acionado. Processando renderização para o estilo '{theme}'...")
        
        output = replicate.run(
            model_id,
            input={
                "prompt": prompt,
                "go_fast": True,
                "num_outputs": 1,
                "aspect_ratio": "9:16" if colorful_mode else "16:9",
                "output_format": "jpg",
                "output_quality": 85
            }
        )
        
        if output and len(output) > 0:
            url = output[0]
            if not isinstance(url, str):
                 url = str(url) # Parser de obj para str
            
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=20) as response, open(output_path, 'wb') as out_file:
                out_file.write(response.read())
            print(f"[IMG] ✓ Replicate LPU gerou a ilustração com sucesso: {output_path}")
            return True
            
        return False
    except Exception as e:
        print(f"[IMG] Replicate LPU falhou (Pode estar sem GPU allocada ou key invalida): {str(e)[:100]}")
        return False


# ---------------------------------------------------------------
# Fallback 2: Pillow — Arte Geométrica Profissional
# ---------------------------------------------------------------
def _create_pillow_image(
    chapter_title: str,
    chapter_index: int,
    theme: str,
    output_path: str,
    colorful_mode: bool = False,
) -> str:
    """Cria arte geométrica profissional com Pillow."""
    palette = _get_palette(theme)
    W, H = (800, 1200) if colorful_mode else (800, 450)
    seed = int(hashlib.md5(chapter_title.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    # Gradient background
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    bg1, bg2 = palette["bg"]
    for y in range(H):
        r = int(bg1[0] + (bg2[0] - bg1[0]) * y / H)
        g = int(bg1[1] + (bg2[1] - bg1[1]) * y / H)
        b = int(bg1[2] + (bg2[2] - bg1[2]) * y / H)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Geometric shapes
    accent1, accent2 = palette["accent"]
    for _ in range(rng.randint(8, 15)):
        shape_type = rng.choice(["circle", "line", "rect"])
        alpha = rng.randint(15, 60)
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        odraw = ImageDraw.Draw(overlay)
        col = (
            rng.choice([accent1, accent2, palette["glow"]])
            + (alpha,)
        )

        if shape_type == "circle":
            cx = rng.randint(-100, W + 100)
            cy = rng.randint(-100, H + 100)
            radius = rng.randint(40, 200)
            odraw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=col)
        elif shape_type == "line":
            x1, y1 = rng.randint(0, W), rng.randint(0, H)
            angle = rng.uniform(0, math.pi * 2)
            length = rng.randint(100, 500)
            x2 = int(x1 + math.cos(angle) * length)
            y2 = int(y1 + math.sin(angle) * length)
            odraw.line([(x1, y1), (x2, y2)], fill=col, width=rng.randint(1, 4))
        else:
            x1 = rng.randint(-50, W - 50)
            y1 = rng.randint(-50, H - 50)
            w = rng.randint(30, 150)
            h = rng.randint(30, 150)
            odraw.rectangle([x1, y1, x1 + w, y1 + h], fill=col)

        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    # Apply blur for soft look
    img = img.filter(ImageFilter.GaussianBlur(radius=3))

    # Glow orb
    glow_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow_overlay)
    gx = rng.randint(W // 4, 3 * W // 4)
    gy = rng.randint(H // 4, 3 * H // 4)
    for r in range(120, 0, -2):
        a = int(40 * (1 - r / 120))
        gdraw.ellipse(
            [gx - r, gy - r, gx + r, gy + r],
            fill=palette["glow"] + (a,),
        )
    img = Image.alpha_composite(img.convert("RGBA"), glow_overlay).convert("RGB")

    # Glass card overlay with chapter title
    card_w, card_h = 420, 100
    card_x = (W - card_w) // 2
    card_y = (H - card_h) // 2
    card_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(card_overlay)
    cdraw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=16,
        fill=(20, 20, 40, 140),
    )
    cdraw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=16,
        outline=accent1 + (80,),
        width=1,
    )

    # Title text
    try:
        font = ImageFont.truetype("segoeui.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
    text = chapter_title[:40]
    bbox = cdraw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    tx = card_x + (card_w - tw) // 2
    ty = card_y + (card_h - 28) // 2
    cdraw.text((tx, ty), text, font=font, fill=(255, 255, 255, 230))

    # Chapter number badge
    num_text = f"Cap. {chapter_index + 1}"
    try:
        small_font = ImageFont.truetype("segoeui.ttf", 12)
    except OSError:
        small_font = ImageFont.load_default()
    cdraw.text((card_x + 15, card_y + 10), num_text, font=small_font, fill=accent2 + (200,))

    img = Image.alpha_composite(img.convert("RGBA"), card_overlay).convert("RGB")
    img.save(output_path, quality=92)
    print(f"[IMG] ✓ Pillow gerou imagem: {output_path}")
    return output_path


# ---------------------------------------------------------------
# API Pública
# ---------------------------------------------------------------
def generate_all_images(
    chapters: list[dict],
    theme: str,
    assets_dir: str,
    colorful_mode: bool = False,
    frequency: str = "Em todos os Capítulos"
) -> list[str]:
    """Gera imagens para cada capítulo (Gemini → Pillow fallback). Respeita frequência definida."""
    Path(assets_dir).mkdir(parents=True, exist_ok=True)
    paths = []

    for i, chapter in enumerate(chapters):
        # Validação da Regra de Frequência de Imagens (Reduz chamadas a API)
        should_generate = True
        if frequency == "Nenhuma Imagem":
            should_generate = False
        elif frequency == "Apenas Capa e Índice" and i > 1:
            should_generate = False
        elif frequency == "A cada 2 Capítulos" and i % 2 != 0:
            should_generate = False
        elif frequency == "A cada 3 Capítulos" and i % 3 != 0:
            should_generate = False
            
        if not should_generate:
            paths.append(None)
            continue

        filename = f"chapter_{i + 1}.png"
        output_path = str(Path(assets_dir) / filename)

        # Extract chapter context to inject into prompt for specific details
        chapter_content_snippet = chapter.get("content", "")[:700].replace("\n", " ").strip()
        
        # Prompt dinâmico de IA (Ilustração vs Corporativo/Educação)
        is_corporate = any(kw in theme for kw in ["Wireframes", "Business", "Infográficos", "Gráficos", "Minimalista"])
        
        if is_corporate:
            if colorful_mode:
                 ai_prompt = (
                    f"Vertical portrait wallpaper 9:16 aspect ratio. Create a clean, professional, high-end {theme} background "
                    f"for a business or academic chapter titled '{chapter['title']}'. The visual should be abstract, conceptual, "
                    f"or a clean diagram loosely inspired by: '{chapter_content_snippet}'. No text in the image. "
                    f"Corporate, clean presentation style."
                )
            else:
                 ai_prompt = (
                    f"Create a clean, professional, high-end {theme} specific graphic, chart, or illustration "
                    f"for a business or academic chapter titled '{chapter['title']}'. Ensure it looks like a premium "
                    f"editorial asset, loosely inspired by: '{chapter_content_snippet}'. No text in the image. "
                    f"Corporate, clean presentation style."
                )
        else:
            # IA inteligente para ler cenas: Se tiver dialogo ou lutas e for mangá/ficção:
            is_action_scene = any(word in chapter_content_snippet.lower() for word in ["espada", "luta", "correu", "tiro", "sangue", "grito"])
            is_dialog_scene = ("\"" in chapter_content_snippet or "—" in chapter_content_snippet or "disse" in chapter_content_snippet.lower())
            
            scene_focus = "focus on the characters, hero, and environment"
            if is_action_scene:
                scene_focus = "focus heavily on the high-stakes action scene, combat motion, and dramatic environment"
            elif is_dialog_scene:
                scene_focus = "focus on an expressive dialogue scene between characters, showing their emotions and interactions"

            if colorful_mode:
                ai_prompt = (
                    f"Vertical portrait wallpaper 9:16 aspect ratio. Create a highly detailed illustration for a book chapter titled "
                    f"'{chapter['title']}'. The visual MUST vividly {scene_focus} described in this excerpt: "
                    f"'{chapter_content_snippet}'. Style: {theme}. The image should be an edge-to-edge wallpaper, "
                    f"immersively capturing the specific scene moment. No text."
                )
            else:
                ai_prompt = (
                    f"Create a highly detailed, elegant illustration for a book chapter titled "
                    f"'{chapter['title']}'. The visual MUST vividly {scene_focus} described in this excerpt: "
                    f"'{chapter_content_snippet}'. Style: {theme}. The image should be atmospheric "
                    f"and capture the scene specifically. No text in the image. "
                    f"Wide format (16:9), high quality, editorial illustration style."
                )

        # Roteador Multi-API (Replicate Flux -> Nano Banana -> Pollinations -> Pillow)
        # O Replicate (LPU Flux) toma a dianteira na Produção Premium se a API Key for viável.
        replicate_prompt = ai_prompt + f" Detailed aesthetics: {theme}"
        
        if not _try_replicate_image(replicate_prompt, output_path, colorful_mode, theme):
            if not _try_gemini_image(ai_prompt, output_path, colorful_mode):
                if not _try_pollinations_image(replicate_prompt, output_path, colorful_mode):
                    _create_pillow_image(
                        chapter_title=chapter["title"],
                        chapter_index=i,
                        theme=theme,
                        output_path=output_path,
                        colorful_mode=colorful_mode
                    )

        paths.append(output_path)

    return paths
