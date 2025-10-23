"""Initialize prompts package."""
from .system_prompts import (
    get_specialist_prompt,
    get_supervisor_prompt,
    get_synthesizer_prompt,
    get_domain_description,
    DOMAIN_DESCRIPTIONS
)

__all__ = [
    'get_specialist_prompt',
    'get_supervisor_prompt',
    'get_synthesizer_prompt',
    'get_domain_description',
    'DOMAIN_DESCRIPTIONS'
]
