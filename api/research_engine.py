import wikipediaapi

def get_wikipedia_context(topic: str, lang: str = 'pt') -> str:
    try:
        user_agent = 'BookBotSpider/1.0 (https://github.com; email@example.com)'
        wiki_wiki = wikipediaapi.Wikipedia(user_agent, lang)
        
        page = wiki_wiki.page(topic)
        if not page.exists():
            return f"Nenhuma página encontrada na Wikipedia para: {topic}"
            
        summary = page.summary[0:2000]
        
        ctx = "--- CONTEXTO EXTRAÍDO DA WIKIPEDIA --- \n"
        ctx += f"Título da Página: {page.title}\n"
        ctx += f"Resumo Oficial: {summary}\n\n"
        return ctx
    except Exception as e:
        return f"Erro ao acessar Wikipedia: {e}"
