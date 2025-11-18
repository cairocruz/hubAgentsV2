"""
Pydantic models for Aurora's conversational API.
"""
from typing import List, Optional, Union
from pydantic import BaseModel, Field

class RiskFactor(BaseModel):
    """Model for a risk factor."""
    factor: str = Field(..., description="The name of the risk factor.")
    severity: str = Field(..., description="The severity level (e.g., 'Baixo', 'Médio', 'Alto').")
    description: str = Field(..., description="Description of the risk factor.")

class AnalysisResult(BaseModel):
    """Model for complete analysis result."""
    consolidated_factors: List[RiskFactor] = Field(..., description="List of consolidated risk factors.")
    synthesis: str = Field(..., description="Holistic analysis synthesis.")
    recommendations: List[str] = Field(..., description="List of recommendations.")

class AuroraSessionStartRequest(BaseModel):
    """Request model to start a new Aurora session."""
    # Support both simple recommendations (backward compatibility) and full analysis
    recommendations: Optional[List[str]] = Field(None, description="Simple list of recommendations (legacy).")
    analysis_result: Optional[AnalysisResult] = Field(None, description="Complete analysis result with factors, synthesis, and recommendations.")
    
    def get_recommendations(self) -> List[str]:
        """Get recommendations from either format."""
        if self.analysis_result:
            return self.analysis_result.recommendations
        return self.recommendations or []
    
    def get_context_summary(self) -> str:
        """Get a rich context summary for Aurora."""
        if self.analysis_result:
            factors_summary = "; ".join([f"{f.factor} ({f.severity})" for f in self.analysis_result.consolidated_factors])
            return f"Fatores de risco: {factors_summary}. Síntese: {self.analysis_result.synthesis}"
        return "Recomendações básicas fornecidas."

class AuroraSessionStartResponse(BaseModel):
    """Response model for a new Aurora session."""
    session_id: str = Field(..., description="The unique identifier for the conversation session.")
    initial_message: str = Field(..., description="Aurora's initial welcoming message.")

class AuroraChatRequest(BaseModel):
    """Request model for a chat turn with Aurora."""
    session_id: str = Field(..., description="The session ID for the ongoing conversation.")
    message: str = Field(..., description="The user's message.")

class AuroraChatResponse(BaseModel):
    """Response model for a chat turn with Aurora."""
    session_id: str = Field(..., description="The session ID for the ongoing conversation.")
    response: str = Field(..., description="Aurora's response to the user's message.")
