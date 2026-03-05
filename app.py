import json
import os
import shutil
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Configurações iniciais de página PRECISAM ser a primeira instrução Streamlit
st.set_page_config(
    page_title="BookBot - Gerador de E-Books AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Imports dos motores base (reutilizados 100% da V5 sem FastAPI)
from api.chat_handler import processar_mensagem
from api.content_generator import gerar_todos_capitulos
from api.text_corrector import corrigir_capitulos
from api.image_generator import generate_all_images
from api.pdf_engine import generate_pdf
from api.epub_engine import create_epub, inject_qr_codes

# Supabase imports
from supabase import create_client, Client

# Configuração de Ambiente
_PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(_PROJECT_ROOT / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None

_ASSETS_DIR = _PROJECT_ROOT / "assets"
_OUTPUT_DIR = _PROJECT_ROOT / "output"
_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# CSS Customizado para uma UI Premium
st.markdown("""
<style>
    /* Esconde footer padrão do streamlit */
    footer {visibility: hidden;}
    
    /* Layout Chat adjustments */
    .stChatMessage { padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)


def load_library():
    # Detecta E-books na Nuvem Global Supabase
    if not supabase:
        return []
    try:
        response = supabase.table("ebooks").select("*").order("created_at", desc=True).limit(20).execute()
        return response.data
    except Exception as e:
        print(f"Erro ao carregar biblioteca da nuvem: {e}")
        return []


def main():
    # Inicializar Sessões
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "api_key_valid" not in st.session_state:
        st.session_state.api_key_valid = bool(os.getenv("GEMINI_API_KEY"))

    # Verifica Chave
    if not st.session_state.api_key_valid:
        st.error("🚨 Chave `GEMINI_API_KEY` não encontrada no ambiente.")
        st.info("Insira a chave no arquivo `.env` localizado na raiz do projeto e reinicie a aplicação.")
        # Pode pedir input caso queira deixar dinâmico:
        temp_key = st.text_input("Cole sua GEMINI_API_KEY provisória aqui:", type="password")
        if st.button("Salvar Chave na Memória"):
            os.environ["GEMINI_API_KEY"] = temp_key
            st.session_state.api_key_valid = True
            st.rerun()
        st.stop()

    # Barra Lateral (Menu de Ferramentas)
    with st.sidebar:
        st.title("📚 BookBot Settings")
        st.markdown("Crie e-books maravilhosos conversando com a IA.")
        
        st.header("🎨 Estética e Design")
        col1, col2 = st.columns(2)
        with col1:
            tema = st.selectbox("Tema Visual Geral", ["Minimalista Moderno", "Fantasia Épica", "Corporativo Clean", "Sci-Fi Neon", "Romance Clássico", "Cyberpunk", "Vintage / Retrô", "Aquarela Suave"])
        with col2:
            arte_fundo = st.selectbox("Estilo de Ilustrações", ["Cinematográfico", "Pintura a Óleo", "Anime / Mangá", "Vetor Flat", "3D Render", "Fotorealista", "Esboço a Lápis", "Dark Fantasy"])

        modo_colorido = st.toggle("🎨 Modo E-book Colorido (Premium)", value=False, help="Substitui o fundo branco por ilustrações dinâmicas de IA cobrindo toda a página.")

        st.header("✍️ Direção de Texto")
        col3, col4 = st.columns(2)
        with col3:
            estilo = st.selectbox("Tom da Escrita", ["Profissional e Direto", "Acadêmico", "Criativo / Poético", "Descontraído (Blog)", "Didático (Passos)", "Humorístico"])
        with col4:
            publico = st.selectbox("Público-Alvo", ["Iniciantes / Leigos", "Profissionais Cultos", "Adolescentes e Jovens", "Crianças", "Público Geral"])
            
        idioma = st.selectbox("Idioma do Conteúdo", ["Português Brasileiro", "English (US)", "Español", "Français"])
        
        st.info("💡 **Dica de Direção**: Se o seu tema for 'Sci-Fi Neon', tente misturar com a arte '3D Render' para criar cenários cibernéticos espetaculares nas capas dos capítulos!")
        
        st.header("⚙️ Configurações Avançadas (KDP & Mídia)")
        sangria = st.number_input("Corte de Sangria (Bleed em mm)", min_value=0, max_value=20, value=3)
        gerar_audiobook = st.checkbox("🎧 Gerar Audiobook (MP3 com Edge-TTS)", value=False)
        pesquisa_web = st.checkbox("🌐 Ativar Agente Spider (Wikipedia)", value=False)
        gerar_3d = st.checkbox("🧊 Retornar Objeto 3D (Capa GLB)", value=False)
        
        st.divider()
        st.header("Sua Biblioteca na Nuvem ☁️")
        biblioteca = load_library()
        if not biblioteca:
            st.caption("Nenhum e-book gerado na nuvem ainda.")
        else:
            for item in biblioteca:
                safe_title = str(item.get('title', 'Sem Título'))
                with st.expander(f"📖 {safe_title[:20]}..."):
                    st.markdown(f"**Tema:** {item.get('theme', 'N/A')}")
                    if item.get("pdf_url"):
                        st.markdown(f"[🔽 Baixar PDF Gráfico]({item['pdf_url']})")
                    if item.get("has_epub") and item.get("epub_url"):
                        st.markdown(f"[🔽 Baixar EPUB Fluido]({item['epub_url']})")

        if st.button("🗑️ Limpar Histórico do Chat"):
            st.session_state.messages = []
            st.rerun()

    # Header Principal
    st.markdown("""
        <div style='text-align: center; padding: 1rem 0 2rem 0;'>
            <h1 style='font-size: 3.5rem; font-weight: 800; background: -webkit-linear-gradient(45deg, #8A2387, #E94057, #F27121); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0;'>BookBot Studio ✨</h1>
            <p style='font-size: 1.1rem; color: gray; margin-top: 0.5rem;'>O motor inteligente que escreve, diagrama e pinta livros inteiros por você.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Resumo das Configurações Atuais como Dashboard
    with st.container(border=True):
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Tema Visual", tema)
        m2.metric("Arte de Capas", arte_fundo)
        m3.metric("Público-Alvo", publico)
        m4.metric("Idioma", idioma)
        st.caption("Estas configurações estão ativas injetadas diretamente no cérebro da Inteligência Artificial. Altere no painel esquerdo.")

    # Renderiza mensagens anteriores do Chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Primeiro Prompts
    if not st.session_state.messages:
        with st.chat_message("assistant", avatar="🤖"):
            intro = f"""Olá! Bem-vindo ao **BookBot Studio**. Estou com meus motores aquecidos e configurado para criar literatura em **{idioma}** apontada para **{publico}**!\n
    Para começar, me conte a sua ideia principal. Exemplo: *"Quero escrever um livro de misterio sobre detetives em marte"*."""
            st.markdown(intro)
            st.session_state.messages.append({"role": "assistant", "content": intro})

    # Campo de input natural (O Chat em si)
    if prompt := st.chat_input("Ex: Escreva um guia prático de 20 páginas sobre culinária japonesa..."):
        # Display user input e guarda no state
        st.chat_message("user").markdown(prompt)
        # Atenção: Passamos o history *antes* de adicionar o user para processar_mensagem mapear os roles.
        # Oh espere, o processar_mensagem na V5 quer o user message separada, com o histórico *até ali*.
        
        # Tema consolidado combinando a Paleta visual e o Estilo artístico
        tema_completo = f"{tema} (Estilo artístico recomendado para imagens geradas: {arte_fundo})"
        
        prompt_final = prompt
        if pesquisa_web:
            with st.spinner("🌐 Agente Spider: Consultando enciclopédia global da Wikipedia..."):
                from api.research_engine import get_wikipedia_context
                wiki_data = get_wikipedia_context(prompt)
                prompt_final = f"{prompt}\\n\\n{wiki_data}"

        try:
            with st.spinner("Pensando e processando histórico..."):
                # Conversa com a IA passando todas as opções sofisticadas do painel lateral
                resp_dict = processar_mensagem(
                    historico=st.session_state.messages, 
                    mensagem_usuario=prompt_final,
                    theme=tema_completo,
                    style=estilo,
                    audience=publico,
                    language=idioma
                )
            
            # Recupera a resposta textual do Bot e guarda na memory
            bot_text = resp_dict.get("response", "Não consegui processar a resposta.")
            ebook_data = resp_dict.get("ebook_data")
            
            # Adiciona user ao st.session_state agora
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Escreve a reposta no chat
            with st.chat_message("assistant"):
                st.markdown(bot_text)
            
            st.session_state.messages.append({"role": "assistant", "content": bot_text})
            
            # Se o bot embutiu um JSON Válido (Significa que é a hora de GERAR O LIVRO!)
            if ebook_data:
                st.info("🎯 E-Book Confirmado! Iniciando Motor de Geração Multithread...")
                
                # Container mágico de status (Substitui os `addMsg('b', ...)`)
                with st.status("Construindo o E-Book...", expanded=True) as status:
                    st.write("📝 **Passo 1/5**: Gerando o conteúdo interno dos Capítulos via IA...")
                    titulo_livro = ebook_data.get("title", "Meu Livro Automático")
                    capitulos_lista = ebook_data.get("chapters", [])
                    total_cap = len(capitulos_lista)
                    
                    progress_bar = st.progress(0)
                    raw_capitulos = []
                    
                    from api.content_generator import gerar_conteudo_capitulo
                    import time
                    
                    for idx, ch in enumerate(capitulos_lista):
                        if idx > 0:
                            time.sleep(3) # Small anti-ratelimit
                        
                        st.write(f"✍️ Escrevendo Capítulo {idx+1}/{total_cap}: *{ch['title']}*")
                        content_md = gerar_conteudo_capitulo(
                            titulo_livro=titulo_livro,
                            titulo_capitulo=ch["title"],
                            numero_capitulo=idx + 1,
                            total_capitulos=total_cap,
                            paginas=ch.get("pages", 5),
                            tema_historia=tema,
                            ideia_principal=prompt,
                            idioma=idioma,
                            publico_alvo=publico,
                            estilo_escrita=estilo,
                        )
                        raw_capitulos.append({
                            "title": ch["title"],
                            "content": content_md,
                            "content_md": content_md
                        })
                        progress_bar.progress((idx + 1) / total_cap)
                    raw_capitulos = corrigir_capitulos(raw_capitulos)
                    
                    import uuid
                    import markdown
                    job_id = uuid.uuid4().hex[:12]
                    job_assets_dir = str(_ASSETS_DIR / job_id)
                    Path(job_assets_dir).mkdir(exist_ok=True)
                    output_pdf_path = str(_OUTPUT_DIR / f"ebook_{job_id}.pdf")
                    
                    st.write("🛠️ **Passo 3/5**: Processando HTML e Criando os Códigos QR...")
                    chapters_data = []
                    for i, ch in enumerate(raw_capitulos):
                        content_md = ch.get("content", ch.get("content_md", ""))
                        content_html = markdown.markdown(content_md)
                        content_html = inject_qr_codes(content_html, job_assets_dir, i)
                        chapters_data.append({
                            "title": ch.get("title", ""),
                            "content": content_md,
                            "content_md": content_md,
                            "content_html": content_html,
                        })

                    st.write("🎨 **Passo 4/5**: Desenhando as imagens dos capítulos via GPU (Stable Diffusion)...")
                    image_paths = generate_all_images(
                        chapters=chapters_data,
                        theme=tema_completo,
                        assets_dir=job_assets_dir,
                        colorful_mode=modo_colorido
                    )
                    
                    st.write("🖨️ **Passo 5/5**: Compilando o layout gráfico no Weasyprint e EbookLib...")
                    pdf_path = generate_pdf(
                        title=ebook_data.get("title", "Meu Livro Automático"),
                        author=ebook_data.get("author", "Autor BookBot"),
                        theme=tema,
                        chapters=raw_capitulos,
                        image_paths=image_paths,
                        output_path=output_pdf_path,
                        bleed_mm=sangria,
                        colorful_mode=modo_colorido
                    )
                    output_epub_path = str(_OUTPUT_DIR / f"ebook_{job_id}.epub")
                    epub_path = create_epub(
                        title=ebook_data.get("title", "Meu Ebook"),
                        author=ebook_data.get("author", "Autor BookBot"),
                        chapters_data=chapters_data,
                        output_path=output_epub_path
                    )
                    
                    mp3_path = None
                    if gerar_audiobook:
                        st.write("🎙️ **Faixa Bônus**: Narrando o Audiobook via TTS...")
                        from api.audio_engine import generate_audiobook_cli
                        mp3_path = str(_OUTPUT_DIR / f"audiobook_{job_id}.mp3")
                        generate_audiobook_cli(ebook_data.get("title", "Audiolivro"), chapters_data, mp3_path)
                        
                    html_3d_path = None
                    if gerar_3d:
                        st.write("🧊 **Faixa Bônus**: Modelando Capa Interativa 3D...")
                        from api.engine_3d import generate_3d_html_cover
                        html_3d_path = str(_OUTPUT_DIR / f"capa_3d_{job_id}.html")
                        capa_img = image_paths.get(0)
                        if capa_img:
                            generate_3d_html_cover(capa_img, ebook_data.get("title", "Ebook"), html_3d_path)
                    
                    # Sincronização com Supabase (Nuvem)
                    st.write("☁️ **Passo Final**: Sincronizando E-book com a Nuvem Global (Supabase)...")
                    if supabase:
                        pdf_blob_name = f"{job_id}/{os.path.basename(output_pdf_path)}"
                        epub_blob_name = f"{job_id}/{os.path.basename(output_epub_path)}"
                        
                        # Upload PDF
                        with open(output_pdf_path, 'rb') as f:
                            supabase.storage.from_("ebooks_storage").upload(file=f, path=pdf_blob_name, file_options={"content-type": "application/pdf"})
                        pdf_public_url = supabase.storage.from_("ebooks_storage").get_public_url(pdf_blob_name)
                        
                        # Upload EPUB
                        with open(output_epub_path, 'rb') as f:
                            supabase.storage.from_("ebooks_storage").upload(file=f, path=epub_blob_name, file_options={"content-type": "application/epub+zip"})
                        epub_public_url = supabase.storage.from_("ebooks_storage").get_public_url(epub_blob_name)
                        
                        # Inserir no DB
                        supabase.table("ebooks").insert({
                            "title": ebook_data.get("title", "Meu Ebook"),
                            "author": ebook_data.get("author", "Autor BookBot"),
                            "theme": tema,
                            "pdf_url": pdf_public_url,
                            "epub_url": epub_public_url,
                            "has_epub": True
                        }).execute()

                    status.update(label="✅ E-Book Gerado com Sucesso!", state="complete", expanded=False)
                
                # Exibir balões de comemoração nativo do Streamlit
                st.balloons()
                st.success(f"**{ebook_data.get('title', 'Livro')}** está PRONTO!")
                
                # Gerar botões de download gigantes na tela principal
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    with open(pdf_path, "rb") as p:
                        st.download_button("📥 Baixar PDF HQ", p, file_name=os.path.basename(pdf_path), mime="application/pdf", use_container_width=True)
                with col2:
                    with open(epub_path, "rb") as e:
                        st.download_button("📱 Baixar ePUB", e, file_name=os.path.basename(epub_path), mime="application/epub+zip", use_container_width=True)
                with col3:
                    if mp3_path:
                        with open(mp3_path, "rb") as a:
                            st.download_button("🎧 Baixar Audiobook", a, file_name=os.path.basename(mp3_path), mime="audio/mpeg", use_container_width=True)
                with col4:
                    if html_3d_path:
                        with open(html_3d_path, "rb") as d:
                            st.download_button("🧊 Ver Capa 3D WebGL", d, file_name=os.path.basename(html_3d_path), mime="text/html", use_container_width=True)
                        
        except Exception as e:
            st.error(f"❌ Ocorreu um erro no processador principal: {str(e)}")

if __name__ == "__main__":
    main()
