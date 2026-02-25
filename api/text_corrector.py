"""
Módulo de Correção Ortográfica e Gramatical
=============================================
Utiliza language-tool-python para analisar e corrigir
automaticamente erros em cada capítulo antes da renderização.
"""

import language_tool_python


# Singleton do LanguageTool para reutilização
_tool: language_tool_python.LanguageTool | None = None


def _get_tool() -> language_tool_python.LanguageTool | None:
    """Retorna a instância singleton do LanguageTool (PT-BR) se disponível."""
    global _tool
    if _tool is None:
        try:
            _tool = language_tool_python.LanguageTool('pt-BR')
        except Exception as e:
            print(f"[Aviso] Corretor ortográfico desativado (Erro: {e}). O Java está instalado?")
            return None
    return _tool


def corrigir_texto(texto: str) -> str:
    """
    Corrige erros ortográficos e gramaticais de um texto.

    Parameters
    ----------
    texto : str
        Texto bruto (pode conter Markdown).

    Returns
    -------
    str
        Texto corrigido.
    """
    tool = _get_tool()
    if not tool:
        return texto  # Fallback: retorna o texto original sem corrigir

    matches = tool.check(texto)
    texto_corrigido = language_tool_python.utils.correct(texto, matches)
    return texto_corrigido


def corrigir_capitulos(chapters: list[dict[str, str]]) -> list[dict[str, str]]:
    """
    Corrige o texto de todos os capítulos.

    Parameters
    ----------
    chapters : list[dict]
        Lista de dicts com 'title' e 'content'.

    Returns
    -------
    list[dict]
        Mesma lista com 'content' corrigido.
    """
    resultado = []
    for ch in chapters:
        # Pega a chave correta baseada de onde a requisição veio
        texto = ch.get("content_md") or ch.get("content", "")
        conteudo_corrigido = corrigir_texto(texto)
        
        # Preserva todas as outras chaves do dict
        novo_ch = ch.copy()
        if "content_md" in novo_ch:
            novo_ch["content_md"] = conteudo_corrigido
        if "content" in novo_ch:
            novo_ch["content"] = conteudo_corrigido
            
        resultado.append(novo_ch)
    return resultado
