# 📑 ÍNDICE COMPLETO DO PROJETO

Navegação rápida para todos os recursos do sistema.

---

## 📖 DOCUMENTAÇÃO

### 🚀 Para Começar
- **[QUICKSTART.md](QUICKSTART.md)** - Início rápido em 5 minutos
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Guia completo de instalação
- **[README.md](README.md)** - Documentação completa da API

### 📚 Referência Técnica
- **[RESUMO_EXPLICATIVO.md](RESUMO_EXPLICATIVO.md)** - Arquitetura e conceitos de IA

---

## 🛠️ SCRIPTS DE AUTOMAÇÃO

### Windows (.bat)
- **`setup.bat`** - Setup automático completo
- **`start_server.bat`** - Inicia o servidor
- **`run_tests.bat`** - Executa testes
- **`run_examples.bat`** - Executa exemplos de uso

### Python
- **`main.py`** - Aplicação principal (FastAPI)
- **`verify_setup.py`** - Verifica estrutura e dependências
- **`tests/test_system.py`** - Suite de testes
- **`examples/usage_examples.py`** - Exemplos práticos

---

## 📁 ESTRUTURA DE CÓDIGO

### 🤖 Agentes (`agents/`)
```
agents/
├── __init__.py                 # Exports do módulo
├── agent_factory.py            # Criação de agentes AutoGen
├── specialist_analysis.py      # Análise paralela dos especialistas
├── review_loop.py              # Loop de revisão com supervisor
└── synthesizer.py              # Síntese final consolidada
```

**Funções Principais:**
- `create_specialist_agent(agent_id, examples)` - Cria agente especialista
- `create_supervisor_agent()` - Cria agente supervisor
- `create_synthesizer_agent()` - Cria agente sintetizador
- `run_specialist_analysis_sync(responses, data_loader)` - Análise paralela
- `run_review_loop(report, data_loader, response)` - Loop de revisão
- `run_synthesis(approved_reports)` - Síntese final

### ⚙️ Configuração (`config/`)
```
config/
├── __init__.py
└── llm_config.py               # Configuração do LLM (Groq/Llama)
```

**Funções Principais:**
- `get_llm_config()` - Config básica do LLM
- `get_json_llm_config()` - Config com JSON mode

### 📊 Dados (`data/`)
```
data/
├── dataset_1.csv               # Tarefas Domésticas (15 exemplos)
├── dataset_2.csv               # Tom Emocional (15 exemplos)
├── dataset_3.csv               # Redes de Apoio (15 exemplos)
├── dataset_4.csv               # Controle Financeiro (15 exemplos)
└── dataset_5.csv               # Bem-estar Físico (15 exemplos)
```

**Estrutura CSV:**
```csv
frase,risco,fator,taxonomia,metadata
```

### 📋 Modelos (`models/`)
```
models/
├── __init__.py
└── schemas.py                  # Schemas Pydantic
```

**Classes Principais:**
- `AnalysisRequest` - Request com 5 respostas
- `SpecialistReport` - Relatório de especialista
- `ReviewFeedback` - Feedback do supervisor
- `FinalAnalysis` - Análise final consolidada
- `RiskFactor` - Fator de risco individual
- `LogEvent` - Evento de log
- `RequestLog` - Log completo de requisição

### 💬 Prompts (`prompts/`)
```
prompts/
├── __init__.py
└── system_prompts.py           # Prompts especializados
```

**Funções Principais:**
- `get_specialist_prompt(agent_id, domain, examples)` - Prompt de especialista
- `get_supervisor_prompt()` - Prompt do supervisor
- `get_synthesizer_prompt()` - Prompt do sintetizador
- `get_domain_description(agent_id)` - Descrição do domínio

**Domínios:**
1. Rotina, Sobrecarga e Divisão de Tarefas Domésticas
2. Tom Emocional, Comunicação e Intimidação
3. Redes de Apoio, Isolamento Social e Vínculos
4. Controle Financeiro e Dependência Econômica
5. Bem-estar Físico, Psicológico e Saúde Mental

