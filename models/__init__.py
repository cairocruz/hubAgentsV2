"""
models/ — Pacote de schemas Pydantic para validação de dados.

Exporta os modelos de entrada e saída da API:
  - AnalysisRequest : valida as 5 respostas da usuária
  - FinalAnalysis   : resultado consolidado final
  - RiskFactor      : fator de risco individual
"""
from .schemas import (
    AnalysisRequest,
    FinalAnalysis,
    RiskFactor
)

__all__ = [
    'AnalysisRequest',
    'FinalAnalysis',
    'RiskFactor'
]
