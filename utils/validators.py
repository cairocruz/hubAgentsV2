"""
Validation utilities for API configuration.
"""
import os
from groq import Groq


def validate_groq_api_key() -> tuple[bool, str]:
    """
    Validate Groq API key.
    
    Returns:
        Tuple of (is_valid, message)
    """
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        return False, "GROQ_API_KEY not found in environment variables"
    
    if not api_key.startswith("gsk_"):
        return False, "Invalid API key format (should start with 'gsk_')"
    
    try:
        # Test the API key with a minimal request
        client = Groq(api_key=api_key)
        client.chat.completions.create(
            messages=[{"role": "user", "content": "test"}],
            model="llama3-8b-8192",
            max_tokens=10
        )
        return True, "API key is valid"
    except Exception as e:
        return False, f"API key validation failed: {str(e)}"


if __name__ == "__main__":
    is_valid, message = validate_groq_api_key()
    print(f"{'✅' if is_valid else '❌'} {message}")
