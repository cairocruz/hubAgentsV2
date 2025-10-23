"""Testa quais modelos estão disponíveis na Groq."""
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Modelos para testar
models = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile", 
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768"
]

print("🔍 Testando modelos disponíveis...\n")

for model in models:
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Oi"}],
            model=model,
            max_tokens=10
        )
        print(f"✅ {model} - FUNCIONANDO")
    except Exception as e:
        print(f"❌ {model} - ERRO: {str(e)[:100]}")

print("\n✨ Teste concluído!")
