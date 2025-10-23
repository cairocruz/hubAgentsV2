"""
Script to verify project structure and dependencies.
"""
import os
import sys
from pathlib import Path


def check_structure():
    """Verify project structure."""
    print("="*60)
    print("VERIFICAÇÃO DE ESTRUTURA DO PROJETO")
    print("="*60 + "\n")
    
    base_dir = Path(__file__).parent
    
    required_dirs = [
        "agents",
        "config",
        "data",
        "examples",
        "models",
        "prompts",
        "tests",
        "utils"
    ]
    
    required_files = [
        "main.py",
        "requirements.txt",
        ".env.example",
        ".gitignore",
        "README.md",
        "SETUP_GUIDE.md",
        "QUICKSTART.md"
    ]
    
    # Check directories
    print("📁 Verificando diretórios:")
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            print(f"  ✅ {dir_name}/")
        else:
            print(f"  ❌ {dir_name}/ - FALTANDO")
    
    print()
    
    # Check files
    print("📄 Verificando arquivos:")
    for file_name in required_files:
        file_path = base_dir / file_name
        if file_path.exists():
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name} - FALTANDO")
    
    print()
    
    # Check datasets
    print("📊 Verificando datasets:")
    for i in range(1, 6):
        dataset_path = base_dir / "data" / f"dataset_{i}.csv"
        if dataset_path.exists():
            # Count lines
            with open(dataset_path, 'r', encoding='utf-8') as f:
                lines = len(f.readlines()) - 1  # Exclude header
            print(f"  ✅ dataset_{i}.csv ({lines} exemplos)")
        else:
            print(f"  ❌ dataset_{i}.csv - FALTANDO")
    
    print()


def check_dependencies():
    """Check if dependencies are installed."""
    print("="*60)
    print("VERIFICAÇÃO DE DEPENDÊNCIAS")
    print("="*60 + "\n")
    
    dependencies = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "pydantic": "Pydantic",
        "pandas": "Pandas",
        "autogen": "AutoGen",
        "groq": "Groq",
        "dotenv": "Python-dotenv"
    }
    
    for module_name, display_name in dependencies.items():
        try:
            __import__(module_name)
            print(f"  ✅ {display_name}")
        except ImportError:
            print(f"  ❌ {display_name} - NÃO INSTALADO")
    
    print()


def check_env():
    """Check environment configuration."""
    print("="*60)
    print("VERIFICAÇÃO DE CONFIGURAÇÃO")
    print("="*60 + "\n")
    
    base_dir = Path(__file__).parent
    env_path = base_dir / ".env"
    
    if env_path.exists():
        print("  ✅ Arquivo .env existe")
        
        # Check if API key is set
        with open(env_path, 'r') as f:
            content = f.read()
            if "your_groq_api_key_here" in content or "GROQ_API_KEY=" not in content:
                print("  ⚠️  GROQ_API_KEY ainda não configurada")
                print("     Configure sua chave no arquivo .env")
            else:
                print("  ✅ GROQ_API_KEY configurada")
    else:
        print("  ❌ Arquivo .env não existe")
        print("     Execute: copy .env.example .env")
    
    print()


def check_python_version():
    """Check Python version."""
    print("="*60)
    print("VERIFICAÇÃO DE VERSÃO DO PYTHON")
    print("="*60 + "\n")
    
    version = sys.version_info
    print(f"  Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 9:
        print("  ✅ Versão compatível (3.9+)")
    else:
        print("  ⚠️  Versão recomendada: Python 3.9+")
    
    print()


def summary():
    """Print summary and next steps."""
    print("="*60)
    print("PRÓXIMOS PASSOS")
    print("="*60 + "\n")
    
    base_dir = Path(__file__).parent
    env_path = base_dir / ".env"
    
    if not env_path.exists():
        print("1. Configure o ambiente:")
        print("   copy .env.example .env")
        print("   notepad .env  # Adicione sua GROQ_API_KEY")
        print()
    
    try:
        import fastapi
        print("2. Execute os testes:")
        print("   python tests/test_system.py")
        print()
        print("3. Inicie o servidor:")
        print("   python main.py")
        print()
        print("4. Acesse a API:")
        print("   http://localhost:8000")
        print()
    except ImportError:
        print("1. Instale as dependências:")
        print("   pip install -r requirements.txt")
        print()
    
    print("Para ajuda detalhada, veja:")
    print("  • QUICKSTART.md - Início rápido (5 min)")
    print("  • SETUP_GUIDE.md - Guia completo")
    print("  • README.md - Documentação completa")
    print()


def main():
    """Run all checks."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     Sistema de Análise de Risco - Verificação Completa      ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    check_python_version()
    check_structure()
    check_dependencies()
    check_env()
    summary()
    
    print("="*60)
    print("Verificação concluída!")
    print("="*60)


if __name__ == "__main__":
    main()
