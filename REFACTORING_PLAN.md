# 📋 PLANO DE REFATORAÇÃO: AutoGen → Microsoft Agent Framework

## 🎯 Objetivo
Migrar o sistema de **AutoGen (descontinuado)** para **Microsoft Agent Framework** (oficial e atual) sem perder funcionalidades.

---

## 📊 Análise de Impacto

### ✅ O QUE PERMANECE INALTERADO (Zero Refatoração)
- ✅ **Arquitetura Multiagente** - Conceito permanece idêntico
- ✅ **Few-Shot Learning** - Datasets CSV e DataLoader
- ✅ **Pydantic Models** - Schemas de validação
- ✅ **FastAPI** - API REST e endpoints
- ✅ **System Prompts** - Lógica de prompts (ajustes menores)
- ✅ **Logger/Audit Trail** - Sistema de logs
- ✅ **Fluxo de 3 Fases** - Análise → Revisão → Síntese
- ✅ **Execução Paralela** - AsyncIO continua funcionando

### 🔄 O QUE PRECISA MIGRAR (Refatoração Necessária)
- 🔄 **Criação de Agentes** - API completamente diferente
- 🔄 **Comunicação entre Agentes** - Método de invocação mudou
- 🔄 **Configuração LLM** - Novo formato de cliente
- 🔄 **Dependencies** - Pacotes Python

---

## 🗺️ Mapeamento de Conceitos: AutoGen → Agent Framework

| **AutoGen 0.2.x** | **Agent Framework** | **Status** |
|-------------------|---------------------|------------|
| `AssistantAgent` | `AIAgent` (via create_agent) | ✅ Equivalente direto |
| `UserProxyAgent` | Não necessário (workflow direto) | ⚠️ Simplifica |
| `initiate_chat()` | `agent.run()` | ✅ Equivalente |
| `llm_config` dict | Chat client (OpenAI/Azure) | 🔄 Diferente |
| `system_message` | `instructions` parameter | ✅ Equivalente |
| JSON mode via config | JSON mode via response_format | ✅ Equivalente |

---

## 📝 PLANO DE EXECUÇÃO (15 Passos)

### **FASE 1: Preparação do Ambiente** 

#### ✅ **Passo 1: Atualizar Requirements**
**Arquivo**: `requirements.txt`
**Mudanças**:
```diff
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0

- # AI and AutoGen (REMOVER)
- pyautogen==0.2.38
- openai==1.12.0

+ # Microsoft Agent Framework (ADICIONAR)
+ agent-framework[all]  # Inclui todos os providers
+ # OU específico:
+ # agent-framework
+ # agent-framework-azure
+ # agent-framework-openai

# Data Processing
pandas==2.1.3

# Utilities
python-multipart==0.0.6
aiofiles==23.2.1
```

**Impacto**: Baixo - Apenas dependências
**Risco**: Baixo - Instalação limpa

---

#### ✅ **Passo 2: Criar .env.example Atualizado**
**Arquivo**: `.env.example`
**Mudanças**:
```ini
# ===== MICROSOFT AGENT FRAMEWORK CONFIG =====

# Opção 1: Azure OpenAI (Recomendado)
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-02-01

# Opção 2: OpenAI direto
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# Opção 3: Groq (se suportado via extensão)
GROQ_API_KEY=your-groq-key-here
GROQ_MODEL=llama3-8b-8192

# ===== CONFIGURAÇÕES GERAIS =====
LLM_TEMPERATURE=0.2
LOG_LEVEL=INFO
```

**Impacto**: Baixo - Documentação
**Risco**: Zero

---

### **FASE 2: Refatorar Camada de Configuração**

#### 🔄 **Passo 3: Reescrever config/llm_config.py**
**Arquivo**: `config/llm_config.py`

**ANTES (AutoGen)**:
```python
def get_llm_config() -> dict:
    config = {
        "config_list": [
            {
                "model": model,
                "api_key": groq_api_key,
                "base_url": "https://api.groq.com/openai/v1",
                "api_type": "openai",
            }
        ],
        "temperature": temperature,
    }
    return config
```

