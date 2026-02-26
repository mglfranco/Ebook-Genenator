import requests
import json
import traceback

def test_health():
    try:
        res = requests.get('http://127.0.0.1:8000/health', timeout=5)
        print("HEALTH STATUS:", res.status_code, res.text)
        return res.status_code == 200
    except Exception as e:
        print("HEALTH ERROR:", e)
        return False

def test_chat():
    try:
        payload = {
            "message": "Crie um livro de 1 capitulo sobre maçãs",
            "history": [],
            "theme": "Minimalista",
            "style": "Profissional",
            "audience": "Geral",
            "language": "PT-BR"
        }
        res = requests.post('http://127.0.0.1:8000/chat', json=payload, timeout=30)
        print("CHAT STATUS:", res.status_code)
        try:
            print("CHAT RESP:", res.json())
        except:
            print("CHAT RAW:", res.text[:200])
    except Exception as e:
        print("CHAT ERROR:", e)

if __name__ == "__main__":
    if test_health():
        print("--- Backend is healthy, testing chat ---")
        test_chat()
    else:
        print("--- Backend is DOWN. Testing aborted. ---")
