# 🚀 GUIA DE SETUP E EXECUÇÃO

Este guia fornece instruções passo-a-passo para configurar e executar o sistema.

---

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter:

- ✅ Python 3.9 ou superior
- ✅ pip (gerenciador de pacotes Python)
- ✅ Conta Groq (gratuita) para obter API Key

---

## 🔧 PASSO 1: Clonar/Baixar o Projeto

Se ainda não tem o projeto localmente:

```bash
cd "C:\Users\cairo\OneDrive\Área de Trabalho\hubAgentsV2"
```

---

## 🐍 PASSO 2: Criar Ambiente Virtual

### Windows PowerShell:

```powershell
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Se houver erro de execução de scripts, execute:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Windows CMD:

```cmd
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
venv\Scripts\activate.bat
```

Após ativar, você verá `(venv)` no início da linha de comando.

---

## 📦 PASSO 3: Instalar Dependências

Com o ambiente virtual ativado:

```bash
pip install -r requirements.txt
```

Isso instalará:
- FastAPI (framework web)
- AutoGen (sistema multiagente)
- Groq (client LLM)
- Pandas (manipulação de dados)
- Pydantic (validação)
- Uvicorn (servidor ASGI)

---

## 🔑 PASSO 4: Configurar API Key

### 4.1. Obter Groq API Key

1. Acesse: https://console.groq.com
2. Crie uma conta (gratuita)
3. Vá para **API Keys**
4. Clique em **Create API Key**
5. Copie a chave gerada

### 4.2. Criar arquivo .env

```bash
# Copiar o exemplo
copy .env.example .env
```

### 4.3. Editar .env

Abra `.env` em um editor de texto e cole sua API Key:

```env
GROQ_API_KEY=gsk_sua_chave_aqui_cole_completa
LLM_MODEL=llama3-8b-8192
LLM_TEMPERATURE=0.2
```

**IMPORTANTE:** Mantenha esta chave em segredo!

---

## ✅ PASSO 5: Verificar Instalação

Execute o script de testes:

```bash
python tests/test_system.py
```

Você deve ver:

```
✅ DataLoader initialized
✅ Retrieved examples for Agent 1
✅ Valid request accepted
✅ Invalid request rejected correctly
```

---

## 🚀 PASSO 6: Iniciar o Servidor

```bash
python main.py
```

Você verá:

```
╔═══════════════════════════════════════════════════════════╗
║   Sistema de Análise de Risco com IA Multiagente        ║
║   Iniciando servidor...                                   ║
╚═══════════════════════════════════════════════════════════╝

✅ DataLoader initialized
✅ Logger initialized

INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

O servidor está rodando! ✅

---

## 🧪 PASSO 7: Testar a API

### Opção 1: Navegador

Abra: http://localhost:8000

Você verá a mensagem de boas-vindas da API.

### Opção 2: Health Check

Abra: http://localhost:8000/health

Deve retornar:
```json
{
  "status": "healthy",
  "data_loader": "initialized",
  "logger": "initialized"
}
```

### Opção 3: Script de Exemplo

**Em outro terminal** (com venv ativado):

```bash
python examples/usage_examples.py
```

Siga as instruções interativas.

### Opção 4: cURL

```bash
curl -X POST http://localhost:8000/analyze -H "Content-Type: application/json" -d "{\"responses\": [\"Eu faço tudo em casa sozinha\", \"Ele grita comigo\", \"Não vejo minhas amigas\", \"Ele controla o dinheiro\", \"Me sinto cansada\"]}"
```

### Opção 5: Python Script

Crie `test_api.py`:

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

result = response.json()
print(f"Score: {result['final_score']}")
print(f"Risco: {result['risk_level']}")
```

Execute:
```bash
python test_api.py
```

---

## 📊 PASSO 8: Verificar Logs

Os logs são salvos automaticamente em `logs/`:

```bash
dir logs
```

Cada requisição gera um arquivo JSON com:
- Timestamp
- Análises de cada agente
- Feedbacks do supervisor
- Síntese final

---

## 🛑 Parar o Servidor

No terminal onde o servidor está rodando:

- **Windows:** `Ctrl + C`
- **Mac/Linux:** `Ctrl + C`

---

## 🔄 Próximas Execuções

Sempre que quiser usar o sistema:

1. **Ativar ambiente virtual:**
   ```bash
   .\venv\Scripts\Activate.ps1  # PowerShell
   # ou
   venv\Scripts\activate.bat     # CMD
   ```

2. **Iniciar servidor:**
   ```bash
   python main.py
   ```

---

## ⚠️ Troubleshooting

### Erro: "GROQ_API_KEY not found"

**Solução:** Verifique se o arquivo `.env` existe e contém a chave correta.

```bash
type .env  # Windows
cat .env   # Linux/Mac
```

### Erro: "No module named 'autogen'"

**Solução:** Instale as dependências novamente:

```bash
pip install -r requirements.txt
```

### Erro: "Port 8000 is already in use"

**Solução:** Altere a porta no `main.py`:

```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Erro ao ativar venv no PowerShell

**Solução:** Habilite execução de scripts:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Erro: "Rate limit exceeded"

**Solução:** Aguarde alguns segundos entre requisições. A API gratuita do Groq tem limites de taxa.

---

## 📈 Performance

**Tempo esperado por análise:** 30-60 segundos

Depende de:
- Velocidade da API Groq
- Complexidade das respostas
- Número de retrabalhos necessários

---

## 🎯 Uso em Produção

Para produção, considere:

1. **Variáveis de Ambiente:**
   ```bash
   # Linux/Mac
   export GROQ_API_KEY=your_key
   
   # Windows PowerShell
   $env:GROQ_API_KEY="your_key"
   ```

2. **Servidor de Produção:**
   ```bash
   pip install gunicorn
   gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
   ```

3. **Docker (opcional):**
   ```dockerfile
   FROM python:3.9
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["python", "main.py"]
   ```

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs em `logs/`
2. Execute os testes: `python tests/test_system.py`
3. Verifique se o `.env` está configurado
4. Confirme que todas as dependências estão instaladas

---

## ✅ Checklist Rápido

- [ ] Python 3.9+ instalado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `.env` criado com GROQ_API_KEY
- [ ] Testes executados com sucesso
- [ ] Servidor iniciado (`python main.py`)
- [ ] API respondendo em http://localhost:8000

---

**Pronto! Seu sistema está funcional! 🎉**