**DEPOIS (Agent Framework)**:
```python
from agent_framework.azure import AzureOpenAIResponsesClient
from agent_framework.openai import OpenAIResponsesClient
from azure.identity import DefaultAzureCredential

def get_chat_client():
    """Retorna cliente configurado para Agent Framework."""
    
    # Opção 1: Azure OpenAI
    if os.getenv("AZURE_OPENAI_ENDPOINT"):
        return AzureOpenAIResponsesClient(
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            # OU credential=DefaultAzureCredential()
        )
    
    # Opção 2: OpenAI direto
    elif os.getenv("OPENAI_API_KEY"):
        from openai import OpenAI
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Opção 3: Groq (via OpenAI compatible API)
    elif os.getenv("GROQ_API_KEY"):
        from openai import OpenAI
        return OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
    
    raise ValueError("Nenhuma configuração LLM encontrada!")

def get_model_config() -> dict:
    """Retorna configurações do modelo."""
    return {
        "temperature": float(os.getenv("LLM_TEMPERATURE", "0.2")),
        "max_tokens": 4000,
    }
```

**Impacto**: Médio - Função central
**Risco**: Médio - Testar bem
**Tempo**: 30 min

---

### **FASE 3: Refatorar Camada de Agentes**

#### 🔄 **Passo 4: Reescrever agents/agent_factory.py**
**Arquivo**: `agents/agent_factory.py`

**ANTES (AutoGen)**:
```python
def create_specialist_agent(agent_id: int, examples: str) -> AssistantAgent:
    agent = AssistantAgent(
        name=f"specialist_{agent_id}",
        system_message=system_message,
        llm_config=get_json_llm_config(),
        human_input_mode="NEVER",
    )
    return agent
```

**DEPOIS (Agent Framework)**:
```python
from config.llm_config import get_chat_client, get_model_config

class SpecialistAgent:
    """Wrapper para agente especialista usando Agent Framework."""
    
    def __init__(self, agent_id: int, examples: str):
        self.agent_id = agent_id
        self.domain = get_domain_description(agent_id)
        self.instructions = get_specialist_prompt(agent_id, self.domain, examples)
        
        # Criar agente usando Agent Framework
        chat_client = get_chat_client()
        self.agent = chat_client.create_agent(
            name=f"specialist_{agent_id}",
            instructions=self.instructions,
            # model_config=get_model_config()  # Se suportado
        )
    
    async def run(self, task: str) -> str:
        """Executa análise e retorna resposta JSON."""
        response = await self.agent.run(task)
        return str(response)  # Converter para string se necessário

def create_specialist_agent(agent_id: int, examples: str) -> SpecialistAgent:
    """Factory para criar agente especialista."""
    return SpecialistAgent(agent_id, examples)
```

**Impacto**: Alto - Core do sistema
**Risco**: Médio - Interface pública preservada
**Tempo**: 1h

---

#### 🔄 **Passo 5: Adaptar agents/specialist_analysis.py**
**Arquivo**: `agents/specialist_analysis.py`

**ANTES (AutoGen)**:
```python
async def analyze_single(agent_id: int, response: str) -> SpecialistReport:
    specialist = create_specialist_agent(agent_id, examples)
    orchestrator = create_orchestrator_agent()
    
    chat_result = orchestrator.initiate_chat(
        specialist,
        message=task_message,
        max_turns=1
    )
    
    response_text = chat_result.chat_history[-1]['content']
```

**DEPOIS (Agent Framework)**:
```python
async def analyze_single(agent_id: int, response: str) -> SpecialistReport:
    specialist = create_specialist_agent(agent_id, examples)
    
    # Agent Framework usa .run() diretamente
    response_text = await specialist.run(task_message)
    
    # Resto do parsing JSON permanece igual
    report_data = json.loads(response_text)
    report = SpecialistReport(**report_data)
    return report
```

**Impacto**: Médio - Simplifica código
**Risco**: Baixo - Remove orchestrator
**Tempo**: 30 min

---

