# 📚 API Geradora de E-books Profissionais V2

Motor Gerador de E-books — API REST (FastAPI) com **correção ortográfica automática**, **direção de arte consistente por tema**, **design Gamma.app com glassmorphism** e compilação PDF via WeasyPrint.

---

## ⚙️ Requisitos do Sistema

| Dependência | Finalidade |
|---|---|
| **Python 3.10+** | Runtime |
| **Java JRE 11+** | Necessário para o LanguageTool (correção ortográfica) |
| **MSYS2** + Pango | Bibliotecas GTK para WeasyPrint |

### Instalação (Windows)

```powershell
# 1. Java JRE
winget install --id EclipseAdoptium.Temurin.21.JRE --silent

# 2. MSYS2 + Pango
winget install --id MSYS2.MSYS2 --silent
C:\msys64\usr\bin\bash.exe -lc "pacman -S --noconfirm mingw-w64-x86_64-pango"
```

---

## 🚀 Setup & Inicialização

```powershell
# 1. Ambiente virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Dependências
pip install -r requirements.txt

# 3. Variáveis de ambiente
$env:WEASYPRINT_DLL_DIRECTORIES = "C:\msys64\mingw64\bin"

# 4. Servidor
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Acesse: **http://localhost:8000/docs** (Swagger UI)

---

## 📖 Endpoint: `POST /generate-ebook`

### Payload JSON

```json
{
    "title": "Inteligência Artificial: O Guia Definitivo",
    "author": "Dr. Ana Carolina Silva",
    "chapter_count": 3,
    "theme": "Ficção Científica Neon",
    "chapters": [
        {
            "title": "Introdução à IA",
            "content": "# O que é IA?\n\nA inteligência artificial é um campo da ciência..."
        },
        {
            "title": "Machine Learning",
            "content": "# Aprendizado de Máquina\n\nO ML permite aprender padrões..."
        },
        {
            "title": "Deep Learning",
            "content": "# Redes Neurais\n\nAs redes neurais são a base do Deep Learning..."
        }
    ]
}
```

### Parâmetros

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `title` | string | ✅ | Título do livro |
| `author` | string | ✅ | Nome do autor |
| `chapter_count` | int | ✅ | Quantidade de capítulos (validado contra `chapters`) |
| `theme` | string | ✅ | Tema visual (âncora de estilo para todas as imagens) |
| `chapters` | array | ✅ | Lista de capítulos (título + conteúdo Markdown) |

### Temas Disponíveis

| Tema | Estética |
|---|---|
| `Ficção Científica Neon` | Ciano-neon, roxo elétrico, linhas futuristas |
| `Minimalista Corporativo` | Tons neutros escuros, linhas discretas |
| `Aquarela Clássica` | Gradientes suaves, círculos orgânicos |
| `Vintage Retrô` | Sépia, marrons elegantes |
| `Natureza Orgânica` | Verdes vibrantes |
| `Romance` | Tons rosa e magenta |
| *(texto livre)* | O sistema interpreta keywords automaticamente |

### Exemplos de Requisição

```bash
# cURL
curl -X POST http://localhost:8000/generate-ebook \
  -H "Content-Type: application/json" \
  -d @test_payload.json \
  --output meu_ebook.pdf
```

```powershell
# PowerShell
$env:WEASYPRINT_DLL_DIRECTORIES = "C:\msys64\mingw64\bin"
Invoke-RestMethod -Uri "http://localhost:8000/generate-ebook" `
  -Method POST -ContentType "application/json" `
  -Body (Get-Content -Raw test_payload.json) `
  -OutFile "meu_ebook.pdf"
```

---

## 🏗️ Arquitetura

```
GERADOR DE EBOOKS/
├── api/
│   ├── main.py              # FastAPI + endpoint
│   ├── models.py            # Modelos Pydantic (chapter_count + theme)
│   ├── text_corrector.py    # Correção ortográfica (LanguageTool PT-BR)
│   ├── image_generator.py   # Imagens tema-consistentes (Pillow)
│   └── pdf_engine.py        # Jinja2 → WeasyPrint → PDF
├── templates/
│   ├── ebook.html           # Template Jinja2 (glassmorphism cards)
│   └── style.css            # CSS Paged Media (Gamma.app aesthetic)
├── assets/                  # Imagens geradas (runtime)
├── output/                  # PDFs compilados (runtime)
└── requirements.txt
```

### Pipeline de Geração

```
POST JSON
  → 1. Correção ortográfica (language-tool-python / PT-BR)
  → 2. Geração de imagens tema-consistentes (Pillow)
  → 3. Markdown → HTML + Jinja2 template rendering
  → 4. CSS Paged Media (glassmorphism, A4, page numbers)
  → 5. WeasyPrint PDF compilation
  → FileResponse (download)
```

---

## 📄 Licença

MIT
