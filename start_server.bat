@echo off
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║   Sistema de Análise de Risco - Iniciando Servidor          ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo.
echo Verificando configuração...
if not exist .env (
    echo ❌ Arquivo .env não encontrado!
    echo.
    echo Execute setup.bat primeiro para configurar o sistema.
    pause
    exit /b 1
)

echo ✅ Configuração OK
echo.
echo 🚀 Iniciando servidor na porta 8000...
echo.
echo O servidor estará disponível em:
echo    http://localhost:8000
echo    http://127.0.0.1:8000
echo.
echo Pressione Ctrl+C para parar o servidor
echo.

python main.py
