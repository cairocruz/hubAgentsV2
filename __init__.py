"""
hubAgentsV2 — Sistema de Análise de Risco com IA Multiagente.

Sistema avançado para análise de risco de violência doméstica utilizando
múltiplos agentes especializados orquestrados pelo framework CrewAI.

Arquitetura em 3 fases:
  Fase 1: 5 Especialistas analisam dimensões distintas (com RAG)
  Fase 2: Supervisor revisa e solicita retrabalho se necessário
  Fase 3: Sintetizador consolida tudo em um parecer final

Versão: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Hub Agents V2 Team"
__description__ = "Sistema Multiagente para Análise de Risco de Violência Doméstica"

# Importações dos módulos principais do pacote
# Nota: estes imports podem falhar se executados fora do contexto do projeto
# (são usados quando o pacote é importado como biblioteca)
from models import AnalysisRequest, FinalAnalysis
from agents import (
    create_specialist_agent,
    create_supervisor_agent,
    create_synthesizer_agent,
    run_specialist_analysis_sync,
    run_synthesis
)
from utils import DataLoader, Logger
from config import get_llm_config

__all__ = [
    '__version__',
    'AnalysisRequest',
    'FinalAnalysis',
    'create_specialist_agent',
    'create_supervisor_agent',
    'create_synthesizer_agent',
    'run_specialist_analysis_sync',
    'run_synthesis',
    'DataLoader',
    'Logger',
    'get_llm_config'
]
