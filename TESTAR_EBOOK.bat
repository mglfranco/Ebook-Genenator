@echo off
chcp 65001 >nul
title 🧪 Teste do E-book Generator
color 0E

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║   🧪  TESTE - GERADOR DE E-BOOKS V2                 ║
echo  ║   Enviando payload de teste para a API...            ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

:: Configurar variáveis de ambiente
set WEASYPRINT_DLL_DIRECTORIES=C:\msys64\mingw64\bin
set PATH=C:\Program Files\Eclipse Adoptium\jre-21.0.10.7-hotspot\bin;%PATH%

:: Ativar venv
call "%~dp0venv\Scripts\activate.bat"

echo  [1/3] Verificando se o servidor esta ativo...

python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/', timeout=5); print('  ✅ Servidor ativo!')" 2>nul
if errorlevel 1 (
    echo.
    echo  ❌ ERRO: O servidor nao esta rodando!
    echo  Execute primeiro o arquivo INICIAR_API.bat
    echo.
    pause
    exit /b 1
)

echo.
echo  [2/3] Enviando payload de teste (3 capitulos)...
echo         Isso pode levar 1-2 minutos na primeira vez
echo         (download do LanguageTool + correção ortografica)
echo.

python -c ^
"import urllib.request, os, time; ^
payload = open(r'%~dp0test_payload.json', 'rb').read(); ^
req = urllib.request.Request('http://localhost:8000/generate-ebook', data=payload, headers={'Content-Type': 'application/json'}, method='POST'); ^
t0 = time.time(); ^
resp = urllib.request.urlopen(req, timeout=600); ^
pdf_path = r'%~dp0output\meu_ebook_teste.pdf'; ^
open(pdf_path, 'wb').write(resp.read()); ^
elapsed = time.time() - t0; ^
print(f'  ✅ PDF gerado com sucesso!'); ^
print(f'  📄 Tamanho: {os.path.getsize(pdf_path):,} bytes'); ^
print(f'  ⏱️  Tempo: {elapsed:.1f}s'); ^
print(f'  📂 Salvo em: {pdf_path}'); ^
"

if errorlevel 1 (
    echo.
    echo  ❌ Erro na geracao do PDF. Verifique os logs do servidor.
    echo.
    pause
    exit /b 1
)

echo.
echo  [3/3] Abrindo PDF gerado...
start "" "%~dp0output\meu_ebook_teste.pdf"

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║   ✅  TESTE CONCLUIDO COM SUCESSO!                  ║
echo  ║   O PDF deve ter aberto no seu visualizador.        ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

pause
