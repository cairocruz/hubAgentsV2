# 🎉 BEM-VINDO AO SISTEMA DE ANÁLISE DE RISCO COM IA MULTIAGENTE

Obrigado por usar nosso sistema! Este guia vai te ajudar a começar rapidamente.

---

## 📖 O QUE É ESTE SISTEMA?

Um sistema avançado de **análise de risco de violência doméstica** que utiliza:
- 🤖 **5 agentes especialistas** de IA trabalhando em paralelo
- 👨‍💼 **1 supervisor** para garantir qualidade
- 🎯 **1 sintetizador** para consolidar resultados
- 📊 **Few-Shot Learning** para análises precisas
- 📝 **Logging completo** para auditoria

---

## ⚡ INÍCIO RÁPIDO (3 MINUTOS)

### Windows - Método Automático

1. **Clique duas vezes em:** `setup.bat`
2. **Configure sua API Key no arquivo `.env`** que será aberto
   - Obtenha em: https://console.groq.com (gratuito)
3. **Clique duas vezes em:** `start_server.bat`

✅ **Pronto! Servidor rodando em http://localhost:8000**

### Outros Sistemas ou Linha de Comando

```bash
# 1. Criar ambiente virtual
python -m venv venv

# 2. Ativar ambiente
.\venv\Scripts\Activate.ps1  # PowerShell
# ou
venv\Scripts\activate.bat     # CMD

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar .env
copy .env.example .env
# Edite .env e adicione sua GROQ_API_KEY

# 5. Iniciar
python main.py
```

---

## 🧪 TESTAR O SISTEMA

### Opção 1: Scripts Prontos
Clique em: `run_tests.bat` ou `run_examples.bat`

### Opção 2: Navegador
Abra: http://localhost:8000

### Opção 3: Python

```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={
        "responses": [
            "Eu faço tudo em casa sozinha",
            "Ele grita comigo sempre",
            "Não vejo mais minhas amigas",
            "Ele controla todo o dinheiro",
            "Me sinto muito cansada"
        ]
    }
)

print(response.json())
```

---

## 📚 DOCUMENTAÇÃO DISPONÍVEL

### Para Começar
- **[QUICKSTART.md](QUICKSTART.md)** ⚡ - Início em 5 minutos
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** 🔧 - Guia completo de instalação

### Para Usar
- **[README.md](README.md)** 📖 - Documentação da API
- **[examples/usage_examples.py](examples/usage_examples.py)** 💻 - Exemplos de código

### Para Entender
- **[ARCHITECTURE.md](ARCHITECTURE.md)** 🏗️ - Arquitetura do sistema
- **[RESUMO_EXPLICATIVO.md](RESUMO_EXPLICATIVO.md)** 🧠 - Conceitos de IA
- **[INDEX.md](INDEX.md)** 📑 - Índice completo

---

## 🎯 ESTRUTURA DE PASTAS

```
📁 hubAgentsV2/
├── 📂 agents/          → Código dos agentes IA
├── 📂 config/          → Configurações do sistema
├── 📂 data/            → Datasets para Few-Shot Learning
├── 📂 models/          → Modelos de dados (Pydantic)
├── 📂 prompts/         → Prompts especializados
├── 📂 utils/           → Utilitários (logger, data loader)
├── 📂 tests/           → Testes automatizados
├── 📂 examples/        → Exemplos de uso
├── 📂 logs/            → Logs de auditoria (criado automaticamente)
├── 🐍 main.py          → Aplicação principal
└── 📄 *.md             → Documentação
```

---

## 🚀 COMANDOS ÚTEIS

### Iniciar Servidor
```bash
python main.py
```

### Executar Testes
```bash
python tests/test_system.py
```

### Verificar Setup
```bash
python verify_setup.py
```

### Ver Exemplos
```bash
python examples/usage_examples.py
```

---

## 🔑 OBTENDO SUA API KEY

1. Acesse: **https://console.groq.com**
2. Crie uma conta **gratuita**
3. Vá para **"API Keys"**
4. Clique em **"Create API Key"**
5. Copie a chave gerada
6. Cole no arquivo **`.env`**:
   ```env
   GROQ_API_KEY=gsk_sua_chave_aqui
   ```

**Nota:** Groq oferece uso gratuito generoso para desenvolvimento!

---

## 📊 O QUE O SISTEMA FAZ?

### Entrada
Você envia **5 respostas** da usuária:
1. Sobre rotina e tarefas domésticas
2. Sobre comunicação e tom emocional
3. Sobre redes de apoio social
4. Sobre controle financeiro
5. Sobre bem-estar físico/mental

### Processamento
- 🔬 **5 agentes especialistas** analisam cada resposta
- 👨‍💼 **Supervisor** revisa e pode solicitar melhorias
- 🎯 **Sintetizador** consolida tudo em análise final

