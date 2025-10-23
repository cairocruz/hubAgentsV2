# 🚀 START HERE - Sistema de Análise de Risco com IA Multiagente

**Bem-vindo!** Este é o **ponto de partida** para usar o sistema.

---

## ⚡ INÍCIO ULTRARRÁPIDO (2 Minutos)

### Windows
1. Clique em: **`setup.bat`**
2. Edite `.env` e adicione sua Groq API Key
3. Clique em: **`start_server.bat`**

✅ **Servidor rodando em http://localhost:8000**

---

## 📚 DOCUMENTAÇÃO COMPLETA

### 🎯 Para Começar
| Arquivo | Descrição | Tempo |
|---------|-----------|-------|
| **[WELCOME.md](WELCOME.md)** | Boas-vindas e visão geral | 3 min |
| **[QUICKSTART.md](QUICKSTART.md)** | Início rápido detalhado | 5 min |
| **[SETUP_GUIDE.md](SETUP_GUIDE.md)** | Guia passo-a-passo completo | 10 min |

### 📖 Para Usar
| Arquivo | Descrição |
|---------|-----------|
| **[README.md](README.md)** | Documentação completa da API |
| **[examples/usage_examples.py](examples/usage_examples.py)** | Exemplos práticos de código |

### 🏗️ Para Entender
| Arquivo | Descrição |
|---------|-----------|
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Arquitetura do sistema |
| **[RESUMO_EXPLICATIVO.md](RESUMO_EXPLICATIVO.md)** | Conceitos de IA |
| **[INDEX.md](INDEX.md)** | Índice completo do projeto |

### 📊 Status do Projeto
| Arquivo | Descrição |
|---------|-----------|
| **[PROJECT_STATUS.md](PROJECT_STATUS.md)** | Status e checklist completo |
| **[FINAL_SUMMARY.md](FINAL_SUMMARY.md)** | Resumo executivo final |

---

## 🤖 O QUE É ESTE SISTEMA?

Um sistema avançado que analisa **risco de violência doméstica** usando:

- **5 agentes especialistas** trabalhando em paralelo
- **1 supervisor** para garantir qualidade
- **1 sintetizador** para consolidar resultados
- **75 exemplos** de Few-Shot Learning
- **API RESTful** simples e poderosa

### Como Funciona

```
Você envia 5 respostas → Sistema analisa com IA → Recebe análise completa
                        (30-60 segundos)
```

---

## 📦 O QUE FOI IMPLEMENTADO

### ✅ Todas as 15 Etapas do Plano
1. ✅ Setup inicial completo
2. ✅ 5 datasets Few-Shot (75 exemplos)
3. ✅ Configuração LLM (Groq/Llama3)
4. ✅ Sistema de prompts especializados
5. ✅ DataLoader para Few-Shot
6. ✅ AgentFactory com AutoGen
7. ✅ Análise paralela (5 agentes)
8. ✅ Loop de revisão com supervisor
9. ✅ Agente sintetizador
10. ✅ Logging auditável
11. ✅ Modelos Pydantic
12. ✅ Endpoints FastAPI
13. ✅ Tratamento de erros robusto
14. ✅ Testes automatizados
15. ✅ Documentação completa

### 📊 Estatísticas
- **2.500+ linhas** de código
- **3.000+ linhas** de documentação
- **35+ arquivos** criados
- **7 agentes** IA implementados
- **75 exemplos** Few-Shot
- **100% conformidade** com especificações

---

## 🔑 REQUISITOS

### Software
- Python 3.9+
- Conta Groq (gratuita) → https://console.groq.com

### Tempo de Setup
- **2-5 minutos** (com scripts automáticos)
- **10 minutos** (manual)

---

## 🚀 COMANDOS RÁPIDOS

```bash
# Setup (uma vez)
setup.bat

# Verificar
python verify_setup.py

# Testar
run_tests.bat

# Iniciar
start_server.bat

# Exemplos
run_examples.bat
```

---

## 🧪 TESTE RÁPIDO

### Opção 1: Navegador
Abra: http://localhost:8000

### Opção 2: Python
```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={
        "responses": [
            "Eu faço tudo sozinha",
            "Ele grita comigo",
            "Não vejo amigas",
            "Ele controla dinheiro",
            "Me sinto cansada"
        ]
    }
)

result = response.json()
print(f"Score: {result['final_score']}")
print(f"Risco: {result['risk_level']}")
```

