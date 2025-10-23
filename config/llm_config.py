"""
LLM Configuration for Microsoft Agent Framework.
Supports Azure OpenAI, OpenAI, and Groq (via OpenAI-compatible API).
"""
import os
from typing import Any
from dotenv import load_dotenv

load_dotenv()


def get_chat_client() -> Any:
    """
    Get configured chat client for Agent Framework.
    Tries providers in order: Azure OpenAI → OpenAI → Groq
    
    Returns:
        Configured chat client for creating agents
        
    Raises:
        ValueError: If no valid configuration is found
    """
    
    # Option 1: Azure OpenAI (Recommended for production)
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    if azure_endpoint:
        from agent_framework.azure import AzureOpenAIResponsesClient
        
        return AzureOpenAIResponsesClient(
            endpoint=azure_endpoint,
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
        )
    
    # Option 2: OpenAI direct
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        from openai import AsyncOpenAI
        
        return AsyncOpenAI(
            api_key=openai_key
        )
    
    # Option 3: Groq (via OpenAI-compatible API)
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        from openai import AsyncOpenAI
        
        return AsyncOpenAI(
            api_key=groq_key,
            base_url="https://api.groq.com/openai/v1"
        )
    
    raise ValueError(
        "No LLM configuration found! Please set one of:\n"
        "  - AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_API_KEY (Azure OpenAI)\n"
        "  - OPENAI_API_KEY (OpenAI)\n"
        "  - GROQ_API_KEY (Groq)"
    )


def get_model_name() -> str:
    """
    Get the model name based on active provider.
    
    Returns:
        str: Model name to use
    """
    if os.getenv("AZURE_OPENAI_ENDPOINT"):
        return os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
    elif os.getenv("OPENAI_API_KEY"):
        return os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    elif os.getenv("GROQ_API_KEY"):
        return os.getenv("GROQ_MODEL", "llama3-8b-8192")
    
    return "gpt-4o-mini"  # Default fallback


def get_model_config() -> dict:
    """
    Get model configuration parameters.
    
    Returns:
        dict: Configuration for model behavior
    """
    return {
        "temperature": float(os.getenv("LLM_TEMPERATURE", "0.2")),
        "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "4000")),
    }


def get_provider_name() -> str:
    """
    Get the name of the active LLM provider.
    
    Returns:
        str: Provider name (azure_openai, openai, or groq)
    """
    if os.getenv("AZURE_OPENAI_ENDPOINT"):
        return "azure_openai"
    elif os.getenv("OPENAI_API_KEY"):
        return "openai"
    elif os.getenv("GROQ_API_KEY"):
        return "groq"
    
    return "unknown"
