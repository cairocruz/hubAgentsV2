"""
Aurora agent with tool-calling capabilities.
"""
import json
from typing import List, Dict, Any, Callable
from agents.agent_factory import AgentWrapper

class AuroraToolAgent(AgentWrapper):
    """
    An agent that can use tools.
    """

    def __init__(self, name: str, instructions: str, tools: Dict[str, Callable] = None):
        """
        Initializes the AuroraToolAgent.

        Args:
            name (str): The name of the agent.
            instructions (str): The system instructions for the agent.
            tools (Dict[str, Callable], optional): A dictionary of tools available to the agent.
        """
        super().__init__(name, instructions)
        self.tools = tools or {}

    async def run(self, task: List[Dict], json_mode: bool = True) -> str:
        """
        Executes the agent task, potentially using tools.

        Args:
            task (List[Dict]): The conversation history.
            json_mode (bool, optional): Whether to enforce JSON response format. Defaults to True.

        Returns:
            str: The agent's response.
        """
        # First, get the initial response from the model
        initial_response_str = await super().run(task, json_mode)

        try:
            initial_response = json.loads(initial_response_str)
        except json.JSONDecodeError:
            return initial_response_str # Return as is if not valid JSON

        # Check if the model wants to call a tool
        if "tool_call" in initial_response:
            tool_call = initial_response["tool_call"]
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("arguments", {})

            if tool_name in self.tools:
                # Execute the tool
                tool_function = self.tools[tool_name]
                try:
                    tool_result = tool_function(**tool_args)
                except Exception as e:
                    tool_result = f"Error executing tool {tool_name}: {str(e)}"

                # Add the tool result to the conversation history
                task.append({"role": "assistant", "content": initial_response_str})
                task.append({"role": "tool", "name": tool_name, "content": tool_result})

                # Call the model again with the tool result
                return await super().run(task, json_mode)
            else:
                # Tool not found, return an error message
                error_message = f"Tool '{tool_name}' not found."
                task.append({"role": "assistant", "content": initial_response_str})
                task.append({"role": "tool", "name": tool_name, "content": error_message})
                return await super().run(task, json_mode)

        # If no tool call, return the initial response
        return initial_response_str
