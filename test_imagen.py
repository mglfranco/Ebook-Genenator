import os
from dotenv import load_dotenv

load_dotenv(".env")
api_key = os.getenv("GEMINI_API_KEY")

from google import genai
from google.genai import types

client = genai.Client(api_key=api_key)

try:
    print("Testando imagen-3.0-generate-002...")
    res = client.models.generate_images(
        model="imagen-3.0-generate-002",
        prompt="A beautiful futuristic city with flying cars",
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="16:9",
            output_mime_type="image/jpeg",
        ),
    )
    print("Sucesso Imagen 3.0 Generate 002!")
except Exception as e:
    print("ERRO 002:", e)

try:
    print("Testando imagen-3.0-fast-generate-001...")
    res2 = client.models.generate_images(
        model="imagen-3.0-fast-generate-001",
        prompt="A beautiful futuristic city with flying cars",
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="16:9",
            output_mime_type="image/jpeg",
        ),
    )
    print("Sucesso Fast Generate 001!")
except Exception as e:
    print("ERRO FAST 001:", e)
