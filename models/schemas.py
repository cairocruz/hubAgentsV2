"""
models/schemas.py — Modelos Pydantic para validação e serialização de dados.

Define os schemas (contratos) utilizados pela API FastAPI:

  - AnalysisRequest  : corpo da requisição POST /analyze (5 respostas da usuária)
  - RiskFactor       : fator de risco individual identificado por um agente
  - SpecialistReport : relatório completo de um agente especialista
  - FinalAnalysis    : resultado consolidado final (sintetizador)

Todos os modelos usam validação automática do Pydantic v2 com Field constraints.
"""
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class AnalysisRequest(BaseModel):
    """
    Modelo de entrada para o endpoint POST /analyze.

    A usuária responde exatamente 5 perguntas (uma por dimensão de risco).
    Cada resposta é uma string livre. A validação garante que o array
    tenha exatamente 5 elementos (min_length=5, max_length=5).
    """
    responses: List[str] = Field(
        ..., 
        min_length=5, 
        max_length=5,
        description="Exatamente 5 respostas da usuária para análise (uma por dimensão)",
        examples=[
            [
                "Sim, ele às vezes grita comigo quando está estressado",
                "Não, nunca tivemos problemas sérios",
                "Ele controla muito o que eu faço",
                "Não tenho família por perto",
                "Tenho medo às vezes"
            ]
        ]
    )
    
    # Exemplo extra para documentação OpenAPI (Swagger)
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "responses": [
                        "Ele me xingou algumas vezes durante discussões",
                        "Sim, ele quebrou objetos na casa quando ficou irritado",
                        "Ele não gosta quando eu saio com minhas amigas",
                        "Tenho uma amiga próxima que me apoia",
                        "Estou preocupada com o comportamento dele ultimamente"
                    ]
                }
            ]
        }
    }


class RiskFactor(BaseModel):
    """
    Fator de risco individual identificado na análise.

    Cada especialista pode retornar múltiplos fatores. O sintetizador
    consolida todos em uma lista final.

    Campos:
      - factor     : nome curto do fator (ex: "Controle excessivo")
      - severity   : nível de gravidade — restrito a Baixo/Médio/Alto
      - description: explicação detalhada do fator observado
    """
    factor: str = Field(
        ..., 
        description="Nome do fator de risco",
        examples=["Controle excessivo", "Isolamento social"]
    )
    severity: Literal["Baixo", "Médio", "Alto"] = Field(
        ..., 
        description="Nível de gravidade do fator"
    )
    description: str = Field(
        ..., 
        description="Descrição detalhada do fator identificado",
        examples=["Parceiro demonstra comportamento controlador sobre atividades sociais"]
    )


class SpecialistReport(BaseModel):
    """
    Relatório gerado por um agente especialista (Fase 1).

    Contém a análise detalhada de uma única dimensão de risco,
    incluindo score preliminar e fatores identificados.

    Campos:
      - agent_id          : identificador do especialista ("1" a "5")
      - domain            : nome do domínio de expertise
      - analysis          : texto completo da análise
      - preliminary_score : score de risco 0-100
      - risk_factors      : lista de RiskFactor identificados
      - justification     : justificativa para o score atribuído
    """
    agent_id: str = Field(..., description="Identificador do agente especialista")
    domain: str = Field(..., description="Domínio de expertise do agente")
    analysis: str = Field(..., description="Análise detalhada da resposta")
    preliminary_score: float = Field(..., ge=0, le=100, description="Score preliminar de risco (0-100)")
    risk_factors: List[RiskFactor] = Field(default_factory=list, description="Fatores de risco identificados")
    justification: str = Field(..., description="Justificativa para o score")


class FinalAnalysis(BaseModel):
    """
    Análise final consolidada pelo agente Sintetizador (Fase 3).

    Combina os resultados dos 5 especialistas em um único parecer final
    com classificação de risco e recomendações de ação.

    Campos:
      - risk_score          : score consolidado 0-100
      - risk_level          : classificação textual (BAIXO/MODERADO/ALTO/CRÍTICO)
      - consolidated_factors: lista unificada de todos os fatores de risco
      - recommendations     : sugestões de ação para a usuária
    """
    risk_score: float = Field(..., ge=0, le=100, description="Score final consolidado de risco (0-100)")
    risk_level: Literal["BAIXO", "MODERADO", "ALTO", "CRÍTICO"] = Field(..., description="Classificação geral de risco")
    consolidated_factors: List[RiskFactor] = Field(..., description="Todos os fatores de risco identificados")
    recommendations: List[str] = Field(default_factory=list, description="Ações recomendadas")
