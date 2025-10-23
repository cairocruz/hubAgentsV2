"""
Example script showing how to use the system programmatically.
"""
import requests
import json


def example_basic_usage():
    """Basic usage example."""
    print("="*60)
    print("EXEMPLO 1: Uso Básico")
    print("="*60 + "\n")
    
    # API endpoint
    url = "http://localhost:8000/analyze"
    
    # Example responses (5 required)
    request_data = {
        "responses": [
            "Eu cuido de tudo em casa: limpo, cozinho, cuido das crianças. Ele só chega e descansa.",
            "Quando eu falo algo que ele não gosta, ele grita comigo e me faz sentir pequena.",
            "Não vejo mais minhas amigas. Ele sempre diz que elas são má influência.",
            "Ele controla todo o dinheiro. Tenho que pedir até para comprar comida.",
            "Tenho dormido mal e me sinto ansiosa o tempo todo."
        ]
    }
    
    print("Enviando requisição para API...")
    print(f"URL: {url}")
    print(f"Respostas: {len(request_data['responses'])}\n")
    
    try:
        response = requests.post(url, json=request_data, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Análise concluída com sucesso!\n")
            print(f"📊 Score Final: {result['final_score']:.1f}/100")
            print(f"⚠️  Nível de Risco: {result['risk_level']}")
            print(f"\n📝 Síntese:")
            print(result['synthesis'][:200] + "..." if len(result['synthesis']) > 200 else result['synthesis'])
            
            print(f"\n🔍 Fatores de Risco Identificados ({len(result['consolidated_factors'])}):")
            for factor in result['consolidated_factors'][:5]:  # Show first 5
                print(f"   • {factor['factor']} ({factor['severity']})")
            
            print(f"\n💡 Recomendações:")
            for rec in result['recommendations']:
                print(f"   • {rec}")
            
        else:
            print(f"❌ Erro: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar à API")
        print("   Certifique-se de que o servidor está rodando (python main.py)")
    except Exception as e:
        print(f"❌ Erro: {e}")


def example_low_risk():
    """Example with low risk scenario."""
    print("\n" + "="*60)
    print("EXEMPLO 2: Cenário de Baixo Risco")
    print("="*60 + "\n")
    
    url = "http://localhost:8000/analyze"
    
    request_data = {
        "responses": [
            "A gente divide as tarefas de casa de forma equilibrada.",
            "Conversamos sobre tudo e nos respeitamos.",
            "Tenho total liberdade para ver meus amigos e família.",
            "Cada um tem sua conta e dividimos as despesas.",
            "Me sinto bem e cuido da minha saúde."
        ]
    }
    
    try:
        response = requests.post(url, json=request_data, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Score: {result['final_score']:.1f} - Risco: {result['risk_level']}")
        else:
            print(f"❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")


def example_health_check():
    """Example health check."""
    print("\n" + "="*60)
    print("EXEMPLO 3: Health Check")
    print("="*60 + "\n")
    
    url = "http://localhost:8000/health"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Sistema operacional")
            print(f"   Status: {result['status']}")
            print(f"   DataLoader: {result['data_loader']}")
            print(f"   Logger: {result['logger']}")
        else:
            print(f"❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")


def main():
    """Run all examples."""
    print("""
╔═══════════════════════════════════════════════════════════╗
║     Sistema de Análise de Risco - Exemplos de Uso       ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Health check first
    example_health_check()
    
    # Wait for user
    input("\nPressione ENTER para executar EXEMPLO 1 (Alto Risco)...")
    example_basic_usage()
    
    input("\nPressione ENTER para executar EXEMPLO 2 (Baixo Risco)...")
    example_low_risk()
    
    print("\n" + "="*60)
    print("Exemplos concluídos!")
    print("="*60)


if __name__ == "__main__":
    main()
