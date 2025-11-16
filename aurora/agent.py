"""
Aurora agent factory.
"""
from agents.agent_factory import AgentWrapper
from aurora.prompts import get_aurora_prompt

def create_aurora_agent() -> AgentWrapper:
    """
    Create the Aurora agent for active listening.

    Returns:
        AgentWrapper configured as Aurora
    """
    return AgentWrapper(
        name="aurora",
        instructions=get_aurora_prompt()
    )
