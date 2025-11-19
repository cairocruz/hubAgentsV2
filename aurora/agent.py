"""
Aurora agent factory.
"""
from aurora.agent_with_tools import AuroraToolAgent
from aurora.prompts import get_aurora_prompt
from services.places_service import PlacesService
from tools.places_tool import PlacesTool

def create_aurora_agent() -> AuroraToolAgent:
    """
    Create the Aurora agent for active listening, with tool-calling capabilities.

    Returns:
        AuroraToolAgent configured as Aurora
    """
    # Initialize the service and tool
    places_service = PlacesService()
    places_tool = PlacesTool(places_service)

    # Define the tools available to Aurora
    tools = {
        "find_places": places_tool.search
    }

    return AuroraToolAgent(
        name="aurora",
        instructions=get_aurora_prompt(),
        tools=tools
    )
