@echo off
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║   Sistema de Análise de Risco - Executando Testes           ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo.
echo Executando testes do sistema...
echo.

python tests/test_system.py

echo.
if %errorlevel% equ 0 (
    echo ✅ Todos os testes passaram!
) else (
    echo ❌ Alguns testes falharam
)

echo.
pause
