"""
Agent factory for creating agents using Microsoft Agent Framework.
Maintains same public interface as original AutoGen implementation.
"""
import json
from typing import Optional, List, Dict, Union
from config.llm_config import get_chat_client, get_model_name, get_model_config, get_provider_name
from prompts.system_prompts import (
    get_specialist_prompt,
    get_supervisor_prompt,
    get_synthesizer_prompt,
    get_domain_description
)


class AgentWrapper:
    """
    Wrapper for Agent Framework agents to provide unified interface.
    Works with Azure OpenAI, OpenAI, and Groq.
    """
    
    def __init__(self, name: str, instructions: str):
        self.name = name
        self.instructions = instructions
        self.client = get_chat_client()
        self.model = get_model_name()
        self.config = get_model_config()
        self.provider = get_provider_name()
    
    async def run(self, task: Union[str, List[Dict]], json_mode: bool = True) -> str:
        """
        Execute agent task and return response.
        
        Args:
            task: Task description/prompt for the agent, or a list of messages for conversational context.
            json_mode: Whether to enforce JSON response format
            
        Returns:
            str: Agent's response (JSON string if json_mode=True)
        """
        if isinstance(task, str):
            messages = [
                {"role": "system", "content": self.instructions},
                {"role": "user", "content": task}
            ]
        else:
            # task is a list of messages (conversation history)
            messages = task.copy()  # Copy to avoid modifying original
            
            # Ensure system instructions are present in the conversation
            # If the first message isn't a system message, prepend our instructions
            if not messages or messages[0]["role"] != "system":
                messages.insert(0, {"role": "system", "content": self.instructions})
            # If there's already a system message, ensure it contains our instructions
            elif self.instructions not in messages[0]["content"]:
                # Merge instructions with existing system message
                messages[0]["content"] = self.instructions + "\n\n" + messages[0]["content"]
        
        try:
            # Handle different provider APIs
            if self.provider == "azure_openai":
                # Agent Framework with Azure OpenAI
                from agent_framework import ChatAgent
                agent = ChatAgent(chat_client=self.client, name=self.name, instructions=self.instructions)

                if isinstance(task, str):
                    response = await agent.run(task)
                else:
                    thread = await agent.get_new_thread()
                    for message in messages:
                        await thread.add_message(message)
                    response = await agent.run(thread)

                return str(response)
            
            else:
                # OpenAI or Groq via AsyncOpenAI client
                kwargs = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": self.config["temperature"],
                    "max_tokens": self.config["max_tokens"],
                }
                
                if json_mode:
                    kwargs["response_format"] = {"type": "json_object"}
                
                response = await self.client.chat.completions.create(**kwargs)
                return response.choices[0].message.content
                
        except Exception as e:
            error_msg = f"Error in agent {self.name}: {str(e)}"
            print(f"⚠️ {error_msg}")
            
            if json_mode:
                return json.dumps({
                    "error": error_msg,
                    "status": "failed",
                    "agent": self.name
                })
            return error_msg


def create_specialist_agent(agent_id: int, examples: str) -> AgentWrapper:
    """
    Create a specialist agent for domain-specific analysis.
    
    Args:
        agent_id: Agent identifier (1-5)
        examples: Few-shot examples for this agent
        
    Returns:
        AgentWrapper configured as specialist
    """
    domain = get_domain_description(agent_id)
    instructions = get_specialist_prompt(agent_id, domain, examples)
    
    return AgentWrapper(
        name=f"specialist_{agent_id}",
        instructions=instructions
    )


def create_supervisor_agent() -> AgentWrapper:
    """
    Create supervisor/reviewer agent for quality control.
    
    Returns:
        AgentWrapper configured as supervisor
    """
    return AgentWrapper(
        name="supervisor",
        instructions=get_supervisor_prompt()
    )


def create_synthesizer_agent() -> AgentWrapper:
    """
    Create synthesizer agent for final analysis consolidation.
    
    Returns:
        AgentWrapper configured as synthesizer
    """
    return AgentWrapper(
        name="synthesizer",
        instructions=get_synthesizer_prompt()
    )