#### 🔄 **Passo 6: Adaptar agents/review_loop.py**
**Arquivo**: `agents/review_loop.py`

**Mudanças**: Mesma lógica do Passo 5
- Substituir `initiate_chat()` por `agent.run()`
- Manter loop de aprovação/retrabalho
- Preservar estrutura de feedback

**Impacto**: Médio
**Risco**: Baixo
**Tempo**: 30 min

---

#### 🔄 **Passo 7: Adaptar agents/synthesizer.py**
**Arquivo**: `agents/synthesizer.py`

**Mudanças**: Mesma lógica do Passo 5
- Substituir `initiate_chat()` por `agent.run()`
- Manter cálculo de score final
- Preservar estrutura JSON final

**Impacto**: Médio
**Risco**: Baixo
**Tempo**: 30 min

---

### **FASE 4: Validação e Ajustes**

#### ✅ **Passo 8: Verificar prompts/system_prompts.py**
**Mudanças**: Provavelmente nenhuma
- Verificar se formato de instruções funciona
- Ajustar se Agent Framework exigir formato diferente
- Manter enforce JSON mode

**Impacto**: Baixo
**Risco**: Baixo
**Tempo**: 15 min

---

#### ✅ **Passo 9: Verificar models/schemas.py**
**Mudanças**: Provavelmente nenhuma
- Pydantic models são agnósticos ao framework
- Manter todas validações

**Impacto**: Zero
**Risco**: Zero
**Tempo**: 5 min

---

#### ✅ **Passo 10: Verificar utils/ (data_loader.py, logger.py)**
**Mudanças**: Nenhuma
- Totalmente agnósticos ao framework de agentes
- Manter como estão

**Impacto**: Zero
**Risco**: Zero
**Tempo**: 5 min

---

#### ✅ **Passo 11: Atualizar main.py**
**Mudanças**: Mínimas ou nenhuma
- Verificar se imports mudaram
- Manter mesma API REST
- Preservar endpoints `/analyze`, `/health`

**Impacto**: Baixo
**Risco**: Baixo
**Tempo**: 15 min

---

### **FASE 5: Documentação e Testes**

#### 📝 **Passo 12: Atualizar Documentação**
**Arquivos**: 
- `README.md`
- `SETUP_GUIDE.md`
- `QUICKSTART.md`
- `ARCHITECTURE.md`

**Mudanças**:
- Substituir menções a "AutoGen" por "Microsoft Agent Framework"
- Atualizar instruções de instalação
- Atualizar variáveis de ambiente
- Manter mesma estrutura geral

**Impacto**: Médio - Documentação
**Risco**: Zero
**Tempo**: 45 min

---

#### 🧪 **Passo 13: Criar Testes de Integração**
**Arquivo**: `tests/test_migration.py`

```python
"""Testes para validar migração para Agent Framework."""

async def test_specialist_agent_creation():
    """Testa criação de agente especialista."""
    agent = create_specialist_agent(1, "examples")
    assert agent is not None

async def test_specialist_analysis():
    """Testa análise completa."""
    responses = ["test"] * 5
    reports = await run_specialist_analysis(responses, data_loader)
    assert len(reports) == 5

async def test_full_pipeline():
    """Testa pipeline completo: análise → revisão → síntese."""
    # Simular request completo
    response = await client.post("/analyze", json={...})
    assert response.status_code == 200
    assert "final_score" in response.json()
```

**Impacto**: Alto - Garantia de qualidade
**Risco**: Zero - Só testes
**Tempo**: 1h

---

#### 🚀 **Passo 14: Atualizar Scripts de Automação**
**Arquivos**:
- `setup.bat`
- `start_server.bat`
- `run_tests.bat`

**Mudanças**:
- Nenhuma mudança significativa
- Apenas documentar novas variáveis de ambiente

**Impacto**: Baixo
**Risco**: Zero
**Tempo**: 15 min

---

