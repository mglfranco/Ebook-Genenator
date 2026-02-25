@echo off
chcp 65001 >nul
title 📚 E-book Generator API V2
color 0B

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║   📚  API GERADORA DE E-BOOKS PROFISSIONAIS V2      ║
echo  ║   Design Gamma.app • Correção Ortográfica • PDF     ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

:: Configurar variáveis de ambiente
set WEASYPRINT_DLL_DIRECTORIES=C:\msys64\mingw64\bin
set PATH=C:\Program Files\Eclipse Adoptium\jre-21.0.10.7-hotspot\bin;%PATH%

:: Ativar venv e iniciar servidor
echo  [1/2] Ativando ambiente virtual...
call "%~dp0venv\Scripts\activate.bat"

echo  [2/2] Iniciando servidor Uvicorn...
echo.
echo  ┌──────────────────────────────────────────────────────┐
echo  │  🌐 API:     http://localhost:8000                   │
echo  │  📖 Swagger: http://localhost:8000/docs              │
echo  │  ❤️  Saúde:   http://localhost:8000/                  │
echo  │                                                      │
echo  │  Pressione CTRL+C para encerrar o servidor.          │
echo  └──────────────────────────────────────────────────────┘
echo.

python -m uvicorn api.main:app --host 0.0.0.0 --port 8000

pause
