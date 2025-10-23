@echo off
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║   Sistema de Análise de Risco - Setup Automático            ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

echo [1/5] Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado! Instale Python 3.9+ primeiro.
    pause
    exit /b 1
)
echo ✅ Python encontrado
echo.

echo [2/5] Criando ambiente virtual...
if not exist venv (
    python -m venv venv
    echo ✅ Ambiente virtual criado
) else (
    echo ℹ️  Ambiente virtual já existe
)
echo.

echo [3/5] Ativando ambiente virtual...
call venv\Scripts\activate.bat
echo ✅ Ambiente virtual ativado
echo.

echo [4/5] Instalando dependências...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar dependências
    pause
    exit /b 1
)
echo ✅ Dependências instaladas
echo.

echo [5/5] Verificando configuração...
if not exist .env (
    echo ⚠️  Arquivo .env não encontrado
    echo.
    echo Criando .env a partir do exemplo...
    copy .env.example .env
    echo.
    echo ⚠️  IMPORTANTE: Edite o arquivo .env e adicione sua GROQ_API_KEY
    echo.
    echo Para obter a chave:
    echo   1. Acesse: https://console.groq.com
    echo   2. Crie uma conta gratuita
    echo   3. Vá para API Keys
    echo   4. Crie uma nova chave
    echo   5. Cole no arquivo .env
    echo.
    notepad .env
) else (
    echo ✅ Arquivo .env encontrado
)
echo.

echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                    Setup Concluído!                          ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.
echo Próximos passos:
echo   1. Certifique-se de que GROQ_API_KEY está configurada no .env
echo   2. Execute: run_tests.bat (para testar)
echo   3. Execute: start_server.bat (para iniciar o servidor)
echo.
pause
