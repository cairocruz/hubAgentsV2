"""
Synthesizer agent for final consolidated analysis using Agent Framework.
"""
import asyncio
import json
from typing import List
from agents.agent_factory import create_synthesizer_agent
from models.schemas import SpecialistReport, FinalAnalysis


async def run_synthesis(approved_reports: List[SpecialistReport]) -> FinalAnalysis:
    """
    Synthesize all approved specialist reports into final analysis.
    
    Args:
        approved_reports: List of approved specialist reports
        
    Returns:
        FinalAnalysis with consolidated results
    """
    synthesizer = create_synthesizer_agent()
    
    # Prepare synthesis task
    reports_summary = "\n\n".join([
        f"=== RELATÓRIO DO AGENTE {report.agent_id} - {report.domain} ===\n{report.model_dump_json(indent=2)}"
        for report in approved_reports
    ])
    
    synthesis_message = f"""Consolide os seguintes relatórios dos agentes especialistas em uma análise final:

{reports_summary}

Forneça uma análise holística que integre todos os domínios, calcule o score final, 
determine o nível de risco e forneça recomendações práticas.

Retorne em formato JSON conforme instruído."""
    
    # Get synthesis (using Agent Framework)
    response_text = await synthesizer.run(synthesis_message, json_mode=True)
    
    # Parse response
    try:
        if '```json' in response_text:
            json_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            json_text = response_text.split('```')[1].split('```')[0].strip()
        else:
            json_text = response_text.strip()
        
        synthesis_data = json.loads(json_text)
        
        # Add specialist reports to synthesis
        synthesis_data['specialist_reports'] = [
            report.model_dump() for report in approved_reports
        ]
        
        final_analysis = FinalAnalysis(**synthesis_data)
        return final_analysis
        
    except Exception as e:
        # Create fallback synthesis
        avg_score = sum(r.preliminary_score for r in approved_reports) / len(approved_reports)
        
        if avg_score < 30:
            risk_level = "Baixo"
        elif avg_score < 65:
            risk_level = "Médio"
        else:
            risk_level = "Alto"
        
        # Collect all risk factors
        all_factors = []
        for report in approved_reports:
            all_factors.extend(report.risk_factors)
        
        return FinalAnalysis(
            final_score=avg_score,
            risk_level=risk_level,
            synthesis=f"Análise consolidada baseada em {len(approved_reports)} relatórios especializados. Score médio: {avg_score:.1f}",
            consolidated_factors=all_factors,
            recommendations=[
                "Buscar apoio de rede de suporte (família, amigos)",
                "Considerar orientação profissional (psicólogo, assistente social)",
                "Documentar situações de risco",
                "Conhecer recursos de proteção disponíveis (delegacia da mulher, casas de apoio)"
            ],
            specialist_reports=[report.model_dump() for report in approved_reports]
        )
