"""
agents/ — Pacote de orquestração multiagente.

Exporta a classe principal RiskAnalysisCrew, que coordena os 7 agentes
(5 especialistas + 1 supervisor + 1 sintetizador) nas 3 fases de análise.
"""
from .risk_analysis_crew import RiskAnalysisCrew

__all__ = [
    'RiskAnalysisCrew'
]
