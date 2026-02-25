"""
config/llm_config.py — Configuração do provedor de LLM para o CrewAI.

Este módulo centraliza a seleção do provedor de modelo de linguagem (Gemini,
OpenAI ou Groq) e seus hiperparâmetros. O CrewAI utiliza o LiteLLM por baixo
dos panos, então os nomes de modelo retornados aqui seguem a convenção do
LiteLLM (ex: "gemini/gemini-1.5-flash", "openai/gpt-4o-mini").

Variáveis de ambiente esperadas (definidas no .env):
  - LLM_PROVIDER        : "gemini" (padrão) | "openai" | "groq"
  - GEMINI_API_KEY       : chave da API do Google Gemini
  - GEMINI_MODEL         : nome do modelo Gemini (padrão: gemini/gemini-1.5-flash)
  - OPENAI_API_KEY       : chave da API da OpenAI
  - OPENAI_MODEL         : nome do modelo OpenAI (padrão: openai/gpt-4o-mini)
  - GROQ_API_KEY         : chave da API da Groq
  - GROQ_MODEL           : nome do modelo Groq (padrão: llama3-8b-8192)
  - LLM_TEMPERATURE      : temperatura de geração (padrão: 0.2)
  - LLM_MAX_TOKENS       : máximo de tokens na resposta (padrão: 4000)
"""
import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env para os.environ
load_dotenv()


def get_model_name() -> str:
    """
    Retorna o nome do modelo de linguagem no formato esperado pelo LiteLLM.

    A lógica seleciona o provedor com base na variável LLM_PROVIDER:
      - "groq"   → prefixo "openai/" para que o CrewAI roteie via OpenAI-compat
      - "openai"  → modelo direto com prefixo "openai/"
      - qualquer outro (padrão) → Gemini, prefixo "gemini/"

    Também emite avisos se a chave de API correspondente não estiver configurada.

    Returns:
        str: String do modelo (ex: "gemini/gemini-1.5-flash")
    """
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()

    # --- Provedor GROQ (modelos Meta Llama via Groq Cloud) ---
    if provider == "groq":
        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key or groq_key.startswith("sua_chave"):
            print("⚠️ AVISO: GROQ_API_KEY não configurada no .env!")
        
        model = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        # O CrewAI/LiteLLM precisa do prefixo "openai/" para rotear
        # chamadas ao endpoint OpenAI-compatible da Groq
        if not model.startswith("openai/"):
            model = f"openai/{model}"
        return model

    # --- Provedor OPENAI ---
    elif provider == "openai":
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or openai_key.startswith("sua_chave"):
            print("⚠️ AVISO: OPENAI_API_KEY não configurada no .env!")
        return os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini")

    # --- Provedor GEMINI (padrão) ---
    else:
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key or gemini_key.startswith("sua_chave"):
            print("⚠️ AVISO: GEMINI_API_KEY não configurada no .env!")
        return os.getenv("GEMINI_MODEL", "gemini/gemini-1.5-flash")


def get_model_config() -> dict:
    """
    Retorna os hiperparâmetros de geração do modelo.

    Lê do .env ou usa valores padrão conservadores:
      - temperature  = 0.2  (respostas mais determinísticas)
      - max_tokens   = 4000 (limite de tokens na resposta)

    Returns:
        dict: Dicionário com "temperature" e "max_tokens".
    """
    return {
        "temperature": float(os.getenv("LLM_TEMPERATURE", "0.2")),
        "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "4000")),
    }


def get_provider_name() -> str:
    """
    Retorna o nome do provedor de LLM ativo (ex: "gemini", "openai", "groq").

    Usado para exibir no log ou no endpoint /health.

    Returns:
        str: Nome do provedor em minúsculas.
    """
    return os.getenv("LLM_PROVIDER", "gemini").lower()
