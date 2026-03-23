"""
main.py — Ponto de entrada da aplicação FastAPI.

Este arquivo define o servidor HTTP que expõe a API REST do Sistema de Análise
de Risco com IA Multiagente. Ele cria a aplicação FastAPI, configura o CORS,
registra os endpoints e, ao ser executado diretamente, inicia o servidor
Uvicorn na porta 8000.

Endpoints disponíveis:
  GET  /         → Informações gerais da API
  GET  /health   → Health check (status do sistema e do Supabase)
  POST /analyze  → Recebe 5 respostas da usuária e devolve a análise de risco
  GET  /docs     → Documentação interativa Swagger UI
  GET  /redoc    → Documentação alternativa ReDoc
"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
from fastapi import FastAPI, HTTPException       # Framework web assíncrono
from fastapi.middleware.cors import CORSMiddleware  # Middleware de Cross-Origin
from contextlib import asynccontextmanager       # Gerenciador de ciclo de vida
import time                                      # Para medir duração da análise
from typing import Dict, List, Any               # Type hints

from models.schemas import AnalysisRequest       # Schema Pydantic da requisição
from utils.supabase_client import SupabaseDB     # Wrapper do banco Supabase
from agents.risk_analysis_crew import RiskAnalysisCrew  # Orquestrador multiagente

# ---------------------------------------------------------------------------
# Variável global do banco de dados
# ---------------------------------------------------------------------------
# Instância global do SupabaseDB, inicializada no lifespan (startup).
# Fica disponível para qualquer endpoint registrar logs de erro etc.
db = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de ciclo de vida do FastAPI (substitui on_event("startup")).

    No startup:
      - Cria a instância global do SupabaseDB e verifica se a conexão
        com o Supabase está funcional (variáveis SUPABASE_URL e SUPABASE_KEY
        definidas no .env).

    No shutdown:
      - Apenas exibe uma mensagem informativa de encerramento.
    """
    global db

    # ---- Startup ----
    db = SupabaseDB()
    if db.client:
        print("✅ DB Supabase inicializado")
    else:
        print("⚠️ Supabase NÃO Mapeado! Verifique o .env")

    yield  # A aplicação roda enquanto o yield está ativo

    # ---- Shutdown ----
    print("🔄 Shutting down...")

# ---------------------------------------------------------------------------
# Criação da aplicação FastAPI
# ---------------------------------------------------------------------------
# O objeto `app` é a aplicação principal. Todos os metadados abaixo aparecem
# automaticamente na documentação Swagger (/docs) e ReDoc (/redoc).
app = FastAPI(
    title="Sistema de Análise de Risco com IA Multiagente",
    description="""
    ## 🤖 Sistema Avançado de Análise de Risco
    
    Sistema multiagente para análise de risco de violência doméstica usando **CrewAI**.
    
    ### ✨ Recursos Principais:
    
    - **5 Agentes Especialistas:** Analisam diferentes dimensões do risco
        - 🧠 Rotina, Sobrecarga e Divisão de Tarefas Domésticas
        - 👤 Tom Emocional, Comunicação e Intimidação
        - ⚠️ Redes de Apoio, Isolamento Social e Vínculos
        - ⚖️ Controle Financeiro e Dependência Econômica
        - 🏠 Bem-estar Físico, Psicológico e Saúde Mental
    
    - **Supervisor de Qualidade:** Revisa e aprova todas as análises
    - **Sintetizador:** Consolida todas as avaliações em um relatório final
    
    ### 🔄 Fluxo de Análise:
    
    1. **Fase 1:** Análise por 5 especialistas
    2. **Fase 2:** Revisão e aprovação pelo supervisor (com loop de retrabalho)
    3. **Fase 3:** Síntese final com score unificado
    
    ### 🎯 Modelos Suportados:
    
    - Gemini (gemini-1.5-flash — padrão)
    - OpenAI (GPT-4, GPT-4o-mini)
    - Groq (Llama3, Mixtral)
    
    ### 📊 Formato de Saída:
    
    - Score de risco: 0-100
    - Nível de risco: BAIXO, MODERADO, ALTO, CRÍTICO
    - Análises detalhadas por especialista
    - Recomendações de ação
    """,
    version="2.0.0",
    contact={
        "name": "Equipe de Desenvolvimento",
        "email": "suporte@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,       # Função de ciclo de vida (startup/shutdown)
    docs_url="/docs",        # Swagger UI
    redoc_url="/redoc",      # ReDoc
    openapi_url="/openapi.json",  # Schema OpenAPI em JSON
)

# ---------------------------------------------------------------------------
# Middleware CORS
# ---------------------------------------------------------------------------
# Permite que qualquer origem (front-end) faça requisições à API.
# Em produção, substitua allow_origins=["*"] pelos domínios reais.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Origens permitidas (todas, por enquanto)
    allow_credentials=True,    # Permite envio de cookies/credenciais
    allow_methods=["*"],       # Métodos HTTP permitidos (GET, POST, etc.)
    allow_headers=["*"],       # Headers permitidos
)


