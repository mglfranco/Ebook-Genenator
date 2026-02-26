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
    Tenta gerar conteúdo com fallback entre os 2 melhores modelos. Rate-limit wait reduzido drasticamente.
    """
    _configure()

    last_error = None

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
        f"Todos os modelos Gemini falharam. Último erro: {last_error}"
    )


def gerar_conteudo_capitulo(
    titulo_livro: str,
    titulo_capitulo: str,
    numero_capitulo: int,
    total_capitulos: int,
    paginas: int,
    tema: str,
) -> str:
    """Gera o conteúdo completo de um capítulo em Markdown."""
    palavras_alvo = paginas * 500

    prompt = f"""Você é um escritor profissional e pesquisador acadêmico. 
Escreva o capítulo {numero_capitulo} de {total_capitulos} para o livro "{titulo_livro}".

**Título do Capítulo:** {titulo_capitulo}
**Tema/Estilo:** {tema}
**Extensão:** Aproximadamente {palavras_alvo} palavras ({paginas} páginas)

## Regras OBRIGATÓRIAS:

1. **SOMENTE INFORMAÇÕES REAIS E VERIFICÁVEIS** — Use apenas fatos, dados, estatísticas e referências de fontes confiáveis (artigos científicos, livros reconhecidos, instituições respeitadas).
2. **NÃO INVENTE dados, citações ou estatísticas.** Se não tiver certeza, indique claramente.
3. Escreva em **Português Brasileiro** com tom profissional mas acessível.
4. Use **formatação Markdown rica**:
   - Cabeçalhos `##` e `###` para subdivisões
   - **Negrito** para termos-chave
   - *Itálico* para ênfase
   - Listas numeradas e com bullets
   - `> Citações` para frases marcantes (com atribuição real)
   - Tabelas quando apropriado para comparações
   - Separadores `---` entre seções
5. O conteúdo deve ser **extenso, detalhado e educativo**.
6. Inclua exemplos práticos e analogias para facilitar compreensão.
7. Termine o capítulo com um parágrafo de transição para o próximo.
8. NÃO inclua o título do capítulo no início (ele é inserido automaticamente).
9. Comece diretamente com o conteúdo, sem repetir o título.

Escreva o capítulo completo agora:"""

    return _gerar_com_retry(prompt)


def gerar_todos_capitulos(
    titulo_livro: str,
    capitulos: list[dict],
    tema: str,
) -> list[dict]:
    """
    Gera conteúdo para todos os capítulos com intervalo entre requisições.
    """
    total = len(capitulos)
    resultado = []

    for i, ch in enumerate(capitulos):
        # Intervalo entre capítulos para evitar rate limit
        if i > 0:
            print(f"[Gemini] Aguardando 5s antes do capítulo {i+1}...")
            import time
            time.sleep(5)

        print(f"[Gemini] Gerando capítulo {i+1}/{total}: {ch['title']}")
        content_md = gerar_conteudo_capitulo(
            titulo_livro=titulo_livro,
            titulo_capitulo=ch["title"],
            numero_capitulo=i + 1,
            total_capitulos=total,
            paginas=ch.get("pages", 5),
            tema=tema,
        )

        resultado.append({
            "title": ch["title"],
            "content": content_md,
            "content_md": content_md,
        })
        print(f"[Gemini] ✓ Capítulo {i + 1} gerado ({len(content_md)} chars)")

    return resultado
