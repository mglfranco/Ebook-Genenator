import { useState, useEffect, useRef } from 'react';
import { Bot, BookOpen, Send, UploadCloud, Library, Loader2, Sparkles, Image as ImageIcon, ChevronRight, ChevronLeft, CheckCircle2, FileText, Activity } from 'lucide-react';
import { niches, imageStyles, coverStyles, writingTones, pageLayouts } from './data/setupOptions';

type Message = { role: 'bot' | 'user', content: string };
type SetupState = {
  niche: string;
  imageStyle: string;
  coverStyle: string;
  writingTone: string;
  pageLayout: string;
};

// Base URL Dynamic (Lê da Nuvem se estiver na Vercel, senão usa Localhost 8000)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [setupStep, setSetupStep] = useState(0); // 0 to 4 (5 is chat)
  const [setupData, setSetupData] = useState<SetupState>({
    niche: '',
    imageStyle: '',
    coverStyle: '',
    writingTone: '',
    pageLayout: ''
  });

  const [messages, setMessages] = useState<Message[]>([
    { role: 'bot', content: 'As configurações foram salvas com sucesso! Digite a premissa inicial do seu livro para que eu comece a escrever e ilustrar o Volume 1.' }
  ]);
  const [prompt, setPrompt] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [libraryMode, setLibraryMode] = useState(false);

  const [libraryItems, setLibraryItems] = useState<any[]>([]);
  const [activeJob, setActiveJob] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<{ message: string; progress: number; status: string }>({ message: '', progress: 0, status: '' });

  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, jobStatus]);

  // Buscar Biblioteca do Supabase
  const fetchLibrary = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/library`);
      const data = await res.json();
      setLibraryItems(data.jobs || []);
    } catch (e) {
      console.error("Failed to fetch library", e);
    }
  };

  // Carregar biblioteca do Supabase
  useEffect(() => {
    if (libraryMode) {
      fetchLibrary();
    }
  }, [libraryMode]);

  const updateSetup = (key: keyof SetupState, value: string) => {
    setSetupData(prev => ({ ...prev, [key]: value }));
  };

  const nextStep = () => setSetupStep(prev => Math.min(prev + 1, 5));
  const prevStep = () => setSetupStep(prev => Math.max(prev - 1, 0));

  const sendMessage = async () => {
    if (!prompt.trim() || isGenerating) return;

    // Validate Setup
    const missing = Object.values(setupData).some(v => v === '');
    if (missing && setupStep < 5) {
      alert("Por favor selecione e finalize as configurações no Wizard antes de gerar.");
      return;
    }

    setMessages(prev => [...prev, { role: 'user', content: prompt }]);
    setIsGenerating(true);

    try {
      const payload = {
        niche: setupData.niche || 'Ficção',
        artStyle: setupData.imageStyle || 'Anime',
        coverStyle: setupData.coverStyle || 'Neon',
        pageLayout: setupData.pageLayout || 'Normal',
        writingTone: setupData.writingTone || 'Aventura',
        prompt: prompt
      };

      setPrompt("");

      const res = await fetch(`${API_BASE_URL}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const data = await res.json();
        setActiveJob(data.job_id);
        setMessages(prev => [...prev, { role: 'bot', content: `🎯 Missão Aceita. Inicializando a pipeline [Job ID: ${data.job_id.substring(0, 6)}]. Acompanhe o progresso abaixo...` }]);
      } else {
        throw new Error("Erro no servidor de PDF.");
      }
    } catch (e) {
      setIsGenerating(false);
      setMessages(prev => [...prev, { role: 'bot', content: '❌ Houve uma falha de conexão com a API Central.' }]);
    }
  };

  // Polling para o Status da Geração Atual
  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (activeJob && isGenerating) {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`${API_BASE_URL}/api/status/${activeJob}`);
          if (res.ok) {
            const data = await res.json();
            setJobStatus({ message: data.message, progress: data.progress, status: data.status });
            console.log("Status: ", data);
            if (data.status === 'complete' || data.status === 'error') {
              clearInterval(interval);
              setIsGenerating(false);
              setActiveJob(null);

              if (data.status === 'complete') {
                setMessages(prev => [...prev, { role: 'bot', content: `🎉 E-Book "${data.result.title}" Finalizado com Sucesso!\nVocê pode acessar a sua Masterpiece diretamente pela Biblioteca na lateral.` }]);
              } else {
                setMessages(prev => [...prev, { role: 'bot', content: `⚠️ A geração congelou. Erro Reportado: ${data.message}` }]);
              }
            }
          }
        } catch (e) {
          console.error(e);
        }
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [activeJob, isGenerating]);


  const isSetupActive = setupStep < 5;

  return (
    <div className="min-h-screen bg-[#0B0C10] text-gray-100 font-sans selection:bg-fuchsia-500/30 flex overflow-hidden">

      {/* FULL-SCREEN SETUP WIZARD */}
      {isSetupActive && (
        <div className="absolute inset-0 z-50 bg-[#0B0C10] flex flex-col items-center justify-center p-4">

          {/* Progress Bar */}
          <div className="w-full max-w-5xl mb-12 flex items-center justify-center gap-2">
            {[1, 2, 3, 4, 5].map(step => (
              <div key={step} className="flex flex-col items-center flex-1 max-w-[120px]">
                <div className={`h-2 w-full rounded-full transition-colors duration-500 ${setupStep >= step - 1 ? 'bg-fuchsia-500 shadow-[0_0_10px_rgba(217,70,239,0.5)]' : 'bg-white/10'}`}></div>
                <span className={`text-[10px] mt-2 font-bold uppercase tracking-widest ${setupStep >= step - 1 ? 'text-fuchsia-400' : 'text-gray-600'}`}>
                  {step === 1 ? 'Nicho' : step === 2 ? 'Arte' : step === 3 ? 'Páginas' : step === 4 ? 'Escrita' : 'RAG'}
                </span>
              </div>
            ))}
          </div>

          <div className="w-full max-w-5xl bg-[#12131A]/80 backdrop-blur-3xl border border-white/10 rounded-3xl shadow-2xl overflow-hidden flex flex-col md:h-[600px]">

            {/* Header Wizard */}
            <div className="px-8 py-6 border-b border-white/5 flex items-center justify-between bg-black/20">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-fuchsia-600 to-orange-500 flex items-center justify-center shadow-lg shadow-fuchsia-500/20">
                  <BookOpen className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-white">Configuração do E-book</h1>
                  <p className="text-xs text-gray-400">Personalizando Motor de IA</p>
                </div>
              </div>
              <button onClick={() => setSetupStep(5)} className="text-xs text-fuchsia-400 hover:text-fuchsia-300 font-medium tracking-wider uppercase">Pular Setup</button>
            </div>

            {/* Wizard Content Area */}
            <div className="flex-1 overflow-y-auto p-8 relative">

              {/* STEP 1: NICHE */}
              {setupStep === 0 && (
                <div className="animate-in fade-in slide-in-from-right-8 duration-500">
                  <h2 className="text-2xl font-bold mb-2">Qual é o foco principal da sua obra?</h2>
                  <p className="text-gray-400 mb-8">Esta escolha calibra automaticamente nossos prompts base.</p>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {niches.map(n => {
                      const Icon = n.icon;
                      const isSelected = setupData.niche === n.id;
                      return (
                        <div
                          key={n.id}
                          onClick={() => updateSetup('niche', n.id)}
                          className={`cursor-pointer p-6 rounded-2xl border transition-all duration-300 ${isSelected ? 'border-fuchsia-500 bg-fuchsia-500/10 shadow-[0_0_30px_rgba(217,70,239,0.15)] ring-1 ring-fuchsia-500' : 'border-white/10 bg-black/40 hover:bg-white/5 hover:border-white/20'}`}
                        >
                          <div className={`w-12 h-12 rounded-full mb-4 flex items-center justify-center bg-gradient-to-tr ${n.color}`}>
                            <Icon className="w-6 h-6 text-white" />
                          </div>
                          <h3 className="text-lg font-bold text-gray-100 mb-2">{n.title}</h3>
                          <p className="text-sm text-gray-400 leading-relaxed">{n.description}</p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* STEP 2: IMAGE STYLES */}
              {setupStep === 1 && (
                <div className="animate-in fade-in slide-in-from-right-8 duration-500">
                  <h2 className="text-2xl font-bold mb-2">Estética Visual das Imagens</h2>
                  <p className="text-gray-400 mb-8">Como as ilustrações e fotos geradas devem parecer?</p>

                  <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
                    {imageStyles.map(style => {
                      const isSelected = setupData.imageStyle === style.id;
                      return (
                        <div
                          key={style.id}
                          onClick={() => updateSetup('imageStyle', style.id)}
                          className={`group cursor-pointer rounded-2xl border overflow-hidden relative transition-all duration-300 ${isSelected ? 'border-fuchsia-500 ring-1 ring-fuchsia-500' : 'border-white/10'}`}
                        >
                          <div className={`h-24 w-full bg-gradient-to-tr ${style.gradient} opacity-80 group-hover:scale-105 transition-transform duration-500 flex items-center justify-center`}>
                            <ImageIcon className={`w-8 h-8 ${style.isLight ? 'text-black/30' : 'text-white/30'}`} />
                          </div>
                          <div className={`p-4 bg-black/60 backdrop-blur-xl border-t ${isSelected ? 'border-fuchsia-500/30 bg-fuchsia-900/20' : 'border-white/5'}`}>
                            <h3 className="font-bold text-gray-100 mb-1">{style.title}</h3>
                            <p className="text-xs text-gray-400">{style.description}</p>
                            {isSelected && <CheckCircle2 className="w-5 h-5 text-fuchsia-500 absolute top-3 right-3 drop-shadow-md" />}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* STEP 3: LAYOUT & COVER */}
              {setupStep === 2 && (
                <div className="animate-in fade-in slide-in-from-right-8 duration-500 flex flex-col md:flex-row gap-8 h-full">
                  <div className="flex-1">
                    <h2 className="text-2xl font-bold mb-2">Design da Capa</h2>
                    <p className="text-gray-400 mb-6">A vitrine do seu E-book.</p>
                    <div className="space-y-3">
                      {coverStyles.map(cover => (
                        <div key={cover.id} onClick={() => updateSetup('coverStyle', cover.id)} className={`p-4 cursor-pointer rounded-xl border transition-all ${setupData.coverStyle === cover.id ? 'border-orange-500 bg-orange-500/10' : 'border-white/10 bg-black/40 hover:bg-white/5'}`}>
                          <h3 className="font-bold text-gray-200">{cover.title}</h3>
                          <p className="text-xs text-gray-400 mt-1">{cover.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="hidden md:block w-px bg-gradient-to-b from-transparent via-white/10 to-transparent"></div>
                  <div className="flex-1">
                    <h2 className="text-2xl font-bold mb-2">Diagramação do Miolo</h2>
                    <p className="text-gray-400 mb-6">Como as páginas serão desenhadas no PDF final.</p>
                    <div className="space-y-3">
                      {pageLayouts.map(layout => (
                        <div key={layout.id} onClick={() => updateSetup('pageLayout', layout.id)} className={`p-4 cursor-pointer rounded-xl border transition-all ${setupData.pageLayout === layout.id ? 'border-fuchsia-500 bg-fuchsia-500/10' : 'border-white/10 bg-black/40 hover:bg-white/5'}`}>
                          <h3 className="font-bold text-gray-200">{layout.title}</h3>
                          <p className="text-xs text-gray-400 mt-1">{layout.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* STEP 4: WRITING TONE & RAG */}
              {setupStep === 3 && (
                <div className="animate-in fade-in slide-in-from-right-8 duration-500">
                  <h2 className="text-2xl font-bold mb-2">Tom da Escrita da IA</h2>
                  <p className="text-gray-400 mb-6">Defina a personalidade do seu autor virtual Ghostwriter.</p>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                    {writingTones.map(tone => (
                      <div key={tone.id} onClick={() => updateSetup('writingTone', tone.id)} className={`p-5 cursor-pointer rounded-2xl border transition-all ${setupData.writingTone === tone.id ? 'border-orange-500 bg-orange-500/10 ring-1 ring-orange-500/50' : 'border-white/10 bg-black/40 hover:bg-white/5'}`}>
                        <h3 className="font-bold text-gray-100 mb-3">{tone.title}</h3>
                        <div className="p-3 bg-black/50 rounded-lg border border-white/5 italic text-sm text-gray-300 font-serif leading-relaxed">
                          {tone.example}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* STEP 5: RAG & FINISH */}
              {setupStep === 4 && (
                <div className="animate-in fade-in slide-in-from-bottom-8 duration-500 h-full flex flex-col items-center justify-center text-center">
                  <div className="w-20 h-20 rounded-full bg-gradient-to-tr from-fuchsia-600 to-orange-500 flex items-center justify-center mb-6 shadow-[0_0_50px_rgba(217,70,239,0.4)]">
                    <Sparkles className="w-10 h-10 text-white animate-pulse" />
                  </div>
                  <h2 className="text-4xl font-bold mb-4">Tudo Pronto!</h2>
                  <p className="text-gray-400 mb-8 max-w-lg">Seu motor personalizado está configurado. Opcionalmente, você pode arrastar um PDF abaixo para a IA basear todo o livro nela (Modo RAG Corporativo), ou ir direto para o chat.</p>

                  <div className="w-full max-w-md border-2 border-dashed border-white/20 rounded-3xl p-8 mb-8 bg-white/5 hover:bg-white/10 hover:border-fuchsia-500/50 transition-all cursor-pointer group">
                    <UploadCloud className="w-10 h-10 text-gray-400 mx-auto mb-4 group-hover:text-fuchsia-400 transition-colors" />
                    <p className="font-bold text-gray-200">Adicionar PDF (Base RAG)</p>
                    <p className="text-xs text-gray-500 mt-2">Arraste e solte o material de referência</p>
                  </div>
                </div>
              )}

            </div>

            {/* Footer Buttons */}
            <div className="p-6 border-t border-white/5 bg-black/40 flex items-center justify-between">
              <button
                onClick={prevStep}
                disabled={setupStep === 0}
                className="px-6 py-3 rounded-xl font-bold flex items-center gap-2 text-gray-400 hover:text-white hover:bg-white/5 disabled:opacity-30 transition-all"
              >
                <ChevronLeft className="w-5 h-5" /> Voltar
              </button>

              <button
                onClick={nextStep}
                className="px-8 py-3 bg-gradient-to-r from-fuchsia-600 to-orange-500 hover:from-fuchsia-500 hover:to-orange-400 rounded-xl font-bold text-white shadow-lg shadow-fuchsia-500/25 transition-all active:scale-95 flex items-center gap-2"
              >
                {setupStep === 4 ? 'Acessar o Estúdio' : 'Próximo Passo'} {setupStep !== 4 && <ChevronRight className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MAIN CONTENT AREA (CHAT & LIBRARY) */}
      <main className="flex-1 flex flex-col relative w-full h-screen">
        {/* Top Navbar */}
        <header className="h-16 border-b border-white/10 bg-black/20 backdrop-blur-md flex items-center justify-between px-6 z-10 sticky top-0">
          <div className="flex items-center gap-4">
            <h2 className="font-semibold text-gray-200">{libraryMode ? 'Biblioteca em Nuvem' : 'Estúdio de Criação'}</h2>
          </div>
          <button
            onClick={() => setLibraryMode(!libraryMode)}
            className={`p-2 rounded-lg border border-white/10 transition-colors flex items-center gap-2 text-sm font-medium ${libraryMode ? 'bg-fuchsia-500/20 text-fuchsia-300 border-fuchsia-500/30' : 'bg-white/5 text-gray-300 hover:bg-white/10'}`}
          >
            <Library className="w-4 h-4" />
            <span>Biblioteca</span>
          </button>
        </header>

        {libraryMode ? (
          /* LIBRARY SCREEN */
          <div className="flex-1 p-8 overflow-y-auto w-full">
            <h2 className="text-3xl font-bold mb-8 flex gap-3 items-center">
              <Library className="w-8 h-8 text-fuchsia-500" /> Histórico (Supabase)
            </h2>
            {libraryItems.length === 0 ? (
              <div className="text-center py-20 text-gray-500">Nenhum Livro encontrado ou Conexão Pendente.</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {libraryItems.map((item, i) => (
                  <div key={i} className="bg-white/5 border border-white/10 rounded-2xl p-5 hover:border-fuchsia-500/50 transition-all group hover:shadow-2xl">
                    <div className="aspect-[3/4] bg-gradient-to-br from-gray-800 to-black rounded-lg mb-4 flex items-center justify-center shadow-inner relative overflow-hidden group-hover:scale-[1.02] transition-transform">
                      {item.status === 'processing' ? (
                        <Loader2 className="w-12 h-12 text-fuchsia-500/50 animate-spin" />
                      ) : (
                        <FileText className="w-12 h-12 text-white/10" />
                      )}
                    </div>
                    <h3 className="font-bold text-lg text-white mb-1 leading-tight truncate px-1">{item.user_prompt || "Ebook Gerado"}</h3>
                    <p className="text-xs text-gray-400 mb-4 px-1">Tema: {item.cover_style} &bull; Arte: {item.art_style}</p>
                    <div className="flex items-center gap-2">
                      {item.pdf_url ? (
                        <a href={item.pdf_url} target="_blank" rel="noopener noreferrer" className="flex-1 py-2 text-center bg-fuchsia-600 hover:bg-fuchsia-500 rounded-lg text-xs font-bold text-white shadow-lg">Download PDF</a>
                      ) : (
                        <button disabled className="flex-1 py-2 bg-white/10 text-gray-500 rounded-lg text-xs font-semibold uppercase tracking-wider">{item.status}</button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          /* CHAT SCREEN */
          <div className="flex-1 flex flex-col relative w-full h-full max-w-5xl mx-auto">
            {/* Chat History */}
            <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 pb-48">
              {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] md:max-w-[70%] p-4 rounded-3xl text-[15px] leading-relaxed ${msg.role === 'user'
                    ? 'bg-gradient-to-br from-fuchsia-600 to-orange-600 text-white shadow-[0_4px_20px_rgba(217,70,239,0.3)] rounded-br-sm'
                    : 'bg-white/5 border border-white/10 text-gray-200 rounded-bl-sm backdrop-blur-md'
                    }`}>
                    {msg.role === 'bot' && (
                      <div className="flex items-center gap-2 mb-2 text-fuchsia-400">
                        <Bot className="w-4 h-4 flex-shrink-0" />
                        <span className="text-xs font-bold uppercase tracking-wider">BookBot Studio</span>
                      </div>
                    )}
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  </div>
                </div>
              ))}

              {/* Dynamic Loader Box if Generating */}
              {isGenerating && activeJob && (
                <div className="flex justify-start animate-in slide-in-from-bottom-4 fade-in duration-500">
                  <div className="max-w-[85%] md:max-w-[70%] p-5 rounded-3xl bg-black/40 border-2 border-fuchsia-500/20 text-gray-200 rounded-bl-sm backdrop-blur-xl">
                    <div className="flex items-center gap-3 mb-4">
                      <Activity className="w-5 h-5 text-fuchsia-500 animate-pulse" />
                      <h4 className="font-bold text-sm tracking-widest uppercase text-fuchsia-400">Engine Processando</h4>
                    </div>

                    <p className="text-sm font-medium text-gray-300 mb-3">{jobStatus.message || "Aguardando..."}</p>

                    {/* Progess Bar */}
                    <div className="w-full h-3 bg-white/5 rounded-full overflow-hidden border border-white/10">
                      <div className="h-full bg-gradient-to-r from-fuchsia-500 to-orange-500 transition-all duration-1000 ease-out" style={{ width: `${jobStatus.progress}%` }}></div>
                    </div>
                    <div className="text-right mt-1 font-mono text-xs text-gray-500">{jobStatus.progress}%</div>
                  </div>
                </div>
              )}

              <div ref={chatEndRef} />
            </div>

            {/* Chat Input */}
            <div className="absolute bottom-4 md:bottom-8 left-4 right-4 md:left-8 md:right-8">
              <div className="relative group">
                <div className="absolute -inset-0.5 bg-gradient-to-r from-fuchsia-600 to-orange-600 rounded-2xl blur opacity-20 group-focus-within:opacity-50 transition duration-500"></div>
                <div className="relative flex flex-col bg-[#1A1C23]/90 backdrop-blur-xl border border-white/10 rounded-2xl shadow-xl overflow-hidden p-2">
                  <textarea
                    disabled={isGenerating}
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
                    placeholder={isGenerating ? "Criação de obra em andamento. Aguarde..." : "Ex: Escreva a história do Samurai Cibernético e adicione muita ação no primeiro ato..."}
                    className="w-full bg-transparent text-white placeholder-gray-500 outline-none resize-none max-h-48 py-3 px-4 min-h-[60px] disabled:opacity-50"
                    rows={2}
                  />
                  <div className="flex items-center justify-between border-t border-white/5 pt-2 px-2 mt-1">
                    <div className="text-xs text-gray-500 font-medium">✨ Motor AI ativado com suas configurações</div>
                    <button
                      onClick={sendMessage}
                      disabled={!prompt.trim() || isGenerating}
                      className="px-6 py-2 bg-gradient-to-r from-fuchsia-600 to-orange-600 hover:from-fuchsia-500 hover:to-orange-500 disabled:opacity-50 text-white rounded-xl transition-all shadow-md font-bold text-sm flex items-center gap-2"
                    >
                      {isGenerating ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Send className="w-4 h-4" /> Go</>}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
