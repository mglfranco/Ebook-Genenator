import os
from dotenv import load_dotenv

load_dotenv(".env")
api_key = os.getenv("GEMINI_API_KEY")

try:
    from google import genai
    client = genai.Client(api_key=api_key)
    print("Models suportados na chave atual:")
    for m in client.models.list():
        print(f"- {m.name}")
except Exception as e:
    print("ERRO:", e)
