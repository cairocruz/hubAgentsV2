@echo off
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║   Sistema de Análise de Risco - Exemplos de Uso             ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

echo ⚠️  IMPORTANTE: Certifique-se de que o servidor está rodando!
echo.
echo Execute start_server.bat em outra janela primeiro.
echo.
pause

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo.
echo Executando exemplos de uso da API...
echo.

python examples/usage_examples.py

echo.
pause
