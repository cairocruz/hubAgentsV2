"""
utils/validators.py — Utilitários de validação de configuração de API.

Contém funções para verificar se as chaves de API estão corretamente
configuradas antes de iniciar o sistema. Atualmente valida apenas
a chave da Groq, mas pode ser estendido para outros provedores.

Uso:
  python -m utils.validators   # executa validação da chave Groq
"""
import os
from groq import Groq


def validate_groq_api_key() -> tuple[bool, str]:
    """
    Valida a chave de API da Groq fazendo uma requisição mínima de teste.

    Verificações realizadas:
      1. A variável GROQ_API_KEY existe no ambiente
      2. O formato começa com "gsk_" (padrão Groq)
      3. A chave é aceita pela API (chamada real com max_tokens=10)

    Returns:
        Tupla (is_valid: bool, message: str) indicando o resultado.
    """
    api_key = os.getenv("GROQ_API_KEY")
    
    # Verificação 1: chave existe?
    if not api_key:
        return False, "GROQ_API_KEY not found in environment variables"
    
    # Verificação 2: formato correto?
    if not api_key.startswith("gsk_"):
        return False, "Invalid API key format (should start with 'gsk_')"
    
    try:
        # Verificação 3: chamada real à API com payload mínimo
        client = Groq(api_key=api_key)
        client.chat.completions.create(
            messages=[{"role": "user", "content": "test"}],
            model="llama3-8b-8192",
            max_tokens=10
        )
        return True, "API key is valid"
    except Exception as e:
        return False, f"API key validation failed: {str(e)}"


# Permite execução direta para teste rápido da chave
if __name__ == "__main__":
    is_valid, message = validate_groq_api_key()
    print(f"{'✅' if is_valid else '❌'} {message}")