#### ✅ **Passo 15: Teste End-to-End Completo**
**Checklist**:
- [ ] Instalação limpa funciona
- [ ] Variáveis de ambiente configuradas
- [ ] Servidor inicia sem erros
- [ ] Endpoint `/health` responde
- [ ] Endpoint `/analyze` funciona com request completo
- [ ] Logs são gerados corretamente
- [ ] JSON final tem estrutura correta
- [ ] Score e risk_level são calculados
- [ ] Performance é aceitável (< 30s por análise)

**Impacto**: Crítico - Validação final
**Risco**: Zero - Só validação
**Tempo**: 1h

---

## 📊 RESUMO DO IMPACTO

| **Categoria** | **Arquivos Afetados** | **Nível de Mudança** | **Tempo Estimado** |
|---------------|-----------------------|----------------------|---------------------|
| **Config** | 2 arquivos | 🔄 Refatoração completa | 1h |
| **Agents** | 4 arquivos | 🔄 Refatoração média | 2.5h |
| **Utils** | 2 arquivos | ✅ Sem mudanças | 0h |
| **Models** | 1 arquivo | ✅ Sem mudanças | 0h |
| **API** | 1 arquivo | ⚠️ Mudanças mínimas | 15min |
| **Docs** | 4 arquivos | 📝 Atualização | 45min |
| **Tests** | 1 arquivo novo | 🧪 Criação | 1h |
| **Scripts** | 3 arquivos | ⚠️ Mudanças mínimas | 15min |

**TOTAL ESTIMADO**: **6-8 horas de trabalho**

---

## ⚠️ RISCOS E MITIGAÇÕES

### Risco 1: Agent Framework não suporta Groq
**Probabilidade**: Média  
**Impacto**: Médio  
**Mitigação**: Groq é compatível com OpenAI API, usar como fallback via OpenAI client

### Risco 2: Performance diferente
**Probabilidade**: Baixa  
**Impacto**: Baixo  
**Mitigação**: Fazer benchmarks antes/depois

### Risco 3: JSON mode não funciona igual
**Probabilidade**: Baixa  
**Impacto**: Médio  
**Mitigação**: Validar respostas com Pydantic (já implementado)

### Risco 4: Async behavior diferente
**Probabilidade**: Baixa  
**Impacto**: Baixo  
**Mitigação**: Agent Framework já é async-first

---

## ✅ CRITÉRIOS DE SUCESSO

1. ✅ **Funcionalidade Preservada**: Todos os endpoints retornam mesmos resultados
2. ✅ **Performance Aceitável**: Tempo de resposta < 30s
3. ✅ **Compatibilidade API**: Clientes existentes funcionam sem mudanças
4. ✅ **Qualidade de Código**: Testes passam com 100% de cobertura nas áreas críticas
5. ✅ **Documentação Atualizada**: Guias refletem nova implementação
6. ✅ **Zero Downtime**: Sistema pode ser migrado incrementalmente

---

## 🚀 ESTRATÉGIA DE IMPLEMENTAÇÃO

### Opção A: Big Bang (Recomendado para este projeto)
- Fazer todas mudanças em branch separada
- Testar completamente
- Deploy único quando 100% validado

### Opção B: Incremental (Se necessário)
- Criar abstração para permitir ambos frameworks
- Migrar agente por agente
- Mais complexo mas menor risco

**Escolha**: **Opção A** - Projeto pequeno, Big Bang é mais eficiente

---

## 📋 PRÓXIMOS PASSOS

1. **Confirmar escolha de provider**:
   - Azure OpenAI (recomendado)
   - OpenAI direto
   - Groq (via OpenAI API)

2. **Criar branch de refatoração**:
   ```bash
   git checkout -b feature/agent-framework-migration
   ```

3. **Começar pelos Passos 1-3** (preparação)

4. **Executar Passos 4-7** (core migration)

5. **Validar com Passos 8-15** (testes e docs)

---

## 📞 PRECISA DE AJUDA?

- Microsoft Agent Framework Docs: https://aka.ms/agent-framework
- Discord: https://discord.gg/b5zjErwbQM
- Migration Guide: https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen

---

**Data de Criação**: 2025-10-22  
**Status**: ✅ PLANO APROVADO - PRONTO PARA EXECUÇÃO
