FROM python:3.11-slim

# Instalar dependências de sistema (Java para LanguageTool, e bibliotecas pro WeasyPrint)
RUN apt-get update && apt-get install -y \
    default-jre \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libjpeg-dev \
    libopenjp2-7-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar os arquivos de dependência primeiro para aproveitar cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto do código da API e Templates
COPY api/ api/
COPY templates/ templates/

# Copiar o diretório static inteiro (contém index.html, JS, CSS, Ícones do PWA)
# O app do FastAPI vai servir a pasta web/static inteira
COPY static/ static/

# Variável de porta e host pro Uvicorn
ENV PORT=10000
EXPOSE 10000

# Comando para rodar a aplicação via Uvicorn na porta 10000 (Padrão do Render)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "10000"]
