"""
Review loop with supervisor for quality control using Agent Framework.
"""
import asyncio
import json
from typing import List, Tuple
from agents.agent_factory import create_supervisor_agent, create_specialist_agent
from models.schemas import SpecialistReport, ReviewFeedback
from utils.data_loader import DataLoader


async def run_review_loop(
    report: SpecialistReport,
    data_loader: DataLoader,
    user_response: str,
    max_rework: int = 1
) -> Tuple[SpecialistReport, List[ReviewFeedback]]:
    """
    Run review loop for a single specialist report.
    
    Args:
        report: Initial specialist report
        data_loader: DataLoader for Few-Shot examples
        user_response: Original user response
        max_rework: Maximum number of rework attempts
        
    Returns:
        Tuple of (final_report, feedback_history)
    """
    supervisor = create_supervisor_agent()
    
    feedback_history = []
    current_report = report
    
    for attempt in range(max_rework + 1):
        # Create review task
        review_message = f"""Revise o seguinte relatório de análise:

RELATÓRIO DO AGENTE:
{current_report.model_dump_json(indent=2)}

Avalie a qualidade da análise e determine se está APROVADO ou precisa de REVISÃO."""
        
        # Get supervisor feedback (using Agent Framework)
        response_text = await supervisor.run(review_message, json_mode=True)
        
        # Parse feedback
        try:
            if '```json' in response_text:
                json_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                json_text = response_text.split('```')[1].split('```')[0].strip()
            else:
                json_text = response_text.strip()
            
            feedback_data = json.loads(json_text)
            feedback = ReviewFeedback(**feedback_data)
        except Exception as e:
            # Default to approval on parse error
            feedback = ReviewFeedback(
                status="APROVADO",
                feedback=None,
                agent_id=current_report.agent_id
            )
        
        feedback_history.append(feedback)
        
        # Check if approved
        if feedback.status == "APROVADO":
            break
        
        # If not last attempt, rework
        if attempt < max_rework:
            current_report = await _rework_analysis(
                current_report,
                feedback,
                data_loader,
                user_response
            )
    
    return current_report, feedback_history


async def _rework_analysis(
    original_report: SpecialistReport,
    feedback: ReviewFeedback,
    data_loader: DataLoader,
    user_response: str
) -> SpecialistReport:
    """
    Have specialist rework the analysis based on feedback.
    
    Args:
        original_report: Original report
        feedback: Supervisor feedback
        data_loader: DataLoader instance
        user_response: Original user response
        
    Returns:
        Improved SpecialistReport
    """
    agent_id = int(original_report.agent_id)
    examples = data_loader.get_few_shot_examples(agent_id, num_examples=5)
    
    specialist = create_specialist_agent(agent_id, examples)
    
    rework_message = f"""RELATO ATUAL DA USUÁRIA:
"{user_response}"

SUA ANÁLISE ANTERIOR:
{original_report.model_dump_json(indent=2)}

FEEDBACK DO SUPERVISOR:
{feedback.feedback}

Por favor, refaça sua análise incorporando o feedback acima.
Retorne a análise melhorada em formato JSON."""
    
    # Run specialist with rework task (using Agent Framework)
    response_text = await specialist.run(rework_message, json_mode=True)
    
    try:
        if '```json' in response_text:
            json_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            json_text = response_text.split('```')[1].split('```')[0].strip()
        else:
            json_text = response_text.strip()
        
        report_data = json.loads(json_text)
        improved_report = SpecialistReport(**report_data)
        return improved_report
    except Exception as e:
        # Return original if rework fails
        return original_report
