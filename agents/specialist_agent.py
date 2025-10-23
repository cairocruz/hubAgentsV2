"""
Pydantic models for data validation and serialization.
"""
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class AnalysisRequest(BaseModel):
    """Request model for analysis endpoint."""
    responses: List[str] = Field(
        ..., 
        min_length=5, 
        max_length=5,
        description="Exactly 5 user responses to analyze",
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
    """Individual risk factor identified."""
    factor: str = Field(
        ..., 
        description="Name of the risk factor",
        examples=["Controle excessivo", "Isolamento social"]
    )
    severity: Literal["Baixo", "Médio", "Alto"] = Field(
        ..., 
        description="Severity level"
    )
    description: str = Field(
        ..., 
        description="Detailed description of the factor",
        examples=["Parceiro demonstra comportamento controlador sobre atividades sociais"]
    )


class SpecialistReport(BaseModel):
    """Report from a specialist agent."""
    agent_id: str = Field(..., description="Specialist agent identifier")
    domain: str = Field(..., description="Domain of expertise")
    analysis: str = Field(..., description="Detailed analysis of the response")
    preliminary_score: float = Field(..., ge=0, le=100, description="Preliminary risk score")
    risk_factors: List[RiskFactor] = Field(default_factory=list, description="Identified risk factors")
    justification: str = Field(..., description="Justification for the score")


class ReviewFeedback(BaseModel):
    """Feedback from supervisor agent."""
    status: Literal["APROVADO", "REVISAR"] = Field(..., description="Review status")
    feedback: Optional[str] = Field(None, description="Detailed feedback if revision needed")
    agent_id: str = Field(..., description="Agent being reviewed")


class FinalAnalysis(BaseModel):
    """Final consolidated analysis."""
    final_score: float = Field(..., ge=0, le=100, description="Final consolidated risk score")
    risk_level: Literal["Baixo", "Médio", "Alto"] = Field(..., description="Overall risk classification")
    consolidated_factors: List[RiskFactor] = Field(..., description="All identified risk factors")
    synthesis: str = Field(..., description="Holistic analysis synthesizing all reports")
    recommendations: List[str] = Field(default_factory=list, description="Recommended actions")
    specialist_reports: List[SpecialistReport] = Field(..., description="All approved specialist reports")


class LogEvent(BaseModel):
    """Individual log event."""
    timestamp: datetime = Field(default_factory=datetime.now)
    event_type: Literal[
        "request_received",
        "specialist_analysis",
        "reviewer_feedback", 
        "rework_attempt",
        "final_synthesis",
        "error"
    ]
    agent_id: Optional[str] = None
    attempt: Optional[int] = None
    data: Dict = Field(default_factory=dict)


class RequestLog(BaseModel):
    """Complete request log."""
    request_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    request_payload: Dict
    events: List[LogEvent] = Field(default_factory=list)
    response: Optional[Dict] = None
    duration_seconds: Optional[float] = None