### 🔧 Utilitários (`utils/`)
```
utils/
├── __init__.py
├── data_loader.py              # Carregamento de datasets
└── logger.py                   # Sistema de logging
```

**DataLoader:**
- `get_few_shot_examples(agent_id, num_examples)` - Exemplos Few-Shot
- `get_dataset(agent_id)` - Dataset completo
- `get_dataset_stats(agent_id)` - Estatísticas do dataset

**Logger:**
- `start_request_log(request_payload)` - Inicia log
- `log_event(event_type, data, agent_id, attempt)` - Registra evento
- `finalize_log(response, duration)` - Finaliza e salva log

---

## 🔌 API ENDPOINTS

### `GET /`
**Informações da API**
```json
{
  "message": "Sistema de Análise de Risco com IA Multiagente",
  "version": "1.0.0",
  "endpoints": {...}
}
```

### `GET /health`
**Health check do sistema**
```json
{
  "status": "healthy",
  "data_loader": "initialized",
  "logger": "initialized"
}
```

### `POST /analyze`
**Endpoint principal de análise**

**Request:**
```json
{
  "responses": [
    "Resposta 1",
    "Resposta 2",
    "Resposta 3",
    "Resposta 4",
    "Resposta 5"
  ]
}
```

**Response:**
```json
{
  "final_score": 75.5,
  "risk_level": "Alto",
  "synthesis": "...",
  "consolidated_factors": [...],
  "recommendations": [...],
  "specialist_reports": [...]
}
```

---

## 📊 FLUXO DE EXECUÇÃO

```
1. POST /analyze (5 respostas)
   ↓
2. Análise Paralela (5 agentes especialistas)
   ↓
3. Loop de Revisão (supervisor revisa cada relatório)
   ↓
4. Retrabalho (se necessário, até 1x por agente)
   ↓
5. Síntese Final (agente sintetizador consolida)
   ↓
6. Retorno JSON (score + risk_level + fatores)
```

---

## 🧪 TESTES

### Executar Todos os Testes
```bash
python tests/test_system.py
```

### Testes Individuais
```python
# Test DataLoader
from utils import DataLoader
loader = DataLoader(data_dir="data")
examples = loader.get_few_shot_examples(1)

# Test API Request
from models import AnalysisRequest
request = AnalysisRequest(responses=["R1", "R2", "R3", "R4", "R5"])
```

---

## 📝 LOGS

**Localização:** `logs/`

**Formato:** `request_<uuid>_<timestamp>.json`

**Conteúdo:**
- Request original
- Análises de cada especialista
- Feedbacks do supervisor
- Tentativas de retrabalho
- Síntese final
- Duração total

**Exemplo:**
```json
{
  "request_id": "abc-123",
  "timestamp": "2025-10-22T10:30:00",
  "events": [
    {
      "event_type": "specialist_analysis",
      "agent_id": "1",
      "attempt": 1,
      "data": {...}
    }
  ]
}
```

---

## 🎯 CASOS DE USO

### Alto Risco
```python
responses = [
    "Eu faço tudo em casa sozinha",
    "Ele grita comigo sempre",
    "Não vejo mais minhas amigas",
    "Ele controla todo o dinheiro",
    "Me sinto muito cansada"
]
# Score esperado: 70-90
# Risk level: Alto
```

### Médio Risco
```python
responses = [
    "A gente divide as tarefas mas sobra mais pra mim",
    "Às vezes ele fala alto quando está irritado",
    "Vejo menos minhas amigas do que antes",
    "Ele cuida da maior parte do dinheiro",
    "Ando um pouco estressada"
]
# Score esperado: 40-65
# Risk level: Médio
```

### Baixo Risco
```python
responses = [
    "Dividimos as tarefas de forma equilibrada",
    "Conversamos com respeito",
    "Tenho liberdade para ver amigos",
    "Cada um tem sua conta",
    "Me sinto bem"
]
# Score esperado: 0-30
# Risk level: Baixo
```

---