# ---------------------------------------------------------------------------
# Endpoint: GET /
# ---------------------------------------------------------------------------
@app.get("/", tags=["Sistema"])
async def root():
    """
    Endpoint raiz — retorna informações básicas sobre a API.

    Útil para:
      - Verificar se o servidor está online.
      - Obter a lista de endpoints disponíveis.
    """
    return {
        "message": "Sistema de Análise de Risco com IA Multiagente",
        "version": "2.0.0",
        "framework": "CrewAI",
        "endpoints": {
            "GET /": "Informações da API",
            "GET /health": "Verifica status do sistema",
            "POST /analyze": "Analisa respostas e retorna avaliação de risco",
            "GET /docs": "Documentação Swagger UI",
            "GET /redoc": "Documentação ReDoc"
        },
        "status": "online"
    }


# ---------------------------------------------------------------------------
# Endpoint: GET /health
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Sistema"])
async def health_check():
    """
    Health check — verifica se o servidor e o Supabase estão operacionais.

    Retorna:
      - status geral do servidor ("healthy")
      - estado da conexão com o Supabase ("connected" / "disconnected")
      - contagem de agentes configurados (5 especialistas + 1 supervisor + 1 sintetizador)
    """
    return {
        "status": "healthy",
        "supabase": "connected" if db and db.client else "disconnected",
        "framework": "CrewAI",
        "agents": {
            "specialists": 5,    # Agentes que analisam cada dimensão de risco
            "supervisor": 1,     # Agente que revisa as análises
            "synthesizer": 1     # Agente que consolida o relatório final
        }
    }


# ---------------------------------------------------------------------------
# Endpoint: POST /analyze
# ---------------------------------------------------------------------------
@app.post("/analyze", response_model=Dict, tags=["Análise de Risco"])
async def analyze_responses(request: AnalysisRequest):
    """
    Rota principal de análise de risco de violência doméstica.

    Recebe exatamente 5 respostas textuais da usuária (uma por dimensão)
    e orquestra o fluxo multiagente em 3 fases:

      Fase 1 — 5 especialistas analisam cada resposta usando RAG (busca de
               casos similares no Supabase via pgvector).
      Fase 2 — Um Supervisor revisa as análises; se reprovar alguma, o
               especialista correspondente refaz (loop de até 2 iterações).
      Fase 3 — Um Sintetizador consolida tudo em um relatório final com
               score de risco (0-100), nível (BAIXO/MODERADO/ALTO/CRÍTICO),
               fatores de risco e recomendações.

    Args:
        request: AnalysisRequest com campo `responses` (lista de 5 strings).

    Returns:
        Dict com risk_score, risk_level, consolidated_factors, recommendations
        e metadados (_meta com duração e analysis_id).

    Raises:
        HTTPException 500 se ocorrer qualquer erro durante a análise.
    """
    start_time = time.time()  # Marca o início para calcular a duração

    try:
        print(f"\n{'='*60}")
        print("🤖 INICIANDO ANÁLISE MULTI-AGENTE (CrewAI – 3 Fases)")
        print(f"{'='*60}\n")

        # Extrai a lista de respostas do body da requisição
        responses_list: List[str] = request.model_dump()["responses"]

        # Cria o orquestrador e dispara o fluxo completo (Fase 1 → 2 → 3)
        crew = RiskAnalysisCrew(responses=responses_list)
        final_assessment = crew.kickoff()

        # Adiciona metadados de desempenho ao resultado
        duration = time.time() - start_time
        final_assessment["_meta"] = {
            "duration_seconds": round(duration, 2),   # Tempo total da análise
            "max_rework_iterations": 2,               # Limite de retrabalho configurado
        }

        print(f"\n⏱️  Tempo total: {duration:.2f}s\n")
        return final_assessment

    except Exception as e:
        # Em caso de erro, loga no Supabase (se disponível) e retorna 500
        print(f"\n❌ ERRO: {str(e)}\n")

        if db:
            db.log_analysis(
                agent_role="Sistema",
                quest="Erro Fatal",
                user_response="N/A",
                analysis_result=str(e),
                metadata={"type": "error"},
            )

        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Execução direta: inicia o servidor Uvicorn
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    import os

    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║   Sistema de Análise de Risco com IA Multiagente            ║
    ║   Iniciando servidor...                                       ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)

    # Cloud Run define a variável de ambiente PORT (ex.: 8080).
    # Localmente, se PORT não estiver definida, usamos 8000 como padrão.
    port = int(os.getenv("PORT", "8000"))

    uvicorn.run(
        app,
        host="0.0.0.0",  # Escuta em todas as interfaces de rede
        port=port,         # Porta vinda da variável de ambiente ou 8000
        log_level="info"  # Nível de log do Uvicorn
    )
