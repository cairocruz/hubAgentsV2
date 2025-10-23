"""
Main FastAPI application for Multi-Agent Risk Analysis System.
Uses Microsoft Agent Framework.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
from typing import Dict

from models.schemas import AnalysisRequest, FinalAnalysis
from utils.data_loader import DataLoader
from utils.logger import Logger
from agents.specialist_analysis import run_specialist_analysis
from agents.review_loop import run_review_loop
from agents.synthesizer import run_synthesis


# Global instances
data_loader = None
logger = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup."""
    global data_loader, logger
    
    # Initialize data loader
    data_loader = DataLoader(data_dir="data")
    print("✅ DataLoader initialized")
    
    # Initialize logger
    logger = Logger(log_dir="logs")
    print("✅ Logger initialized")
    
    yield
    
    # Cleanup (if needed)
    print("🔄 Shutting down...")


# Create FastAPI app with complete metadata
app = FastAPI(
    title="Sistema de Análise de Risco com IA Multiagente",
    description="""
    ## 🤖 Sistema Avançado de Análise de Risco
    
    Sistema multiagente para análise de risco de violência doméstica usando **Microsoft Agent Framework**.
    
    ### ✨ Recursos Principais:
    
    - **5 Agentes Especialistas:** Analisam diferentes dimensões do risco
        - 🧠 Especialista Emocional
        - 👤 Especialista Comportamental  
        - ⚠️ Especialista em Agressão
        - ⚖️ Especialista Legal
        - 🏠 Especialista Ambiental
    
    - **Supervisor de Qualidade:** Revisa e aprova todas as análises
    - **Sintetizador:** Consolida todas as avaliações em um relatório final
    
    ### 🔄 Fluxo de Análise:
    
    1. **Fase 1:** Análise paralela por 5 especialistas
    2. **Fase 2:** Revisão e aprovação pelo supervisor
    3. **Fase 3:** Síntese final com score unificado
    
    ### 🎯 Modelos Suportados:
    
    - Azure OpenAI (GPT-4, GPT-4o-mini)
    - OpenAI (GPT-4, GPT-3.5-turbo)
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
    lifespan=lifespan,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json",  # OpenAPI schema
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Sistema"])
async def root():
    """
    ## 🏠 Endpoint Raiz
    
    Retorna informações básicas sobre a API e endpoints disponíveis.
    
    ### Resposta:
    - Mensagem de boas-vindas
    - Versão da API
    - Lista de endpoints disponíveis
    """
    return {
        "message": "Sistema de Análise de Risco com IA Multiagente",
        "version": "2.0.0",
        "framework": "Microsoft Agent Framework",
        "endpoints": {
            "GET /": "Informações da API",
            "GET /health": "Verifica status do sistema",
            "POST /analyze": "Analisa respostas e retorna avaliação de risco",
            "GET /docs": "Documentação Swagger UI",
            "GET /redoc": "Documentação ReDoc"
        },
        "status": "online"
    }


@app.get("/health", tags=["Sistema"])
async def health_check():
    """
    ## 💚 Health Check
    
    Verifica o estado de saúde do sistema e componentes.
    
    ### Verificações:
    - Status do servidor
    - DataLoader (dados few-shot)
    - Logger (sistema de logs)
    
    ### Resposta:
    ```json
    {
        "status": "healthy",
        "data_loader": "initialized",
        "logger": "initialized"
    }
    ```
    """
    return {
        "status": "healthy",
        "data_loader": "initialized" if data_loader else "not initialized",
        "logger": "initialized" if logger else "not initialized",
        "framework": "Microsoft Agent Framework",
        "agents": {
            "specialists": 5,
            "supervisor": 1,
            "synthesizer": 1
        }
    }


@app.post("/analyze", response_model=Dict, tags=["Análise de Risco"])
async def analyze_responses(request: AnalysisRequest):
    """
    ## 🎯 Análise Completa de Risco
    
    Executa análise multiagente completa sobre as respostas fornecidas.
    
    ### 📋 Processo de Análise (3 Fases):
    
    #### Fase 1: Análise Paralela (5 Especialistas)
    Cada especialista analisa as respostas de forma independente:
    - **Especialista Emocional:** Avalia estado emocional e dependência
    - **Especialista Comportamental:** Analisa padrões comportamentais
    - **Especialista em Agressão:** Identifica sinais de violência
    - **Especialista Legal:** Avalia histórico legal e medidas protetivas
    - **Especialista Ambiental:** Analisa contexto social e suporte
    
    #### Fase 2: Revisão pelo Supervisor
    - Supervisor revisa cada análise individual
    - Pode solicitar retrabalho se análise não for satisfatória
    - Máximo de 1 tentativa de retrabalho por especialista
    
    #### Fase 3: Síntese Final
    - Consolida todas as análises aprovadas
    - Calcula score unificado (0-100)
    - Define nível de risco (BAIXO/MODERADO/ALTO/CRÍTICO)
    - Gera recomendações de ação
    
    ### 📥 Entrada Esperada:
    ```json
    {
        "responses": [
            {"question": "Pergunta 1", "answer": "Resposta da usuária"},
            {"question": "Pergunta 2", "answer": "Resposta da usuária"},
            {"question": "Pergunta 3", "answer": "Resposta da usuária"},
            {"question": "Pergunta 4", "answer": "Resposta da usuária"},
            {"question": "Pergunta 5", "answer": "Resposta da usuária"}
        ]
    }
    ```
    
    ### 📤 Saída:
    ```json
    {
        "risk_score": 75.5,
        "risk_level": "ALTO",
        "specialist_analyses": [...],
        "consolidated_factors": {...},
        "recommendations": [...]
    }
    ```
    
    ### ⚠️ Observações:
    - Tempo médio: 30-60 segundos
    - Requer API key válida (Groq/OpenAI/Azure)
    - Todas as respostas são processadas em paralelo
    
    ### 🔒 Privacidade:
    - Dados não são armazenados permanentemente
    - Logs são salvos apenas para auditoria
    """
    start_time = time.time()
    
    try:
        # Start logging
        request_id = logger.start_request_log(request.model_dump())
        logger.log_event(
            event_type="request_received",
            data={"num_responses": len(request.responses)}
        )
        
        # Phase 1: Parallel Specialist Analysis
        print(f"\n{'='*60}")
        print("🔬 FASE 1: ANÁLISE PARALELA DOS ESPECIALISTAS")
        print(f"{'='*60}\n")
        
        specialist_reports = await run_specialist_analysis(
            request.responses,
            data_loader
        )
        
        for idx, report in enumerate(specialist_reports, 1):
            logger.log_event(
                event_type="specialist_analysis",
                agent_id=report.agent_id,
                attempt=1,
                data=report.model_dump()
            )
            print(f"✅ Agente {idx} ({report.domain}): Score {report.preliminary_score:.1f}")
        
        # Phase 2: Review Loop with Supervisor
        print(f"\n{'='*60}")
        print("👨‍💼 FASE 2: LOOP DE REVISÃO COM SUPERVISOR")
        print(f"{'='*60}\n")
        
        approved_reports = []
        
        for idx, report in enumerate(specialist_reports):
            print(f"Revisando Agente {report.agent_id}...")
            
            final_report, feedback_history = await run_review_loop(
                report=report,
                data_loader=data_loader,
                user_response=request.responses[idx],
                max_rework=1
            )
            
            # Log feedback
            for attempt_num, feedback in enumerate(feedback_history, 1):
                logger.log_event(
                    event_type="reviewer_feedback",
                    agent_id=feedback.agent_id,
                    attempt=attempt_num,
                    data=feedback.model_dump()
                )
                
                if feedback.status == "APROVADO":
                    print(f"  ✅ APROVADO (Tentativa {attempt_num})")
                else:
                    print(f"  🔄 REVISAR (Tentativa {attempt_num})")
            
            approved_reports.append(final_report)
        
        # Phase 3: Final Synthesis
        print(f"\n{'='*60}")
        print("🎯 FASE 3: SÍNTESE FINAL")
        print(f"{'='*60}\n")
        
        final_analysis = await run_synthesis(approved_reports)
        
        logger.log_event(
            event_type="final_synthesis",
            data=final_analysis.model_dump()
        )
        
        print(f"📊 Score Final: {final_analysis.final_score:.1f}")
        print(f"⚠️  Nível de Risco: {final_analysis.risk_level}")
        print(f"🔍 Fatores Identificados: {len(final_analysis.consolidated_factors)}")
        
        # Finalize log
        duration = time.time() - start_time
        logger.finalize_log(
            response=final_analysis.model_dump(),
            duration=duration
        )
        
        print(f"\n⏱️  Tempo total: {duration:.2f}s")
        print(f"📝 Log salvo: {request_id}\n")
        
        return final_analysis.model_dump()
        
    except Exception as e:
        # Log error
        if logger.current_log:
            logger.log_event(
                event_type="error",
                data={"error": str(e), "type": type(e).__name__}
            )
            logger.finalize_log()
        
        print(f"\n❌ ERRO: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║   Sistema de Análise de Risco com IA Multiagente            ║
    ║   Iniciando servidor...                                       ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
