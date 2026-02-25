"""
config/ — Pacote de configuração do sistema.

Exporta funções para obter o nome do modelo LLM, seus hiperparâmetros
e o nome do provedor ativo (Gemini, OpenAI ou Groq).
"""
from .llm_config import (
    get_model_name,
    get_model_config,
    get_provider_name
)

__all__ = [
    'get_model_name',
    'get_model_config',
    'get_provider_name'
]
