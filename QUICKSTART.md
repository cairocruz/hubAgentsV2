# ⚡ INÍCIO RÁPIDO - 5 Minutos

Guia express para ter o sistema funcionando rapidamente!

---

## 🚀 Método 1: Scripts Automáticos (Recomendado - Windows)

### Passo 1: Setup Inicial
Clique duas vezes em: **`setup.bat`**

Isso vai:
- ✅ Criar ambiente virtual
- ✅ Instalar todas as dependências
- ✅ Criar arquivo .env

### Passo 2: Configurar API Key
1. Abra o arquivo `.env` que foi criado
2. Acesse https://console.groq.com
3. Crie uma conta gratuita
4. Copie sua API Key
5. Cole no `.env`:
   ```
   GROQ_API_KEY=gsk_sua_chave_aqui
   ```

### Passo 3: Testar
Clique duas vezes em: **`run_tests.bat`**

Se tudo estiver OK, você verá:
```
✅ DataLoader initialized
✅ All tests passed!
```

### Passo 4: Iniciar
Clique duas vezes em: **`start_server.bat`**

Servidor rodando em: http://localhost:8000

### Passo 5: Usar
Abra outra janela e clique em: **`run_examples.bat`**

---

## 🖥️ Método 2: Linha de Comando Manual

```bash
# 1. Criar ambiente virtual
python -m venv venv

# 2. Ativar (PowerShell)
.\venv\Scripts\Activate.ps1

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar .env
copy .env.example .env
notepad .env  # Adicione sua GROQ_API_KEY

# 5. Iniciar servidor
python main.py
```

---

## 🧪 Teste Rápido da API

Abra outra janela do PowerShell e execute:

```powershell
# Método 1: Health Check
curl http://localhost:8000/health

# Método 2: Análise Completa
$body = @{
    responses = @(
        "Eu faço tudo em casa sozinha",
        "Ele grita comigo sempre",
        "Não vejo mais minhas amigas",
        "Ele controla todo o dinheiro",
        "Me sinto muito cansada"
    )
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/analyze -Method POST -Body $body -ContentType "application/json"
```

---

## 📊 Estrutura de Resposta

Você receberá algo como:

```json
{
  "final_score": 72.5,
  "risk_level": "Alto",
  "synthesis": "Análise identificou múltiplos fatores...",
  "consolidated_factors": [
    {
      "factor": "Controle Financeiro Total",
      "severity": "Alto",
      "description": "..."
    }
  ],
  "recommendations": [
    "Buscar apoio de rede de suporte",
    "..."
  ]
}
```

---

## 🎯 Próximos Passos

1. **Ver Logs:** Pasta `logs/` tem histórico completo
2. **Modificar Dados:** Edite arquivos em `data/dataset_*.csv`
3. **Ajustar Prompts:** Veja `prompts/system_prompts.py`
4. **Documentação:** Leia `README.md` para detalhes

---

## ⚠️ Problemas Comuns

### "GROQ_API_KEY not found"
→ Edite `.env` e adicione a chave

### "Port 8000 already in use"  
→ Feche outras instâncias do servidor

### Scripts .bat não funcionam
→ Use o Método 2 (linha de comando manual)

### Testes falhando
→ Verifique se o `.env` está configurado

---

## 📞 Precisa de Ajuda?

1. Veja `SETUP_GUIDE.md` para guia detalhado
2. Veja `README.md` para documentação completa
3. Execute `python tests/test_system.py` para diagnóstico

---

**Tempo estimado: 5 minutos** ⏱️

**Pronto para usar!** 🎉
