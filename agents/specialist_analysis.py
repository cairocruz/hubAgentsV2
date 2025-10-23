"""
Specialist analysis with parallel execution using Agent Framework.
"""
import asyncio
import json
from typing import List
from agents.agent_factory import create_specialist_agent
from utils.data_loader import DataLoader
from models.schemas import SpecialistReport


async def run_specialist_analysis(
    responses: List[str],
    data_loader: DataLoader
) -> List[SpecialistReport]:
    """
    Run parallel analysis by all 5 specialist agents.
    
    Args:
        responses: List of 5 user responses
        data_loader: DataLoader instance for Few-Shot examples
        
    Returns:
        List of SpecialistReport objects
    """
    
    async def analyze_single(agent_id: int, response: str) -> SpecialistReport:
        """Analyze single response with one specialist."""
        # Get Few-Shot examples for this agent
        examples = data_loader.get_few_shot_examples(agent_id, num_examples=5)
        
        # Create specialist agent (using Agent Framework)
        specialist = create_specialist_agent(agent_id, examples)
        
        # Create task message
        task_message = f"""RELATO ATUAL DA USUÁRIA:
"{response}"

Analise este relato com base no seu domínio de expertise e nos exemplos fornecidos.
Retorne sua análise em formato JSON conforme instruído."""
        
        # Run agent (Agent Framework uses .run() instead of initiate_chat)
        response_text = await specialist.run(task_message, json_mode=True)
        
        # Parse JSON response
        try:
            # Try to extract JSON from response
            if '```json' in response_text:
                json_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                json_text = response_text.split('```')[1].split('```')[0].strip()
            else:
                json_text = response_text.strip()
            
            report_data = json.loads(json_text)
            report = SpecialistReport(**report_data)
            return report
        except Exception as e:
            # Return error report
            return SpecialistReport(
                agent_id=str(agent_id),
                domain=f"Specialist {agent_id}",
                analysis=f"Error parsing response: {str(e)}",
                preliminary_score=50.0,
                risk_factors=[],
                justification=f"Raw response: {response_text[:500]}"
            )
    
    # Run all 5 specialists in parallel
    tasks = [
        analyze_single(agent_id, response)
        for agent_id, response in enumerate(responses, start=1)
    ]
    
    reports = await asyncio.gather(*tasks)
    return reports


def run_specialist_analysis_sync(
    responses: List[str],
    data_loader: DataLoader
) -> List[SpecialistReport]:
    """
    Synchronous wrapper for run_specialist_analysis.
    
    Args:
        responses: List of 5 user responses
        data_loader: DataLoader instance
        
    Returns:
        List of SpecialistReport objects
    """
    return asyncio.run(run_specialist_analysis(responses, data_loader))
