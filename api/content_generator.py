"""
Módulo de Geração de Conteúdo via Google Gemini
=================================================
Gera conteúdo extenso e confiável para cada capítulo do e-book.
Inclui fallback entre modelos e retry automático para rate limits.
"""

import os
import time
import google.generativeai as genai


# Modelos em ordem de preferência (fallback automático)
# Prioriza modelos com quotas separadas do gemini-2.0-flash
_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
]

_configured = False


def _configure():
    global _configured
    if _configured:
        return
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não definida. Configure no arquivo .env")
    genai.configure(api_key=api_key)
    _configured = True


def _gerar_com_retry(prompt: str, max_retries: int = 2) -> str:
    """
    Tenta gerar conteúdo de forma Híbrida. 
    Prioridade 1: GroqCloud (Llama 3 70B LPU) - Foco em extrema velocidade e zero throttling.
    Prioridade 2: Google Gemini (Fallback)
    """
    groq_api_key = os.getenv("GROQ_API_KEY", "")
    
    # 1. Tentar Groq (Llama 3)
    if groq_api_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_api_key)
            print("[Groq LPU] Iniciando Roteirização Engine via Llama-3-70b...")
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Você é um escritor profissional e conhecedor excepcional de literatura."},
                    {"role": "user", "content": prompt}
                ],
                model="llama3-70b-8192",
                temperature=0.7,
                max_tokens=8000,
            )
            content = response.choices[0].message.content
            if content:
                print("[Groq LPU] Geração concluída com sucesso em hiper-velocidade.")
                return content
        except Exception as e:
            print(f"[Groq LPU] Erro na geração com Llama 3: {str(e)}. Fazendo Fallback para Gemini...")

    # 2. Fallback para Gemini
    _configure()
    last_error = None

    print("[Gemini Fallback] Iniciando roteirização via Google Neural Net...")
    for model_name in _MODELS:
        for attempt in range(max_retries):
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=8192,
                        temperature=0.7,
                    ),
                )
                return response.text

            except Exception as e:
                last_error = e
                error_str = str(e)

                if "429" in error_str or "quota" in error_str.lower():
                    wait = 15
                    print(f"[Gemini] Rate limit em {model_name}, aguardando {wait}s (tentativa {attempt+1})...")
                    time.sleep(wait)
                    continue
                elif "404" in error_str or "not found" in error_str.lower():
                    print(f"[Gemini] Modelo {model_name} indisponível, tentando próximo...")
                    break  # próximo modelo
                else:
                    print(f"[Gemini] Erro em {model_name}: {error_str}")
                    break  # próximo modelo

    raise RuntimeError(
        f"Todos os motores falharam (Groq e Gemini). Último erro: {last_error}"
    )


def gerar_conteudo_capitulo(
    titulo_livro: str,
    titulo_capitulo: str,
    numero_capitulo: int,
    total_capitulos: int,
    paginas: int,
    tema_historia: str,
    ideia_principal: str,
    idioma: str = "Português",
    publico_alvo: str = "Geral",
    estilo_escrita: str = "Profissional",
) -> str:
    """Gera o conteúdo completo de um capítulo em Markdown dinâmico baseado no Painel."""
    palavras_alvo = paginas * 500

    prompt = f"""Você é um escritor profissional e conhecedor excepcional de literatura. 
Escreva o capítulo {numero_capitulo} de {total_capitulos} para o livro "{titulo_livro}".

**Ideia Principal do Livro:** {ideia_principal}
**Título do Capítulo:** {titulo_capitulo}
**Gênero/Tema da História:** {tema_historia}
**Público-Alvo:** {publico_alvo}
**Tom/Estilo de Escrita:** {estilo_escrita}
**Idioma Obrigatório:** {idioma}
**Extensão:** Aproximadamente {palavras_alvo} palavras ({paginas} páginas)

## Regras OBRIGATÓRIAS:

1. **SOMENTE INFORMAÇÕES REAIS E VERIFICÁVEIS** — Use fatos, dados e uma narrativa que se conecte estritamente com a Ideia Principal do livro especificada.
2. Escreva OBRIGATORIAMENTE no idioma: **{idioma}**.
3. Aplique o tom de escrita **{estilo_escrita}** e garanta que o vocabulário seja ajustado perfeitamente para **{publico_alvo}**.
4. Use **formatação Markdown rica**:
   - Cabeçalhos `##` e `###` para subdivisões
   - **Negrito** para termos-chave
   - *Itálico* para ênfase
   - Listas numeradas e com bullets
   - `> Citações` quando apropriado
5. NÃO faça referências a "estilos visuais" ou "capas". Foque 100% no CONTEÚDO LITERAL e na LITERATURA do capítulo.
6. O conteúdo deve ser extenso, detalhado, educativo e fluído.
7. Termine o capítulo com um parágrafo de transição para o próximo.
8. NÃO inclua o título do capítulo no início (ele é inserido automaticamente).
9. Comece diretamente com o conteúdo.

Escreva o capítulo completo agora:"""

    return _gerar_com_retry(prompt)


def gerar_todos_capitulos(
    titulo_livro: str,
    capitulos: list[dict],
    tema: str,
) -> list[dict]:
    # Mantido para compatibilidade legado, app.py agora chama gerar_conteudo_capitulo diretamente.
    pass