---

## 📊 ESTRUTURA DO PROJETO

```
hubAgentsV2/
├── 📖 Documentação (8 guias .md)
├── 🤖 agents/ (Código dos agentes)
├── ⚙️ config/ (Configurações)
├── 📊 data/ (5 datasets CSV)
├── 📋 models/ (Schemas Pydantic)
├── 💬 prompts/ (Prompts especializados)
├── 🔧 utils/ (Logger, DataLoader)
├── 🧪 tests/ (Testes)
├── 📚 examples/ (Exemplos de uso)
├── 🚀 Scripts (.bat para automação)
└── 🐍 main.py (Aplicação FastAPI)
```

---

## 🎯 CASOS DE USO

### Alto Risco
```json
{
  "responses": [
    "Faço tudo sozinha",
    "Ele grita comigo",
    "Não vejo amigas",
    "Ele controla dinheiro",
    "Me sinto cansada"
  ]
}
```
→ Score: 70-90, Risco: Alto

### Baixo Risco
```json
{
  "responses": [
    "Dividimos tarefas",
    "Conversamos com respeito",
    "Liberdade total",
    "Cada um sua conta",
    "Me sinto bem"
  ]
}
```
→ Score: 0-30, Risco: Baixo

---

## 📞 PRECISA DE AJUDA?

### Setup
→ Veja **[SETUP_GUIDE.md](SETUP_GUIDE.md)**

### Uso da API
→ Veja **[README.md](README.md)**

### Entender o Sistema
→ Veja **[ARCHITECTURE.md](ARCHITECTURE.md)**

### Problemas Técnicos
→ Execute `python verify_setup.py`

---

## 🎓 TECNOLOGIAS

- **AutoGen** (Microsoft) - Multiagentes
- **Groq** - Inferência LLM
- **Llama 3** - Modelo de linguagem
- **FastAPI** - Framework web
- **Pydantic** - Validação de dados

---

## ⚡ PERFORMANCE

- **Tempo de resposta:** 30-60 segundos
- **Análises paralelas:** Suportado
- **Uso de memória:** ~200-300MB
- **Precisão:** Alta (Few-Shot Learning)

---

## 🌟 DESTAQUES

✅ Sistema Multiagente Avançado  
✅ Few-Shot Learning Contextualizado  
✅ Análise Paralela de Alta Performance  
✅ Sistema de Revisão com Qualidade  
✅ Logging Completo e Auditável  
✅ API RESTful Documentada  
✅ Scripts de Automação Prontos  
✅ Documentação Extensiva (8 guias)  
✅ Testes Automatizados  
✅ Pronto para Produção  

---

## ✅ STATUS

**✅ 100% COMPLETO E FUNCIONAL**

- Todas as 15 etapas implementadas
- Conformidade 100% com especificações
- Código testado e documentado
- Pronto para uso imediato

---

## 🎯 PRÓXIMO PASSO

### Escolha seu caminho:

**🚀 Quero usar rápido:**  
→ Execute `setup.bat` → Configure `.env` → Execute `start_server.bat`

**📖 Quero entender primeiro:**  
→ Leia [WELCOME.md](WELCOME.md) → [QUICKSTART.md](QUICKSTART.md) → [README.md](README.md)

**🏗️ Quero ver a arquitetura:**  
→ Leia [ARCHITECTURE.md](ARCHITECTURE.md) → [RESUMO_EXPLICATIVO.md](RESUMO_EXPLICATIVO.md)

**💻 Quero ver código:**  
→ Veja `agents/` → `main.py` → [examples/usage_examples.py](examples/usage_examples.py)

---

## 📋 CHECKLIST RÁPIDO

- [ ] Python 3.9+ instalado
- [ ] Executou `setup.bat`
- [ ] Obteve Groq API Key
- [ ] Configurou `.env`
- [ ] Executou `start_server.bat`
- [ ] Testou em http://localhost:8000

---

**Versão:** 1.0.0  
**Status:** ✅ Pronto para Uso  
**Data:** Outubro 2025

---

## 🎉 COMECE AGORA!

```
1. setup.bat
2. Configure .env
3. start_server.bat
4. http://localhost:8000
```

**🚀 Boa análise!**
