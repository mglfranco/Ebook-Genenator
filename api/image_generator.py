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
        "bg": [(30, 30, 50), (45, 35, 65)],
        "accent": [(124, 58, 237), (167, 139, 250)],
        "glow": (124, 58, 237),
    },
    "Ficção Científica Neon": {
        "bg": [(5, 5, 25), (10, 10, 40)],
        "accent": [(0, 245, 212), (123, 47, 247)],
        "glow": (0, 245, 212),
    },
    "Aquarela Clássica": {
        "bg": [(60, 40, 50), (80, 50, 70)],
        "accent": [(240, 147, 251), (245, 87, 108)],
        "glow": (240, 147, 251),
    },
    "Corporativo Elegante": {
        "bg": [(25, 30, 35), (40, 45, 50)],
        "accent": [(45, 52, 54), (99, 110, 114)],
        "glow": (99, 110, 114),
    },
    "Vintage Retrô": {
        "bg": [(50, 35, 20), (70, 50, 30)],
        "accent": [(201, 149, 107), (139, 105, 20)],
        "glow": (201, 149, 107),
    },
    "Natureza Orgânica": {
        "bg": [(10, 35, 30), (20, 50, 40)],
        "accent": [(17, 153, 142), (56, 239, 125)],
        "glow": (17, 153, 142),
    },
}


def _get_palette(theme: str) -> dict:
    return THEME_PALETTES.get(theme, THEME_PALETTES["Minimalista Moderno"])


# ---------------------------------------------------------------
# Tentativa 1: Gemini Image Generation (google-genai SDK)
# ---------------------------------------------------------------
def _try_gemini_image(prompt: str, output_path: str, colorful_mode: bool = False) -> bool:
    """Tenta gerar imagem via Gemini. Retorna True se sucesso."""
    try:
        from google import genai
        from google.genai import types

        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            return False

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )

        # Extract image from response
        if response.candidates:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                    img_data = part.inline_data.data
                    if isinstance(img_data, str):
                        img_data = base64.b64decode(img_data)

                    img = Image.open(BytesIO(img_data))
                    
                    # Resize based on colorful mode (Vertical vs Horizontal)
                    if colorful_mode:
                        img = img.resize((800, 1200), Image.LANCZOS)
                    else:
                        img = img.resize((800, 450), Image.LANCZOS)
                        
                    img.save(output_path, quality=92)
                    print(f"[IMG] ✓ Gemini gerou imagem: {output_path}")
                    return True

        return False

    except Exception as e:
        print(f"[IMG] Gemini falhou: {str(e)[:100]}, usando fallback Pillow")
        return False


# ---------------------------------------------------------------
# Fallback: Pillow — Arte Geométrica Profissional
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
    colorful_mode: bool = False
) -> list[str]:
    """Gera imagens para cada capítulo (Gemini → Pillow fallback)."""
    Path(assets_dir).mkdir(parents=True, exist_ok=True)
    paths = []

    for i, chapter in enumerate(chapters):
        filename = f"chapter_{i + 1}.png"
        output_path = str(Path(assets_dir) / filename)

        # Prompt para Gemini (ilustração profissional)
        if colorful_mode:
            ai_prompt = (
                f"Vertical portrait wallpaper 9:16 aspect ratio. Create a professional, immersive full-page illustration for a book chapter titled "
                f"'{chapter['title']}'. Style: {theme}. The image should be an edge-to-edge wallpaper, "
                f"clean, and suitable to be used as a premium e-book background. No text in the image."
            )
        else:
            ai_prompt = (
                f"Create a professional, elegant illustration for a book chapter titled "
                f"'{chapter['title']}'. Style: {theme}. The image should be atmospheric, "
                f"clean, and suitable for a premium e-book. No text in the image. "
                f"Wide format (16:9), high quality, editorial illustration style."
            )

        # Tentar Gemini primeiro, depois Pillow
        if not _try_gemini_image(ai_prompt, output_path, colorful_mode):
            _create_pillow_image(
                chapter_title=chapter["title"],
                chapter_index=i,
                theme=theme,
                output_path=output_path,
                colorful_mode=colorful_mode
            )

        paths.append(output_path)

    return paths