### Saída
Você recebe:
- 📊 **Score de risco** (0-100)
- ⚠️ **Nível de risco** (Baixo/Médio/Alto)
- 🔍 **Fatores identificados** (detalhados)
- 💡 **Recomendações** práticas
- 📝 **Relatórios completos** de cada especialista

---

## ⏱️ TEMPO DE RESPOSTA

**Análise completa:** 30-60 segundos

O sistema executa análises complexas com múltiplas validações, então é normal demorar um pouco!

---

## 🎨 EXEMPLO DE USO

**Request:**
```json
{
  "responses": [
    "Eu cuido de tudo sozinha",
    "Ele sempre me interrompe quando falo",
    "Parei de ver minhas amigas",
    "Ele não me deixa trabalhar",
    "Me sinto muito ansiosa"
  ]
}
```

**Response:**
```json
{
  "final_score": 78.5,
  "risk_level": "Alto",
  "synthesis": "Análise identificou múltiplos fatores de alto risco...",
  "consolidated_factors": [
    {
      "factor": "Isolamento Social Progressivo",
      "severity": "Alto",
      "description": "Perda de rede de apoio..."
    }
  ],
  "recommendations": [
    "Buscar apoio de rede de suporte familiar",
    "Considerar orientação profissional especializada"
  ]
}
```

---

## ⚠️ PROBLEMAS COMUNS

### "GROQ_API_KEY not found"
✅ **Solução:** Edite `.env` e adicione sua chave da Groq

### "Port 8000 already in use"
✅ **Solução:** Feche outros servidores ou mude a porta em `main.py`

### "No module named 'autogen'"
✅ **Solução:** Execute `pip install -r requirements.txt`

### Scripts .bat não funcionam
✅ **Solução:** Use os comandos manuais listados acima

---

## 💡 DICAS

### 1. Veja os Logs
Todos os logs ficam em `logs/` com histórico completo de cada análise!

### 2. Personalize os Datasets
Edite os arquivos em `data/dataset_*.csv` para adicionar novos exemplos

### 3. Ajuste os Prompts
Modifique `prompts/system_prompts.py` para refinar as análises

### 4. Monitore Performance
Use `verify_setup.py` para verificar o estado do sistema

---

## 🎓 APRENDA MAIS

### Conceitos de IA Utilizados
- **Multi-Agent Systems** - Múltiplos agentes colaborando
- **Few-Shot Learning** - Aprendizado por exemplos
- **Chain of Thought** - Raciocínio passo-a-passo
- **Self-Correction** - Auto-correção via feedback

### Tecnologias
- **AutoGen** (Microsoft) - Framework multiagente
- **FastAPI** - Framework web Python
- **Groq** - Inferência LLM ultrarrápida
- **Llama 3** - Modelo de linguagem

---

## 📞 PRECISA DE AJUDA?

1. 📖 Leia **QUICKSTART.md** para início rápido
2. 🔧 Consulte **SETUP_GUIDE.md** para problemas de instalação
3. 📚 Veja **README.md** para documentação completa da API
4. 🏗️ Leia **ARCHITECTURE.md** para entender o sistema
5. 🧪 Execute `python verify_setup.py` para diagnóstico

---

## ✅ CHECKLIST PRÉ-USO

- [ ] Python 3.9+ instalado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `.env` criado e configurado com GROQ_API_KEY
- [ ] Testes executados com sucesso
- [ ] Servidor iniciado

---

## 🎉 PRONTO PARA COMEÇAR!

Agora você tem tudo que precisa! Execute:

```bash
# Windows - Método rápido
setup.bat           # Configurar (uma vez)
start_server.bat    # Iniciar servidor

# Ou método manual
python main.py      # Iniciar servidor
```

Depois acesse: **http://localhost:8000**

---

## 🌟 CARACTERÍSTICAS PRINCIPAIS

- ✅ Sistema Multiagente Avançado
- ✅ Análise Paralela (5 agentes simultâneos)
- ✅ Sistema de Revisão com Supervisor
- ✅ Few-Shot Learning Contextualizado
- ✅ Logging Completo e Auditável
- ✅ API RESTful Documentada
- ✅ Scripts de Automação
- ✅ Testes Automatizados
- ✅ Documentação Extensiva

---

## 📈 PRÓXIMOS PASSOS

Após ter o sistema rodando:

1. **Explore a documentação** - Entenda todos os recursos
2. **Teste com diferentes cenários** - Veja como o sistema se comporta
3. **Analise os logs** - Entenda o processo de decisão
4. **Personalize** - Ajuste datasets e prompts para seu caso de uso

---

**Versão:** 1.0.0  
**Status:** ✅ Pronto para Uso  
**Última Atualização:** Outubro 2025

---

**🚀 Vamos começar! Boa análise!**
