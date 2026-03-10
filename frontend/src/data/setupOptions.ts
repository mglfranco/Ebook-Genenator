import { Sparkles, Briefcase, BookOpen, GraduationCap, Code } from 'lucide-react';

export const niches = [
    { id: 'fiction', title: 'Ficção & Entretenimento', description: 'Romances, Animes, Fantasia e Sci-Fi com foco em storytelling e emoção.', icon: Sparkles, color: 'from-fuchsia-500 to-purple-600' },
    { id: 'business', title: 'Vendas & Negócios', description: 'Manuais corporativos, pitch decks, relatórios de vendas persuasivos.', icon: Briefcase, color: 'from-blue-500 to-cyan-500' },
    { id: 'education', title: 'Educação & Ensino', description: 'Apostilas, resumos didáticos, livros infantis e material de apoio.', icon: GraduationCap, color: 'from-green-500 to-emerald-600' },
    { id: 'selfhelp', title: 'Autodesenvolvimento', description: 'Livros de psicologia, filosofia de vida e guias práticos.', icon: BookOpen, color: 'from-orange-500 to-yellow-500' },
    { id: 'tech', title: 'Tecnologia & Dev', description: 'Tutoriais pesados em código, manuais de arquitetura e whitepapers.', icon: Code, color: 'from-slate-600 to-gray-800' }
];

export const imageStyles = [
    { id: 'anime', title: 'Anime / Mangá', description: 'Estilo de animação japonesa 2D com cores vibrantes e expressivas.', gradient: 'from-pink-500 via-red-500 to-yellow-500' },
    { id: 'cinematic', title: 'Cinematic 3D', description: 'Renderização 3D muito realista, iluminação de cinema (Unreal Engine).', gradient: 'from-indigo-900 via-purple-900 to-black' },
    { id: 'watercolor', title: 'Aquarela Clássica', description: 'Traços suaves e artísticos, ideal para livros infantis e contos leves.', gradient: 'from-blue-200 via-teal-200 to-emerald-200' },
    { id: 'neon', title: 'Sci-Fi Neon / Cyberpunk', description: 'Luzes de neon brilhantes, ambientes escuros, alta tecnologia estética.', gradient: 'from-fuchsia-600 via-purple-600 to-cyan-500' },
    { id: 'minimalist', title: 'Minimalista & Vetorial', description: 'Formas geométricas limpas, cores flat style corporativo.', gradient: 'from-gray-100 via-gray-200 to-gray-300', isLight: true },
    { id: 'none', title: 'Sem Imagens', description: 'Apenas texto, focando 100% no conteúdo.', gradient: 'from-gray-800 to-gray-900' }
];

export const coverStyles = [
    { id: 'modern', title: 'Moderno & Tipográfico', description: 'Foco na fonte grande e chamativa, com fundo abstrato super clean.' },
    { id: 'full-image', title: 'Imagem Full-Screen', description: 'A arte selecionada ocupa toda a capa, título com sombra suave no rodapé.' },
    { id: 'classic', title: 'Clássico Literário', description: 'Margens brancas e serifas elegantes remetendo a livros tradicionais físicos.' },
];

export const writingTones = [
    { id: 'creative', title: 'Criativo & Emotivo', example: '"O vento cortava como lâminas na escuridão. Akira sabia que a cidade nunca dormia, apenas aguardava a próxima batida cibernética."' },
    { id: 'direct', title: 'Direto & Persuasivo', example: '"Se você quer dobrar suas Vendas B2B este trimestre, esta estratégia simples e pragmática mudará completamente seu jogo."' },
    { id: 'didactic', title: 'Didático & Acessível', example: '"Imagine que uma célula é como uma pequena cidade. O núcleo seria a prefeitura governando tudo de forma organizada."' },
    { id: 'formal', title: 'Formal Acadêmico', example: '"Os dados empíricos demonstram uma correlação substancial entre a variável observada e a anomalia estrutural reportada neste documento."' },
];

export const pageLayouts = [
    { id: 'standard', title: 'Padrão Editorial', description: 'Fundo branco ou creme, fontes escuras, margens confortáveis. (Ideal para impressão)' },
    { id: 'darkmode', title: 'Dark Mode (Sci-Fi)', description: 'Fundo escuro profundo, fontes claras com ocasionais destaques em néon. (Apenas Digital)' },
    { id: 'twocolumns', title: 'Revista / Duas Colunas', description: 'Texto diagramado em dupla coluna para relatórios dinâmicos e manuais técnicos.' }
];
