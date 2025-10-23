"""
Agent factory for creating agents using Microsoft Agent Framework.
Maintains same public interface as original AutoGen implementation.
"""
import json
from typing import Optional
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
    
    async def run(self, task: str, json_mode: bool = True) -> str:
        """
        Execute agent task and return response.
        
        Args:
            task: Task description/prompt for the agent
            json_mode: Whether to enforce JSON response format
            
        Returns:
            str: Agent's response (JSON string if json_mode=True)
        """
        messages = [
            {"role": "system", "content": self.instructions},
            {"role": "user", "content": task}
        ]
        
        try:
            # Handle different provider APIs
            if self.provider == "azure_openai":
                # Agent Framework with Azure OpenAI
                agent = self.client.create_agent(
                    name=self.name,
                    instructions=self.instructions,
                )
                response = await agent.run(task)
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