## 🔧 CONFIGURAÇÃO

### Variáveis de Ambiente (`.env`)
```env
GROQ_API_KEY=gsk_your_key_here
LLM_MODEL=llama3-8b-8192
LLM_TEMPERATURE=0.2
LOG_LEVEL=INFO
MAX_REWORK_ATTEMPTS=1
```

### Dependências (`requirements.txt`)
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- pydantic==2.5.0
- python-dotenv==1.0.0
- pyautogen==0.2.3
- groq==0.4.2
- pandas==2.1.3
- python-multipart==0.0.6
- aiofiles==23.2.1

---

## 📈 MÉTRICAS

### Performance
- **Tempo médio por análise:** 30-60 segundos
- **Análise paralela:** 5 agentes simultâneos
- **Retrabalho máximo:** 1 tentativa por agente

### Qualidade
- **Datasets:** 75 exemplos (15 por domínio)
- **Agentes especializados:** 5
- **Sistema de revisão:** 1 supervisor
- **Auditabilidade:** 100% (todos os logs salvos)

---

## 🛡️ SEGURANÇA

### API Key
- ✅ Armazenada em `.env` (não commitada)
- ✅ Nunca exposta nos logs
- ✅ Usar variáveis de ambiente em produção

### Dados
- ✅ Nenhum dado de usuário armazenado permanentemente
- ✅ Logs podem conter dados sensíveis (proteja a pasta logs/)
- ✅ Use HTTPS em produção

---

## 🚀 PRODUÇÃO

### Checklist
- [ ] Configure `GROQ_API_KEY` como variável de ambiente
- [ ] Use servidor WSGI/ASGI (Gunicorn + Uvicorn)
- [ ] Configure HTTPS/SSL
- [ ] Implemente rate limiting
- [ ] Configure backup de logs
- [ ] Monitore uso da API Groq
- [ ] Configure alertas de erro

### Deploy Sugerido
```bash
# Instalar Gunicorn
pip install gunicorn

# Rodar em produção
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

---

## 📞 SUPORTE

### Problemas Comuns
1. **API Key não configurada**
   - Veja: SETUP_GUIDE.md → Configuração

2. **Porta 8000 em uso**
   - Altere porta em `main.py`

3. **Dependências faltando**
   - Execute: `pip install -r requirements.txt`

4. **Testes falhando**
   - Verifique: `python verify_setup.py`

### Diagnóstico
```bash
# Verificar setup
python verify_setup.py

# Testar sistema
python tests/test_system.py

# Verificar logs
dir logs
```

---

## 🎓 RECURSOS DE APRENDIZADO

### Conceitos de IA
- **Multi-Agent Systems (MAS)**
- **Few-Shot Learning**
- **Chain of Thought Prompting**
- **Self-Correction Loop**
- **Hierarchical Orchestration**

### Frameworks
- **AutoGen** - Microsoft
- **FastAPI** - Python web framework
- **Pydantic** - Validação de dados
- **Groq** - Inferência LLM

### Documentação Externa
- [AutoGen Docs](https://microsoft.github.io/autogen/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Groq Console](https://console.groq.com/)

---

## 📊 ESTATÍSTICAS DO PROJETO

```
Total de Arquivos: 30+
Linhas de Código: 2000+
Datasets: 5 CSVs (75 exemplos)
Agentes: 7 (5 especialistas + 1 supervisor + 1 sintetizador)
Endpoints: 3 (/analyze, /health, /)
Dependências: 9 principais
```

---

## 🏆 CARACTERÍSTICAS

- ✅ Sistema Multiagente
- ✅ Análise Paralela
- ✅ Few-Shot Learning
- ✅ Loop de Revisão
- ✅ Logging Auditável
- ✅ API RESTful
- ✅ Validação Pydantic
- ✅ Documentação Completa
- ✅ Scripts de Automação
- ✅ Testes Automatizados

---

**Versão:** 1.0.0  
**Última Atualização:** Outubro 2025  
**Status:** ✅ Funcional e Pronto para Uso
