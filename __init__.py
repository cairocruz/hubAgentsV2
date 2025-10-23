"""
Sistema de Análise de Risco com IA Multiagente

Sistema avançado para análise de risco de violência doméstica
utilizando múltiplos agentes especializados com framework AutoGen.

Versão: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Hub Agents V2 Team"
__description__ = "Sistema Multiagente para Análise de Risco de Violência Doméstica"

# Import principais módulos
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
