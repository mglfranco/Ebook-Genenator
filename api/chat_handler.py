"""
Chat Handler — Conversational AI para geração de e-books
==========================================================
Usa Gemini para conversar naturalmente com o usuário,
extrair parâmetros do e-book, e orquestrar a geração.
"""

import json
import os
import re
import google.generativeai as genai


_configured = False
_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash",
    "gemma-3-27b-it",
]


def _configure():
    global _configured
    if _configured:
        return
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não definida.")
    genai.configure(api_key=api_key)
    _configured = True


SYSTEM_PROMPT = """Você é o BookBot, um assistente de criação de e-books profissionais.
Seu papel é conversar com o usuário para entender exatamente que e-book ele quer criar.

## REGRAS:

1. Seja simpático, breve e direto. Use emojis moderadamente.
2. Você precisa coletar estas informações:
   - **title**: Título do livro
   - **author**: Nome do autor (se não informado, use "Autor")
   - **theme**: Tema visual (já vem configurado na sidebar)
   - **chapters**: Lista com título e quantidade de páginas de cada capítulo

3. As mensagens virão com metadata [CONFIGURAÇÕES DO USUÁRIO: ...] no final.
   Use essas configurações ao gerar o e-book. NÃO mencione essa metadata na resposta.
   Adapte o idioma da resposta conforme o campo "Idioma" das configurações.

4. Se o usuário der informações parciais, pergunte o que falta de forma natural.
5. Se o usuário disser algo vago como "crie um ebook sobre Python", sugira uma estrutura de capítulos e pergunte se ele concorda.
6. Quando tiver TODAS as informações, responda com uma confirmação E inclua um bloco JSON entre as tags <<<EBOOK_DATA>>> e <<<END_EBOOK_DATA>>> com a estrutura:

<<<EBOOK_DATA>>>
{
  "title": "...",
  "author": "...",
  "theme": "...",
  "chapters": [
    {"title": "...", "pages": N},
    ...
  ]
}
<<<END_EBOOK_DATA>>>

7. NUNCA gere o JSON antes de ter todos os dados confirmados.
8. Se o usuário pedir para mudar algo, ajuste e gere um novo JSON.
9. Sugira temas visuais proativamente quando fizer sentido.
10. NÃO coloque ```json ou blocos de código. Use APENAS as tags <<<EBOOK_DATA>>> e <<<END_EBOOK_DATA>>>.
11. Use o idioma definido nas configurações do usuário para responder.
"""



def processar_mensagem(
    historico: list[dict], 
    mensagem_usuario: str,
    theme: str = "Minimalista Moderno",
    style: str = "Profissional",
    audience: str = "Geral",
    language: str = "PT-BR"
) -> dict:
    """
    Processa uma mensagem do usuário via chat.

    Returns
    -------
    dict com:
        - response: texto da resposta do bot
        - ebook_data: dict com dados do ebook (ou None se ainda coletando)
    """
    _configure()

    # Construir histórico para o Gemini
    gemini_history = []
    for msg in historico:
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [msg["content"]]})

    last_error = None
    for model_name in _MODELS:
        try:
            custom_instruction = SYSTEM_PROMPT + f"""
            
[CONFIGURAÇÕES DO USUÁRIO]
Idioma: {language}
Público-Alvo: {audience}
Estilo da Escrita: {style}
Tema Visual do Livro (Importante para as Capas): {theme}
"""
            model = genai.GenerativeModel(
                model_name,
                system_instruction=custom_instruction,
            )
            chat = model.start_chat(history=gemini_history)
            response = chat.send_message(mensagem_usuario)
            response_text = response.text

            # Extrair dados do ebook se presentes
            ebook_data = _extrair_ebook_data(response_text)

            # Limpar tags do texto de resposta
            clean_text = re.sub(
                r'<<<EBOOK_DATA>>>.*?<<<END_EBOOK_DATA>>>',
                '',
                response_text,
                flags=re.DOTALL
            ).strip()

            return {
                "response": clean_text,
                "ebook_data": ebook_data,
            }

        except Exception as e:
            last_error = e
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower():
                import time
                time.sleep(10)
                continue
            elif "404" in error_str:
                continue
            else:
                raise

    raise RuntimeError(f"Chat falhou em todos os modelos. Erro: {last_error}")


def _extrair_ebook_data(text: str) -> dict | None:
    """Extrai JSON de ebook_data do texto se presente."""
    match = re.search(
        r'<<<EBOOK_DATA>>>\s*(\{.*?\})\s*<<<END_EBOOK_DATA>>>',
        text,
        flags=re.DOTALL
    )
    if not match:
        return None

    try:
        data = json.loads(match.group(1))
        # Validar campos mínimos
        if "title" in data and "chapters" in data:
            if not data.get("author"):
                data["author"] = "Autor"
            if not data.get("theme"):
                data["theme"] = "Minimalista Moderno"
            return data
    except json.JSONDecodeError:
        pass

    return None
