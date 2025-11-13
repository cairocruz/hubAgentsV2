# 🏗️ ARQUITETURA VISUAL DO SISTEMA

Diagramas e visualizações da arquitetura completa.

---

## 🎯 VISÃO GERAL DO SISTEMA

```
┌───────────────────────────────────────────────────────────────┐
│                        USUÁRIO/CLIENTE                         │
│                    (Envia 5 respostas)                         │
└──────────────────────────┬────────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────────┐
│                      FASTAPI SERVER                            │
│                    (main.py - Port 8000)                       │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  POST /analyze                                           │ │
│  │  • Valida request (Pydantic)                            │ │
│  │  • Inicia logging                                        │ │
│  │  • Orquestra fluxo completo                             │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────┬────────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────────┐
│                  FASE 1: ANÁLISE PARALELA                      │
│                    (specialist_analysis.py)                    │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Agent 1  │  │ Agent 2  │  │ Agent 3  │  │ Agent 4  │     │
│  │ Tarefas  │  │   Tom    │  │  Redes   │  │Financeiro│     │
│  │Domésticas│  │Emocional │  │  Apoio   │  │          │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
│       │             │             │             │             │
│       │             │             │             │             │
│  ┌────▼─────────────▼─────────────▼─────────────▼─────┐     │
│  │             Agent 5 - Bem-estar Físico           │     │
│  └──────────────────────────────────────────────────────┘     │
│                                                                 │
│  Cada agente:                                                   │
│  • Recebe 1 resposta + Few-Shot examples                       │
│  • Analisa com base no seu domínio                            │
│  • Retorna SpecialistReport (JSON)                            │
└──────────────────────────┬────────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────────┐
│                FASE 2: LOOP DE REVISÃO                         │
│                     (review_loop.py)                           │
│                                                                 │
│  Para cada relatório:                                          │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  1. Supervisor analisa relatório                         │ │
│  │     ↓                                                     │ │
│  │  2. Decisão: APROVADO ou REVISAR?                       │ │
│  │     ↓                ↓                                    │ │
│  │  APROVADO         REVISAR                                │ │
│  │     ↓                ↓                                    │ │
│  │  Próximo        3. Feedback detalhado                    │ │
│  │  relatório         ↓                                     │ │
│  │                 4. Agente refaz análise                  │ │
│  │                    ↓                                     │ │
│  │                 5. Volta para supervisor                 │ │
│  │                    (máx 1 retrabalho)                    │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────┬────────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────────┐
│                  FASE 3: SÍNTESE FINAL                         │
│                     (synthesizer.py)                           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Agente Sintetizador                                     │ │
│  │  • Recebe todos os 5 relatórios aprovados               │ │
│  │  • Identifica conexões entre domínios                   │ │
│  │  • Calcula score final consolidado (0-100)              │ │
│  │  • Define risk_level (Baixo/Médio/Alto)                 │ │
│  │  • Consolida fatores de risco                           │ │
│  │  • Gera recomendações                                    │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────┬────────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────────┐
│                    RESPOSTA JSON FINAL                         │
│                                                                 │
│  {                                                              │
│    "final_score": 75.5,                                        │
│    "risk_level": "Alto",                                       │
│    "synthesis": "...",                                         │
│    "consolidated_factors": [...],                              │
│    "recommendations": [...],                                   │
│    "specialist_reports": [...]                                 │
│  }                                                              │
└──────────────────────────┬────────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────────┐
│                   LOGGING AUDITÁVEL                            │
│                   (logs/*.json)                                │
│                                                                 │
│  • Histórico completo da análise                              │
│  • Timestamp de cada etapa                                     │
│  • Tentativas de retrabalho                                   │
│  • Duração total                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## 📊 FLUXO DE DADOS

```
INPUT (5 Respostas)
    │
    ├─► Response 1 ──► Agent 1 (Tarefas)    ──┐
    ├─► Response 2 ──► Agent 2 (Emocional)  ──┤
    ├─► Response 3 ──► Agent 3 (Redes)      ──┼─► Few-Shot Examples
    ├─► Response 4 ──► Agent 4 (Financeiro) ──┤   (data/*.csv)
    └─► Response 5 ──► Agent 5 (Bem-estar)  ──┘
            │
            ▼
    [5 Specialist Reports]
            │
            ▼
    ┌───────────────┐
    │   Supervisor   │ ◄─── Revisa cada relatório
    │   Agent        │
    └───────┬───────┘
            │
            ├─► APROVADO ──► Coleta para síntese
            │
            └─► REVISAR ──┐
                          │
                    [Feedback]
                          │
                          ▼
                  ┌─────────────┐
                  │  Rework     │
                  │  Specialist │
                  └──────┬──────┘
                          │
                          └─► Volta para Supervisor
                                  │
                                  ▼
                            [Report Aprovado]
                                  │
                                  ▼
                         ┌────────────────┐
                         │ Synthesizer    │
                         │ Agent          │
                         └────────┬───────┘
                                  │
                                  ▼
                         [Final Analysis]
                                  │
                                  ▼
                            OUTPUT (JSON)
```

---

## 🧩 COMPONENTES E RESPONSABILIDADES

```
┌─────────────────────────────────────────────────────────────┐
│                        MAIN.PY                               │
│  Responsabilidade: Aplicação FastAPI e orquestração         │
│  • Define endpoints                                          │
│  • Gerencia lifecycle                                        │
│  • Coordena fluxo entre fases                               │
└─────────────────────────────────────────────────────────────┘
                         ▲
                         │ usa
                         │
    ┌────────────────────┴────────────────────┐
    │                                          │
    ▼                                          ▼
┌─────────────────────┐            ┌────────────────────┐
│   AGENTS MODULE     │            │   UTILS MODULE     │
│  agent_factory.py   │            │  data_loader.py    │
│  specialist_ana...  │            │  logger.py         │
│  review_loop.py     │            └────────────────────┘
│  synthesizer.py     │                     ▲
└─────────────────────┘                     │
         ▲                                  │
         │ usa                              │ usa
         │                                  │
    ┌────┴───────────┐               ┌─────┴─────┐
    ▼                ▼               ▼           ▼
┌──────────┐  ┌───────────┐  ┌──────────┐  ┌─────────┐
│ CONFIG   │  │ PROMPTS   │  │  DATA    │  │  LOGS   │
│llm_conf..│  │system_pr..│  │*.csv     │  │*.json   │
└──────────┘  └───────────┘  └──────────┘  └─────────┘
```

---

## 🔄 CICLO DE VIDA DE UMA REQUISIÇÃO

```
TEMPO (segundos)
│
├─ 0s:  Request recebido
│       └─► Logger.start_request_log()
│
├─ 1s:  Validação Pydantic
│       └─► AnalysisRequest.validate()
│
├─ 2s:  Início análise paralela
│       └─► run_specialist_analysis_sync()
│
├─ 3-15s: Agentes especialistas trabalhando
│       ├─► Agent 1 analisa Response 1
│       ├─► Agent 2 analisa Response 2
│       ├─► Agent 3 analisa Response 3
│       ├─► Agent 4 analisa Response 4
│       └─► Agent 5 analisa Response 5
│       
│       Cada agente:
│       1. Carrega Few-Shot examples
│       2. Executa LLM (Groq/Llama3)
│       3. Parse JSON response
│       4. Cria SpecialistReport
│
├─ 16s: 5 relatórios coletados
│       └─► Logger.log_event("specialist_analysis")
│
├─ 17s: Início loop de revisão
│       └─► run_review_loop() para cada relatório
│
├─ 18-35s: Supervisor revisando
│       Para cada relatório (5x):
│       1. Supervisor analisa (3-5s)
│       2. Decision: APROVADO/REVISAR
│       3. Se REVISAR:
│          ├─► Gera feedback
│          ├─► Agente refaz (5-8s)
│          └─► Supervisor re-analisa
│       4. Logger.log_event("reviewer_feedback")
│
├─ 36s: Todos relatórios aprovados
│       └─► 5 SpecialistReports prontos
│
├─ 37s: Início síntese
│       └─► run_synthesis()
│
├─ 38-50s: Sintetizador trabalhando
│       1. Analisa todos os 5 relatórios
│       2. Identifica padrões
│       3. Calcula score final
│       4. Define risk_level
│       5. Gera recomendações
│       6. Logger.log_event("final_synthesis")
│
├─ 51s: Resposta pronta
│       └─► FinalAnalysis criada
│
├─ 52s: Finaliza log
│       └─► Logger.finalize_log()
│
└─ 53s: Response enviado ao cliente
        └─► return FinalAnalysis.model_dump()
```

---

## 🗂️ ESTRUTURA DE ARQUIVOS DETALHADA

```
hubAgentsV2/
│
├── 📄 DOCUMENTAÇÃO
│   ├── README.md              # Documentação completa
│   ├── SETUP_GUIDE.md         # Guia de setup detalhado
│   ├── QUICKSTART.md          # Início rápido
│   ├── INDEX.md               # Índice completo
│   ├── ARCHITECTURE.md        # Este arquivo
│   └── RESUMO_EXPLICATIVO.md  # Conceitos de IA
│
├── 🔧 CONFIGURAÇÃO
│   ├── .env                   # Variáveis de ambiente (gitignored)
│   ├── .env.example           # Template de .env
│   ├── .gitignore             # Arquivos ignorados
│   └── requirements.txt       # Dependências Python
│
├── 🤖 AGENTES (agents/)
│   ├── __init__.py
│   ├── agent_factory.py       # Criação de agentes
│   ├── specialist_analysis.py # Análise paralela
│   ├── review_loop.py         # Revisão com supervisor
│   └── synthesizer.py         # Síntese final
│
├── ⚙️ CONFIGURAÇÃO (config/)
│   ├── __init__.py
│   └── llm_config.py          # Config Groq/Llama
│
├── 📊 DADOS (data/)
│   ├── dataset_1.csv          # 15 exemplos - Tarefas
│   ├── dataset_2.csv          # 15 exemplos - Emocional
│   ├── dataset_3.csv          # 15 exemplos - Redes
│   ├── dataset_4.csv          # 15 exemplos - Financeiro
│   └── dataset_5.csv          # 15 exemplos - Bem-estar
│
├── 📋 MODELOS (models/)
│   ├── __init__.py
│   └── schemas.py             # Schemas Pydantic
│
├── 💬 PROMPTS (prompts/)
│   ├── __init__.py
│   └── system_prompts.py      # Prompts especializados
│
├── 🔧 UTILITÁRIOS (utils/)
│   ├── __init__.py
│   ├── data_loader.py         # Carregador de datasets
│   └── logger.py              # Sistema de logging
│
├── 🧪 TESTES (tests/)
│   └── test_system.py         # Suite de testes
│
├── 📚 EXEMPLOS (examples/)
│   └── usage_examples.py      # Exemplos de uso
│
├── 📝 LOGS (logs/)
│   └── request_*.json         # Logs auditáveis
│
├── 🚀 SCRIPTS
│   ├── main.py                # Aplicação principal
│   ├── verify_setup.py        # Verificação de setup
│   ├── setup.bat              # Setup automático
│   ├── start_server.bat       # Iniciar servidor
│   ├── run_tests.bat          # Executar testes
│   └── run_examples.bat       # Executar exemplos
│
└── 🔌 AMBIENTE VIRTUAL
    └── venv/                  # Ambiente Python isolado
```

---

## 🎯 PADRÕES DE DESIGN UTILIZADOS

### 1. Factory Pattern
```python
# agent_factory.py
create_specialist_agent(agent_id, examples)
create_supervisor_agent()
create_synthesizer_agent()
```

### 2. Strategy Pattern
```python
# Cada agente tem estratégia específica via prompt
specialist_1 → Domínio: Tarefas Domésticas
specialist_2 → Domínio: Tom Emocional
specialist_3 → Domínio: Redes de Apoio
...
```

### 3. Observer Pattern
```python
# Logger observa e registra todos os eventos
logger.log_event("specialist_analysis", data)
logger.log_event("reviewer_feedback", data)
logger.log_event("final_synthesis", data)
```

### 4. Chain of Responsibility
```python
# Fluxo sequencial com possibilidade de retrabalho
Specialist → Supervisor → (Rework?) → Synthesizer
```

### 5. Singleton Pattern
```python
# Instâncias globais compartilhadas
data_loader = DataLoader()  # Uma instância
logger = Logger()            # Uma instância
```

---

## 🔐 FLUXO DE SEGURANÇA

```
┌────────────────────────────────────────────┐
│           REQUEST EXTERNO                   │
└──────────────┬─────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────┐
│        VALIDAÇÃO PYDANTIC                   │
│  • Tipo correto de dados                   │
│  • 5 respostas obrigatórias                │
│  • Formato JSON válido                     │
└──────────────┬─────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────┐
│         GROQ API (HTTPS)                    │
│  • API Key via header                      │
│  • TLS encryption                          │
│  • Rate limiting                           │
└──────────────┬─────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────┐
│      PROCESSAMENTO INTERNO                  │
│  • Sem armazenamento permanente            │
│  • Logs locais (proteger em prod)          │
└──────────────┬─────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────┐
│         RESPONSE SANITIZADO                 │
│  • Apenas JSON estruturado                 │
│  • Sem dados sensíveis extras              │
└────────────────────────────────────────────┘
```

---

## 📊 DIAGRAMA DE CLASSES SIMPLIFICADO

```
┌─────────────────────┐
│   FastAPI App       │
├─────────────────────┤
│ + analyze()         │
│ + health_check()    │
└──────┬──────────────┘
       │ usa
       │
┌──────▼──────────────┐
│   AgentFactory      │
├─────────────────────┤
│ + create_specialist │
│ + create_supervisor │
│ + create_synthesizer│
└──────┬──────────────┘
       │ cria
       │
┌──────▼──────────────┐
│  AssistantAgent     │ (AutoGen)
├─────────────────────┤
│ - system_message    │
│ - llm_config        │
│ + initiate_chat()   │
└─────────────────────┘

┌─────────────────────┐
│   DataLoader        │
├─────────────────────┤
│ + get_few_shot()    │
│ + get_dataset()     │
└─────────────────────┘

┌─────────────────────┐
│   Logger            │
├─────────────────────┤
│ + start_log()       │
│ + log_event()       │
│ + finalize_log()    │
└─────────────────────┘

┌─────────────────────┐
│  AnalysisRequest    │ (Pydantic)
├─────────────────────┤
│ - responses: List   │
└─────────────────────┘

┌─────────────────────┐
│  FinalAnalysis      │ (Pydantic)
├─────────────────────┤
│ - final_score       │
│ - risk_level        │
│ - synthesis         │
│ - factors           │
└─────────────────────┘
```

---

## 🌐 DIAGRAMA DE REDE

```
┌─────────────┐
│   Cliente   │
│  (Browser,  │
│   Python)   │
└──────┬──────┘
       │ HTTP/JSON
       │
       ▼
┌──────────────────────┐
│  FastAPI Server      │
│  localhost:8000      │
│                      │
│  Endpoints:          │
│  • GET /             │
│  • GET /health       │
│  • POST /analyze     │
└──────┬───────────────┘
       │ API Call
       │
       ▼
┌──────────────────────┐
│   Groq API           │
│   (External)         │
│                      │
│  • Llama3-8b-8192    │
│  • Temperature: 0.2  │
│  • JSON mode         │
└──────────────────────┘
```

---

## 💾 PERSISTÊNCIA DE DADOS

```
RUNTIME (Memória)
│
├─► data_loader (carregado no startup)
│   └─► 5 DataFrames em memória
│
├─► logger (instância global)
│   └─► RequestLog temporário
│
└─► Análises (processadas e descartadas)

STORAGE (Disco)
│
├─► data/*.csv (datasets estáticos)
│   └─► Lidos no startup
│
└─► logs/*.json (logs auditáveis)
    └─► Escritos após cada request
```

---

## ⚡ OTIMIZAÇÕES IMPLEMENTADAS

### 1. Análise Paralela
```python
# 5 agentes executam simultaneamente
tasks = [analyze_single(i, r) for i, r in enumerate(responses)]
reports = await asyncio.gather(*tasks)
```

### 2. Few-Shot Caching
```python
# DataLoader carrega CSVs uma vez no startup
self.datasets = {}  # Mantido em memória
```

### 3. JSON Mode Enforcement
```python
# Força LLM a retornar JSON válido
config["response_format"] = {"type": "json_object"}
```

### 4. Temperature Baixa
```python
# Reduz variabilidade, aumenta consistência
temperature = 0.2
```

---

**Este documento descreve a arquitetura completa do sistema.**  
**Para implementação, consulte os arquivos fonte.**  
**Para uso, consulte QUICKSTART.md ou README.md**
