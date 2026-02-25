"""
prompts/ — Pacote de prompts e mapeamentos de domínio.

Exporta as descrições dos 5 domínios de risco e funções auxiliares
para obter a descrição textual de cada dimensão.
"""
from .system_prompts import (
    get_domain_description,
    DOMAIN_DESCRIPTIONS
)

__all__ = [
    'get_domain_description',
    'DOMAIN_DESCRIPTIONS'
]
